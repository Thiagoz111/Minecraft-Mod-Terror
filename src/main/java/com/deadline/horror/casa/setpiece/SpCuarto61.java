package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.director.Run;
import com.deadline.entity.MunecaEntity;
import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.hunt.HuntEntities;
import com.deadline.horror.casa.hunt.NonaRotaEntity;
import com.deadline.item.FlashlightItem;
import com.deadline.item.FlashlightLights;
import com.deadline.item.ItemUtil;
import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Act 6 (design 2, "El cuarto de 1961"): behind the broken wall of the basement, the sealed room -- sand on the floor,
 * the iron bed with its straps, the old salt circle, LEMAZA scratched into the walls. The whole family stands there,
 * each one with the face to a wall, perfectly still, murmuring; Ofelia sits on the bed with her back to him. When he
 * steps in, every head turns round at once, 180 degrees, the bodies not moving -- the cracks of four necks, the doll's
 * porcelain creak. The candles go out; the flashlight dies. When he gets it back on: the Nona, hanging from the ceiling
 * right over him like a spider, her face turned down at his. She screams. Then she is gone and something runs on all
 * fours behind him, all the way up: and the hall of the ground floor, on the way to the front door, goes on and on --
 * twice, as he reaches the entrance hall, he is back at the basement door at the far end of it (P.T.). The third time
 * the hall ends, and the front door, bolted all night, now stands open. Posts {@code cuarto61:fin} there (or once he is
 * out of it).
 * <p>CasaScript fires it as he reaches the basement (the family is put in the room while he cannot see into it).
 */
public class SpCuarto61 extends HorrorEvent {
	private static final int WAIT = 0, TURN = 1, DARK = 2, RUN = 3;
	private static final String[] WHO = {Stage.MARTA, Stage.JORGE, Stage.LUCIA, Stage.TOTI};
	private static final int LOOPS = 2;
	/** Distance along the hall he is sent back each time it "repeats" when the site has no entrance hall (fallback). */
	private static final double LOOP_BACK = 20.0;
	/** Ticks the heads take to come round before the blackout; the run-up after which the front door opens anyway. */
	private static final int TURN_TICKS = 64, RUN_DOOR_ANYWAY = 20 * 100;

