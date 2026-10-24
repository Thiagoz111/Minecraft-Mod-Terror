package com.deadline.horror.casa.setpiece;

import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Act 4 (design 2, "Lucía en el techo"): Marta has just written that Lucía is not in her bed. She is not: she is on the
 * ceiling. Upside down over the room, every limb bent the wrong way, her face turned down at him. Something drips on the
 * floor beside him, a drop at a time (blood), and a giggle comes from nowhere -- until he looks up. She holds still a
 * moment; her neck cracks; and she scuttles across the ceiling straight over his head (the jumpscare). Never seen in
 * 45 s: something runs across the ceiling and is gone.
 * <p>In her own room ({@code lucia_techo}) when he is there; otherwise on the ceiling of the room he is in (the 1P hall:
 * {@code pasillo_techo}).
 */
public class SpLuciaTecho extends HorrorEvent {
	private static final double BODY = 1.5;
	private static final int DRIP = 30, GIGGLE = 20 * 9, NEVER = 20 * 45;

	public SpLuciaTecho() {
		super("sp_lucia_techo", Kind.SETPIECE);
		this.acts(4, 6).intensity(5).cooldown(300).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		Vec3 spot = null;
		// her room first (the marker on her ceiling), then the upstairs hall's ceiling, then the middle of his room
		for (String m : List.of("lucia_techo", "pasillo_techo")) {
			Vec3 v = Apparitions.at(c.run, m);
			if (v != null && ok(c, v)) {
				spot = v;
				break;
			}
		}
		String room = c.room();
		if (spot == null && room != null && !room.startsWith("esc_") && Apparitions.hasArea(c.run, room)) {
			AABB box = c.run.area(room);
			if (box.getXsize() >= 3 && box.getZsize() >= 3) {
				Vec3 mid = new Vec3(box.getCenter().x, c.p.getY() + 1.0, box.getCenter().z);
				if (ok(c, mid)) {
					spot = mid;
				}
			}
		}
		if (spot == null) {
			return false;
		}
		double ceil = Apparitions.ceilingY(c.run, new Vec3(spot.x, c.p.getY() + 1.0, spot.z));
		if (Double.isNaN(ceil) || ceil - c.p.getY() < 2.6) {
			return false;
		}
		c.put("pos", new Vec3(spot.x, ceil - BODY, spot.z));
		c.put("ceil", ceil);
		return true;
	}

	/** On his floor, 3-9 blocks away, not on his screen, with a ceiling he can see it on. */
	private static boolean ok(Ctx c, Vec3 v) {
		double dy = Math.abs(Math.floor(v.y) - Math.floor(c.p.getY()));
		if (dy > 3.0) {
			return false;
		}
		Vec3 flat = new Vec3(v.x, c.p.getY(), v.z);
		double d = c.p.position().distanceTo(flat);
		if (d < 3.0 || d > 9.0) {
			return false;
		}
		double ceil = Apparitions.ceilingY(c.run, new Vec3(v.x, c.p.getY() + 1.0, v.z));
		if (Double.isNaN(ceil)) {
			return false;
		}
		Vec3 body = new Vec3(v.x, ceil - 0.6, v.z);
		return !Apparitions.sees(c, body, 70F) && Apparitions.clear(c.run, c.p.getEyePosition(), body, c.p);
	}

