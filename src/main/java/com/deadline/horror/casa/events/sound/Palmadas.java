package com.deadline.horror.casa.events.sound;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/** 3 palmadas (acts 3-5, intensity 3; The Conjuring): two claps right behind him. There is nobody there. */
public class Palmadas extends HorrorEvent {
	public Palmadas() {
		super("palmadas", Kind.SOUND);
		this.acts(3, 5).intensity(3).cooldown(200).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		double yaw = Math.toRadians(c.p.getYRot());
		Vec3 back = new Vec3(Math.sin(yaw), 0, -Math.cos(yaw));
		for (double d = 1.4; d >= 0.7; d -= 0.35) {
			Vec3 at = c.p.position().add(back.scale(d)).add(0, 1.35, 0);
			if (CasaProps.passable(c.level(), at)) {
				c.put("at", at);
				return true;
			}
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		Vec3 at = c.get("at");
		c.run.sound(ModSounds.POLTER_PALMADAS, at, 1.0F, Polter.pitch(c, 0.95F, 1.05F));
	}
}
