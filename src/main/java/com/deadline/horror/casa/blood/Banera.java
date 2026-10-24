package com.deadline.horror.casa.blood;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * 50 banera (acts 4-6, intensity 4): the bathtub of the upstairs bathroom fills with blood from the bottom up and
 * bubbles; out of it rise the top of a white head and two cataract eyes -- the Nona, under the blood, looking at him
 * -- and she sinks again. The tub gurgles and drains, leaving a red ring (which stays, {@link BloodDecals#clear}).
 * The blood never stays IN the tub: the bathtub is a hiding place of the hunt.
 */
public class Banera extends HorrorEvent {
	/** Tub geometry of the kit (pixels of a north model): basin floor, blood level, basin length/width in blocks. */
	private static final double FLOOR = 1.8 / 16.0, LEVEL = 7.4 / 16.0, LENGTH = 1.72, WIDTH = 0.68;
	private static final int FILL = 60, HEAD = 70, RISE = 40, HOLD = 70, SINK = 24;

	public Banera() {
		super("banera", Kind.BLOOD);
		this.acts(4, 6).intensity(4).cooldown(400).weight(6).once();
	}

	record Tub(Vec3 center, Vec3 axis, double floor, double level) {
	}

	static Tub tub(Ctx c) {
		if (!Apparitions.hasArea(c.run, "bano_1p")) {
			return null;
		}
		List<BlockPos> blocks = HouseQuery.blocks(c.run, "bano_1p", st -> HouseQuery.key(st).startsWith("casa_banadera"));
		if (blocks.isEmpty()) {
			return null;
		}
		BlockPos a = blocks.get(0);
		Vec3 center;
		Vec3 axis;
		if (blocks.size() >= 2) {
			BlockPos b = blocks.get(1);
			center = Vec3.atCenterOf(a).add(Vec3.atCenterOf(b)).scale(0.5);
			axis = Vec3.atCenterOf(b).subtract(Vec3.atCenterOf(a)).normalize();
		} else {
			BlockState st = c.level().getBlockState(a);
			Direction f = st.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? st.getValue(BlockStateProperties.HORIZONTAL_FACING)
					: Direction.NORTH;
			center = Vec3.atCenterOf(a);
			axis = new Vec3(f.getStepZ(), 0, -f.getStepX());
		}
		return new Tub(center, axis, a.getY() + FLOOR, a.getY() + LEVEL);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		Tub t = tub(c);
		if (t == null) {
			return false;
		}
		double d = Apparitions.dist(c, t.center());
		if (d < 1.6 || d > 7.0 || !Apparitions.sees(c, new Vec3(t.center().x, t.level(), t.center().z), 60F)) {
			return false;
		}
		c.put("tub", t);
		return true;
	}

	private static Vec3 across(Tub t) {
		return new Vec3(t.axis().z, 0, -t.axis().x);
	}

	@Override
	public void start(Ctx c) {
		Tub t = c.get("tub");
		if (t == null) {
			t = tub(c);  // fired without its conditions (a command)
			c.put("tub", t);
		}
		if (t == null) {
			return;
		}
		Vec3 at = new Vec3(t.center().x, t.floor(), t.center().z);
		// it comes up from the plug: the surface starts at the basin floor and rises (interpolated)
		Display.ItemDisplay surf = BloodDecals.spawn(c.run, BloodDecals.TUB, at.add(0, 0.01, 0), new Vec3(0, 1, 0), across(t),
				(float) LENGTH * 0.9F, (float) WIDTH * 0.9F);
		c.put("surf", surf);
		Apparitions.sound(c, ModSounds.SANGRE_BURBUJEA, t.center(), 1.0F, 0.9F);
		Apparitions.noise(c, t.center(), 30F);
	}

	@Override
	public boolean tick(Ctx c) {
		Tub t = c.get("tub");
		Display.ItemDisplay surf = c.get("surf");
		if (t == null || surf == null) {
			return true;
		}
		FamilyEntity n = c.get("e");
		if (Apparitions.hidden(c.p)) {
			Apparitions.vanish(n, false);
			return true;
		}
		double rise = t.level() - t.floor();
		if (c.t == 2) {
			BloodDecals.resize(surf, new Vec3(0, 1, 0), across(t), (float) LENGTH, (float) WIDTH, new Vector3f(0F, (float) rise, 0F), FILL);
		}
		if (c.t > 20 && c.t % 3 == 0) {
			bubbles(c, t, c.t > HEAD ? 2 : 1);
		}
		if (c.t == HEAD) {
			// the head comes up: the top of it, white hair, and the eyes
			Vec3 from = new Vec3(t.center().x, t.level() - 1.6, t.center().z);
			FamilyEntity e = Apparitions.spawn(c, FamilyEntities.NONA, from, Apparitions.yawTo(from, c.p.position()));
			if (e != null) {
				e.propSounds = false;
				e.setVariant(FamilyEntity.LOOK_POSSESSED);
				e.setAction(FamilyEntity.POSE_IDLE);
				e.setFloating(true);
				e.floatTo(new Vec3(from.x, t.level() - 1.22, from.z), RISE);
				e.watch(c.p);
			}
			c.put("e", e);
			Apparitions.sound(c, ModSounds.SANGRE_BURBUJEA, t.center(), 1.1F, 0.75F);
		}
		Integer seenAt = c.get("seenAt");
		if (n != null && seenAt == null && c.t > HEAD + 20 && Apparitions.watches(c, n, 30F)) {
			c.put("seenAt", c.t);
			seenAt = c.t;
		}
		Integer sinkAt = c.get("sinkAt");
		if (sinkAt == null && n != null && (c.t >= HEAD + RISE + HOLD || seenAt != null && c.t - seenAt > 30
				|| Apparitions.dist(c, t.center()) < 1.3)) {
			sinkAt = c.t;
			c.put("sinkAt", sinkAt);
			n.floatTo(new Vec3(n.getX(), t.level() - 2.0, n.getZ()), SINK);
			Apparitions.sound(c, ModSounds.SANGRE_HUNDE, t.center(), 1.0F, 1.0F);
			Apparitions.noise(c, t.center(), 25F);
		}
		if (sinkAt == null) {
			return false;
		}
		int s = c.t - sinkAt;
		if (s == SINK + 2) {
			Apparitions.despawnAll(c);
			c.put("e", null);
		}
		if (s == SINK + 16) {
			// it drains: the level goes down to the plug, with a long gurgle
			BloodDecals.resize(surf, new Vec3(0, 1, 0), across(t), (float) LENGTH * 0.8F, (float) WIDTH * 0.8F, new Vector3f(), 50);
			Apparitions.sound(c, ModSounds.SANGRE_HUNDE, t.center(), 0.7F, 1.35F);
		}
		return s > SINK + 70;
	}

	private static void bubbles(Ctx c, Tub t, int n) {
		Vec3 ax = t.axis();
		Vec3 ac = across(t);
		for (int i = 0; i < n; i++) {
			double u = (c.rnd.nextDouble() - 0.5) * LENGTH * 0.8;
			double v = (c.rnd.nextDouble() - 0.5) * WIDTH * 0.7;
			Vec3 p = t.center().add(ax.scale(u)).add(ac.scale(v));
			double y = Math.min(t.level(), t.floor() + (t.level() - t.floor()) * Math.min(1.0, c.t / (double) FILL)) + 0.03;
			c.level().sendParticles(ParticleTypes.BUBBLE_POP, p.x, y, p.z, 1, 0.02, 0.0, 0.02, 0.0);
			if (c.rnd.nextInt(3) == 0) {
				c.level().sendParticles(new DustParticleOptions(0x5A0606, 1.1F), p.x, y + 0.02, p.z, 1, 0.03, 0.02, 0.03, 0.0);
			}
		}
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
		Tub t = c.get("tub");
		Display.ItemDisplay surf = c.get("surf");
		if (surf != null) {
			BloodDecals.remove(c.run, surf);
		}
		if (t != null) {
			// what is left: a red ring on the enamel, and nothing to hide in
			BloodDecals.spawn(c.run, BloodDecals.TUB_RING, new Vec3(t.center().x, t.floor() + 0.015, t.center().z), new Vec3(0, 1, 0),
					across(t), (float) LENGTH, (float) WIDTH);
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 16;
	}
}
