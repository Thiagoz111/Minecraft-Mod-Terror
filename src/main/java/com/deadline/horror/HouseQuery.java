package com.deadline.horror;

import com.deadline.director.Run;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** Questions events ask about the house: where is the player, what can he see, where is a dark spot behind him. */
public final class HouseQuery {
	/** Areas that are not rooms (they contain other rooms). */
	private static final List<String> NOT_ROOMS = List.of("sitio", "casa", "exterior");

	private HouseQuery() {
	}

	/** The smallest room area that contains the entity (null outside every room). */
	public static String room(Run r, Entity e) {
		return roomAt(r, e.position());
	}

	public static String roomAt(Run r, Vec3 pos) {
		String best = null;
		double vol = Double.MAX_VALUE;
		for (Map.Entry<String, SiteDef.Area> a : r.def.areas.entrySet()) {
			if (NOT_ROOMS.contains(a.getKey())) {
				continue;
			}
			AABB box = a.getValue().at(r.origin);
			if (box.contains(pos)) {
				double v = box.getXsize() * box.getYsize() * box.getZsize();
				if (v < vol) {
					vol = v;
					best = a.getKey();
				}
			}
		}
		return best;
	}

	public static boolean inHouse(Run r, Entity e) {
		return r.def.areas.containsKey("casa") && r.inside(e, "casa");
	}

	/** Point markers whose name starts with prefix (e.g. "escritura_", "hide_"), in authored order. */
	public static List<String> points(Run r, String prefix) {
		List<String> out = new ArrayList<>();
		for (String k : r.def.points.keySet()) {
			if (k.startsWith(prefix)) {
				out.add(k);
			}
		}
		return out;
	}

	/** True when the player has the spot on screen (60 degrees off-centre at most) with nothing in between. */
	public static boolean sees(Run r, ServerPlayer p, Vec3 at) {
		return r.looking(p, at, 60F, 64.0);
	}

	/** The nearest point with this prefix within [minDist, maxDist] that passes the filter (null if none). */
	public static String nearest(Run r, String prefix, Vec3 from, double minDist, double maxDist, Predicate<String> filter) {
		String best = null;
		double bd = Double.MAX_VALUE;
		for (String k : points(r, prefix)) {
			double d = r.at(k).distanceTo(from);
			if (d >= minDist && d <= maxDist && d < bd && (filter == null || filter.test(k))) {
				bd = d;
				best = k;
			}
		}
		return best;
	}

	/** A random point with this prefix the player can NOT see right now, within the distance range. */
	public static String outOfView(Run r, ServerPlayer p, String prefix, double minDist, double maxDist) {
		return random(r, prefix, p.position(), minDist, maxDist, k -> !sees(r, p, r.at(k).add(0, 1.0, 0)));
	}

	/** A random point with this prefix the player sees right now, within the distance range. */
	public static String inView(Run r, ServerPlayer p, String prefix, double minDist, double maxDist) {
		return random(r, prefix, p.position(), minDist, maxDist, k -> sees(r, p, r.at(k).add(0, 1.0, 0)));
	}

	public static String random(Run r, String prefix, Vec3 from, double minDist, double maxDist, Predicate<String> filter) {
		List<String> ok = new ArrayList<>();
		for (String k : points(r, prefix)) {
			double d = r.at(k).distanceTo(from);
			if (d >= minDist && d <= maxDist && (filter == null || filter.test(k))) {
				ok.add(k);
			}
		}
		return ok.isEmpty() ? null : ok.get(r.level.getRandom().nextInt(ok.size()));
	}

	/** Door markers within maxDist of a position (nearest first). */
	public static List<String> doorsNear(Run r, Vec3 from, double maxDist) {
		List<String> out = new ArrayList<>();
		for (Map.Entry<String, BlockPos> d : r.def.doors.entrySet()) {
			if (Vec3.atCenterOf(r.origin.offset(d.getValue())).distanceTo(from) <= maxDist) {
				out.add(d.getKey());
			}
		}
		out.sort((a, b) -> Double.compare(doorPos(r, a).distanceTo(from), doorPos(r, b).distanceTo(from)));
		return out;
	}

	public static Vec3 doorPos(Run r, String door) {
		BlockPos rel = r.def.doors.get(door);
		return rel == null ? null : Vec3.atCenterOf(r.origin.offset(rel));
	}

	/** A standing spot (2 blocks of air over a solid floor) about dist blocks straight behind the player, or null. */
	public static Vec3 behind(Run r, ServerPlayer p, double dist) {
		double yaw = Math.toRadians(p.getYRot());
		Vec3 back = new Vec3(Math.sin(yaw), 0, -Math.cos(yaw));
		for (double d = dist; d >= 0.9; d -= 0.4) {
			Vec3 at = p.position().add(back.scale(d));
			BlockPos feet = BlockPos.containing(at);
			for (int dy = 0; dy >= -1; dy--) {
				BlockPos f = feet.above(dy);
				if (standable(r, f)) {
					return new Vec3(at.x, f.getY(), at.z);
				}
			}
		}
		return null;
	}

	public static boolean standable(Run r, BlockPos feet) {
		var lvl = r.level;
		return lvl.getBlockState(feet).getCollisionShape(lvl, feet).isEmpty()
				&& lvl.getBlockState(feet.above()).getCollisionShape(lvl, feet.above()).isEmpty()
				&& !lvl.getBlockState(feet.below()).getCollisionShape(lvl, feet.below()).isEmpty();
	}

	/** Dark enough that only a flashlight shows things (block light and sky light both low). */
	public static boolean dark(Run r, BlockPos pos) {
		return r.level.getBrightness(LightLayer.BLOCK, pos) <= 4 && r.level.getBrightness(LightLayer.SKY, pos) <= 6;
	}

	/** Absolute positions of the blocks inside an area whose state passes the test (e.g. chairs, drawers). */
	public static List<BlockPos> blocks(Run r, String area, Predicate<BlockState> test) {
		List<BlockPos> out = new ArrayList<>();
		if (!r.def.areas.containsKey(area)) {
			return out;
		}
		AABB box = r.area(area);
		BlockPos a = BlockPos.containing(box.minX, box.minY, box.minZ);
		BlockPos b = BlockPos.containing(box.maxX - 1e-3, box.maxY - 1e-3, box.maxZ - 1e-3);
		for (BlockPos pos : BlockPos.betweenClosed(a, b)) {
			if (test.test(r.level.getBlockState(pos))) {
				out.add(pos.immutable());
			}
		}
		return out;
	}

	/** Registry path of a block state ("casa_silla_comedor"), handy to match kit blocks by key. */
	public static String key(BlockState s) {
		return net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(s.getBlock()).getPath();
	}
}
