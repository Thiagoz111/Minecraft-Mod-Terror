package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.horror.casa.Tap;
import com.deadline.sanity.SanityManager;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 29 canilla_sangre (acts 3-6, intensity 3): a tap near him (the kitchen sink, a washbasin, the bathtub, the laundry
 * sink) opens by itself: water, then, in gouts, thick dark blood. It runs until he closes it (right click) or it stops.
 */
public class CanillaSangre extends HorrorEvent {
	public CanillaSangre() {
		super("canilla_sangre", Kind.POLTER);
		this.acts(3, 6).intensity(3).cooldown(220).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String room = c.room();
		for (BlockPos p : Polter.kitNear(c.run, c.p.position(), 8, 2, CanillaSangre::isTap)) {
			Vec3 v = Vec3.atCenterOf(p);
			double d = Apparitions.dist(c, v);
			if (d < 1.5 || d > 8.0) {
				continue;
			}
			String r = HouseQuery.roomAt(c.run, v);
			if (r != null && r.equals(room) || Apparitions.clear(c.run, v, c.p.getEyePosition(), c.p)) {
				c.put("pos", p);
				return true;
			}
		}
		return false;
	}

	private static boolean isTap(String k) {
		return k.equals("casa_mesada_pileta") || k.equals("casa_lavatorio") || k.equals("casa_banadera_izq") || k.equals("casa_pileta_lavar");
	}

	@Override
	public void start(Ctx c) {
		BlockPos p = c.get("pos");
		Tap t = Tap.open(c.run, p, 50 + c.rnd.nextInt(20), 20 * 13);
		c.put("tap", t);
		if (t != null) {
			Polter.noise(c.run, t.spout(), 25F);
		}
		c.put("felt", false);
	}

	@Override
	public boolean tick(Ctx c) {
		Tap t = c.get("tap");
		if (t == null) {
			return true;
		}
		if (Polter.got(c, "canilla") && Apparitions.dist(c, t.spout()) < 3.5) {
			t.stop();
			return true;
		}
		boolean felt = c.get("felt");
		if (!felt && t.blood() && Apparitions.dist(c, t.spout()) < 7) {
			c.put("felt", true);
			SanityManager.add(c.p, -4F);
		}
		return t.tick();
	}

	@Override
	public void stop(Ctx c) {
		Tap t = c.get("tap");
		if (t != null) {
			t.stop();
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 16;
	}
}
