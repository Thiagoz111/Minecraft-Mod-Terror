package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Drawers;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 26 cajones (acts 2-5, intensity 3): he turns round and every drawer of the room is open, all of them, at once. It
 * happened without a sound while his back was turned. A couple of seconds after he sees them they all slam shut
 * together.
 */
public class Cajones extends HorrorEvent {
	public Cajones() {
		super("cajones", Kind.POLTER);
		this.acts(2, 5).intensity(3).cooldown(200).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String room = c.room();
		if (room == null || room.startsWith("pasillo")) {
			return false;
		}
		List<BlockPos> drawers = Polter.kitIn(c.run, room, Drawers::isKey);
		if (drawers.isEmpty()) {
			return false;
		}
		for (BlockPos p : drawers) {
			if (Apparitions.sees(c, Vec3.atCenterOf(p), 70F)) {
				return false;  // all of them behind his back
			}
		}
		c.put("drawers", drawers);
		return true;
	}

	@Override
	public void start(Ctx c) {
		List<BlockPos> drawers = c.get("drawers");
		List<String> actors = new ArrayList<>();
		for (BlockPos p : drawers) {
			int n = Drawers.count(c.level().getBlockState(p));
			for (int i = 0; i < n; i++) {
				actors.addAll(Drawers.open(c.run, p, i));
			}
		}
		c.put("actors", actors);
		c.put("seen", -1);
	}

	private static Vec3 mid(List<BlockPos> ps) {
		double x = 0, y = 0, z = 0;
		for (BlockPos p : ps) {
			x += p.getX() + 0.5;
			y += p.getY() + 0.5;
			z += p.getZ() + 0.5;
		}
		return new Vec3(x / ps.size(), y / ps.size(), z / ps.size());
	}

	@Override
	public boolean tick(Ctx c) {
		List<BlockPos> drawers = c.get("drawers");
		List<String> actors = c.get("actors");
		int seen = c.get("seen");
		if (actors.isEmpty()) {
			return true;
		}
		if (seen < 0) {
			for (BlockPos p : drawers) {
				if (Apparitions.sees(c, Vec3.atCenterOf(p), 40F)) {
					c.put("seen", c.t);
					return false;
				}
			}
			if (c.t > 20 * 40) {
				Drawers.close(c.run, actors);  // never noticed: they close as quietly as they opened
				return true;
			}
			return false;
		}
		if (c.t - seen >= 40) {
			Vec3 m = mid(drawers);
			Drawers.close(c.run, actors);
			c.run.sound(ModSounds.POLTER_CAJONES, m, 1.4F, Polter.pitch(c, 0.9F, 1.05F));
			Polter.noise(c.run, m, 55F);
			Fx.shake(c.p, 0.3F, 6);
			return true;
		}
		return false;
	}

	@Override
	public void stop(Ctx c) {
		Drawers.close(c.run, c.get("actors"));
	}

	@Override
	public int maxTicks() {
		return 20 * 50;
	}
}
