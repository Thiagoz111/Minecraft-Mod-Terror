package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 1 pasos_arriba (acts 1-5, intensity 1): slow footsteps on the floor above, coming across the room up there until
 * they are right over his head, and stopping there. Nothing else. Only where there is a floor above him.
 */
public class PasosArriba extends HorrorEvent {
	private static final int GAP = 21;

	public PasosArriba() {
		super("pasos_arriba", Kind.SOUND);
		this.acts(1, 5).intensity(1).cooldown(80).weight(12);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		double ceil = Apparitions.ceilingY(c.run, c.p.position().add(0, 1.0, 0));
		if (Double.isNaN(ceil) || ceil - c.p.getY() > 4.5) {
			return false;
		}
		// the floor up there: the top of the ceiling slab, with a room above it
		BlockPos slab = BlockPos.containing(c.p.getX(), ceil + 0.01, c.p.getZ());
		BlockPos up = slab;
		for (int i = 0; i < 3 && !c.level().getBlockState(up).getCollisionShape(c.level(), up).isEmpty(); i++) {
			up = up.above();
		}
		Vec3 above = new Vec3(c.p.getX(), up.getY(), c.p.getZ());
		if (!c.level().getBlockState(up).getCollisionShape(c.level(), up).isEmpty() || HouseQuery.roomAt(c.run, above.add(0, 0.5, 0)) == null) {
			return false;
		}
		double yaw = c.rnd.nextDouble() * Math.PI * 2;
		Vec3 dir = new Vec3(Math.cos(yaw), 0, Math.sin(yaw));
		c.put("over", above.add(0, 0.05, 0));
		c.put("dir", dir);
		c.put("steps", 5 + c.rnd.nextInt(3));
		return true;
	}

	@Override
	public void start(Ctx c) {
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 over = c.get("over");
		Vec3 dir = c.get("dir");
		int steps = c.get("steps");
		if (c.t % GAP == 0 && c.t / GAP < steps) {
			int i = c.t / GAP;
			// they come from steps*0.75 blocks away and stop right above him
			Vec3 at = over.add(dir.scale((steps - 1 - i) * 0.75));
			c.run.sound(ModSounds.POLTER_PASOS_ARRIBA, at, 1.1F, Polter.pitch(c, 0.85F, 1.0F));
		}
		return c.t >= steps * GAP + 10;
	}

	@Override
	public int maxTicks() {
		return 20 * 12;
	}
}
