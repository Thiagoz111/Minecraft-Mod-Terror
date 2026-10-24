package com.deadline.horror.casa;

import com.deadline.casa.CasaProps;
import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.Haunt;
import com.deadline.horror.HouseQuery;
import com.deadline.net.Fx;
import com.deadline.site.Fixtures;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.protocol.game.ClientboundStopSoundPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Shared stagecraft of the Casa poltergeist (catalogue 1-32 of docs/design/casa_terror.md 5) and of the
 * interactables (6.3): who may be scared, sounds at the ear, kit blocks by key, the north-model frame of a kit block
 * (to build displays that match a placed block exactly), the light group of a room, plain doors, floors.
 * Visual rules are those of {@link Apparitions} (never a hidden hunter; loud things are heard by the hunt).
 */
public final class Polter {
	/** Run event prefix the interactables post for running events ("polter:knock", "polter:phone"...). */
	public static final String SIGNAL = "polter:";
	private static final Vector3f ONE = new Vector3f(1F, 1F, 1F);

	private Polter() {
	}

	// ------------------------------------------------------------------ who, when
	/** A hunter inside the house who is not hidden (every poltergeist event asks this first). */
	public static boolean canHaunt(Ctx c) {
		return Apparitions.canScare(c);
	}

	/** The act of the run's horror director (0 when it has none yet). */
	public static int act(Run r) {
		Haunt h = Haunt.peek(r);
		return h == null ? 0 : h.act();
	}

	public static boolean running(Run r, String id) {
		Haunt h = Haunt.peek(r);
		return h != null && h.isRunning(id);
	}

	/** Posted by the interactables for a running event (visible to it on the next tick). */
	public static void signal(Run r, String what) {
		r.post(SIGNAL + what);
	}

	public static boolean got(Ctx c, String what) {
		return c.run.event(SIGNAL + what);
	}

	// ------------------------------------------------------------------ sound
	/** The world position at the player's ear: side +1 right, -1 left, 0 just in front of the face. */
	public static Vec3 ear(ServerPlayer p, double side, double out) {
		double yaw = Math.toRadians(p.getYRot());
		Vec3 fwd = new Vec3(-Math.sin(yaw), 0, Math.cos(yaw));
		Vec3 right = new Vec3(-fwd.z, 0, fwd.x);
		return p.getEyePosition().add(right.scale(side * out)).add(fwd.scale(side == 0 ? out : 0.05));
	}

	/** A sound only this player hears, at a world position (breath at the ear, a denture click). */
	public static void heard(ServerPlayer p, SoundEvent s, Vec3 at, float volume) {
		if (s != null) {
			Fx.soundAt(p, s, at, volume);
		}
	}

	/** A positional world sound (everyone near hears it). */
	public static void sound(Run r, SoundEvent s, Vec3 at, float volume, float pitch) {
		r.sound(s, at, volume, pitch);
	}

	/** A loud thing happened here: in the hunt (Act 5) the Nona hears it (15 a creak, 40 a plate, 70 a slam). */
	public static void noise(Run r, Vec3 at, float loudness) {
		com.deadline.horror.casa.hunt.Hunt.noise(r, at, loudness);
	}

	/** Stops a playing sound (a music box cut short, the static of a TV turned off) for every hunter. */
	public static void stopSound(Run r, SoundEvent s) {
		if (s == null) {
			return;
		}
		for (ServerPlayer p : r.hunters()) {
			if (p.connection != null) {
				p.connection.send(new ClientboundStopSoundPacket(s.location(), SoundSource.HOSTILE));
			}
		}
	}

	public static float pitch(Ctx c, float lo, float hi) {
		return lo + c.rnd.nextFloat() * (hi - lo);
	}

	// ------------------------------------------------------------------ kit blocks
	/** Registry path of a DEAD LINE block ("casa_silla_comedor"), "" for anything else. */
	public static String key(BlockState s) {
		return CasaProps.path(s);
	}

	public static boolean keyIn(BlockState s, String... keys) {
		String k = key(s);
		for (String w : keys) {
			if (k.equals(w)) {
				return true;
			}
		}
		return false;
	}

	public static boolean keyStarts(BlockState s, String... prefixes) {
		String k = key(s);
		for (String w : prefixes) {
			if (k.startsWith(w)) {
				return true;
			}
		}
		return false;
	}

