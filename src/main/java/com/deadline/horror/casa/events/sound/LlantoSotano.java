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
 * 12 llanto_sotano (acts 3-5, intensity 2): a small child crying in the basement, heard through a vent (the metal of
 * the duct rings with it) or up through the floorboards of the ground floor. It stops when he goes down.
 */
public class LlantoSotano extends HorrorEvent {
	private static final int LENGTH = 20 * 7;

	public LlantoSotano() {
		super("llanto_sotano", Kind.SOUND);
		this.acts(3, 5).intensity(2).cooldown(200).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.hasArea(c.run, "sotano") || c.run.inside(c.p, "sotano")) {
			return false;
		}
		List<BlockPos> vents = Polter.kitNear(c.run, c.p.position(), 10, 4, k -> k.equals("casa_rejilla"));
		Vec3 at = null;
		if (!vents.isEmpty()) {
			at = Vec3.atCenterOf(vents.get(0));
		} else if ("pb".equals(Polter.floor(c.run, c.p.position()))) {
			// through the floor: from under the boards he stands on
			at = c.p.position().add(c.rnd.nextDouble() * 2 - 1, -1.6, c.rnd.nextDouble() * 2 - 1);
		} else {
			for (String s : new String[] {"esc_servicio_pie", "sotano_escalera"}) {
				if (Apparitions.has(c.run, s) && Apparitions.dist(c, c.run.at(s)) < 14) {
					at = c.run.at(s).add(0, 0.5, 0);
					break;
				}
			}
		}
		if (at == null) {
			return false;
		}
		c.put("at", at);
		return true;
	}

	@Override
	public void start(Ctx c) {
		c.run.sound(ModSounds.POLTER_LLANTO_REJILLA, c.<Vec3>get("at"), 1.0F, Polter.pitch(c, 0.95F, 1.05F));
	}

	@Override
	public boolean tick(Ctx c) {
		if (c.run.inside(c.p, "sotano")) {
			Polter.stopSound(c.run, ModSounds.POLTER_LLANTO_REJILLA);
			return true;
		}
		return c.t >= LENGTH;
	}

	@Override
	public int maxTicks() {
		return LENGTH + 20;
	}
}
