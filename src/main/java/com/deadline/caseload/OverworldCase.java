package com.deadline.caseload;

import com.deadline.car.CarKeysItem;
import com.deadline.car.GpsPayload;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModSounds;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gamerules.GameRules;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Overworld cases (the Casa Morales, docs/design/casa_terror.md 2 and 6.9-6.10): accepting one places the site in the
 * real overworld (once; afterwards it is re-placed at the same stored origin), gives the car keys and the car, and
 * points the GPS at the house. While any online hunter works an overworld case the world clock is taken to night and
 * frozen there (restored when nobody works one any more) and natural hostile mobs never load near the house.
 */
public final class OverworldCase {
	/** Natural hostile mobs are discarded within the site box grown by this many blocks. */
	public static final int MOB_RADIUS = 48;
	/** The night the clock is frozen at (time of day), and how fast the clock runs there (ticks of day per tick). */
	public static final long NIGHT = 18000L;
	private static final long RAMP = 60L;
	/** The GPS hides within this distance of the arrival marker. */
	public static final double GPS_HIDE = 30.0;

	private static final List<Entity> LOADED = new ArrayList<>();
	private static final Set<UUID> GPS_ON = new HashSet<>();
	/** Site boxes of the overworld cases being worked, refreshed every second. */
	private static final Map<CaseType, AABB> ZONES = new HashMap<>();
	/** Absolute day time the frozen clock is still being wound to (-1: none). */
	private static long rampTo = -1;

	private OverworldCase() {
	}

