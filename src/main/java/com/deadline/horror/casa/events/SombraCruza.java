package com.deadline.horror.casa.events;

import com.deadline.entity.SombraEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * 33 sombra_cruza (acts 1-5, intensity 2): a tall shadow crosses the frame of an open door at the far end, from
 * behind one jamb to behind the other, in a few heavy strides. Never closer than 6 blocks; gone at once if he comes
 * within 3.5 blocks of it.
 */
public class SombraCruza extends HorrorEvent {
	private static final int CROSS_TICKS = 30;
	private static final double HALF_WIDTH = 2.2, BEHIND = 1.6;

	public SombraCruza() {
		super("sombra_cruza", Kind.APPARITION);
		this.acts(1, 5).intensity(2).cooldown(110).weight(10);
	}

	private record Plan(Vec3 from, Vec3 to, Vec3 door) {
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		for (String d : HouseQuery.doorsNear(c.run, c.p.position(), 18.0)) {
			if (d.startsWith("ropero") || d.startsWith("porton") || d.startsWith("baul") || d.equals("entrada") || !c.run.doorOpen(d)) {
				continue;
			}
			Vec3 dp = HouseQuery.doorPos(c.run, d);
			if (dp == null || dp.distanceTo(c.p.position()) < 6.0 || Math.abs(dp.y - c.p.getY() - 0.5) > 2.0) {
				continue;
			}
			if (!Apparitions.sees(c, dp.add(0, 0.6, 0), 45F)) {
				continue;
			}
			Plan p = plan(c, dp);
			if (p != null) {
				c.put("plan", p);
				return true;
			}
		}
		return false;
	}

	/** Across the doorway on the far side of the door: from behind one jamb to behind the other. */
	private static Plan plan(Ctx c, Vec3 dp) {
		BlockPos pos = BlockPos.containing(dp);
		BlockState st = c.level().getBlockState(pos);
		if (!(st.getBlock() instanceof DoorBlock)) {
			return null;
		}
		Direction f = st.getValue(DoorBlock.FACING);
		Vec3 axis = new Vec3(f.getStepX(), 0, f.getStepZ());
		double side = dp.subtract(c.p.position()).dot(axis) >= 0 ? 1.0 : -1.0;
		Vec3 far = dp.add(axis.scale(BEHIND * side));
		Vec3 lat = new Vec3(-axis.z, 0, axis.x);
		double y = Apparitions.floorY(c.run, BlockPos.containing(far.x, dp.y, far.z));
		Vec3 base = new Vec3(far.x, y, far.z);
		if (!HouseQuery.standable(c.run, BlockPos.containing(base.x, base.y + 0.1, base.z))) {
			return null;
		}
		boolean flip = c.chance(0.5F);
		Vec3 a = base.add(lat.scale(flip ? HALF_WIDTH : -HALF_WIDTH));
		Vec3 b = base.add(lat.scale(flip ? -HALF_WIDTH : HALF_WIDTH));
		return new Plan(a, b, dp);
	}

	@Override
	public void start(Ctx c) {
		Plan p = c.get("plan");
		SombraEntity s = Apparitions.spawn(c, ModEntities.SOMBRA, p.from(), Apparitions.yawTo(p.from(), p.to()));
		if (s != null) {
			s.setVariant(SombraEntity.VARIANT_VISITANTE);
			s.noPhysics = true;
			s.setNoGravity(true);
		}
		c.put("e", s);
	}

	@Override
	public boolean tick(Ctx c) {
		SombraEntity s = c.get("e");
		Plan p = c.get("plan");
		if (Apparitions.gone(s)) {
			return true;
		}
		if (Apparitions.dist(c, s.position()) < 3.5) {
			Apparitions.vanish(s, true);
			return true;
		}
		float u = Math.min(1F, c.t / (float) CROSS_TICKS);
		// strides: it surges forward on each step and almost stops between them
		float stride = u + 0.05F * (float) Math.sin(u * Math.PI * 8.0);
		Apparitions.glide(s, p.from().lerp(p.to(), Math.max(0F, Math.min(1F, stride))), true);
		if (c.t == 2 || c.t == 16) {
			Apparitions.sound(c, ModSounds.APARICION_SOMBRA_PASO, p.door(), 1.2F, Apparitions.pitch(c, 0.75F, 0.9F));
		}
		return c.t >= CROSS_TICKS;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 6;
	}
}
