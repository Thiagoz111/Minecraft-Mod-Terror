package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.director.Exec;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.PoltergeistEvents;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 22 torre_sillas (acts 3-5, intensity 4; Poltergeist): he has been out of the dining room for ten seconds; when he
 * comes back the eight chairs are stacked in a tower on the table, up to the ceiling, the top one swaying
 * (CasaProps.chairTower, built the moment nobody looks). They are back around the table once he has gone again.
 * The script also fires it as one of the night's set pieces (Act 4).
 */
public class TorreSillas extends HorrorEvent {
	private static final String PREFIX = "casa:silla:";

	public TorreSillas() {
		super("torre_sillas", Kind.POLTER);
		this.acts(3, 5).intensity(4).cooldown(400).weight(6);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (Apparitions.hidden(c.p) || !Apparitions.hasArea(c.run, "comedor") || c.run.def.group("comedor_sillas").size() < 4
				|| c.run.inside(c.p, "comedor") || PoltergeistEvents.sinceIn(c.run, "comedor") < 200) {
			return false;
		}
		CasaProps.sweep(c.run);
		for (BlockPos rel : c.run.def.group("comedor_sillas")) {
			BlockPos p = c.run.origin.offset(rel);
			if (c.level().getBlockState(p).isAir() || CasaProps.held(c.run, p)) {
				return false;  // a chair is missing or somebody else holds it
			}
		}
		Vec3 mid = mid(c);
		return Apparitions.dist(c, mid) < 30 && !Apparitions.sees(c, mid, 60F);
	}

	private static Vec3 mid(Ctx c) {
		List<BlockPos> g = c.run.def.group("comedor_sillas");
		double x = 0, y = 0, z = 0;
		for (BlockPos rel : g) {
			BlockPos p = c.run.origin.offset(rel);
			x += p.getX() + 0.5;
			y += p.getY() + 0.5;
			z += p.getZ() + 0.5;
		}
		return new Vec3(x / g.size(), y / g.size(), z / g.size());
	}

	@Override
	public void start(Ctx c) {
		Set<String> before = new HashSet<>();
		for (String k : c.run.actors.keySet()) {
			if (k.startsWith(PREFIX)) {
				before.add(k);
			}
		}
		c.put("before", before);
		Vec3 mid = mid(c);
		Exec e = CasaProps.chairTower(c.run, "comedor_sillas", BlockPos.containing(mid));
		c.put("exec", e);
		c.put("mid", mid);
		c.put("built", -1);
		c.put("seen", -1);
	}

	@Override
	public boolean tick(Ctx c) {
		Vec3 mid = c.get("mid");
		int built = c.get("built");
		int seen = c.get("seen");
		if (built < 0 && c.run.event("sillas:torre")) {
			c.put("built", c.t);
			built = c.t;
			Polter.noise(c.run, mid, 50F);
		}
		if (built < 0) {
			return c.t > 20 * 40;  // he never left it alone: nothing happened
		}
		if (seen < 0 && (c.run.event("sillas:vistas") || c.run.inside(c.p, "comedor") && Apparitions.sees(c, mid.add(0, 1.0, 0), 40F))) {
			c.put("seen", c.t);
			Fx.shake(c.p, 0.3F, 10);
			return false;
		}
		if (seen < 0) {
			return c.t - built > 20 * 60;  // he did not come back: it was never there
		}
		// it stays until he has gone again and nobody sees the table
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(Apparitions.sees(c, mid.add(0, 1.0, 0), 55F));
		return c.t - seen > 60 && g.lost > 60 && !c.run.inside(c.p, "comedor");
	}

	@Override
	public void stop(Ctx c) {
		Exec e = c.get("exec");
		if (e != null) {
			e.cancel();
		}
		Set<String> before = c.get("before");
		List<String> mine = new ArrayList<>();
		for (String k : c.run.actors.keySet()) {
			if (k.startsWith(PREFIX) && (before == null || !before.contains(k))) {
				mine.add(k);
			}
		}
		for (String k : mine) {
			c.run.despawn(k);
		}
		CasaProps.sweep(c.run);  // the chairs whose displays are gone are put back around the table
	}

	@Override
	public int maxTicks() {
		return 20 * 130;
	}
}
