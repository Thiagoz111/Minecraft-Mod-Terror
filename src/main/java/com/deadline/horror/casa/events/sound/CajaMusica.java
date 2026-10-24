package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * 5 caja_musica (acts 1-4, intensity 2): Lucía's music box plays by itself in her room. The moment he steps into the
 * room (or touches it), it stops mid-phrase.
 */
public class CajaMusica extends HorrorEvent {
	/** Length of the lullaby (POLTER_CAJA_MUSICA), ticks. */
	private static final int LENGTH = 20 * 15;

	public CajaMusica() {
		super("caja_musica", Kind.SOUND);
		this.acts(1, 4).intensity(2).cooldown(240).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.has(c.run, "caja_musica") || !Apparitions.hasArea(c.run, "lucia")
				|| c.run.inside(c.p, "lucia")) {
			return false;
		}
		double d = Apparitions.dist(c, c.run.at("caja_musica"));
		return d >= 4.0 && d <= 28.0;
	}

	@Override
	public void start(Ctx c) {
		Vec3 at = c.run.at("caja_musica").add(0, 0.6, 0);
		c.put("at", at);
		c.run.sound(ModSounds.POLTER_CAJA_MUSICA, at, 0.9F, 1.0F);
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 at = c.get("at");
		if (c.run.inside(c.p, "lucia") || Apparitions.dist(c, at) < 2.5 || Polter.got(c, "caja")) {
			// it stops dead, and the little dancer clicks round once more
			Polter.stopSound(c.run, ModSounds.POLTER_CAJA_MUSICA);
			c.run.sound(ModSounds.DOLL_TURN, at, 0.5F, 1.4F);
			return true;
		}
		return c.t >= LENGTH;
	}

	@Override
	public int maxTicks() {
		return LENGTH + 40;
	}
}
