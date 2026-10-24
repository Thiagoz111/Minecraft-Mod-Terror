package com.deadline.horror.casa.events;

import com.deadline.entity.ApparitionEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.ApparitionEntities;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 39 bajo_cama (acts 3-6, intensity 3; Aterrados): a grey hand on far too long an arm slides out from under a bed in
 * his room, feels along the floorboards, digs its nails in... and is yanked back into the dark. The beds are the hiding
 * spots of the site (hide_cama_* = the space under the bed, hide_cama_*_out = in front of it). If he steps up to it,
 * it is pulled back at once.
 */
public class BajoCama extends HorrorEvent {
	private static final int CREEP = 36, GRIP = 26, RETRACT = 7;
	private static final double OUT = 1.15;

	public BajoCama() {
		super("bajo_cama", Kind.APPARITION);
		this.acts(3, 6).intensity(3).cooldown(150).weight(9);
	}

	private record Bed(Vec3 in, Vec3 dir) {
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		String room = c.room();
		List<Bed> ok = new ArrayList<>();
		for (String k : HouseQuery.points(c.run, "hide_cama_")) {
			if (k.endsWith("_out") || !Apparitions.has(c.run, k + "_out")) {
				continue;
			}
			Vec3 in = c.run.at(k);
			Vec3 out = c.run.at(k + "_out");
			Vec3 dir = out.subtract(in).multiply(1, 0, 1);
			if (dir.lengthSqr() < 0.25) {
				continue;
			}
			dir = dir.normalize();
			double d = Apparitions.dist(c, out);
			if (d < 2.5 || d > 9.0 || Math.abs(in.y - c.p.getY()) > 1.0) {
				continue;
			}
			if (room != null && !room.equals(HouseQuery.roomAt(c.run, in.add(0, 0.5, 0)))) {
				continue;
			}
			// he is facing the floor in front of the bed
			Vec3 floor = in.add(dir.scale(0.9)).add(0, 0.15, 0);
			if (!Apparitions.sees(c, floor, 55F)) {
				continue;
			}
			ok.add(new Bed(in, dir));
		}
		if (ok.isEmpty()) {
			return false;
		}
		c.put("bed", ok.get(c.rnd.nextInt(ok.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		Bed b = c.get("bed");
		double y = Apparitions.floorY(c.run, BlockPos.containing(b.in().x, b.in().y + 0.1, b.in().z));
		Vec3 start = new Vec3(b.in().x, y, b.in().z).subtract(b.dir().scale(0.25));
		ApparitionEntity hand = Apparitions.spawn(c, ApparitionEntities.MANO, start, Apparitions.yawTo(start, start.add(b.dir())));
		if (hand != null) {
			hand.setAction(ApparitionEntities.MANO_CREEP);
		}
		c.put("e", hand);
		c.put("start", start);
		Apparitions.sound(c, ModSounds.APARICION_MANO_RASGUNO, start, 0.8F, Apparitions.pitch(c, 0.85F, 1.0F));
	}

	@Override
	public boolean tick(Ctx c) {
		ApparitionEntity hand = c.get("e");
		if (Apparitions.gone(hand)) {
			return true;
		}
		if (Apparitions.hidden(c.p)) {
			// he hid: whatever was there is not there when he comes out
			Apparitions.vanish(hand, false);
			return true;
		}
		Bed b = c.get("bed");
		Vec3 start = c.get("start");
		Integer back = c.get("back");
		if (back == null && Apparitions.dist(c, hand.position()) < 1.7) {
			back = c.t;
			c.put("back", back);
			c.put("from", hand.position());
			hand.setAction(ApparitionEntities.MANO_RETRACT);
			Apparitions.sound(c, ModSounds.APARICION_MANO_RETIRA, hand.position(), 1.0F, 1.0F);
		}
		if (back == null) {
			if (c.t <= CREEP) {
				float u = c.t / (float) CREEP;
				// it does not slide: it pulls itself out, finger-step by finger-step
				float steps = u + 0.06F * (float) Math.sin(u * Math.PI * 10.0);
				Vec3 at = start.add(b.dir().scale(OUT * Math.max(0F, Math.min(1F, steps))));
				hand.setPos(at.x, at.y, at.z);
			} else if (c.t == CREEP + 1) {
				hand.setAction(ApparitionEntities.MANO_GRIP);
				Apparitions.sound(c, ModSounds.APARICION_MANO_RASGUNO, hand.position(), 1.0F, 0.8F);
			} else if (c.t > CREEP + GRIP) {
				c.put("back", c.t);
				c.put("from", hand.position());
				hand.setAction(ApparitionEntities.MANO_RETRACT);
				Apparitions.sound(c, ModSounds.APARICION_MANO_RETIRA, hand.position(), 1.0F, 1.0F);
			}
			return false;
		}
		// yanked back under the bed, fast, then gone
		Vec3 from = c.get("from");
		float u = Math.min(1F, (c.t - back) / (float) RETRACT);
		Vec3 at = from.lerp(start.subtract(b.dir().scale(1.4)), u * u);
		hand.setPos(at.x, at.y, at.z);
		return u >= 1F;
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
