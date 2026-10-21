package com.deadline.caseload;

import com.deadline.DeadLine;
import com.deadline.caseload.sites.SiteBuilder;
import com.deadline.entity.AnchorEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
import com.deadline.net.PhoneActionPayload;
import com.deadline.net.PhoneDataPayload;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/** The hotline: incoming calls, accepting cases, travelling to the haunted site and back. */
public final class CaseManager {
	/** Ticks between calls (randomised in this range). */
	public static int callMinTicks = 2400;
	public static int callMaxTicks = 6000;
	public static final int MAX_PENDING = 3;

	/** Shop: item -> price. Order is the order shown in the phone. */
	public static final List<ShopEntry> SHOP = new ArrayList<>();

	public record ShopEntry(Item item, int price, int count) {
	}

	private CaseManager() {
	}

	public static void initShop() {
		if (!SHOP.isEmpty()) {
			return;
		}
		SHOP.add(new ShopEntry(ModItems.HOLY_WATER, 40, 2));
		SHOP.add(new ShopEntry(ModItems.SALT, 60, 1));
		SHOP.add(new ShopEntry(ModItems.PILLS, 50, 2));
		SHOP.add(new ShopEntry(ModItems.FLARE, 45, 2));
		SHOP.add(new ShopEntry(ModItems.CRUCIFIX, 150, 1));
		SHOP.add(new ShopEntry(ModItems.FLASHLIGHT, 100, 1));
		SHOP.add(new ShopEntry(ModItems.EMF, 120, 1));
		SHOP.add(new ShopEntry(ModItems.SPIRIT_JAR, 120, 1));
		SHOP.add(new ShopEntry(ModItems.CAMERA, 180, 1));
		SHOP.add(new ShopEntry(ModItems.SPIRIT_BOX, 200, 1));
		SHOP.add(new ShopEntry(ModItems.ROSARY, 160, 1));
		SHOP.add(new ShopEntry(ModItems.SILVER_DAGGER, 300, 1));
		SHOP.add(new ShopEntry(ModItems.RITUAL_BOOK, 350, 1));
	}

	// ------------------------------------------------------------------ lifecycle hooks
	public static void onJoin(ServerPlayer p) {
		initShop();
		HunterData d = ModAttachments.get(p);
		if (!d.welcomed) {
			d.welcomed = true;
			giveKit(p, false);
			d.nextCall = p.level().getGameTime() + 300;
			p.sendSystemMessage(Component.translatable("deadline.msg.welcome"));
		}
		Fx.sanity(p, d.sanity);
		if (d.active != null && d.active.type.scripted()) {
			com.deadline.director.Run r = com.deadline.director.Director.of(p);
			if (r != null) {
				r.sync(p);
			}
		} else if (d.active != null) {
			Fx.objective(p, d.active.type.key(), d.active.stage);
		}
	}

	public static void giveKit(ServerPlayer p, boolean full) {
		suitUp(p);
		give(p, new ItemStack(ModItems.PHONE));
		give(p, new ItemStack(ModItems.FLASHLIGHT));
		give(p, new ItemStack(ModItems.CRUCIFIX));
		give(p, new ItemStack(ModItems.HOLY_WATER, 4));
		give(p, new ItemStack(ModItems.SALT));
		give(p, new ItemStack(ModItems.EMF));
		give(p, new ItemStack(ModItems.SPIRIT_JAR));
		give(p, new ItemStack(ModItems.PILLS, 2));
		if (full) {
			give(p, new ItemStack(ModItems.SPIRIT_BOX));
			give(p, new ItemStack(ModItems.CAMERA));
			give(p, new ItemStack(ModItems.RITUAL_BOOK));
			give(p, new ItemStack(ModItems.ROSARY));
			give(p, new ItemStack(ModItems.SILVER_DAGGER));
			give(p, new ItemStack(ModItems.FLARE, 4));
		}
	}

