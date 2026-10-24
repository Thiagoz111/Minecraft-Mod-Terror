package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 11 telefono_fijo (acts 2-5, intensity 2): the landline in the hall rings (the line was cut in March). If he picks it
 * up (right click on the phone, see {@link com.deadline.horror.casa.Interactables}): static, and somebody breathing
 * slowly into the receiver; then the click of somebody hanging up. If he lets it ring, it stops after seven rings.
 */
public class TelefonoFijo extends HorrorEvent {
	private static final int RING_EVERY = 72, RINGS = 7;

	public TelefonoFijo() {
		super("telefono_fijo", Kind.SOUND);
		this.acts(2, 5).intensity(2).cooldown(300).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.has(c.run, "telefono_fijo")) {
			return false;
		}
		List<BlockPos> phones = Polter.kitNear(c.run, c.run.at("telefono_fijo"), 3, 2, k -> k.equals("casa_telefono"));
		if (phones.isEmpty()) {
			return false;
		}
		Vec3 at = Vec3.atCenterOf(phones.get(0));
		double d = Apparitions.dist(c, at);
		if (d < 3.0 || d > 30.0) {
			return false;
		}
		c.put("at", at);
		return true;
	}

	@Override
	public void start(Ctx c) {
		c.put("answered", -1);
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 at = c.get("at");
		int answered = c.get("answered");
		if (answered < 0) {
			if (Polter.got(c, "telefono")) {
				answered = c.t;
				c.put("answered", answered);
				Polter.stopSound(c.run, ModSounds.POLTER_TELEFONO_RING);
				Polter.heard(c.p, ModSounds.POLTER_TELEFONO_RESPIRA, Polter.ear(c.p, 1, 0.3), 1.0F);
				return false;
			}
			if (c.t % RING_EVERY == 0) {
				if (c.t / RING_EVERY >= RINGS) {
					return true;
				}
				c.run.sound(ModSounds.POLTER_TELEFONO_RING, at, 1.4F, 1.0F);
				Polter.noise(c.run, at, 55F);
			}
			return false;
		}
		if (c.t - answered == 132) {
			Polter.heard(c.p, ModSounds.POLTER_LLAVE_LUZ, Polter.ear(c.p, 1, 0.3), 0.8F);  // they hang up
		}
		return c.t - answered >= 140;
	}

	@Override
	public void stop(Ctx c) {
		Polter.stopSound(c.run, ModSounds.POLTER_TELEFONO_RING);
	}

	@Override
	public int maxTicks() {
		return RING_EVERY * RINGS + 200;
	}
}
