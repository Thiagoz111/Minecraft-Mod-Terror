package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.util.Mth;

/**
 * 8 respiracion (acts 2-5, intensity 2): heavy, wet breathing pressed against him, on one side only. Only he hears it.
 * If he does not turn towards it, it breathes again, closer.
 */
public class Respiracion extends HorrorEvent {
	public Respiracion() {
		super("respiracion", Kind.SOUND);
		this.acts(2, 5).intensity(2).cooldown(150).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		return Polter.canHaunt(c);
	}

	@Override
	public void start(Ctx c) {
		double side = c.chance(0.5F) ? 1 : -1;
		c.put("side", side);
		c.put("yaw", c.p.getYRot());
		Polter.heard(c.p, ModSounds.POLTER_RESPIRA, Polter.ear(c.p, side, 0.55), 1.0F);
		SanityManager.add(c.p, -2F);
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.t == 80) {
			float yaw0 = c.get("yaw");
			if (Math.abs(Mth.wrapDegrees(c.p.getYRot() - yaw0)) < 45F) {
				double side = c.get("side");
				Polter.heard(c.p, ModSounds.POLTER_RESPIRA, Polter.ear(c.p, side, 0.3), 1.2F);
				SanityManager.add(c.p, -2F);
			}
		}
		return c.t >= 82;
	}
}
