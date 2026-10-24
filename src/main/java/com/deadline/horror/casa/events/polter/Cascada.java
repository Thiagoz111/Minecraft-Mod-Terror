package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.director.Exec;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 15 cascada (acts 4-6, intensity 4): every door of the upstairs hall slams shut, one after another, from the far end
 * towards him (the "pasillo_1p_cascada" doors). The ones he cannot see open first, silently.
 */
public class Cascada extends HorrorEvent {
	private static final int GAP = 7, LEAD = 14;

	public Cascada() {
		super("cascada", Kind.POLTER);
		this.acts(4, 6).intensity(4).cooldown(300).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c) || !Apparitions.hasArea(c.run, "pasillo_1p")
				|| !c.run.area("pasillo_1p").inflate(0.6, 0, 0.6).contains(c.p.position())) {
			return false;
		}
		List<String> doors = doors(c);
		if (doors.size() < 2) {
			return false;
		}
		c.put("doors", doors);
		return true;
	}

	/** The door markers of the cascade group (block positions authored far end first), else the hall's room doors. */
	private static List<String> doors(Ctx c) {
		List<String> out = new ArrayList<>();
		for (BlockPos rel : c.run.def.group("pasillo_1p_cascada")) {
			for (Map.Entry<String, BlockPos> d : c.run.def.doors.entrySet()) {
				BlockPos q = d.getValue();
				if (Math.abs(q.getX() - rel.getX()) + Math.abs(q.getZ() - rel.getZ()) <= 1 && Math.abs(q.getY() - rel.getY()) <= 1
						&& Polter.plainDoor(d.getKey()) && Polter.isDoor(c.run, d.getKey()) && !out.contains(d.getKey())) {
					out.add(d.getKey());
					break;
				}
			}
		}
		if (out.isEmpty()) {
			for (String d : HouseQuery.doorsNear(c.run, c.p.position(), 24.0)) {
				Vec3 dp = HouseQuery.doorPos(c.run, d);
				if (Polter.plainDoor(d) && Polter.isDoor(c.run, d) && c.run.area("pasillo_1p").inflate(2.6, 0, 2.6).contains(dp)) {
					out.add(d);
				}
			}
		}
		return out;
	}

	@Override
	public void start(Ctx c) {
		List<String> doors = c.get("doors");
		for (String d : doors) {
			if (!c.run.doorOpen(d) && !HouseQuery.sees(c.run, c.p, HouseQuery.doorPos(c.run, d).add(0, 0.5, 0))) {
				c.run.door(d, true, false);
			}
		}
	}

	@Override
	public boolean tick(Ctx c) {
		List<String> doors = c.get("doors");
		if (c.t == LEAD) {
			Exec e = CasaProps.doorCascade(c.run, doors, GAP);
			c.put("exec", e);
			Vec3 mid = c.run.area("pasillo_1p").getCenter();
			Polter.noise(c.run, mid, 85F);
		}
		if (c.t > LEAD && (c.t - LEAD) % GAP == 0 && (c.t - LEAD) / GAP <= doors.size()) {
			Fx.shake(c.p, 0.35F, 6);
		}
		return c.t > LEAD + 2 && (c.run.event("puertas:fin") || c.t > LEAD + GAP * doors.size() + 30);
	}

	@Override
	public void stop(Ctx c) {
		Exec e = c.get("exec");
		if (e != null) {
			e.cancel();
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 15;
	}
}
