package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.Vec3;

/**
 * 2 tres_golpes (acts 1-5, intensity 2): three knocks inside the wall right beside him. If he knocks back (right click
 * on a wall within reach: see {@link com.deadline.horror.casa.Interactables}), something inside the wall answers
 * with as many knocks, from right where he knocked; the third time it answers with one more.
 */
public class TresGolpes extends HorrorEvent {
	private static final int SPACING = 7;

	public TresGolpes() {
		super("tres_golpes", Kind.SOUND);
		this.acts(1, 5).intensity(2).cooldown(120).weight(10);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		BlockPos head = BlockPos.containing(c.p.getEyePosition());
		Vec3 best = null;
		double bd = Double.MAX_VALUE;
		for (Direction d : Direction.Plane.HORIZONTAL) {
			for (int k = 1; k <= 2; k++) {
				BlockPos q = head.relative(d, k);
				if (Polter.wall(c.run, q)) {
					Vec3 face = Vec3.atCenterOf(q).subtract(d.getStepX() * 0.45, 0, d.getStepZ() * 0.45);
					double dist = face.distanceTo(c.p.getEyePosition());
					if (dist < 1.9 && dist < bd) {
						bd = dist;
						best = face;
					}
					break;
				}
			}
		}
		if (best == null) {
			return false;
		}
		c.put("wall", best);
		return true;
	}

	@Override
	public void start(Ctx c) {
		List<Integer> knocks = new ArrayList<>(List.of(0, SPACING, SPACING * 2));
		c.put("knocks", knocks);
		c.put("from", c.<Vec3>get("wall"));
		c.put("heard", 0);
		c.put("last", 0);
		c.put("answers", 0);
	}

	@Override
	public boolean tick(Ctx c) {
		List<Integer> knocks = c.get("knocks");
		Vec3 from = c.get("from");
		for (int k : knocks) {
			if (k == c.t) {
				c.run.sound(ModSounds.POLTER_GOLPE, from, 1.0F, Polter.pitch(c, 0.85F, 0.95F));
			}
		}
		int heard = c.get("heard");
		int last = c.get("last");
		int answers = c.get("answers");
		// he knocks back: count his knocks, and when he stops, the wall answers
		if (Polter.got(c, "knock")) {
			heard++;
			last = c.t;
			Object at = c.run.vars.get("polter:knock_at");
			if (at instanceof Vec3 v) {
				c.put("from", v);
			}
		}
		if (heard > 0 && c.t - last > 22 && answers < 3) {
			answers++;
			int n = Math.min(6, answers == 3 ? heard + 1 : heard);
			knocks.clear();
			for (int i = 0; i < n; i++) {
				knocks.add(c.t + 6 + i * SPACING);
			}
			heard = 0;
			last = c.t + 6 + n * SPACING;
		}
		c.put("heard", heard);
		c.put("last", last);
		c.put("answers", answers);
		int quiet = c.t - Math.max(last, SPACING * 2);
		return answers >= 3 && quiet > 30 || heard == 0 && quiet > 20 * 12;
	}

	@Override
	public int maxTicks() {
		return 20 * 60;
	}
}
