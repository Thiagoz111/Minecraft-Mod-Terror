package com.deadline.horror.casa.events;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * 35 nona_ventana (acts 2-5, intensity 4): the Nona looking in from OUTSIDE a window of the upper floor, where there
 * is no balcony (marker ventana_1p_afuera: a point in the air). Her head follows him. Once he has stared at her for a
 * moment her nails tap the glass three times; a little later she sinks below the sill. Looking away or walking up to
 * the window: gone.
 */
public class NonaVentana extends HorrorEvent {
	private static final String MARK = "ventana_1p_afuera";

	public NonaVentana() {
		super("nona_ventana", Kind.APPARITION);
		this.acts(2, 5).intensity(4).cooldown(300).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		Vec3 v = Apparitions.at(c.run, MARK);
		if (v == null || !Apparitions.canScare(c)) {
			return false;
		}
		double d = Apparitions.dist(c, v);
		// on the upper floor, in reach of the window, and not looking at it yet
		return d > 3.0 && d < 16.0 && Math.abs(v.y - 1.0 - c.p.getY()) < 2.0 && !Apparitions.sees(c, v.add(0, 1.2, 0), 70F);
	}

	@Override
	public void start(Ctx c) {
		Vec3 v = c.run.at(MARK);
		// floating outside: the face fills the window, nothing under her feet
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, v.add(0, -0.3, 0), c.run.yaw(MARK));
		if (n != null) {
			n.propSounds = false;
			n.setAction(FamilyEntity.POSE_IDLE);
			n.setFloating(true);
			n.watchPlayers(true);
		}
		c.put("e", n);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity n = c.get("e");
		if (Apparitions.gone(n)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			// he hid: whatever was there is not there when he comes out
			Apparitions.vanish(n, false);
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(Apparitions.watches(c, n, 45F));
		Vec3 face = n.position().add(0, 1.3, 0);
		if (g.total == 5) {
			Apparitions.sound(c, ModSounds.APARICION_NONA_RESPIRA, face, 0.6F, 0.8F);
		}
		if (g.total == 30) {
			Apparitions.sound(c, ModSounds.APARICION_VIDRIO_UNAS, face, 1.1F, 1.0F);
		}
		if (g.total == 70 && c.get("sink") == null) {
			c.put("sink", c.t);
			n.floatTo(n.position().add(0, -2.4, 0), 40);
		}
		Integer sink = c.get("sink");
		if (sink != null && c.t - sink > 42) {
			return true;
		}
		if (Apparitions.dist(c, n.position()) < 2.2 || g.lookedAway(6)) {
			Apparitions.vanish(n, false);
			return true;
		}
		return !g.ever && c.t > 20 * 30;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 45;
	}
}
