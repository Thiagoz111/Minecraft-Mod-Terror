package com.deadline.horror.casa.blood;

import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModSounds;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * 48 pisadas (acts 3-6, intensity 3): bare bloody footprints, one after another at a slow walking pace, from the door
 * of the room to a closed wardrobe -- somebody he cannot see walks in and stops in front of it, feet together. A
 * moment later, from inside the wardrobe, breathing. The footprints stay ({@link BloodDecals#clear}).
 * <p>The way is found on the floor of the room (a breadth-first walk over standable cells), so the prints go round
 * the beds and the tables like a person would.
 */
public class Pisadas extends HorrorEvent {
	private static final double STRIDE = 0.62;
	private static final int STEP_TICKS = 9;

	public Pisadas() {
		super("pisadas", Kind.BLOOD);
		this.acts(3, 6).intensity(3).cooldown(200).weight(8);
	}

	record Step(Vec3 at, float yaw, boolean left) {
	}

	record Plan(String wardrobe, Vec3 inside, List<Step> steps) {
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		List<Plan> ok = new ArrayList<>();
		for (String k : HouseQuery.points(c.run, "hide_ropero_")) {
			if (k.endsWith("_out") || !Apparitions.has(c.run, k + "_out")) {
				continue;
			}
			Vec3 out = c.run.at(k + "_out");
			double d = Apparitions.dist(c, out);
			if (d < 3.0 || d > 12.0 || Math.abs(out.y - c.p.getY()) > 1.5) {
				continue;
			}
			String wardrobe = k.substring("hide_".length());
			if (anyOpen(c.run, wardrobe)) {
				continue;  // it has to lead to a CLOSED wardrobe
			}
			List<Vec3> path = path(c.run, out);
			if (path == null || path.size() < 4) {
				continue;
			}
			ok.add(new Plan(wardrobe, c.run.at(k), steps(c.run, path, c.run.at(k))));
		}
		if (ok.isEmpty()) {
			return false;
		}
		c.put("plan", ok.get(c.rnd.nextInt(ok.size())));
		return true;
	}

	static boolean anyOpen(Run r, String wardrobe) {
		for (String d : r.def.doors.keySet()) {
			if (d.startsWith(wardrobe) && r.doorOpen(d)) {
				return true;
			}
		}
		return false;
	}

	/**
	 * Cell centres (at floor level) from the door of the room the wardrobe is in to the spot in front of it, or null.
	 * Breadth-first over the standable cells of the room; it starts next to the room's door, or at the far end of the
	 * room when no door is near.
	 */
	static List<Vec3> path(Run r, Vec3 out) {
		BlockPos goal = BlockPos.containing(out.x, out.y + 0.2, out.z);
		String room = HouseQuery.roomAt(r, out.add(0, 0.5, 0));
		AABB box = room != null && r.def.areas.containsKey(room) ? r.area(room) : new AABB(goal).inflate(6, 0, 6);
		box = box.inflate(0.01);
		int y = goal.getY();
		if (!HouseQuery.standable(r, goal)) {
			return null;
		}
		Map<BlockPos, BlockPos> next = new HashMap<>();  // cell -> the cell after it on the way to the goal
		Map<BlockPos, Integer> dist = new HashMap<>();
		ArrayDeque<BlockPos> q = new ArrayDeque<>();
		q.add(goal);
		dist.put(goal, 0);
		while (!q.isEmpty() && dist.size() < 400) {
			BlockPos cur = q.poll();
			for (BlockPos n : new BlockPos[] {cur.north(), cur.south(), cur.east(), cur.west()}) {
				if (dist.containsKey(n) || !box.contains(Vec3.atCenterOf(n)) || n.getY() != y || !HouseQuery.standable(r, n)) {
					continue;
				}
				dist.put(n, dist.get(cur) + 1);
				next.put(n, cur);
				q.add(n);
			}
		}
		// start: the reachable cell next to a door of this room, else the farthest one
		BlockPos start = null;
		for (String door : HouseQuery.doorsNear(r, out, 12.0)) {
			if (door.startsWith("ropero_") || r.def.doors.get(door) == null) {
				continue;
			}
			BlockPos dp = r.origin.offset(r.def.doors.get(door));
			for (BlockPos n : new BlockPos[] {dp.north(), dp.south(), dp.east(), dp.west()}) {
				if (n.getY() == y && dist.containsKey(n) && dist.get(n) >= 3) {
					start = n;
					break;
				}
			}
			if (start != null) {
				break;
			}
		}
		if (start == null) {
			int best = 0;
			for (Map.Entry<BlockPos, Integer> e : dist.entrySet()) {
				if (e.getValue() > best) {
					best = e.getValue();
					start = e.getKey();
				}
			}
			if (best < 4) {
				return null;
			}
		}
		List<Vec3> out2 = new ArrayList<>();
		BlockPos cur = start;
		int guard = 0;
		while (cur != null && guard++ < 400) {
			out2.add(new Vec3(cur.getX() + 0.5, y, cur.getZ() + 0.5));
			if (cur.equals(goal)) {
				break;
			}
			cur = next.get(cur);
		}
		return out2;
	}

	/** Footprints every STRIDE along the path, left and right of it, and the last two side by side facing `face`. */
	static List<Step> steps(Run r, List<Vec3> path, Vec3 face) {
		List<Step> out = new ArrayList<>();
		// walk the polyline, dropping a print every STRIDE
		double carry = 0.3;
		boolean left = true;
		for (int i = 0; i + 1 < path.size(); i++) {
			Vec3 a = path.get(i);
			Vec3 b = path.get(i + 1);
			Vec3 seg = b.subtract(a);
			double len = seg.length();
			if (len < 1.0E-4) {
				continue;
			}
			Vec3 dir = seg.scale(1.0 / len);
			// smooth the turn: look one cell further ahead
			Vec3 ahead = i + 2 < path.size() ? path.get(i + 2).subtract(a).normalize() : dir;
			Vec3 heading = dir.add(ahead).normalize();
			double s = carry;
			while (s < len) {
				Vec3 p = a.add(dir.scale(s));
				Vec3 side = new Vec3(heading.z, 0, -heading.x).scale(left ? 0.11 : -0.11);
				Vec3 at = BloodDecals.onFloor(r, p.add(side));
				out.add(new Step(at, yaw(heading), left));
				left = !left;
				s += STRIDE;
			}
			carry = s - len;
		}
		// he stops in front of the wardrobe: feet together
		Vec3 end = path.get(path.size() - 1);
		Vec3 to = face.subtract(end).multiply(1, 0, 1);
		Vec3 h = to.lengthSqr() > 1.0E-4 ? to.normalize() : new Vec3(0, 0, 1);
		Vec3 side = new Vec3(h.z, 0, -h.x);
		out.add(new Step(BloodDecals.onFloor(r, end.add(side.scale(0.12))), yaw(h), true));
		out.add(new Step(BloodDecals.onFloor(r, end.add(side.scale(-0.12))), yaw(h), false));
		return out;
	}

	/** Yaw (degrees) whose direction is h (BloodDecals.dirOf convention). */
	static float yaw(Vec3 h) {
		return (float) Math.toDegrees(Math.atan2(-h.x, h.z));
	}

	@Override
	public void start(Ctx c) {
		if (c.get("plan") == null) {
			canRun(c);  // fired by hand: find a wardrobe now (no plan = nothing happens)
		}
	}

	@Override
	public boolean tick(Ctx c) {
		Plan plan = c.get("plan");
		if (plan == null || Apparitions.hidden(c.p)) {
			return true;
		}
		List<Step> steps = plan.steps();
		int i = (c.t - 4) / STEP_TICKS;
		if (c.t >= 4 && (c.t - 4) % STEP_TICKS == 0 && i < steps.size()) {
			Step s = steps.get(i);
			BloodDecals.floor(c.run, s.left() ? BloodDecals.FOOT_L : BloodDecals.FOOT_R, s.at(), s.yaw() + (c.rnd.nextFloat() - 0.5F) * 8F,
					0.17F, 0.36F);
			Apparitions.sound(c, ModSounds.SANGRE_PISADA, s.at(), 0.55F, Apparitions.pitch(c, 0.85F, 1.05F));
		}
		int done = 4 + steps.size() * STEP_TICKS;
		if (c.t > 4 && anyOpen(c.run, plan.wardrobe())) {
			return true;  // he opened it: nobody inside
		}
		if (c.t == done + 30) {
			// whoever walked in is inside now
			Apparitions.sound(c, ModSounds.SANGRE_RESPIRA, plan.inside().add(0, 1.4, 0), 0.6F, 0.9F);
		}
		return c.t > done + 60;
	}

	@Override
	public int maxTicks() {
		return 20 * 40;
	}
}
