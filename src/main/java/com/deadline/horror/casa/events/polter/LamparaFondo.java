package com.deadline.horror.casa.events.polter;

import com.deadline.entity.SombraEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 19 lampara_fondo (acts 3-5, intensity 4): in the dark hall, the lamp at the far end comes on by itself, buzzing.
 * Under it, standing, a tall figure facing him. The lamp stutters and goes out, and with it the figure.
 */
public class LamparaFondo extends HorrorEvent {
	public LamparaFondo() {
		super("lampara_fondo", Kind.POLTER);
		this.acts(3, 5).intensity(4).cooldown(300).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String room = c.room();
		if (room == null || !room.startsWith("pasillo")) {
			return false;
		}
		String g = Polter.roomLights(c.run, room);
		if (g == null) {
			return false;
		}
		int best = -1;
		double bd = 0;
		for (int i = 0; i < c.run.def.group(g).size(); i++) {
			BlockPos lamp = Polter.fixture(c.run, g, i);
			Vec3 lc = Vec3.atCenterOf(lamp);
			double d = Math.hypot(lc.x - c.p.getX(), lc.z - c.p.getZ());
			if (Polter.lit(c.run, g, i) || d < 8.0 || d > 22.0) {
				continue;
			}
			double fy = Polter.floorAt(c.run, lc.add(0, -0.6, 0), 5);
			if (Double.isNaN(fy) || !HouseQuery.standable(c.run, BlockPos.containing(lc.x, fy + 0.1, lc.z))) {
				continue;
			}
			Vec3 feet = new Vec3(lc.x, fy, lc.z);
			if (!Apparitions.sees(c, feet.add(0, 1.3, 0), 35F)) {
				continue;
			}
			if (d > bd) {
				bd = d;
				best = i;
				c.put("feet", feet);
			}
		}
		if (best < 0) {
			return false;
		}
		c.put("group", g);
		c.put("lamp", best);
		return true;
	}

	@Override
	public void start(Ctx c) {
		String g = c.get("group");
		int i = c.get("lamp");
		Vec3 feet = c.get("feet");
		c.run.light(g, i, true);
		c.run.sound(ModSounds.POLTER_ZUMBIDO, Vec3.atCenterOf(Polter.fixture(c.run, g, i)), 1.0F, 0.85F);
		SombraEntity s = Apparitions.spawn(c, ModEntities.SOMBRA, feet, Apparitions.yawTo(feet, c.p.position()));
		if (s != null) {
			s.setVariant(SombraEntity.VARIANT_VISITANTE);
			s.setNoGravity(true);
		}
		c.put("e", s);
		c.put("out", -1);
	}

	@Override
	public boolean tick(Ctx c) {
		String g = c.get("group");
		int i = c.get("lamp");
		SombraEntity s = c.get("e");
		int out = c.get("out");
		if (out < 0) {
			Apparitions.Gaze gz = Apparitions.gaze(c);
			boolean was = gz.ever;
			gz.update(s != null && Apparitions.watches(c, s, 40F));
			if (!was && gz.ever) {
				c.run.sound(ModSounds.APARICION_VISITANTE, s.position().add(0, 2.0, 0), 0.8F, 0.9F);
				SanityManager.add(c.p, -6F);
			}
			boolean near = s != null && Apparitions.dist(c, s.position()) < 5.0;
			if (Apparitions.hidden(c.p) || near || gz.total >= 30 || c.t >= 70 || gz.lookedAway(15)) {
				out = c.t;
				c.put("out", out);
			}
			return false;
		}
		// it stutters and goes out; the figure with it
		int k = c.t - out;
		if (k == 0 || k == 6) {
			c.run.light(g, i, false);
		} else if (k == 3) {
			c.run.light(g, i, true);
			c.run.sound(ModSounds.POLTER_ZUMBIDO, Vec3.atCenterOf(Polter.fixture(c.run, g, i)), 0.7F, 1.2F);
		}
		if (k == 6) {
			Apparitions.vanish(s, false);
		}
		return k >= 14;
	}

	@Override
	public void stop(Ctx c) {
		String g = c.get("group");
		Integer i = c.get("lamp");
		if (g != null && i != null) {
			c.run.light(g, i, false);
		}
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return 20 * 10;
	}
}