	/** Kit blocks whose key passes the test in a cube of `radius` around a point (nearest first). */
	public static List<BlockPos> kitNear(Run r, Vec3 at, int radius, int dy, Predicate<String> test) {
		List<BlockPos> out = new ArrayList<>();
		BlockPos c = BlockPos.containing(at);
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-radius, -dy, -radius), c.offset(radius, dy, radius))) {
			BlockState s = r.level.getBlockState(p);
			if (!s.isAir() && test.test(key(s))) {
				out.add(p.immutable());
			}
		}
		out.sort((a, b) -> Double.compare(Vec3.atCenterOf(a).distanceToSqr(at), Vec3.atCenterOf(b).distanceToSqr(at)));
		return out;
	}

	/** Kit blocks of a room area whose key passes the test. */
	public static List<BlockPos> kitIn(Run r, String area, Predicate<String> test) {
		return HouseQuery.blocks(r, area, s -> !s.isAir() && test.test(key(s)));
	}

	public static Direction facing(BlockState s) {
		return CasaProps.facing(s);
	}

	/** The state turned to face north (displays are built from the north model and turned by {@link #yaw}). */
	public static BlockState north(BlockState s) {
		return s.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? s.setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH) : s;
	}

	// ------------------------------------------------------------------ the north-model frame of a kit block
	/** Rotation of a north-facing kit model to facing f (the blockstate's y rotation: east 90, south 180, west 270). */
	public static Quaternionf yaw(Direction f) {
		return new Quaternionf().rotationY(yawRad(f));
	}

	public static float yawRad(Direction f) {
		return switch (f) {
			case EAST -> (float) (-Math.PI / 2);
			case SOUTH -> (float) Math.PI;
			case WEST -> (float) (Math.PI / 2);
			default -> 0F;
		};
	}

	/** World position of a point of a north-facing model (pixels 0..16) placed at `base` with facing f. */
	public static Vec3 local(BlockPos base, Direction f, double px, double py, double pz) {
		Vector3f v = new Vector3f((float) (px / 16.0 - 0.5), 0F, (float) (pz / 16.0 - 0.5));
		yaw(f).transform(v);
		return new Vec3(base.getX() + 0.5 + v.x, base.getY() + py / 16.0, base.getZ() + 0.5 + v.z);
	}

	/** The world direction of a horizontal vector of the north model (x along the model's x, z along its z). */
	public static Vec3 localDir(Direction f, double x, double y, double z) {
		Vector3f v = new Vector3f((float) x, (float) y, (float) z);
		yaw(f).transform(v);
		return new Vec3(v.x, v.y, v.z);
	}

	/**
	 * Poses a display of a north model as if it were the kit block at `base` with facing f, then turned by `local`
	 * (model space) and scaled about `pivot` (model coordinates in block units, 0..1). With identity and scale 1 it
	 * renders exactly like the placed block. The entity sits on the pivot.
	 */
	public static void poseLocal(Display d, BlockPos base, Direction f, Quaternionf local, Vector3f scale, Vector3f pivot, int lerp) {
		if (d == null) {
			return;
		}
		Vec3 at = local(base, f, pivot.x * 16.0, pivot.y * 16.0, pivot.z * 16.0);
		CasaProps.move(d, at);
		CasaProps.pose(d, yaw(f).mul(local), scale, pivot, lerp);
	}

	public static void poseLocal(Display d, BlockPos base, Direction f, Quaternionf local, Vector3f pivot, int lerp) {
		poseLocal(d, base, f, local, ONE, pivot, lerp);
	}

	/**
	 * A cuboid display of a full-cube block state spanning [x0..x1]x[y0..y1]x[z0..z1] pixels of the north model of the
	 * block at `base` with facing f (a drawer pulled out, the inside of a fridge). Registered as a run actor.
	 */
	public static Display.BlockDisplay box(Run r, String actor, BlockPos base, Direction f, BlockState st, double x0, double y0, double z0,
			double x1, double y1, double z1) {
		Vec3 at = local(base, f, x0, y0, z0);
		Display.BlockDisplay d = CasaProps.block(r, actor, at, st);
		if (d == null) {
			return null;
		}
		Vector3f s = new Vector3f((float) ((x1 - x0) / 16.0), (float) ((y1 - y0) / 16.0), (float) ((z1 - z0) / 16.0));
		CasaProps.pose(d, yaw(f), s, CasaProps.ZERO, 0);
		return d;
	}

	// ------------------------------------------------------------------ rooms, floors, lights
	/** Every room area that contains the point (smallest first). */
	public static List<String> roomsAt(Run r, Vec3 at) {
		List<String> out = new ArrayList<>();
		List<Double> vol = new ArrayList<>();
		for (Map.Entry<String, SiteDef.Area> a : r.def.areas.entrySet()) {
			String k = a.getKey();
			if (k.equals("sitio") || k.equals("casa") || k.equals("exterior")) {
				continue;
			}
			AABB box = a.getValue().at(r.origin);
			if (box.contains(at)) {
				double v = box.getXsize() * box.getYsize() * box.getZsize();
				int i = 0;
				while (i < vol.size() && vol.get(i) <= v) {
					i++;
				}
				out.add(i, k);
				vol.add(i, v);
			}
		}
		return out;
	}

	/** The light groups ("luces_&lt;area&gt;") of every room at a point, smallest room first. */
	public static List<String> lightGroups(Run r, Vec3 at) {
		List<String> out = new ArrayList<>();
		for (String room : roomsAt(r, at)) {
			String g = "luces_" + room;
			if (r.def.groups.containsKey(g) && !r.def.group(g).isEmpty() && !out.contains(g)) {
				out.add(g);
			}
		}
		return out;
	}

	/** The light group of a room, null when it has none. */
	public static String roomLights(Run r, String room) {
		if (room == null) {
			return null;
		}
		String g = "luces_" + room;
		return r.def.groups.containsKey(g) && !r.def.group(g).isEmpty() ? g : null;
	}

	public static BlockPos fixture(Run r, String group, int i) {
		return r.origin.offset(r.def.group(group).get(i));
	}

	public static boolean lit(Run r, String group, int i) {
		List<BlockPos> g = r.def.group(group);
		return i >= 0 && i < g.size() && Fixtures.burning(r.level.getBlockState(r.origin.offset(g.get(i))));
	}

	public static boolean anyLit(Run r, String group) {
		for (int i = 0; i < r.def.group(group).size(); i++) {
			if (lit(r, group, i)) {
				return true;
			}
		}
		return false;
	}

	/** Every "luces_*" group of the site. */
	public static List<String> allLights(Run r) {
		List<String> out = new ArrayList<>();
		for (String g : r.def.groups.keySet()) {
			if (g.startsWith("luces_")) {
				out.add(g);
			}
		}
		return out;
	}

	/** "sotano", "pb", "1p" or "altillo" by height over the site origin (the casona: PB y 0-4, 1P y 5-9, attic 10+). */
	public static String floor(Run r, Vec3 at) {
		double y = at.y - r.origin.getY();
		return y < -0.5 ? "sotano" : y < 4.5 ? "pb" : y < 9.5 ? "1p" : "altillo";
	}

	// ------------------------------------------------------------------ doors
	/** A room door (not a wardrobe, a gate, the attic trunk, the shed or the front door). */
	public static boolean plainDoor(String name) {
		return !(name.startsWith("ropero") || name.startsWith("porton") || name.startsWith("baul") || name.equals("galpon")
				|| name.equals("entrada") || name.equals("portoncito"));
	}

	/** The door of the room the player is in (named like the room, else the nearest plain door on its walls). */
	public static String roomDoor(Run r, String room, Vec3 near) {
		if (room == null) {
			return null;
		}
		if (r.def.doors.containsKey(room)) {
			return room;
		}
		if (!r.def.areas.containsKey(room)) {
			return null;
		}
		AABB box = r.area(room).inflate(1.01, 0, 1.01);
		AABB in = r.area(room).deflate(0.99, 0, 0.99);
		for (String d : HouseQuery.doorsNear(r, near, 14.0)) {
			Vec3 dp = HouseQuery.doorPos(r, d);
			if (plainDoor(d) && box.contains(dp) && !in.contains(dp)) {
				return d;
			}
		}
		return null;
	}

	/** True when the door marker's lower half is a door block (the site has it and it was not broken). */
	public static boolean isDoor(Run r, String name) {
		BlockPos rel = r.def.doors.get(name);
		return rel != null && r.level.getBlockState(r.origin.offset(rel)).getBlock() instanceof DoorBlock;
	}

	// ------------------------------------------------------------------ geometry
	/** Height of the floor surface at or below a point (looking down `max` blocks), NaN if there is none. */
	public static double floorAt(Run r, Vec3 at, int max) {
		BlockPos p = BlockPos.containing(at);
		for (int dy = 0; dy <= max; dy++) {
			BlockPos q = p.below(dy);
			VoxelShape s = r.level.getBlockState(q).getCollisionShape(r.level, q);
			if (!s.isEmpty()) {
				double top = q.getY() + s.max(Direction.Axis.Y);
				if (top <= at.y + 1e-3) {
					return top;
				}
			}
		}
		return Double.NaN;
	}

	/** A wall-like block: solid collision filling most of the cell (knockable). */
	public static boolean wall(Run r, BlockPos p) {
		BlockState s = r.level.getBlockState(p);
		if (s.isAir() || s.getBlock() instanceof DoorBlock) {
			return false;
		}
		VoxelShape v = s.getCollisionShape(r.level, p);
		if (v.isEmpty()) {
			return false;
		}
		AABB b = v.bounds();
		return b.getXsize() * b.getYsize() * b.getZsize() > 0.6;
	}

	/** Never more than leaves him with half a heart: things that fly at him hurt, the house does not kill. */
	public static void hurt(Run r, ServerPlayer p, float amount) {
		float a = Math.min(amount, Math.max(0F, p.getHealth() - 1F));
		if (a > 0F) {
			p.hurtServer(r.level, r.level.damageSources().magic(), a);
		}
	}
}
