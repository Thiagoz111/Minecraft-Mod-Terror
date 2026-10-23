package com.deadline.horror.casa.events;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * 40 toti_rincon (acts 3-5, intensity 4): Toti standing in the corner of his room, his face to the wall, not moving
 * (marker toti_rincon). If he is looked at for 3 seconds his head turns all the way round -- the body does not move --
 * and he stares back, with the creak and the cracks of the neck. Looking away or walking up to him: gone.
 */
public class TotiRincon extends HorrorEvent {
	private static final String MARK = "toti_rincon";
	private static final int STARE = 60;

	public TotiRincon() {
		super("toti_rincon", Kind.APPARITION);
		this.acts(3, 5).intensity(4).cooldown(300).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		Vec3 v = Apparitions.at(c.run, MARK);
		if (v == null || !Apparitions.canScare(c)) {
			return false;
		}
		double d = Apparitions.dist(c, v);
		if (d < 3.0 || d > 12.0 || Math.abs(v.y - c.p.getY()) > 1.5 || Apparitions.sees(c, v.add(0, 1.0, 0), 70F)) {
			return false;
		}
		// the real Toti is not standing around nearby
		return c.level().getEntitiesOfClass(FamilyEntity.class, new AABB(v, v).inflate(16.0), e -> e.getType() == FamilyEntities.TOTI).isEmpty();
	}

	@Override
	public void start(Ctx c) {
		FamilyEntity t = Apparitions.spawn(c, FamilyEntities.TOTI, c.run.at(MARK), c.run.yaw(MARK));
		if (t != null) {
			t.watchPlayers(false);
			t.setAction(FamilyEntity.POSE_CORNER);
		}
		c.put("e", t);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity t = c.get("e");
		if (Apparitions.gone(t)) {
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(Apparitions.sees(c, t, 45F));
		Integer turned = c.get("turned");
		if (turned == null && g.total >= STARE) {
			turned = c.t;
			c.put("turned", turned);
			t.setAction(FamilyEntity.POSE_CORNER_TURN);
			Apparitions.sound(c, ModSounds.APARICION_CUELLO, t.position().add(0, 1.6, 0), 1.0F, 0.95F);
		}
		if (turned != null && c.t - turned == 16) {
			Apparitions.sound(c, ModSounds.APARICION_CUELLO, t.position().add(0, 1.6, 0), 1.1F, 0.8F);
		}
		if (Apparitions.dist(c, t.position()) < 1.8 || g.lookedAway(turned != null ? 6 : 14)) {
			Apparitions.vanish(t, false);
			return true;
		}
		return !g.ever && c.t > 20 * 45;
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
