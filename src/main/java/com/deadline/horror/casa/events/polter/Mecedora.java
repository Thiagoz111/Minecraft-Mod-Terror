package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.horror.casa.Rocker;
import com.deadline.sanity.SanityManager;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 27 mecedora (acts 1-5, intensity 2): the Nona's rocking chair (the living room's or the one in her room) rocks by
 * itself, faster and faster, creaking, and then stops dead, as if somebody had just stood up from it.
 */
public class Mecedora extends HorrorEvent {
	public Mecedora() {
		super("mecedora", Kind.POLTER);
		this.acts(1, 5).intensity(2).cooldown(150).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		CasaProps.sweep(c.run);
		for (BlockPos p : Polter.kitNear(c.run, c.p.position(), 14, 2, k -> k.equals("casa_mecedora"))) {
			Vec3 v = Vec3.atCenterOf(p);
			double d = Apparitions.dist(c, v);
			if (d >= 3.0 && d <= 14.0 && !CasaProps.held(c.run, p) && Apparitions.sees(c, v, 50F)) {
				c.put("pos", p);
				return true;
			}
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		BlockPos p = c.get("pos");
		Rocker k = Rocker.frenzy(c.run, p);
		c.put("rocker", k);
		Polter.noise(c.run, Vec3.atCenterOf(p), 20F);
	}

	@Override
	public boolean tick(Ctx c) {
		Rocker k = c.get("rocker");
		if (k == null) {
			return true;
		}
		if (k.age() == Rocker.RAMP + 1) {
			SanityManager.add(c.p, -3F);
		}
		return k.tick();
	}

	@Override
	public void stop(Ctx c) {
		Rocker k = c.get("rocker");
		if (k != null) {
			k.stop();
		}
	}

	@Override
	public int maxTicks() {
		return Rocker.RAMP + 60;
	}
}
