package com.deadline.horror.casa.events;

import com.deadline.director.Props;
import com.deadline.entity.SombraEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 45 visitante (acts 3-6, intensity 4; Gerald's Game): a tall figure (~2.6 blocks), standing perfectly still in the
 * darkest corner of the room he is in. It is only there in the dark: the moment his flashlight beam (or the room light)
 * touches it, there is nothing in the corner. Walking up to it, or looking away after seeing it: gone.
 */
public class Visitante extends HorrorEvent {
	public Visitante() {
		super("visitante", Kind.APPARITION);
		this.acts(3, 6).intensity(4).cooldown(260).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		String room = c.room();
		if (room == null || room.startsWith("pasillo") || !Apparitions.canScare(c)) {
			return false;
		}
		for (Vec3 v : Apparitions.corners(c.run, room, c.p.getY())) {
			double d = Apparitions.dist(c, v);
			if (d < 3.5 || d > 9.0 || !HouseQuery.dark(c.run, BlockPos.containing(v.x, v.y + 1.2, v.z))) {
				continue;
			}
			double ceil = Apparitions.ceilingY(c.run, v.add(0, 0.5, 0));
			if (Double.isNaN(ceil) || ceil - v.y < 2.7 || Apparitions.sees(c, v.add(0, 1.4, 0), 70F)) {
				continue;
			}
			c.put("spot", v);
			return true;
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		Vec3 v = c.get("spot");
		SombraEntity s = Apparitions.spawn(c, ModEntities.SOMBRA, v, Apparitions.yawTo(v, c.p.position()));
		if (s != null) {
			s.setVariant(SombraEntity.VARIANT_VISITANTE);
			s.setNoGravity(true);
		}
		c.put("e", s);
	}

	@Override
	public boolean tick(Ctx c) {
		SombraEntity s = c.get("e");
		if (Apparitions.gone(s)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			// he hid: whatever was there is not there when he comes out
			Apparitions.vanish(s, false);
			return true;
		}
		// in the light it was never there
		if (Props.beamOn(c.p, s) || !HouseQuery.dark(c.run, BlockPos.containing(s.getX(), s.getY() + 1.2, s.getZ()))) {
			Apparitions.vanish(s, false);
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.watches(c, s, 40F));
		if (!was && g.ever) {
			Apparitions.sound(c, ModSounds.APARICION_VISITANTE, s.position().add(0, 2.0, 0), 0.9F, 1.0F);
		}
		if (Apparitions.dist(c, s.position()) < 3.0 || g.lookedAway(20)) {
			Apparitions.vanish(s, false);
			return true;
		}
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