	public SpCuarto61() {
		super("sp_cuarto61", Kind.SETPIECE);
		this.acts(6, 6).intensity(5).cooldown(600).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.hasArea(c.run, "cuarto61") || !Apparitions.has(c.run, "familia61_1")) {
			return false;
		}
		return Stage.in(c.run, c.p, "cuarto61") || Stage.in(c.run, c.p, "sotano");
	}

	@Override
	public void start(Ctx c) {
		c.put("phase", WAIT);
		c.put("phaseAt", 0);
		c.put("spawned", false);
		c.put("loops", 0);
		c.put("inside", 0);
		c.put("still", 0);
		c.put("tapDist", 6.0);
		if (c.run.def.groups.containsKey("cuarto61_velas")) {
			c.run.lights("cuarto61_velas", true);  // the old candles lit, by nobody
		}
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.t >= maxTicks() - 1) {
			// safety net (he never made it): the way out opens all the same, the act goes on
			openFrontDoor(c);
			c.run.post("cuarto61:fin");
			c.put("done", true);
			return true;
		}
		int phase = c.get("phase");
		if (phase != WAIT && Apparitions.hidden(c.p)) {
			c.put("phaseAt", c.<Integer>get("phaseAt") + 1);  // never on a hidden hunter: the scene holds its breath
			return false;
		}
		int k = c.t - c.<Integer>get("phaseAt");
		return switch (phase) {
			case WAIT -> waiting(c);
			case TURN -> turning(c, k);
			case DARK -> dark(c, k);
			default -> running(c, k);
		};
	}

	// ------------------------------------------------------------------ the family facing the walls
	private boolean waiting(Ctx c) {
		Run r = c.run;
		if (!c.<Boolean>get("spawned")) {
			boolean seen = false;
			for (int i = 1; i <= 4; i++) {
				Vec3 v = Apparitions.at(r, "familia61_" + i);
				seen |= v != null && Apparitions.sees(c, v.add(0, 1.0, 0), 80F);
			}
			if (!seen || c.t > 20 * 6) {
				spawnFamily(c);
				c.put("spawned", true);
			}
			return false;
		}
		if (c.t % 100 == 30 && c.p.position().distanceTo(r.at("familia61_1")) < 16.0) {
			// a murmur through the hole in the wall: four voices, the same word, backwards
			Vec3 mid = Apparitions.has(r, "cuarto61") ? r.at("cuarto61").add(0, 1.2, 0) : r.at("familia61_1");
			r.sound(ModSounds.MONJA_WHISPER, mid, 0.5F, 0.6F);
		}
		int inside = Stage.in(r, c.p, "cuarto61") ? c.<Integer>get("inside") + 1 : 0;
		c.put("inside", inside);
		if (inside >= 25 || Apparitions.has(r, "cuarto61") && c.p.position().distanceTo(r.at("cuarto61")) < 3.0) {
			next(c, TURN);
		}
		return false;
	}

	private void spawnFamily(Ctx c) {
		Run r = c.run;
		for (int i = 0; i < WHO.length; i++) {
			String m = "familia61_" + (i + 1);
			if (!Apparitions.has(r, m)) {
				continue;
			}
			Vec3 v = r.at(m);
			float yaw = r.yaw(m);  // the marker looks at the wall
			if (WHO[i].equals(Stage.LUCIA)) {
				PoseidaEntity l = Apparitions.spawn(c, ModEntities.POSEIDA, v, yaw);
				if (l != null) {
					l.setVariant(PoseidaEntity.LOOK_POSSESSED);
					l.setAction(PoseidaEntity.ACT_IDLE);
				}
				c.put("lucia", l);
			} else {
				FamilyEntity f = Apparitions.spawn(c, Stage.type(WHO[i]), v, yaw);
				if (f != null) {
					f.setVariant(FamilyEntity.LOOK_COPIA);
					f.setAction(FamilyEntity.POSE_CORNER);
					f.watchPlayers(false);
				}
				c.put(WHO[i], f);
			}
		}
		// Ofelia sitting on the iron bed, her back to the hole he comes in by (her head turns with theirs)
		Vec3 bed = bedTop(c);
		if (bed != null) {
			Vec3 hole = Apparitions.has(r, "sotano_pared") ? r.at("sotano_pared") : c.p.position();
			MunecaEntity doll = Apparitions.spawn(c, ModEntities.MUNECA, bed, Apparitions.yawTo(hole, bed));
			if (doll != null) {
				doll.setNoGravity(true);
				doll.setAction(MunecaEntity.ACT_SIT);
			}
			c.put("ofelia", doll);
		}
	}

	private static Vec3 bedTop(Ctx c) {
		Vec3 m = Apparitions.at(c.run, "cuarto61_cama");
		if (m == null) {
			return null;
		}
		BlockPos bed = Stage.kitNear(c.run, m, "cama", 2);
		return bed != null ? Stage.top(c.run, bed) : null;
	}

	// ------------------------------------------------------------------ every head turns
	private boolean turning(Ctx c, int k) {
		Run r = c.run;
		if (k == 0) {
			for (String who : WHO) {
				Entity e = c.get(who);
				if (e instanceof FamilyEntity f) {
					f.setAction(FamilyEntity.POSE_CORNER_TURN);
				} else if (e instanceof PoseidaEntity l) {
					l.setAction(PoseidaEntity.ACT_HEADSPIN);
				}
				if (e != null) {
					r.sound(ModSounds.APARICION_CUELLO, e.getEyePosition(), 1.1F, 0.8F + c.rnd.nextFloat() * 0.2F);
				}
			}
			if (c.get("ofelia") instanceof MunecaEntity doll && !doll.isRemoved()) {
				doll.setAction(MunecaEntity.ACT_SIT_TURN);
				r.sound(ModSounds.DOLL_TURN, doll.position().add(0, 0.5, 0), 0.9F, 0.85F);
			}
			Vec3 mid = Apparitions.has(r, "cuarto61") ? r.at("cuarto61").add(0, 1.2, 0) : c.p.getEyePosition();
			r.sound(ModSounds.APARICION_COPIA, mid, 1.0F, 0.85F);
			Fx.shake(c.p, 0.35F, 20);
		}
		if (k == 14) {
			for (String who : WHO) {
				Entity e = c.get(who);
				if (e != null) {
					r.sound(ModSounds.APARICION_CUELLO, e.getEyePosition(), 1.2F, 0.7F);
				}
			}
		}
		if (k >= TURN_TICKS) {
			blackout(c);
			next(c, DARK);
		}
		return false;
	}

	/** The candles go out, the flashlight dies; the family is not there any more. Over him, on the ceiling: her. */
	private void blackout(Ctx c) {
		Run r = c.run;
		if (r.def.groups.containsKey("cuarto61_velas")) {
			r.lights("cuarto61_velas", false);
		}
		if (r.def.groups.containsKey("luces_cuarto61")) {
			r.lights("luces_cuarto61", false);
		}
		r.sound(ModSounds.CANDLES_OUT, c.p.getEyePosition(), 1.2F, 0.8F);
		r.sound(ModSounds.FLASHLIGHT_FLICKER, c.p.getEyePosition(), 1.0F, 0.8F);
		r.sound(ModSounds.HORROR_HEARTBEAT, c.p.getEyePosition(), 1.0F, 1.0F);
		killFlashlight(c.p);
		Apparitions.despawnAll(c);
		for (String who : WHO) {
			c.put(who, null);
		}
		c.put("lucia", null);
		c.put("ofelia", null);
		// the Nona, hanging from the ceiling right over him (box top on the ceiling, the model hangs in it)
		double ceil = Apparitions.ceilingY(r, c.p.getEyePosition());
		if (!Double.isNaN(ceil)) {
			Vec3 at = new Vec3(c.p.getX(), ceil - 1.45, c.p.getZ());
			NonaRotaEntity n = Apparitions.spawn(c, HuntEntities.NONA_ROTA, at, c.p.getYRot() + 180F);
			if (n != null) {
				n.setNoGravity(true);
				n.setVariant(NonaRotaEntity.LOOK_ROTA);
				n.holdPose(NonaRotaEntity.ACT_CEILING);
			}
			c.put("nona", n);
		}
	}

	/** Off goes the flashlight in his hand (he has to switch it back on). */
	private static void killFlashlight(ServerPlayer p) {
		for (ItemStack s : new ItemStack[] {p.getMainHandItem(), p.getOffhandItem()}) {
			if (s.is(ModItems.FLASHLIGHT) && FlashlightItem.isOn(s)) {
				ItemUtil.setFlags(s, false, FlashlightItem.isUv(s));
			}
		}
		FlashlightLights.clear(p);
	}

	// ------------------------------------------------------------------ the ceiling
	private boolean dark(Ctx c, int k) {
		NonaRotaEntity n = c.get("nona");
		if (Apparitions.gone(n)) {
			next(c, RUN);
			return false;
		}
		// she stays over him (he may step back: so does she)
		if (k % 2 == 0 && k < 200) {
			double ceil = Apparitions.ceilingY(c.run, c.p.getEyePosition());
			if (!Double.isNaN(ceil) && n.position().distanceTo(new Vec3(c.p.getX(), n.getY(), c.p.getZ())) > 1.6) {
				Apparitions.glide(n, new Vec3(c.p.getX(), ceil - 1.45, c.p.getZ()), false);
			}
		}
		if (k % 30 == 10) {
			c.run.sound(ModSounds.HUNT_SNIFF, n.position().add(0, 0.6, 0), 0.6F, 0.8F);
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean light = com.deadline.director.Props.lit(c.p) || Apparitions.light(c.run, n.position()) >= 4;
		g.update(light && Apparitions.watches(c, n, 35F));
		Integer screamAt = c.get("screamAt");
		if (screamAt == null && (g.seen >= 5 || k > 20 * 9)) {
			screamAt = c.t;
			c.put("screamAt", screamAt);
			c.run.sound(ModSounds.HUNT_SCREAM, n.position(), 2.4F, 1.0F);
			if (c.haunt.canJumpscare()) {
				Fx.jumpscare(c.p, "nona_rota");
				c.haunt.jumpscared();
			} else {
				Fx.redFlash(c.p, 0.6F);
			}
			Fx.shake(c.p, 1.4F, 24);
			Apparitions.noise(c, n.position(), 100F);
		}
		if (screamAt != null && c.t - screamAt >= 10) {
			// she drops into the dark -- and is behind him
			Apparitions.vanish(n, true);
			c.put("nona", null);
			next(c, RUN);
		}
		return false;
	}

	// ------------------------------------------------------------------ the run up, and the hall that repeats
	private boolean running(Ctx c, int k) {
		Run r = c.run;
		ServerPlayer p = c.p;
		// something on all fours behind him: closer whenever he stops
		boolean moving = p.getDeltaMovement().horizontalDistance() > 0.05;
		int still = moving ? 0 : c.<Integer>get("still") + 1;
		c.put("still", still);
		double tap = c.get("tapDist");
		tap = moving ? Math.min(6.0, tap + 0.02) : still > 30 ? Math.max(1.6, tap - 0.05) : tap;
		c.put("tapDist", tap);
		if (k % 5 == 0 && !nearDoor(c)) {
			Vec3 behind = p.position().subtract(Stage.look(p).scale(tap));
			r.sound(ModSounds.HUNT_CRAWL_TAP, behind.add(0, 0.3, 0), 0.9F, 0.9F + c.rnd.nextFloat() * 0.2F);
			if (k % 60 == 0) {
				r.sound(c.rnd.nextBoolean() ? ModSounds.HUNT_HISS : ModSounds.HUNT_GROAN, behind.add(0, 0.6, 0), 1.0F, 0.85F);
			}
		}
		if (tap <= 1.7 && still > 0 && still % 40 == 0) {
			// right at his neck: a breath -- she never takes him here, she wants him to run
			r.sound(ModSounds.APARICION_ALIENTO, p.getEyePosition().subtract(Stage.look(p).scale(0.5)), 1.1F, 0.8F);
			Fx.shake(p, 0.5F, 10);
			c.put("tapDist", 4.0);
		}
		hallLoop(c);
		hallLamps(c);
		// the front door: bolted all night, open now -- once the hall has let him go (or it never could hold him)
		Vec3 door = HouseQuery.doorPos(r, "entrada");
		boolean lapsDone = c.<Integer>get("loops") >= LOOPS || !loopable(c) || k > RUN_DOOR_ANYWAY;
		if (c.get("doorOpen") == null && lapsDone && c.get("loopAt") == null && door != null && p.position().distanceTo(door) < 14.0) {
			openFrontDoor(c);
			r.sound(ModSounds.SP_PUERTA_CRUJE, door, 1.0F, 0.8F);
		}
		boolean out = c.get("doorOpen") != null && !HouseQuery.inHouse(r, p);
		if (nearDoor(c) && c.get("doorOpen") != null || out) {
			r.post("cuarto61:fin");
			c.put("done", true);
			return true;
		}
		return false;
	}

	private static void openFrontDoor(Ctx c) {
		if (c.get("doorOpen") == null && c.run.def.doors.containsKey("entrada")) {
			c.run.door("entrada", true, false);
			c.put("doorOpen", true);
		}
	}

	/** At the front door (inside, a few steps from it): the way out is open. */
	private static boolean nearDoor(Ctx c) {
		Vec3 door = HouseQuery.doorPos(c.run, "entrada");
		return door != null && c.p.position().distanceTo(door) < 3.2 && HouseQuery.inHouse(c.run, c.p);
	}

	/**
	 * P.T.: running down the ground-floor hall toward the front of the house, as he reaches the entrance hall he is back
	 * at the far end of it, by the basement door, facing the way he was running -- twice. A blink of black hides the seam;
	 * each lap something is different. (A site without an entrance hall: near the front end of the hall he is sent back
	 * {@link #LOOP_BACK} blocks along it.)
	 */
	private void hallLoop(Ctx c) {
		Run r = c.run;
		ServerPlayer p = c.p;
		Integer pending = c.get("loopAt");
		if (pending != null) {
			if (c.t - pending >= 7) {
				Vec3 to = c.get("loopTo");
				float yaw = c.get("loopYaw");
				p.teleportTo(r.level, to.x, to.y, to.z, java.util.Set.of(), yaw, p.getXRot(), false);
				int loops = c.<Integer>get("loops") + 1;
				c.put("loops", loops);
				c.put("lastLoop", c.t);
				lapChange(c, loops);
				c.put("loopAt", null);
			}
			return;
		}
		Integer last = c.get("lastLoop");
		if (c.<Integer>get("loops") >= LOOPS || last != null && c.t - last < 60) {
			return;
		}
		Vec3 to = null;
		float yaw = p.getYRot();
		Vec3[] start = corridorStart(c);
		if (start != null && Apparitions.hasArea(r, "hall")) {
			if (Stage.in(r, p, "hall")) {
				to = start[0];
				yaw = Stage.yawTo(Vec3.ZERO, start[1]);
			}
		} else {
			to = sentBack(c);
		}
		if (to == null) {
			return;
		}
		Fx.fade(p, 14);
		c.put("loopAt", c.t);
		c.put("loopTo", to);
		c.put("loopYaw", yaw);
	}

	/**
	 * Where the ground-floor hall begins (a step from its far end, pasillo_pb_fondo, by the basement door) and the unit
	 * direction along it toward the front door; null when the site lacks the markers or there is no floor there.
	 */
	private static Vec3[] corridorStart(Ctx c) {
		Run r = c.run;
		Vec3 fondo = Apparitions.at(r, "pasillo_pb_fondo");
		Vec3 door = HouseQuery.doorPos(r, "entrada");
		if (fondo == null || door == null || !Apparitions.hasArea(r, "pasillo_pb")) {
			return null;
		}
		AABB hall = r.area("pasillo_pb");
		boolean alongX = hall.getXsize() >= hall.getZsize();
		double sign = Math.signum(alongX ? door.x - fondo.x : door.z - fondo.z);
		if (sign == 0.0) {
			return null;
		}
		Vec3 dir = alongX ? new Vec3(sign, 0, 0) : new Vec3(0, 0, sign);
		Vec3 at = Stage.stand(r, fondo.add(dir.scale(2.5)));
		return at == null || at.distanceTo(door) < 15.0 ? null : new Vec3[] {at, dir};
	}

	/** The fallback loop: near the front end of the hall, heading that way, he is sent back along it. */
	private static Vec3 sentBack(Ctx c) {
		Run r = c.run;
		if (!Apparitions.hasArea(r, "pasillo_pb") || !Stage.in(r, c.p, "pasillo_pb")) {
			return null;
		}
		Vec3 door = HouseQuery.doorPos(r, "entrada");
		if (door == null) {
			return null;
		}
		AABB hall = r.area("pasillo_pb");
		boolean alongX = hall.getXsize() >= hall.getZsize();
		double len = alongX ? hall.getXsize() : hall.getZsize();
		if (len < LOOP_BACK + 6.0) {
			return null;
		}
		// which end of the hall is the front (the end nearer the front door), and how far he is from it
		double pos = alongX ? c.p.getX() : c.p.getZ();
		double lo = alongX ? hall.minX : hall.minZ;
		double hi = alongX ? hall.maxX : hall.maxZ;
		double doorAxis = alongX ? door.x : door.z;
		boolean frontHigh = Math.abs(doorAxis - hi) < Math.abs(doorAxis - lo);
		double toFront = frontHigh ? hi - pos : pos - lo;
		Vec3 look = Stage.look(c.p);
		double heading = (alongX ? look.x : look.z) * (frontHigh ? 1.0 : -1.0);
		if (toFront > 6.0 || heading < 0.3) {
			return null;
		}
		double back = frontHigh ? -LOOP_BACK : LOOP_BACK;
		Vec3 to = c.p.position().add(alongX ? back : 0, 0, alongX ? 0 : back);
		Vec3 ok = Stage.stand(r, to);
		return ok == null ? null : new Vec3(to.x, ok.y, to.z);
	}

	/** True when this site lets the hall repeat at all (otherwise the front door simply opens). */
	private static boolean loopable(Ctx c) {
		if (corridorStart(c) != null && Apparitions.hasArea(c.run, "hall")) {
			return true;
		}
		if (!Apparitions.hasArea(c.run, "pasillo_pb") || HouseQuery.doorPos(c.run, "entrada") == null) {
			return false;
		}
		AABB hall = c.run.area("pasillo_pb");
		return Math.max(hall.getXsize(), hall.getZsize()) >= LOOP_BACK + 6.0;
	}

	/** What is different each time the hall comes round again. */
	private void lapChange(Ctx c, int lap) {
		Run r = c.run;
		if (lap == 1) {
			// the basement door, right behind him, slams
			if (r.def.doors.containsKey("sotano")) {
				r.door("sotano", false, true);
			}
			r.sound(ModSounds.AMBIENT_STINGER, c.p.getEyePosition(), 0.7F, 0.6F);
		} else {
			// the hall lamps come on one after the other toward the front of the house, then burst behind him
			List<BlockPos> g = r.def.group("luces_pasillo_pb");
			List<Integer> order = new ArrayList<>();
			for (int i = 0; i < g.size(); i++) {
				order.add(i);
			}
			Vec3 door = HouseQuery.doorPos(r, "entrada");
			if (door != null) {
				order.sort((a, b) -> Double.compare(Vec3.atCenterOf(r.origin.offset(g.get(b))).distanceTo(door),
						Vec3.atCenterOf(r.origin.offset(g.get(a))).distanceTo(door)));
			}
			c.put("lampOrder", order);
			c.put("lampAt", c.t);
		}
		c.put("tapDist", 3.0);
	}

	/** Second lap: the lamps light up one by one toward the front, then all of them burst at once. */
	private void hallLamps(Ctx c) {
		List<Integer> order = c.get("lampOrder");
		Integer at = c.get("lampAt");
		if (order == null || at == null) {
			return;
		}
		int k = c.t - at;
		int i = k / 5;
		if (k % 5 == 0 && i < order.size()) {
			c.run.light("luces_pasillo_pb", order.get(i), true);
		}
		if (k >= order.size() * 5 + 16) {
			List<BlockPos> g = c.run.def.group("luces_pasillo_pb");
			for (int j = 0; j < g.size(); j++) {
				if (j % 2 == 0) {
					c.run.sound(ModSounds.BULB_POP, Vec3.atCenterOf(c.run.origin.offset(g.get(j))), 1.0F, 0.8F + 0.05F * j);
				}
			}
			c.run.lights("luces_pasillo_pb", false);
			c.put("lampAt", null);
		}
	}

	private static void next(Ctx c, int phase) {
		c.put("phase", phase);
		c.put("phaseAt", c.t);
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		Run r = c.run;
		if (r.def.groups.containsKey("cuarto61_velas")) {
			r.lights("cuarto61_velas", false);
		}
		List<Integer> order = c.get("lampOrder");
		if (order != null) {
			r.lights("luces_pasillo_pb", false);
		}
		if (c.get("done") == null && c.get("doorOpen") != null) {
			r.door("entrada", false, false);  // aborted (a replay of the act): bolted again until he earns it
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 60 * 15;
	}
}
