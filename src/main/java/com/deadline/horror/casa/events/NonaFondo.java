package com.deadline.horror.casa.events;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * 34 nona_fondo (acts 2-4, intensity 3): the Nona standing at the far end of the hall, her face to the wall, still.
 * She is put there while he is not looking; when he comes within 5 blocks -- or looks away after he has seen her --
 * she is gone.
 */
public class NonaFondo extends HorrorEvent {
	private static final String[] ENDS = {"pasillo_1p_fondo", "pasillo_pb_fondo"};

	public NonaFondo() {
		super("nona_fondo", Kind.APPARITION);
		this.acts(2, 4).intensity(3).cooldown(180).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		String best = null;
		for (String m : ENDS) {
			Vec3 v = Apparitions.at(c.run, m);
			if (v == null) {
				continue;
			}
			double d = Apparitions.dist(c, v);
			if (d < 7.0 || d > 26.0 || Math.abs(v.y - c.p.getY()) > 2.0 || Apparitions.sees(c, v.add(0, 1.0, 0), 70F)) {
				continue;
			}
			String hall = m.substring(0, m.length() - "_fondo".length());
			if (best == null || hall.equals(c.room())) {
				best = m;
			}
		}
		if (best == null) {
			return false;
		}
		c.put("m", best);
		return true;
	}

	@Override
	public void start(Ctx c) {
		String m = c.get("m");
		// her face to the wall: the marker looks back down the hall
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, c.run.at(m), c.run.yaw(m) + 180F);
		if (n != null) {
			n.propSounds = false;
			n.watchPlayers(false);
			n.setAction(FamilyEntity.POSE_IDLE);
		}
		c.put("e", n);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity n = c.get("e");
		if (Apparitions.gone(n)) {
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.sees(c, n, 50F));
		if (!was && g.ever) {
			Apparitions.sound(c, ModSounds.APARICION_NONA_RESPIRA, n.position().add(0, 1.3, 0), 0.7F, Apparitions.pitch(c, 0.85F, 0.95F));
		}
		if (Apparitions.dist(c, n.position()) < 5.0 || g.lookedAway(8)) {
			Apparitions.vanish(n, false);
			return true;
		}
		// never seen in 40 s: she was never there
		return !g.ever && c.t > 20 * 40;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 60;
	}
}