	/** Dresses the player in the exorcist's suit (pieces go to the inventory when a slot is already taken). */
	public static void suitUp(ServerPlayer p) {
		equip(p, EquipmentSlot.HEAD, ModItems.EXORCIST_HAT);
		equip(p, EquipmentSlot.CHEST, ModItems.EXORCIST_CASSOCK);
		equip(p, EquipmentSlot.LEGS, ModItems.EXORCIST_SKIRT);
		equip(p, EquipmentSlot.FEET, ModItems.EXORCIST_BOOTS);
	}

	private static void equip(ServerPlayer p, EquipmentSlot slot, net.minecraft.world.item.Item item) {
		if (p.getItemBySlot(slot).is(item) || p.getInventory().contains(new ItemStack(item))) {
			return;
		}
		if (p.getItemBySlot(slot).isEmpty()) {
			p.setItemSlot(slot, new ItemStack(item));
		} else {
			give(p, new ItemStack(item));
		}
	}

	private static void give(Player p, ItemStack stack) {
		if (!p.getInventory().add(stack)) {
			p.drop(stack, false);
		}
	}

	public static void onRespawn(ServerPlayer p, boolean alive) {
		HunterData d = ModAttachments.get(p);
		d.sanity = Math.max(d.sanity, 60.0F);
		Fx.sanity(p, d.sanity);
		if (!alive && d.active != null && d.active.type.scripted()) {
			// death never fails a scripted case: back to the chapter checkpoint (fail forward)
			ActiveCase ac = d.active;
			ServerLevel level = p.level().getServer().getLevel(ac.type.levelKey());
			com.deadline.director.Run run = com.deadline.director.Director.get(ac.type, ac.site);
			if (level != null && run != null) {
				p.teleport(new TeleportTransition(level, run.at("spawn"), Vec3.ZERO, run.yaw("spawn"), 0.0F, TeleportTransition.DO_NOTHING));
				run.checkpoint(p);
				run.say("operadora.muerte", null);
				return;
			}
		}
		if (!alive && d.active != null) {
			ActiveCase ac = d.active;
			cleanupSite(p.level().getServer(), ac);
			d.active = null;
			p.sendSystemMessage(Component.translatable("deadline.msg.case_failed", Component.translatable(ac.type.langKey("place"))));
			Fx.caseEnd(p, false, 0);
		}
	}

	// ------------------------------------------------------------------ ticking
	public static void tick(MinecraftServer server) {
		if (server.getTickCount() % 20 != 0) {
			return;
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			HunterData d = ModAttachments.get(p);
			long now = p.level().getGameTime();
			if (d.active == null) {
				if (d.requests.size() < MAX_PENDING && now >= d.nextCall && hasPhone(p)) {
					ring(p, randomRequest(p, now));
				}
			} else if (!d.active.type.scripted() && d.active.stage >= 3) {
				// legacy cases: stage 3 = solved; scripted cases keep their chapter in stage and end from the script
				if (--d.active.solvedTimer <= 0) {
					returnHome(p, true);
				}
			}
		}
	}