	public static void register() {
		ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
			if (world.dimension().equals(Level.OVERWORLD) && naturalHostile(entity)) {
				LOADED.add(entity); // discarded next tick if it is near a house (never inside the load callback)
			}
		});
		ServerTickEvents.END_SERVER_TICK.register(OverworldCase::tick);
		ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
			GPS_ON.remove(handler.getPlayer().getUUID());
			syncGps(handler.getPlayer());
		});
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> GPS_ON.remove(handler.getPlayer().getUUID()));
		ServerLifecycleEvents.SERVER_STARTED.register(OverworldSite::resume);
		ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
			OverworldSite.clear();
			LOADED.clear();
			GPS_ON.clear();
			ZONES.clear();
			rampTo = -1;
		});
	}

	/** A vanilla hostile mob (zombies, skeletons, creepers, spiders, phantoms...): never one of ours, never named. */
	public static boolean naturalHostile(Entity e) {
		return e.getType().getCategory() == MobCategory.MONSTER && !e.hasCustomName()
				&& "minecraft".equals(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace());
	}

	// ------------------------------------------------------------------ starting / ending
	/**
	 * Accepting an overworld case: no teleport. The site is found (first time) or reused, levelled and placed in batches
	 * (unless a hunter is already playing it: then the new hunter joins that run), chapter 1 starts, the hunter gets the
	 * car keys and the car, and the GPS points at the house.
	 */
	public static boolean start(ServerPlayer p, CaseRequest req, ServerLevel level, SiteDef def) {
		CaseType type = req.type();
		CaseSites sites = CaseSites.get(level.getServer());
		HunterData d = ModAttachments.get(p);
		int site = 0;
		BlockPos origin = sites.overworldOrigin(type);
		if (origin == null) {
			origin = OverworldSite.findOrigin(level, p.blockPosition(), def, level.getRandom());
			sites.setOverworldOrigin(type, origin);
		}
		d.active = new ActiveCase(type, site, req.caller(), 1, 0, p.level().dimension().identifier(), p.blockPosition(), level.getGameTime(), 0);
		d.bestiary |= 1 << type.ordinal();
		p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_ACCEPT, SoundSource.PLAYERS, 0.8F, 1.0F);
		Run run = Director.get(type, site);
		boolean others = false;
		if (run != null) {
			for (ServerPlayer h : run.hunters()) {
				others |= h != p;
			}
		}
		if (others) {
			run.sync(p); // somebody is in the house right now: join their night instead of rebuilding it under them
		} else {
			run = Director.create(type, site, level, origin, def);
			if (!OverworldSite.busy(type)) {
				OverworldSite.prepareAndPlace(level, type, origin, def, null);
			}
			run.startChapter(1, false);
		}
		CarKeysItem.giveForCase(p, arrival(origin, def));
		GPS_ON.remove(p.getUUID());
		syncGps(p);
		CaseManager.syncPhone(p, false);
		return true;
	}

	/** The hunter left an overworld case (solved, abandoned, sent home): nobody is teleported, the house stays. */
	public static void ended(ServerPlayer p) {
		syncGps(p);
	}

	/** Entities of a finished case to clean up: the site box + 48, or null while other hunters still work the house. */
	public static AABB cleanupBox(MinecraftServer server, ActiveCase ac) {
		for (ServerPlayer h : server.getPlayerList().getPlayers()) {
			ActiveCase other = ModAttachments.get(h).active;
			if (other != null && other != ac && other.type == ac.type) {
				return null;
			}
		}
		return siteBox(server, ac.type, MOB_RADIUS);
	}

	/** The placed site's bounding box grown by `grow` blocks (null before the site has an origin). */
	public static AABB siteBox(MinecraftServer server, CaseType type, double grow) {
		BlockPos o = CaseSites.get(server).overworldOrigin(type);
		SiteDef def = type.script() == null ? null : SiteDef.get(server, type.script().siteKey());
		if (o == null || def == null) {
			return null;
		}
		return new AABB(o.offset(def.min)).expandTowards(def.w, def.h, def.d).inflate(grow);
	}

	/** True while a hunter working an overworld case is at its house (8 blocks around the site's box). */
	public static boolean atSite(ServerPlayer p) {
		ActiveCase ac = ModAttachments.get(p).active;
		if (ac == null || !ac.type.overworld() || !p.level().dimension().equals(Level.OVERWORLD)) {
			return false;
		}
		AABB box = siteBox(p.level().getServer(), ac.type, 8);
		return box != null && box.contains(p.position());
	}

	/** World position of the arrival marker ("llegada", fallback "spawn"). */
	public static Vec3 arrival(BlockPos origin, SiteDef def) {
		return def.point(def.points.containsKey("llegada") ? "llegada" : "spawn").at(origin);
	}

	/** The arrival point of the overworld case a hunter works, or null. */
	public static Vec3 target(ServerPlayer p) {
		ActiveCase ac = ModAttachments.get(p).active;
		if (ac == null || !ac.type.overworld() || ac.type.script() == null) {
			return null;
		}
		MinecraftServer server = p.level().getServer();
		BlockPos o = CaseSites.get(server).overworldOrigin(ac.type);
		SiteDef def = SiteDef.get(server, ac.type.script().siteKey());
		return o == null || def == null ? null : arrival(o, def);
	}

	// ------------------------------------------------------------------ GPS
	/** Sends the GPS target (or hides the GPS) when it changed. */
	public static void syncGps(ServerPlayer p) {
		Vec3 t = target(p);
		boolean on = t != null;
		if (on == GPS_ON.contains(p.getUUID()) || !ServerPlayNetworking.canSend(p, GpsPayload.TYPE)) {
			return;
		}
		if (on) {
			GPS_ON.add(p.getUUID());
			ServerPlayNetworking.send(p, new GpsPayload(true, t.x, t.y, t.z, ModAttachments.get(p).active.type.key()));
		} else {
			GPS_ON.remove(p.getUUID());
			ServerPlayNetworking.send(p, new GpsPayload(false, 0, 0, 0, ""));
		}
	}

	// ------------------------------------------------------------------ ticking
	private static void tick(MinecraftServer server) {
		OverworldSite.tick(server);
		ServerLevel ow = server.overworld();
		if (server.getTickCount() % 20 == 0) {
			refresh(server, ow);
		}
		if (!LOADED.isEmpty()) {
			for (Entity e : LOADED) {
				if (!e.isRemoved() && inZone(e)) {
					e.discard();
				}
			}
			LOADED.clear();
		}
		if (rampTo > 0 && !ZONES.isEmpty() && CaseSites.get(server).timeFrozen) {
			// the clock runs fast to the night (a few seconds of sky racing by) and stops there
			long now = ow.getDayTime();
			if (now < rampTo) {
				ow.setDayTime(Math.min(now + RAMP, rampTo));
			} else {
				rampTo = -1;
			}
		}
	}

	/** Where the clock is taken when an overworld case freezes it: on to the next NIGHT, or nowhere if it is night already. */
	private static long nightTarget(long now) {
		long tod = Math.floorMod(now, 24000L);
		return tod >= 13000L && tod <= 23000L ? -1 : now + Math.floorMod(NIGHT - tod, 24000L);
	}

	private static boolean inZone(Entity e) {
		for (AABB z : ZONES.values()) {
			if (z.contains(e.position())) {
				return true;
			}
		}
		return false;
	}

	/** Every second: which houses are being worked, the hostile sweep, the frozen clock and the GPS of everyone. */
	private static void refresh(MinecraftServer server, ServerLevel ow) {
		ZONES.clear();
		List<ServerPlayer> players = server.getPlayerList().getPlayers();
		for (ServerPlayer p : players) {
			ActiveCase ac = ModAttachments.get(p).active;
			if (ac != null && ac.type.overworld() && !ZONES.containsKey(ac.type)) {
				AABB box = siteBox(server, ac.type, MOB_RADIUS);
				if (box != null) {
					ZONES.put(ac.type, box);
				}
			}
			syncGps(p);
		}
		for (AABB z : ZONES.values()) {
			for (Entity e : ow.getEntities((Entity) null, z, OverworldCase::naturalHostile)) {
				e.discard();
			}
		}
		CaseSites sites = CaseSites.get(server);
		GameRules rules = ow.getGameRules();
		if (!ZONES.isEmpty() && !sites.timeFrozen) {
			sites.savedAdvanceTime = rules.get(GameRules.ADVANCE_TIME);
			sites.savedDayTime = ow.getDayTime();
			sites.timeFrozen = true;
			sites.setDirty();
			rules.set(GameRules.ADVANCE_TIME, false, server);
			rampTo = nightTarget(ow.getDayTime());
		} else if (ZONES.isEmpty() && sites.timeFrozen && !players.isEmpty()) {
			// nobody online works an overworld case any more: give the world its clock back
			rules.set(GameRules.ADVANCE_TIME, sites.savedAdvanceTime, server);
			ow.setDayTime(sites.savedDayTime);
			rampTo = -1;
			sites.timeFrozen = false;
			sites.setDirty();
		}
	}
}
