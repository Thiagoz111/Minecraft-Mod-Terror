package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.world.phys.Vec3;

/** 14 portazo (acts 1-5, intensity 2): a door slams hard somewhere else in the house, where he cannot see it. */
public class Portazo extends HorrorEvent {
	public Portazo() {
		super("portazo", Kind.POLTER);
		this.acts(1, 5).intensity(2).cooldown(80).weight(11);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		List<String> open = new ArrayList<>();
		List<String> shut = new ArrayList<>();
		String mine = Polter.roomDoor(c.run, c.room(), c.p.position());
		for (String d : HouseQuery.doorsNear(c.run, c.p.position(), 26.0)) {
			if (!Polter.plainDoor(d) || !Polter.isDoor(c.run, d) || d.equals(mine)) {
				continue;
			}
			Vec3 dp = HouseQuery.doorPos(c.run, d);
			if (dp.distanceTo(c.p.position()) < 6.0 || HouseQuery.sees(c.run, c.p, dp.add(0, 0.5, 0))) {
				continue;
			}
			(c.run.doorOpen(d) ? open : shut).add(d);
		}
		List<String> pool = open.isEmpty() ? shut : open;
		if (pool.isEmpty()) {
			return false;
		}
		c.put("door", pool.get(c.rnd.nextInt(pool.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		String d = c.get("door");
		Vec3 dp = HouseQuery.doorPos(c.run, d).add(0, 0.5, 0);
		if (c.run.doorOpen(d)) {
			c.run.door(d, false, true);
		} else {
			c.run.sound(ModSounds.DOOR_SLAM, dp, 1.6F, Polter.pitch(c, 0.85F, 1.0F));
		}
		Polter.noise(c.run, dp, 70F);
		if (dp.distanceTo(c.p.position()) < 12) {
			Fx.shake(c.p, 0.25F, 6);
		}
	}
}