	@Override
	public void start(Ctx c) {
		if (c.get("pos") == null && !canRun(c)) {
			c.put("abort", true);  // fired by hand without its place (a command): nothing to stage
			return;
		}
		Vec3 pos = c.get("pos");
		PoseidaEntity l = Apparitions.spawn(c, ModEntities.POSEIDA, pos, Apparitions.yawTo(pos, c.p.position()));
		if (l != null) {
			l.setVariant(PoseidaEntity.LOOK_POSSESSED);
			l.setAction(PoseidaEntity.ACT_CEILING);
			l.setNoGravity(true);
		}
		c.put("e", l);
		c.put("seenAt", -1);
		c.put("drops", 0);
		// where she hangs, the plaster is stained (a thing to notice before he finds her)
		double ceil = c.get("ceil");
		BloodDecals.ceiling(c.run, BloodDecals.CEILING, new Vec3(pos.x, ceil, pos.z), c.rnd.nextFloat() * 360F, 1.1F, 1.1F);
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.get("abort") != null) {
			return true;
		}
		PoseidaEntity l = c.get("e");
		if (Apparitions.gone(l)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			Apparitions.vanish(l, false);
			return true;
		}
		int seenAt = c.get("seenAt");
		if (seenAt < 0) {
			return waiting(c, l);
		}
		return reveal(c, l, c.t - seenAt);
	}

	/** Up there in the dark, waiting to be found: drops on the floor by him, a giggle, the bones settling. */
	private boolean waiting(Ctx c, PoseidaEntity l) {
		double ceil = c.get("ceil");
		Vec3 head = new Vec3(l.getX(), ceil - 1.2, l.getZ());
		if (c.t % DRIP == 0) {
			// a drop falls from her face to the floor, between her and him
			Vec3 drop = head.lerp(new Vec3(c.p.getX(), head.y, c.p.getZ()), 0.35);
			c.level().sendParticles(ModParticles.BLOOD_DRIP, drop.x, drop.y, drop.z, 1, 0.02, 0.0, 0.02, 0.0);
			c.run.sound(ModSounds.SANGRE_GOTA, new Vec3(drop.x, c.p.getY(), drop.z), 0.6F, 0.9F);
			int drops = c.<Integer>get("drops");
			if (drops < 6 && (c.t / DRIP) % 2 == 1) {
				// the drops stay on the floor (blood is cleaned only when the case ends: BloodDecals.clear)
				double floor = Apparitions.floorY(c.run, BlockPos.containing(drop.x, c.p.getY() + 0.1, drop.z));
				BloodDecals.floor(c.run, BloodDecals.SPLATS[drops % BloodDecals.SPLATS.length], new Vec3(drop.x, floor, drop.z),
						c.rnd.nextFloat() * 360F, 0.16F + 0.04F * drops, 0.16F + 0.04F * drops);
				c.put("drops", drops + 1);
			}
		}
		if (c.t == GIGGLE) {
			Apparitions.sound(c, ModSounds.POSEIDA_GIGGLE, head, 0.45F, 0.8F);
		}
		if (c.t % 97 == 50) {
			Apparitions.sound(c, ModSounds.POSEIDA_CRACK, head, 0.35F, 0.7F);
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(Apparitions.seesAny(c, 40F, head, head.add(0, 0.6, 0), new Vec3(l.getX(), ceil - 0.2, l.getZ())));
		if (g.seen >= 6) {
			c.put("seenAt", c.t);
			Apparitions.sound(c, ModSounds.APARICION_CUELLO, head, 1.0F, 0.85F);
			return false;
		}
		if (c.t > NEVER) {
			// never found: something runs across the ceiling and is gone
			Apparitions.sound(c, ModSounds.APARICION_TECHO_CORRE, head, 1.2F, 1.0F);
			Apparitions.noise(c, head, 40F);
			Apparitions.vanish(l, false);
			return true;
		}
		return false;
	}

	/** Found: a breath of stillness, the neck cracks, and she comes across the ceiling at him. */
	private boolean reveal(Ctx c, PoseidaEntity l, int k) {
		double ceil = c.get("ceil");
		if (k < 22) {
			return false;  // still, the face turned down at him
		}
		if (k == 22) {
			l.setAction(PoseidaEntity.ACT_CEILING_RUN);
			Apparitions.sound(c, ModSounds.APARICION_TECHO_CORRE, l.position().add(0, BODY, 0), 1.4F, 1.1F);
			Apparitions.noise(c, l.position(), 45F);
		}
		// once per run and earned (he found her): the scare is always hers, not traded for an exit by the generic 3-minute
		// rule (the night's set pieces only start once the peak of the last scare has relaxed)
		Vec3 goal = new Vec3(c.p.getX(), ceil - BODY, c.p.getZ());
		Vec3 pos = l.position();
		Vec3 delta = goal.subtract(pos);
		double len = delta.length();
		double speed = 0.45;
		if (len > speed) {
			Apparitions.glide(l, pos.add(delta.scale(speed / len)), false);
			Apparitions.face(l, Apparitions.yawTo(pos, goal));
		}
		boolean there = len <= speed + 0.05 || k > 22 + 30;
		if (!there) {
			return false;
		}
		Fx.jumpscare(c.p, "lucia");
		c.haunt.jumpscared();
		Fx.shake(c.p, 1.2F, 18);
		Apparitions.sound(c, ModSounds.POSEIDA_SCREAM, c.p.getEyePosition().add(0, 0.8, 0), 1.6F, 0.9F);
		Apparitions.vanish(l, false);
		return true;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return NEVER + 20 * 10;
	}
}
