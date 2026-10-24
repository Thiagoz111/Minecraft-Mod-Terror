package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * 9 rezo_reves (acts 2-5, intensity 2): from the Nona's room, an old woman's murmured prayer, every word of it
 * backwards. It stops the moment he steps into the room.
 */
public class RezoReves extends HorrorEvent {
	private static final int LENGTH = 20 * 9;

	public RezoReves() {
		super("rezo_reves", Kind.SOUND);
		this.acts(2, 5).intensity(2).cooldown(160).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.hasArea(c.run, "nona_cuarto") || c.run.inside(c.p, "nona_cuarto")) {
			return false;
		}
		String at = Apparitions.has(c.run, "nona_altar") ? "nona_altar" : Apparitions.has(c.run, "nona_cama") ? "nona_cama" : null;
		if (at == null) {
			return false;
		}
		double d = Apparitions.dist(c, c.run.at(at));
		if (d < 3.0 || d > 26.0) {
			return false;
		}
		c.put("at", c.run.at(at).add(0, 1.0, 0));
		return true;
	}

	@Override
	public void start(Ctx c) {
		c.run.sound(ModSounds.POLTER_REZO_REVES, c.<Vec3>get("at"), 1.0F, Polter.pitch(c, 0.95F, 1.02F));
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.run.inside(c.p, "nona_cuarto")) {
			Polter.stopSound(c.run, ModSounds.POLTER_REZO_REVES);
			return true;
		}
		return c.t >= LENGTH;
	}

	@Override
	public int maxTicks() {
		return LENGTH + 20;
	}
}
