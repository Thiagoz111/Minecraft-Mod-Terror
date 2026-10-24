package com.deadline.horror.casa.events;

import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * 42 lucia_techo_corre (acts 4-6, intensity 5): Lucía, possessed, upside down on the ceiling of the upstairs hall,
 * scuttles like a spider down the hall TOWARD him and darts into a bedroom -- and that door slams shut. The bedroom doors
 * of the 1P hall are the site's door markers; she runs along the ceiling (box top on it) and drops into the doorway.
 */
public class LuciaTechoCorre extends HorrorEvent {
	private static final List<String> DOORS = List.of("lucia", "toti", "matrimonial", "huespedes", "bano_1p", "cuarto_nono");
	private static final double RUN = 0.42, DOORWAY = 0.3, BODY = 1.5;

	public LuciaTechoCorre() {
		super("lucia_techo_corre", Kind.APPARITION);
		this.acts(4, 6).intensity(5).cooldown(400).weight(6);
	}

	private record Plan(String door, Vec3 start, Vec3 mid, Vec3 doorway, Vec3 room) {
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c) || !Apparitions.hasArea(c.run, "pasillo_1p")) {
			return false;
		}
		AABB hall = c.run.area("pasillo_1p");
		if (!hall.inflate(1.5, 1.0, 1.5).contains(c.p.position())) {
			return false;
		}
		boolean alongX = hall.getXsize() >= hall.getZsize();
		Vec3 centre = hall.getCenter();
		for (String d : DOORS) {
			Vec3 dp = HouseQuery.doorPos(c.run, d);
			if (dp == null) {
				continue;
			}
			// the hall's centre line next to the door, and a start 6 blocks further along it, away from him
			Vec3 at = alongX ? new Vec3(dp.x, dp.y, centre.z) : new Vec3(centre.x, dp.y, dp.z);
			double dist = at.distanceTo(c.p.position());
			if (dist < 4.0 || dist > 14.0) {
				continue;
			}
			Vec3 axis = alongX ? new Vec3(1, 0, 0) : new Vec3(0, 0, 1);
			double away = at.subtract(c.p.position()).dot(axis) >= 0 ? 1.0 : -1.0;
			Vec3 start = at.add(axis.scale(6.0 * away));
			if (!hall.inflate(0.0, 2.0, 0.0).contains(start)) {
				start = at.add(axis.scale(3.5 * away));
			}
			// the door sits deep in the wall (never visible from along the hall): he looks at its doorway or at the
			// stretch of ceiling she runs along
			Vec3 mouth = Apparitions.doorway(c.run, d, at);
			if (mouth == null || !Apparitions.seesAny(c, 60F, mouth.add(0, 1.0, 0), start.add(0, BODY, 0), at.add(0, BODY, 0))) {
				continue;
			}
			double ceilA = Apparitions.ceilingY(c.run, start);
			double ceilB = Apparitions.ceilingY(c.run, at);
			double floor = dp.y - 0.5;
			if (Double.isNaN(ceilA) || Double.isNaN(ceilB) || ceilA - floor < 2.6 || ceilB - floor < 2.6) {
				continue;
			}
			// through the doorway (box top under the lintel: 2 above the floor) and into the room
			Vec3 into = dp.subtract(at).multiply(1, 0, 1);
			if (into.lengthSqr() < 1.0E-4) {
				continue;
			}
			into = into.normalize();
			Vec3 a = new Vec3(start.x, ceilA - BODY, start.z);
			Vec3 b = new Vec3(at.x, ceilB - BODY, at.z);
			Vec3 door = new Vec3(dp.x, floor + 2.0 - BODY, dp.z);
			Vec3 room = door.add(into.scale(1.6));
			c.put("plan", new Plan(d, a, b, door, room));
			return true;
		}
		return false;
	}

	@Override
	public void start(Ctx c) {
		Plan p = c.get("plan");
		if (!c.run.doorOpen(p.door())) {
			c.run.door(p.door(), true, false);
		}
		PoseidaEntity l = Apparitions.spawn(c, ModEntities.POSEIDA, p.start(), Apparitions.yawTo(p.start(), p.mid()));
		if (l != null) {
			l.setVariant(PoseidaEntity.LOOK_POSSESSED);
			l.setAction(PoseidaEntity.ACT_CEILING_RUN);
			l.setNoGravity(true);
		}
		c.put("e", l);
		c.put("leg", 0);
		Apparitions.sound(c, ModSounds.APARICION_TECHO_CORRE, p.start().add(0, BODY, 0), 1.4F, 1.0F);
		Apparitions.noise(c, p.start(), 40F);
	}

	@Override
	public boolean tick(Ctx c) {
		PoseidaEntity l = c.get("e");
		Plan p = c.get("plan");
		if (Apparitions.gone(l)) {
			return true;
		}
		int leg = c.<Integer>get("leg");
		Vec3[] pts = {p.start(), p.mid(), p.doorway(), p.room()};
		if (leg >= 3) {
			// in: the door slams behind her, and from the room a giggle
			Apparitions.sound(c, ModSounds.POSEIDA_GIGGLE, l.position(), 1.2F, 0.85F);
			c.run.door(p.door(), false, true);
			Apparitions.noise(c, l.position(), 70F);
			Apparitions.vanish(l, false);
			return true;
		}
		Vec3 to = pts[leg + 1];
		Vec3 pos = l.position();
		double speed = leg == 0 ? RUN : DOORWAY;
		Vec3 delta = to.subtract(pos);
		double len = delta.length();
		if (len <= speed) {
			Apparitions.glide(l, to, false);
			c.put("leg", leg + 1);
		} else {
			Apparitions.glide(l, pos.add(delta.scale(speed / len)), false);
		}
		if (delta.x * delta.x + delta.z * delta.z > 1.0E-4) {
			Apparitions.face(l, Apparitions.yawTo(pos, to));
		}
		return false;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 8;
	}
}
