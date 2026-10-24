package com.deadline.horror.casa.blood;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Display;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * 49 gotea_techo (acts 3-6, intensity 2): a dark stain spreads on the ceiling of his room and blood drips from it,
 * drop after thick drop; under it a pool grows on the floor. It stops after a while; the stain and the pool stay
 * ({@link BloodDecals#clear}).
 */
public class GoteaTecho extends HorrorEvent {
	private static final List<String> OUTSIDE = List.of("patio", "jardin", "cucha", "galpon", "balcon");

	public GoteaTecho() {
		super("gotea_techo", Kind.BLOOD);
		this.acts(3, 6).intensity(2).cooldown(160).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		String room = c.room();
		if (room == null || OUTSIDE.contains(room) || !Apparitions.hasArea(c.run, room)) {
			return false;
		}
		AABB box = c.run.area(room);
		Vec3 best = null;
		double bestCeil = 0;
		boolean bestSeen = false;
		for (int i = 0; i < 16; i++) {
			double a = c.rnd.nextDouble() * Math.PI * 2;
			double d = 1.6 + c.rnd.nextDouble() * 2.8;
			Vec3 v = c.p.position().add(Math.cos(a) * d, 0, Math.sin(a) * d);
			if (!box.contains(v.add(0, 0.5, 0))) {
				continue;
			}
			BlockPos feet = BlockPos.containing(v.x, c.p.getY() + 0.2, v.z);
			if (!HouseQuery.standable(c.run, feet)) {
				continue;
			}
			double fy = Apparitions.floorY(c.run, feet);
			double cy = Apparitions.ceilingY(c.run, new Vec3(v.x, fy + 0.6, v.z));
			if (Double.isNaN(cy) || cy - fy < 1.8 || cy - fy > 4.5) {
				continue;
			}
			Vec3 spot = new Vec3(v.x, fy, v.z);
			boolean seen = Apparitions.sees(c, spot, 60F);
			if (best == null || seen && !bestSeen) {
				best = spot;
				bestCeil = cy;
				bestSeen = seen;
			}
		}
		if (best == null) {
			return false;
		}
		c.put("spot", best);
		c.put("ceil", bestCeil);
		return true;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("spot") == null && !canRun(c)) {
			return;  // fired by hand with no ceiling over him
		}
		Vec3 spot = c.get("spot");
		double ceil = c.get("ceil");
		float yaw = c.rnd.nextFloat() * 360F;
		Display.ItemDisplay stain = BloodDecals.ceiling(c.run, BloodDecals.CEILING, new Vec3(spot.x, ceil, spot.z), yaw, 0.3F, 0.3F);
		float poolYaw = c.rnd.nextFloat() * 360F;
		Display.ItemDisplay pool = BloodDecals.floor(c.run, BloodDecals.POOL, spot, poolYaw, 0.06F, 0.06F);
		c.put("stain", stain);
		c.put("pool", pool);
		c.put("yaw", yaw);
		c.put("pyaw", poolYaw);
		c.put("next", 14);
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 spot = c.get("spot");
		if (spot == null || c.get("next") == null) {
			return true;
		}
		double ceil = c.get("ceil");
		if (c.t == 2) {
			// both spread slowly (the client interpolates the growth)
			Display.ItemDisplay stain = c.get("stain");
			Display.ItemDisplay pool = c.get("pool");
			float yaw = c.get("yaw");
			float poolYaw = c.get("pyaw");
			BloodDecals.resize(stain, new Vec3(0, -1, 0), BloodDecals.dirOf(yaw), 0.8F, 0.8F, null, 20 * 14);
			float size = 1.1F + c.rnd.nextFloat() * 0.35F;
			BloodDecals.resize(pool, new Vec3(0, 1, 0), BloodDecals.dirOf(poolYaw), size, size, null, 20 * 22);
		}
		int next = c.get("next");
		if (c.t >= next) {
			c.level().sendParticles(ModParticles.BLOOD_DRIP, spot.x, ceil - 0.06, spot.z, 1, 0.04, 0.0, 0.04, 0.0);
			Apparitions.sound(c, ModSounds.SANGRE_GOTA, spot.add(0, 0.05, 0), 0.6F, Apparitions.pitch(c, 0.85F, 1.1F));
			c.put("next", c.t + c.between(9, 17));
		}
		return c.t > 20 * 24 || Apparitions.dist(c, spot) > 16.0;
	}

	@Override
	public int maxTicks() {
		return 20 * 30;
	}
}
