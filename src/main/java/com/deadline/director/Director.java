package com.deadline.director;

import com.deadline.DeadLine;
import com.deadline.caseload.ActiveCase;
import com.deadline.caseload.CaseSites;
import com.deadline.caseload.CaseType;
import com.deadline.caseload.HunterData;
import com.deadline.registry.ModAttachments;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;

/** Keeps one {@link Run} per active scripted site and feeds it ticks and player events. */
public final class Director {
	private static final Map<String, Run> RUNS = new HashMap<>();
	private static final List<Runnable> LATER = new ArrayList<>();
	/** Director-tagged entities that just loaded; the ones no run claims by the next tick are leftovers from disk. */
	private static final List<net.minecraft.world.entity.Entity> LOADED = new ArrayList<>();

	private Director() {
	}

	public static void register() {
		net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
			if (entity.getTags().contains(Props.ACTOR_TAG)) {
				LOADED.add(entity);
			}
		});
		UseBlockCallback.EVENT.register((player, world, hand, hit) -> {
			if (player instanceof ServerPlayer sp) {
				Run r = of(sp);
				if (r != null) {
					BlockPos pos = hit.getBlockPos();
					var st = world.getBlockState(pos);
					if (st.getBlock() instanceof net.minecraft.world.level.block.DoorBlock
							|| st.getBlock() instanceof net.minecraft.world.level.block.TrapDoorBlock) {
						com.deadline.voice.NoiseMeter.add(sp, 10F);
					}
					String m = r.markerAt(pos);
					if (m == null) {
						m = r.markerAt(pos.above());
					}
					if (m == null) {
						m = r.markerAt(pos.relative(hit.getDirection()));  // a prop hanging on the wall that was clicked through
					}
					if (m != null && r.def.doors.containsKey(m) && r.locked(m)) {
						world.playSound(null, pos, net.minecraft.sounds.SoundEvents.CHEST_LOCKED, net.minecraft.sounds.SoundSource.BLOCKS, 1.0F, 0.8F);
						sp.displayClientMessage(net.minecraft.network.chat.Component.translatable("deadline.door.locked"), true);
						return InteractionResult.FAIL;
					}
					if (m != null) {
						r.post("use:" + m);
						if (!r.def.doors.containsKey(m)) {
							return InteractionResult.SUCCESS; // props are story objects, not containers or lecterns
						}
					}
				}
			}
			return InteractionResult.PASS;
		});
		UseItemCallback.EVENT.register((player, world, hand) -> {
			if (player instanceof ServerPlayer sp) {
				Run r = of(sp);
				if (r != null) {
					r.post("item:" + BuiltInRegistries.ITEM.getKey(sp.getItemInHand(hand).getItem()));
				}
			}
			return InteractionResult.PASS;
		});
	}

	static String key(CaseType type, int site) {
		return type.key() + "#" + site;
	}

	/** Creates the run for a freshly placed site (does not start a chapter). */
	public static Run create(CaseType type, int site, ServerLevel level, BlockPos origin, SiteDef def) {
		Run r = new Run(type, site, level, origin, def, type.script());
		Run old = RUNS.put(key(type, site), r);
		if (old != null) {
			old.end();
		}
		return r;
	}

	public static Run get(CaseType type, int site) {
		return RUNS.get(key(type, site));
	}

	/** The run of the case this hunter is working, re-created (at its checkpoint chapter) after a server restart. */
	public static Run of(ServerPlayer p) {
		HunterData d = ModAttachments.get(p);
		ActiveCase ac = d.active;
		if (ac == null || !ac.type.scripted()) {
			return null;
		}
		Run r = RUNS.get(key(ac.type, ac.site));
		if (r == null && p.level() instanceof ServerLevel level && level.dimension().equals(ac.type.levelKey())) {
			SiteDef def = SiteDef.get(level.getServer(), ac.type.script().siteKey());
			if (def == null) {
				return null;
			}
			r = create(ac.type, ac.site, level, CaseSites.origin(ac.site), def);
			// after a restart: back to the checkpoint of the saved chapter and replay it (flags and actors were not saved)
			r.chapter = Math.max(1, ac.stage);
			r.checkpoint(p);
		}
		return r;
	}

	public static void end(CaseType type, int site) {
		Run r = RUNS.remove(key(type, site));
		if (r != null) {
			r.end();
		}
	}

	/** Runs a task at the start of the next server tick. */
	public static void later(Runnable task) {
		LATER.add(task);
	}

	public static void tick(MinecraftServer server) {
		if (!LATER.isEmpty()) {
			List<Runnable> now = new ArrayList<>(LATER);
			LATER.clear();
			now.forEach(Runnable::run);
		}
		if (!LOADED.isEmpty()) {
			for (net.minecraft.world.entity.Entity e : LOADED) {
				if (!e.isRemoved() && RUNS.values().stream().noneMatch(r -> r.actors.containsValue(e))) {
					e.discard();
				}
			}
			LOADED.clear();
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			of(p); // lazily restores runs after a restart
		}
		List<Run> runs = new ArrayList<>(RUNS.values());
		for (Run r : runs) {
			try {
				r.tick();
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Director run {} failed", r.type.key(), ex);
			}
		}
	}

	public static void clear() {
		for (Run r : RUNS.values()) {
			r.end();
		}
		RUNS.clear();
	}
}
