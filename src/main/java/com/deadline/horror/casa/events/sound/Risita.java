package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** 4 risita (acts 1-5, intensity 1): a little girl giggling in another room of the house. */
public class Risita extends HorrorEvent {
	public Risita() {
		super("risita", Kind.SOUND);
		this.acts(1, 5).intensity(1).cooldown(90).weight(11);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		Vec3 at = otherRoom(c, 6.0, 20.0);
		if (at == null) {
			return false;
		}
		c.put("at", at);
		return true;
	}

	/** The middle of another room of the house (floor + 1.1), within the distance range, that he cannot see. */
	public static Vec3 otherRoom(Ctx c, double min, double max) {
		String mine = c.room();
		List<Vec3> ok = new ArrayList<>();
		for (Map.Entry<String, SiteDef.Area> a : c.run.def.areas.entrySet()) {
			String k = a.getKey();
			if (k.equals(mine) || List.of("sitio", "casa", "exterior", "patio", "jardin", "cucha", "galpon").contains(k)) {
				continue;
			}
			AABB box = a.getValue().at(c.run.origin);
			Vec3 v = new Vec3(box.getCenter().x, box.minY + 1.1, box.getCenter().z);
			double d = v.distanceTo(c.p.position());
			if (d >= min && d <= max && HouseQuery.inHouse(c.run, c.p) && !HouseQuery.sees(c.run, c.p, v)) {
				ok.add(v);
			}
		}
		return ok.isEmpty() ? null : ok.get(c.rnd.nextInt(ok.size()));
	}

	@Override
	public void start(Ctx c) {
		Vec3 at = c.get("at");
		c.run.sound(ModSounds.POLTER_RISITA, at, 1.1F, Polter.pitch(c, 0.95F, 1.1F));
	}
}
