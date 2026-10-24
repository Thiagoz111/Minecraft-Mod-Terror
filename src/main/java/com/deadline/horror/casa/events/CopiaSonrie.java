package com.deadline.horror.casa.events;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * 41 copia_sonrie (acts 4-6, intensity 4; the copies of Act 5): Marta, Jorge or Toti standing still in a corner of
 * the room, smiling far too wide (look {@link FamilyEntity#LOOK_COPIA}), the head following him wherever he goes. When
 * he looks back after having looked away, it is not there any more.
 */
public class CopiaSonrie extends HorrorEvent {
	public CopiaSonrie() {
		super("copia_sonrie", Kind.APPARITION);
		this.acts(4, 6).intensity(4).cooldown(200).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		String room = c.room();
		if (room == null || !Apparitions.canScare(c)) {
			return false;
		}
		List<Vec3> spots = new ArrayList<>();
		for (Vec3 v : Apparitions.corners(c.run, room, c.p.getY())) {
			double d = Apparitions.dist(c, v);
			if (d >= 3.0 && d <= 10.0 && !Apparitions.sees(c, v.add(0, 1.0, 0), 70F)) {
				spots.add(v);
			}
		}
		if (spots.isEmpty()) {
			return false;
		}
		// one of the three whose real self is not standing around nearby
		List<EntityType<FamilyEntity>> who = new ArrayList<>(List.of(FamilyEntities.MARTA, FamilyEntities.JORGE, FamilyEntities.TOTI));
		Vec3 spot = spots.get(0);
		who.removeIf(t -> !c.level().getEntitiesOfClass(FamilyEntity.class, new AABB(spot, spot).inflate(16.0), e -> e.getType() == t).isEmpty());
		if (who.isEmpty()) {
			return false;
		}
		c.put("spot", spot);
		c.put("type", who.get(c.rnd.nextInt(who.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		Vec3 spot = c.get("spot");
		EntityType<FamilyEntity> type = c.get("type");
		FamilyEntity f = Apparitions.spawn(c, type, spot, Apparitions.yawTo(spot, c.p.position()));
		if (f != null) {
			f.setVariant(FamilyEntity.LOOK_COPIA);
			f.setAction(FamilyEntity.POSE_IDLE);
			f.watch(c.p);
		}
		c.put("e", f);
	}

	@Override
	public boolean tick(Ctx c) {
		FamilyEntity f = c.get("e");
		if (Apparitions.gone(f)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			// he hid: whatever was there is not there when he comes out
			Apparitions.vanish(f, false);
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.sees(c, f, 45F));
		if (!was && g.ever) {
			Apparitions.sound(c, ModSounds.APARICION_COPIA, f.getEyePosition(), 0.7F, Apparitions.pitch(c, 0.9F, 1.05F));
		}
		if (Apparitions.dist(c, f.position()) < 1.8 || g.lookedAway(6)) {
			Apparitions.vanish(f, false);
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
		return 20 * 70;
	}
}
