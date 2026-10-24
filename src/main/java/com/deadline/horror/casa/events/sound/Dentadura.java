package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;

/**
 * 6 dentadura (acts 3-5, intensity 3; Hereditary's tongue click, here the Nona's dentures): a wet denture click right
 * at his ear. Only he hears it.
 */
public class Dentadura extends HorrorEvent {
	public Dentadura() {
		super("dentadura", Kind.SOUND);
		this.acts(3, 5).intensity(3).cooldown(180).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		return Polter.canHaunt(c);
	}

	@Override
	public void start(Ctx c) {
		double side = c.chance(0.5F) ? 1 : -1;
		Polter.heard(c.p, ModSounds.POLTER_DENTADURA, Polter.ear(c.p, side, 0.35), 1.0F);
		SanityManager.add(c.p, -3F);
	}
}