	private static boolean hasPhone(ServerPlayer p) {
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			if (inv.getItem(i).is(ModItems.PHONE)) {
				return true;
			}
		}
		return false;
	}

	private static CaseRequest randomRequest(ServerPlayer p, long now) {
		CaseType[] all = CaseType.values();
		HunterData d = ModAttachments.get(p);
		// Early hunters get the easier cases first.
		int cap = Math.min(all.length, 2 + d.solved);
		CaseType t = all[p.getRandom().nextInt(cap)];
		return new CaseRequest(t, p.getRandom().nextInt(t.callers()), now);
	}

	/** Adds a request and makes the phone ring. */
	public static void ring(ServerPlayer p, CaseRequest req) {
		HunterData d = ModAttachments.get(p);
		d.requests.add(req);
		while (d.requests.size() > MAX_PENDING) {
			d.requests.remove(0);
		}
		long now = p.level().getGameTime();
		d.nextCall = now + callMinTicks + p.getRandom().nextInt(Math.max(1, callMaxTicks - callMinTicks));
		Fx.incomingCall(p, req.type().key(), req.caller());
		p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_VIBRATE, SoundSource.PLAYERS, 0.6F, 1.0F);
		syncPhone(p, false);
	}

	// ------------------------------------------------------------------ phone actions
	public static void handlePhoneAction(ServerPlayer p, PhoneActionPayload a) {
		initShop();
		HunterData d = ModAttachments.get(p);
		switch (a.action()) {
			case PhoneActionPayload.ACCEPT -> {
				if (d.active == null && a.arg() >= 0 && a.arg() < d.requests.size()) {
					CaseRequest req = d.requests.remove(a.arg());
					startCase(p, req);
				}
			}
			case PhoneActionPayload.DECLINE -> {
				if (a.arg() >= 0 && a.arg() < d.requests.size()) {
					d.requests.remove(a.arg());
					p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_HANGUP, SoundSource.PLAYERS, 0.6F, 1.0F);
				}
			}
			case PhoneActionPayload.RETURN_HOME -> {
				if (d.active != null) {
					returnHome(p, !d.active.type.scripted() && d.active.stage >= 3);
				}
			}
			case PhoneActionPayload.ABANDON -> {
				if (d.active != null) {
					returnHome(p, false);
				}
			}
			case PhoneActionPayload.BUY -> {
				if (a.arg() >= 0 && a.arg() < SHOP.size()) {
					ShopEntry e = SHOP.get(a.arg());
					if (d.money >= e.price()) {
						d.money -= e.price();
						give(p, new ItemStack(e.item(), e.count()));
						p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_NOTIFY, SoundSource.PLAYERS, 0.6F, 1.3F);
					} else {
						p.displayClientMessage(Component.translatable("deadline.msg.no_money"), true);
					}
				}
			}
			default -> {
			}
		}
		syncPhone(p, false);
	}

	public static void syncPhone(ServerPlayer p, boolean open) {
		if (!ServerPlayNetworking.canSend(p, PhoneDataPayload.TYPE)) {
			return;
		}
		HunterData d = ModAttachments.get(p);
		long now = p.level().getGameTime();
		List<PhoneDataPayload.Request> reqs = new ArrayList<>();
		for (CaseRequest r : d.requests) {
			reqs.add(new PhoneDataPayload.Request(r.type().key(), r.caller(), (int) Math.max(0, (now - r.createdAt()) / 20)));
		}
		ActiveCase ac = d.active;
		ServerPlayNetworking.send(p, new PhoneDataPayload(open, d.money, d.solved, d.sanity, d.bestiary, reqs,
				ac == null ? "" : ac.type.key(), ac == null ? 0 : ac.caller, ac == null ? 0 : ac.stage, ac == null ? 0 : ac.evidence));
	}

	// ------------------------------------------------------------------ cases
	public static boolean startCase(ServerPlayer p, CaseRequest req) {
		MinecraftServer server = p.level().getServer();
		CaseType type = req.type();
		ServerLevel level = server.getLevel(type.levelKey());
		if (level == null) {
			p.sendSystemMessage(Component.translatable("deadline.msg.no_dimension"));
			DeadLine.LOGGER.error("Case dimension {} is missing", type.levelKey().identifier());
			return false;
		}
		HunterData d = ModAttachments.get(p);
		CaseSites sites = CaseSites.get(server);
		if (type.scripted()) {
			return startScripted(p, req, level, sites);
		}
		int site = sites.allocate(type);
		BlockPos origin = CaseSites.origin(site);
		SiteBuilder builder = type.newBuilder();
		SiteBuilder.Layout layout = builder.build(level, origin, level.getRandom());

		HauntEntity boss = (HauntEntity) type.boss().create(level, EntitySpawnReason.EVENT);
		if (boss != null) {
			boss.snapTo(layout.boss().x, layout.boss().y, layout.boss().z, level.getRandom().nextFloat() * 360, 0);
			boss.setSiteIndex(site);
			boss.setAnchored(true);
			level.addFreshEntity(boss);
		}
		AnchorEntity anchor = ModEntities.ANCHOR.create(level, EntitySpawnReason.EVENT);
		if (anchor != null) {
			anchor.setItem(new ItemStack(type.anchor()));
			anchor.setSiteIndex(site);
			anchor.snapTo(layout.anchor().x, layout.anchor().y, layout.anchor().z, 0, 0);
			level.addFreshEntity(anchor);
		}
		for (SiteBuilder.Extra e : layout.extras()) {
			Entity ent = e.type().create(level, EntitySpawnReason.EVENT);
			if (ent != null) {
				ent.snapTo(e.pos().x, e.pos().y, e.pos().z, level.getRandom().nextFloat() * 360, 0);
				if (ent instanceof HauntEntity h) {
					h.setSiteIndex(site);
				}
				level.addFreshEntity(ent);
			}
		}

		d.active = new ActiveCase(type, site, req.caller(), 0, 0, p.level().dimension().identifier(), p.blockPosition(), level.getGameTime(), 0);
		d.bestiary |= 1 << type.ordinal();
		p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_ACCEPT, SoundSource.PLAYERS, 0.8F, 1.0F);
		Fx.fade(p, 70);
		p.teleport(new TeleportTransition(level, layout.spawn(), Vec3.ZERO, layout.yaw(), 0.0F, TeleportTransition.DO_NOTHING));
		level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.TELEPORT_WHOOSH, SoundSource.PLAYERS, 1.0F, 1.0F);
		Fx.title(p, type.langKey("place"), 100);
		Fx.objective(p, type.key(), 0);
		syncPhone(p, false);
		return true;
	}

	/** Scripted cases: place the Python-authored site in batches during the fade, then start chapter 1. */
	private static boolean startScripted(ServerPlayer p, CaseRequest req, ServerLevel level, CaseSites sites) {
		CaseType type = req.type();
		com.deadline.site.SiteDef def = com.deadline.site.SiteDef.get(level.getServer(), type.script().siteKey());
		if (def == null) {
			p.sendSystemMessage(Component.translatable("deadline.msg.no_dimension"));
			return false;
		}
		HunterData d = ModAttachments.get(p);
		int site = sites.allocate(type);
		BlockPos origin = CaseSites.origin(site);
		d.active = new ActiveCase(type, site, req.caller(), 1, 0, p.level().dimension().identifier(), p.blockPosition(), level.getGameTime(), 0);
		d.bestiary |= 1 << type.ordinal();
		p.level().playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PHONE_ACCEPT, SoundSource.PLAYERS, 0.8F, 1.0F);
		Fx.fade(p, 90);
		com.deadline.director.Run run = com.deadline.director.Director.create(type, site, level, origin, def);
		com.deadline.site.SitePlacer.place(level, origin, def, () -> {
			if (p.isRemoved() || ModAttachments.get(p).active == null) {
				return;
			}
			p.teleport(new TeleportTransition(level, run.at("spawn"), Vec3.ZERO, run.yaw("spawn"), 0.0F, TeleportTransition.DO_NOTHING));
			level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.TELEPORT_WHOOSH, SoundSource.PLAYERS, 1.0F, 1.0F);
			Fx.title(p, type.langKey("place"), 100);
			run.startChapter(1, false);
			syncPhone(p, false);
		});
		syncPhone(p, false);
		return true;
	}

	public static void returnHome(ServerPlayer p, boolean solved) {
		HunterData d = ModAttachments.get(p);
		ActiveCase ac = d.active;
		if (ac == null) {
			return;
		}
		MinecraftServer server = p.level().getServer();
		ServerLevel home = server.getLevel(ResourceKey.create(Registries.DIMENSION, ac.returnDim));
		if (home == null) {
			home = server.overworld();
		}
		if (!solved) {
			cleanupSite(server, ac);
		}
		d.active = null;
		if (ac.type.scripted()) {
			com.deadline.director.Run run = com.deadline.director.Director.get(ac.type, ac.site);
			if (run != null && run.hunters().isEmpty()) {
				com.deadline.director.Director.end(ac.type, ac.site);
			}
		}
		if (solved) {
			int reward = ac.type.reward() + ac.evidence * 50;
			d.money += reward;
			d.solved++;
			Fx.caseEnd(p, true, reward);
		} else {
			Fx.caseEnd(p, false, 0);
		}
		Fx.fade(p, 50);
		BlockPos rp = ac.returnPos;
		p.teleport(new TeleportTransition(home, Vec3.atBottomCenterOf(rp), Vec3.ZERO, p.getYRot(), 0.0F, TeleportTransition.DO_NOTHING));
		SanityManager.add(p, 25.0F);
		syncPhone(p, false);
	}

	private static void cleanupSite(MinecraftServer server, ActiveCase ac) {
		ServerLevel level = server.getLevel(ac.type.levelKey());
		if (level == null) {
			return;
		}
		BlockPos o = CaseSites.origin(ac.site);
		var box = new net.minecraft.world.phys.AABB(o).inflate(200, 128, 200);
		for (Entity e : level.getEntities((Entity) null, box, e -> e instanceof HauntEntity || e instanceof AnchorEntity)) {
			e.discard();
		}
	}

	// ------------------------------------------------------------------ progress events
	private static List<ServerPlayer> huntersOf(ServerLevel level, int site) {
		List<ServerPlayer> out = new ArrayList<>();
		CaseType type = CaseType.forLevel(level.dimension());
		for (ServerPlayer p : level.getServer().getPlayerList().getPlayers()) {
			HunterData d = ModAttachments.get(p);
			if (d.active != null && d.active.type == type && d.active.site == site) {
				out.add(p);
			}
		}
		return out;
	}

	private static void advance(ServerLevel level, int site, int stage, String msgKey) {
		for (ServerPlayer p : huntersOf(level, site)) {
			HunterData d = ModAttachments.get(p);
			if (!d.active.type.scripted() && d.active.stage < stage) {
				d.active.stage = stage;
				Fx.objective(p, d.active.type.key(), stage);
				p.displayClientMessage(Component.translatable(msgKey), false);
				syncPhone(p, false);
			}
		}
	}

	public static void onAnchorPurified(ServerLevel level, AnchorEntity anchor, ServerPlayer by) {
		int site = anchor.siteIndex();
		for (HauntEntity h : level.getEntitiesOfClass(HauntEntity.class, anchor.getBoundingBox().inflate(256, 128, 256))) {
			if (h.siteIndex() == site && h.isAnchored()) {
				h.setAnchored(false);
				h.setTarget(by);
				level.playSound(null, h.getX(), h.getY(), h.getZ(), h.getHurtSoundEvent(), SoundSource.HOSTILE, 3.0F, 0.5F);
			}
		}
		advance(level, site, 1, "deadline.msg.anchor_purified");
		for (ServerPlayer p : huntersOf(level, site)) {
			ModAttachments.get(p).active.evidence++;
		}
	}

	public static void onBossWeakened(HauntEntity boss) {
		if (boss.level() instanceof ServerLevel level && boss.siteIndex() >= 0) {
			advance(level, boss.siteIndex(), 2, boss.requiresExorcism() ? "deadline.msg.stage_exorcise" : "deadline.msg.stage_jar");
		}
	}

	public static void onBossBanished(HauntEntity boss, Player by) {
		if (!(boss.level() instanceof ServerLevel level) || boss.siteIndex() < 0) {
			return;
		}
		if (boss.getType() != CaseType.forLevel(level.dimension()).boss()) {
			return;
		}
		for (ServerPlayer p : huntersOf(level, boss.siteIndex())) {
			HunterData d = ModAttachments.get(p);
			if (d.active.type.scripted()) {
				continue; // the director decides when a scripted case is over
			}
			d.active.stage = 3;
			d.active.solvedTimer = 12;
			Fx.objective(p, d.active.type.key(), 3);
			Fx.title(p, "deadline.title.solved", 80);
			level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.CASE_SOLVED, SoundSource.PLAYERS, 1.0F, 1.0F);
			syncPhone(p, false);
		}
	}

	/** Records evidence (EMF 5, spirit box answer, photo) once per kind per case. */
	public static void evidence(ServerPlayer p, int bit) {
		HunterData d = ModAttachments.get(p);
		if (d.active != null && d.active.evidence < 6) {
			d.active.evidence++;
			p.displayClientMessage(Component.translatable("deadline.msg.evidence", d.active.evidence), true);
		}
	}

	public static boolean inCaseLevel(Level level) {
		return CaseType.forLevel(level.dimension()) != null;
	}
}
