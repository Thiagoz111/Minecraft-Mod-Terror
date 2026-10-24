package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Exec;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.director.Step;
import com.deadline.net.Fx;
import com.deadline.registry.ModBlocks;
import com.deadline.registry.ModSounds;
import com.mojang.math.Transformation;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Casa Morales stagecraft made of vanilla display entities: furniture that floats, plates, knives,
 * chairs stacked while nobody looks, door cascades and bulbs that pop. Positions are absolute (world) unless a parameter
 * is a marker name or a site group.
 * <p>
 * Every block a set piece takes away is remembered and put back when the displays linked to it are gone (a chapter
 * replayed from its checkpoint, the case ending) or when the server stops, so the house is never left without its
 * furniture. A background guard does it every 10 ticks, and every set piece {@link #sweep}s before it reads the blocks
 * it takes. The case script must still call {@link #restore}(run) from {@code onCheckpoint}: a replay discards the
 * displays and the replayed chapter's setup may read those blocks before the guard runs. All display setters are
 * called from here (one place to touch if a mapping changes).
 */
public final class CasaProps {
	/** Pivots in model space: the block's centre, the middle of its floor, the middle of its ceiling, a loose prop. */
	public static final Vector3f CENTER = new Vector3f(0.5F, 0.5F, 0.5F);
	public static final Vector3f FLOOR = new Vector3f(0.5F, 0F, 0.5F);
	public static final Vector3f TOP = new Vector3f(0.5F, 1F, 0.5F);
	public static final Vector3f ZERO = new Vector3f();
	private static final Vector3f PLATE = new Vector3f(0.5F, 0.03F, 0.5F);
	private static final float CHAIR_SCALE = 0.9F;
	private static final List<Change> CHANGES = new ArrayList<>();
	private static int seq;

	private CasaProps() {
	}

	// ------------------------------------------------------------------ displays
	/** A fresh actor name for a set-piece display ("casa:&lt;kind&gt;:&lt;n&gt;"). */
	public static String uid(String kind) {
		return "casa:" + kind + ":" + (++seq);
	}

	/**
	 * A block display whose model corner sits on `at` until posed. Not a director actor: the caller removes it (a
	 * director-tagged entity that no run claims is discarded as an orphan, so only the run variant is tagged).
	 */
	public static Display.BlockDisplay block(ServerLevel level, Vec3 at, BlockState state) {
		return spawnBlock(level, at, state, false);
	}

	/** A block display registered as a run actor (removed on a chapter replay or when the case ends). */
	public static Display.BlockDisplay block(Run r, String actor, Vec3 at, BlockState state) {
		Display.BlockDisplay d = spawnBlock(r.level, at, state, true);
		if (d != null) {
			r.actor(actor, d);
		}
		return d;
	}

	private static Display.BlockDisplay spawnBlock(ServerLevel level, Vec3 at, BlockState state, boolean actor) {
		Display.BlockDisplay d = EntityType.BLOCK_DISPLAY.create(level, EntitySpawnReason.EVENT);
		if (d == null) {
			return null;
		}
		d.snapTo(at.x, at.y, at.z, 0F, 0F);
		d.setBlockState(state);
		d.setPosRotInterpolationDuration(2);
		if (actor) {
			d.addTag(Props.ACTOR_TAG);
		}
		level.addFreshEntity(d);
		return d;
	}

	/** An item display (item centred on `at`) registered as a run actor. */
	public static Display.ItemDisplay item(Run r, String actor, Vec3 at, ItemStack stack) {
		Display.ItemDisplay d = EntityType.ITEM_DISPLAY.create(r.level, EntitySpawnReason.EVENT);
		if (d == null) {
			return null;
		}
		d.snapTo(at.x, at.y, at.z, 0F, 0F);
		d.setItemStack(stack);
		d.setPosRotInterpolationDuration(2);
		d.addTag(Props.ACTOR_TAG);
		r.level.addFreshEntity(d);
		r.actor(actor, d);
		return d;
	}

	/**
	 * Rotates and scales a display about a pivot of its model (block units: 0..1 for a block display, 0,0,0 is the
	 * centre of an item display); the pivot lands on the entity position. lerp &gt; 0 interpolates over that many ticks.
	 */
	public static void pose(Display d, Quaternionf rot, Vector3f scale, Vector3f pivot, int lerp) {
		if (d == null) {
			return;
		}
		Vector3f t = new Vector3f(pivot).mul(scale);
		new Quaternionf(rot).transform(t);
		t.negate();
		d.setTransformationInterpolationDuration(Math.max(0, lerp));
		d.setTransformationInterpolationDelay(0);
		d.setTransformation(new Transformation(t, new Quaternionf(rot), new Vector3f(scale), new Quaternionf()));
	}

	public static void pose(Display d, Quaternionf rot, float scale, Vector3f pivot, int lerp) {
		pose(d, rot, new Vector3f(scale, scale, scale), pivot, lerp);
	}

	public static void move(Entity e, Vec3 to) {
		if (e != null) {
			e.setPos(to.x, to.y, to.z);
		}
	}

	/** Rotation that points the model's +X axis along dir (a knife's blade), rolled about that axis. */
	public static Quaternionf alongX(Vec3 dir, float roll) {
		double h = Math.sqrt(dir.x * dir.x + dir.z * dir.z);
		return new Quaternionf().rotationY((float) Math.atan2(-dir.z, dir.x)).rotateZ((float) Math.atan2(dir.y, h)).rotateX(roll);
	}

	/** Rotation that points the model's +Z axis along dir (a yarn thread; the face of an item sprite). */
	public static Quaternionf alongZ(Vec3 dir) {
		double h = Math.sqrt(dir.x * dir.x + dir.z * dir.z);
		return new Quaternionf().rotationY((float) Math.atan2(dir.x, dir.z)).rotateX((float) Math.atan2(-dir.y, h));
	}

	// ------------------------------------------------------------------ kit blocks
	/** A building-kit block by key ("casa_plato"), null when it does not exist. */
	public static BlockState kit(String key) {
		Block b = BuiltInRegistries.BLOCK.getOptional(DeadLine.id(key)).orElse(null);
		return b == null ? null : b.defaultBlockState();
	}

	/** A kit block turned like another block (same horizontal facing). */
	public static BlockState kit(String key, BlockState like) {
		BlockState s = kit(key);
		if (s != null && like.hasProperty(BlockStateProperties.HORIZONTAL_FACING) && s.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			s = s.setValue(BlockStateProperties.HORIZONTAL_FACING, like.getValue(BlockStateProperties.HORIZONTAL_FACING));
		}
		return s;
	}

	public static BlockState kitOr(String key, BlockState fallback) {
		BlockState s = kit(key);
		return s == null ? fallback : s;
	}

	/** Registry path of a DEAD LINE block ("casa_cuchillos"), "" for anything else. */
	public static String path(BlockState s) {
		var id = BuiltInRegistries.BLOCK.getKey(s.getBlock());
		return DeadLine.MOD_ID.equals(id.getNamespace()) ? id.getPath() : "";
	}

	public static Direction facing(BlockState s) {
		return s.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? s.getValue(BlockStateProperties.HORIZONTAL_FACING) : Direction.NORTH;
	}

	/** A point of a north-facing kit model (pixels, 0..16 per block) turned to the block's facing; block units. */
	public static Vec3 local(Direction f, double px, double py, double pz) {
		Vec3 o = turn(f, px / 16.0 - 0.5, pz / 16.0 - 0.5);
		return new Vec3(o.x + 0.5, py / 16.0, o.z + 0.5);
	}

	/** A horizontal offset (u along the model's x, w along its z) turned like a kit block facing f. */
	public static Vec3 turn(Direction f, double u, double w) {
		double x = u;
		double z = w;
		if (f == Direction.EAST) {
			x = -w;
			z = u;
		} else if (f == Direction.SOUTH) {
			x = -u;
			z = -w;
		} else if (f == Direction.WEST) {
			x = w;
			z = -u;
		}
		return new Vec3(x, 0, z);
	}

	// ------------------------------------------------------------------ world queries
	/** True when a hunter looks at the point (within halfAngle degrees, closer than maxDist, line of sight). */
	public static boolean seen(Run r, Vec3 at, float halfAngle, double maxDist) {
		for (ServerPlayer p : r.hunters()) {
			if (!p.isSpectator() && r.looking(p, at, halfAngle, maxDist)) {
				return true;
			}
		}
		return false;
	}

	public static ServerPlayer nearest(Run r, Vec3 at) {
		ServerPlayer best = null;
		double bd = Double.MAX_VALUE;
		for (ServerPlayer p : r.hunters()) {
			double d = p.position().distanceToSqr(at);
			if (!p.isSpectator() && d < bd) {
				bd = d;
				best = p;
			}
		}
		return best;
	}

	/** A consecrated salt line in the column under a point (the floor-level salt stops what flies over it too). */
	public static boolean saltAt(Level level, Vec3 at) {
		BlockPos p = BlockPos.containing(at);
		for (int dy = 0; dy <= 2; dy++) {
			if (level.getBlockState(p.below(dy)).is(ModBlocks.SALT_LINE)) {
				return true;
			}
		}
		return false;
	}

	/** Nothing to bump into at that point. */
	public static boolean passable(Level level, Vec3 at) {
		BlockPos p = BlockPos.containing(at);
		return level.getBlockState(p).getCollisionShape(level, p).isEmpty();
	}

	/** Height of the first surface at or under a point (looking down at most `max` blocks); at.y if none. */
	public static double floorUnder(Level level, Vec3 at, int max) {
		BlockPos p = BlockPos.containing(at);
		for (int dy = 0; dy <= max; dy++) {
			BlockPos q = p.below(dy);
			VoxelShape s = level.getBlockState(q).getCollisionShape(level, q);
			if (!s.isEmpty()) {
				return Math.min(at.y, q.getY() + s.max(Direction.Axis.Y));
			}
		}
		return at.y;
	}

	/** Shortest distance between segments p1-q1 and p2-q2 (a point is a segment of length 0). */
	public static double segDist(Vec3 p1, Vec3 q1, Vec3 p2, Vec3 q2) {
		Vec3 d1 = q1.subtract(p1);
		Vec3 d2 = q2.subtract(p2);
		Vec3 r = p1.subtract(p2);
		double a = d1.dot(d1);
		double e = d2.dot(d2);
		double f = d2.dot(r);
		double s;
		double t;
		if (a <= 1e-9 && e <= 1e-9) {
			return p1.distanceTo(p2);
		}
		if (a <= 1e-9) {
			s = 0;
			t = clamp(f / e);
		} else {
			double c = d1.dot(r);
			if (e <= 1e-9) {
				t = 0;
				s = clamp(-c / a);
			} else {
				double b = d1.dot(d2);
				double den = a * e - b * b;
				s = den > 1e-9 ? clamp((b * f - c * e) / den) : 0;
				t = (b * s + f) / e;
				if (t < 0) {
					t = 0;
					s = clamp(-c / a);
				} else if (t > 1) {
					t = 1;
					s = clamp((b - c) / a);
				}
			}
		}
		return p1.add(d1.scale(s)).distanceTo(p2.add(d2.scale(t)));
	}

	private static double clamp(double v) {
		return v < 0 ? 0 : v > 1 ? 1 : v;
	}

	public static double ease(double u) {
		u = clamp(u);
		return u * u * (3 - 2 * u);
	}

	static double rnd(Level level, double a) {
		return (level.random.nextDouble() * 2 - 1) * a;
	}

	static List<BlockPos> abs(Run r, String group) {
		List<BlockPos> out = new ArrayList<>();
		for (BlockPos rel : r.def.group(group)) {
			out.add(r.origin.offset(rel));
		}
		return out;
	}

	static Vec3 centroid(List<BlockPos> list) {
		double x = 0;
		double y = 0;
		double z = 0;
		for (BlockPos p : list) {
			x += p.getX() + 0.5;
			y += p.getY() + 0.5;
			z += p.getZ() + 0.5;
		}
		int n = Math.max(1, list.size());
		return new Vec3(x / n, y / n, z / n);
	}

	static void shakeNear(Run r, Vec3 at, double radius, float intensity, int ticks) {
		for (ServerPlayer p : r.hunters()) {
			if (p.position().distanceToSqr(at) < radius * radius) {
				Fx.shake(p, intensity, ticks);
			}
		}
	}

	// ------------------------------------------------------------------ remembered blocks
	private static final class Change {
		final Run run;
		final BlockPos pos;
		final BlockState original;
		final List<String> links;

		Change(Run run, BlockPos pos, BlockState original, List<String> links) {
			this.run = run;
			this.pos = pos;
			this.original = original;
			this.links = links;
		}

		boolean linksGone() {
			if (links.isEmpty()) {
				return false;
			}
			for (String a : links) {
				if (run.actor(a) != null) {
					return false;
				}
			}
			return true;
		}

		void put() {
			if (run.level.getBlockState(pos) != original) {
				run.setBlock(pos, original);
			}
		}
	}

	/**
	 * Remembers a block a set piece took away; it comes back when every linked actor is gone (chapter replay, case end),
	 * on {@link #settleAt}, {@link #restore} or when the server stops. An older change at the same spot comes back first.
	 */
	public static void remember(Run r, BlockPos pos, BlockState original, List<String> links) {
		settleAt(r, pos);
		CHANGES.add(new Change(r, pos.immutable(), original, new ArrayList<>(links)));
	}

	/**
	 * Swaps a block and remembers the original (see {@link #remember}). A change still pending at pos comes back first, so
	 * the original remembered is the real block, never another set piece's stand-in (that one's displays stay up).
	 */
	public static void swap(Run r, BlockPos pos, BlockState to, List<String> links) {
		if (to == null) {
			return;
		}
		settleAt(r, pos);
		remember(r, pos, r.level.getBlockState(pos), links);
		r.setBlock(pos, to);
	}

	/** True when a set piece of the run still holds the block at pos (call {@link #sweep} first to drop dead ones). */
	public static boolean held(Run r, BlockPos pos) {
		for (Change c : CHANGES) {
			if (c.run == r && c.pos.equals(pos)) {
				return true;
			}
		}
		return false;
	}

	/** Puts back the remembered block at pos (and forgets it); false if nothing was remembered there. */
	public static boolean settleAt(Run r, BlockPos pos) {
		for (Iterator<Change> it = CHANGES.iterator(); it.hasNext(); ) {
			Change c = it.next();
			if (c.run == r && c.pos.equals(pos)) {
				it.remove();
				c.put();
				return true;
			}
		}
		return false;
	}

	/** Forgets a remembered block without putting it back (the change is meant to stay). */
	public static void forget(Run r, BlockPos pos) {
		CHANGES.removeIf(c -> c.run == r && c.pos.equals(pos));
	}

	/**
	 * Undoes every set piece of a run: the remembered blocks come back and their displays go. The case script calls it
	 * from {@code onCheckpoint} (a chapter replay), so the replayed setup finds the house whole.
	 */
	public static void restore(Run r) {
		for (Iterator<Change> it = CHANGES.iterator(); it.hasNext(); ) {
			Change c = it.next();
			if (c.run == r) {
				it.remove();
				for (String a : c.links) {
					r.despawn(a);
				}
				c.put();
			}
		}
	}

	/**
	 * Puts back now (and forgets) every remembered block of the run whose displays are gone, and every one left by a run
	 * that is over. A chapter replay discards the displays in the same tick the replayed setup starts, before the guard
	 * runs, so every set piece calls this before it reads the blocks it takes.
	 */
	public static void sweep(Run r) {
		if (CHANGES.isEmpty()) {
			return;
		}
		for (Change c : new ArrayList<>(CHANGES)) {
			boolean over = Director.get(c.run.type, c.run.site) != c.run;
			if (over || (c.run == r && c.linksGone())) {
				CHANGES.remove(c);
				c.put();
			}
		}
	}

	static void tickGuard(MinecraftServer server) {
		if (CHANGES.isEmpty() || server.getTickCount() % 10 != 0) {
			return;
		}
		for (Change c : new ArrayList<>(CHANGES)) {
			if (Director.get(c.run.type, c.run.site) != c.run || c.linksGone()) {
				CHANGES.remove(c);
				c.put();
			}
		}
	}

	static void restoreAll() {
		for (Change c : new ArrayList<>(CHANGES)) {
			c.put();
		}
		CHANGES.clear();
	}

	// ------------------------------------------------------------------ lifted furniture
	/**
	 * Lifts a block into an identical display centred on it (pivot {@link #CENTER}); the real block becomes air. Null for
	 * air, doors, block entities and blocks another set piece still holds (lifting its stand-in would leave it there).
	 */
	public static Display.BlockDisplay lift(Run r, BlockPos pos, String actor) {
		sweep(r);
		if (held(r, pos)) {
			return null;
		}
		BlockState s = r.level.getBlockState(pos);
		if (s.isAir() || s.getBlock() instanceof DoorBlock || r.level.getBlockEntity(pos) != null) {
			return null;
		}
		Display.BlockDisplay d = block(r, actor, Vec3.atCenterOf(pos), s);
		if (d == null) {
			return null;
		}
		pose(d, new Quaternionf(), 1F, CENTER, 0);
		remember(r, pos, s, List.of(actor));
		r.setBlock(pos, Blocks.AIR.defaultBlockState());
		return d;
	}

	/** Puts a lifted block back in its place and removes its display. */
	public static void settle(Run r, BlockPos pos, String actor) {
		r.despawn(actor);
		settleAt(r, pos);
	}

	private static final class Floater {
		final BlockPos pos;
		final String actor;
		final int delay;
		final double height;
		final double phase;
		double y;
		boolean done;

		Floater(BlockPos pos, String actor, int delay, double height, double phase) {
			this.pos = pos;
			this.actor = actor;
			this.delay = delay;
			this.height = height;
			this.phase = phase;
		}
	}

	/** 6-10 pieces of furniture rise one after another, float rocking for `ticks`, then crash back into place. */
	public static Exec levitate(Run r, List<BlockPos> blocks, int ticks) {
		sweep(r);
		List<Floater> fl = new ArrayList<>();
		for (BlockPos pos : blocks) {
			String a = uid("flota");
			if (lift(r, pos, a) != null) {
				fl.add(new Floater(pos.immutable(), a, fl.size() * 5, 0.5 + r.level.random.nextDouble() * 0.9,
						r.level.random.nextDouble() * Math.PI * 2));
			}
		}
		if (fl.isEmpty()) {
			return null;
		}
		List<BlockPos> lifted = new ArrayList<>();
		fl.forEach(f -> lifted.add(f.pos));
		r.sound(ModSounds.SILLA_ARRASTRA, centroid(lifted), 1.3F, 0.6F);
		return r.start("casa:levitate", r.star(), List.of(e -> floatTick(r, fl, e.t, ticks)));
	}

	/** Same, for every block of a site group. */
	public static Exec levitate(Run r, String group, int ticks) {
		return levitate(r, abs(r, group), ticks);
	}

	private static boolean floatTick(Run r, List<Floater> fl, int t, int ticks) {
		boolean all = true;
		for (Floater f : fl) {
			if (f.done) {
				continue;
			}
			if (!(r.actor(f.actor) instanceof Display d)) {
				f.done = true;  // removed from outside: the guard puts the block back
				continue;
			}
			all = false;
			Vec3 c = Vec3.atCenterOf(f.pos);
			int land = ticks + f.delay / 2;
			if (t < land) {
				double u = ease((t - f.delay) / 25.0);
				f.y = f.height * u + 0.1 * Math.sin(t * 0.12 + f.phase) * u;
				move(d, c.add(0.04 * Math.sin(t * 0.05 + f.phase) * u, f.y, 0.04 * Math.cos(t * 0.06 + f.phase) * u));
				if (t % 4 == 0 && u > 0) {
					float yaw = (float) (0.25 * Math.sin(t * 0.05 + f.phase) * u);
					float pitch = (float) (0.16 * Math.sin(t * 0.07 + f.phase * 2) * u);
					float roll = (float) (0.12 * Math.sin(t * 0.06 + f.phase) * u);
					pose(d, new Quaternionf().rotationYXZ(yaw, pitch, roll), 1F, CENTER, 4);
				}
			} else {
				int lt = t - land;
				if (lt == 0) {
					pose(d, new Quaternionf(), 1F, CENTER, 4);
				}
				double k = Math.min(1.0, lt / 7.0);
				move(d, c.add(0, f.y * (1 - k * k), 0));
				if (k >= 1) {
					f.done = true;
					settle(r, f.pos, f.actor);
					r.sound(ModSounds.ALACENA_GOLPE, c, 1.0F, 0.6F + r.level.random.nextFloat() * 0.3F);
					shakeNear(r, c, 10, 0.25F, 6);
				}
			}
		}
		if (all) {
			r.post("flotan:fin");
		}
		return all;
	}

	// ------------------------------------------------------------------ chair tower
	private static final class Tower {
		String top;
		float topYaw;
		Vec3 mid;
		boolean seen;
	}

	/**
	 * The dining chairs (a site group) become a tower of displays stacked to the ceiling on `base` the moment nobody looks
	 * at the dining room; the top chair keeps swaying. Posts "sillas:torre" when built and "sillas:vistas" when first seen.
	 */
	public static Exec chairTower(Run r, String group, BlockPos base) {
		List<BlockPos> chairs = abs(r, group);
		if (chairs.isEmpty()) {
			DeadLine.LOGGER.warn("Site {} has no group '{}'", r.def.key, group);
			return null;
		}
		Vec3 mid = centroid(chairs);
		Vec3 b = Vec3.atCenterOf(base);
		Tower tw = new Tower();
		Step build = e -> {
			e.n = seen(r, mid, 55F, 48) || seen(r, b, 55F, 48) ? 0 : e.n + 1;
			if (e.n < 10) {
				return false;
			}
			buildTower(r, chairs, base, tw);
			return true;
		};
		Step sway = e -> {
			if (tw.top == null || !(r.actor(tw.top) instanceof Display d)) {
				return true;
			}
			if (e.t % 14 == 0) {
				float a = (e.t / 14) % 2 == 0 ? 0.13F : -0.13F;
				pose(d, new Quaternionf().rotationY(tw.topYaw).rotateX(a), CHAIR_SCALE, FLOOR, 14);
			}
			if (!tw.seen && seen(r, tw.mid, 30F, 32)) {
				tw.seen = true;
				r.post("sillas:vistas");
			}
			return false;
		};
		return r.start("casa:sillas", r.star(), List.of(build, sway));
	}

	private static void buildTower(Run r, List<BlockPos> chairs, BlockPos base, Tower tw) {
		sweep(r);
		ServerLevel level = r.level;
		VoxelShape shape = level.getBlockState(base).getCollisionShape(level, base);
		double bottom = shape.isEmpty() ? base.getY() : base.getY() + shape.max(Direction.Axis.Y);
		int ceiling = (int) Math.ceil(bottom - 1e-3);
		int limit = ceiling + 6;
		while (ceiling < limit) {
			BlockPos q = new BlockPos(base.getX(), ceiling, base.getZ());
			if (!level.getBlockState(q).getCollisionShape(level, q).isEmpty()) {
				break;
			}
			ceiling++;
		}
		List<BlockPos> real = new ArrayList<>();
		for (BlockPos p : chairs) {
			if (!level.getBlockState(p).isAir() && !held(r, p)) {
				real.add(p);
			}
		}
		int n = real.size();
		if (n == 0) {
			return;
		}
		double spacing = Math.max(0.22, Math.min(0.6, (ceiling - bottom - CHAIR_SCALE) / Math.max(1, n - 1)));
		for (int i = 0; i < n; i++) {
			BlockPos cp = real.get(i);
			BlockState s = level.getBlockState(cp);
			String actor = uid("silla");
			Vec3 at = new Vec3(base.getX() + 0.5 + rnd(level, 0.08), bottom + i * spacing, base.getZ() + 0.5 + rnd(level, 0.08));
			Display.BlockDisplay d = block(r, actor, at, s);
			if (d == null) {
				continue;
			}
			boolean flip = (n - 1 - i) % 2 == 1;
			float yaw = level.random.nextFloat() * (float) (Math.PI * 2);
			Quaternionf q = new Quaternionf().rotationY(yaw);
			if (flip) {
				q.rotateX((float) Math.PI);
			}
			q.rotateZ((float) rnd(level, 0.06));
			pose(d, q, CHAIR_SCALE, flip ? TOP : FLOOR, 0);
			remember(r, cp, s, List.of(actor));
			r.setBlock(cp, Blocks.AIR.defaultBlockState());
			if (i == n - 1) {
				tw.top = actor;
				tw.topYaw = yaw;
			}
		}
		tw.mid = new Vec3(base.getX() + 0.5, bottom + n * spacing * 0.5, base.getZ() + 0.5);
		r.sound(ModSounds.CHAIR_STACK, Vec3.atCenterOf(base), 1.5F, 1.0F);
		r.post("sillas:torre");
	}

	// ------------------------------------------------------------------ plates
	private static final class Plate {
		final String actor;
		final Vec3 from;
		final Vec3 ctrl;
		final Vec3 to;
		final int n;
		final float spin;
		final boolean harmless;
		Vec3 pos;
		int t;

		Plate(String actor, Vec3 from, Vec3 ctrl, Vec3 to, int n, float spin, boolean harmless) {
			this.actor = actor;
			this.from = from;
			this.ctrl = ctrl;
			this.to = to;
			this.n = n;
			this.spin = spin;
			this.harmless = harmless;
			this.pos = from;
		}
	}

	/** Plates fly from `from` toward `to` (spread around it) for `ticks`, at most 10 in the air; they smash and hurt. */
	public static Exec plateStorm(Run r, Vec3 from, Vec3 to, int ticks) {
		BlockState plate = kitOr("casa_plato", Blocks.WHITE_CARPET.defaultBlockState());
		List<Plate> air = new ArrayList<>();
		r.sound(ModSounds.PLATE_STORM, from, 1.6F, 1.0F);
		return r.start("casa:platos", r.star(), List.of(e -> {
			if (e.t < ticks && e.t >= e.n && air.size() < 10) {
				Vec3 a = from.add(rnd(r.level, 0.4), rnd(r.level, 0.2), rnd(r.level, 0.4));
				Vec3 b = to.add(rnd(r.level, 1.5), rnd(r.level, 0.4), rnd(r.level, 1.5));
				Plate p = throwPlate(r, plate, a, b, false);
				if (p != null) {
					air.add(p);
				}
				e.n = e.t + 3 + r.level.random.nextInt(4);
			}
			flyPlates(r, plate, air);
			if (e.t >= ticks && air.isEmpty()) {
				r.post("platos:fin");
				return true;
			}
			return false;
		}));
	}

	/** One plate that just misses (fixed path, no collision) and smashes at `to`: "...Mucha humedad." */
	public static Exec plateWhoosh(Run r, Vec3 from, Vec3 to) {
		BlockState plate = kitOr("casa_plato", Blocks.WHITE_CARPET.defaultBlockState());
		List<Plate> air = new ArrayList<>();
		Plate p = throwPlate(r, plate, from, to, true);
		if (p == null) {
			return null;
		}
		air.add(p);
		return r.start("casa:plato", r.star(), List.of(e -> {
			flyPlates(r, plate, air);
			return air.isEmpty();
		}));
	}

	private static Plate throwPlate(Run r, BlockState state, Vec3 a, Vec3 b, boolean harmless) {
		String actor = uid("plato");
		Display.BlockDisplay d = block(r, actor, a, state);
		if (d == null) {
			return null;
		}
		pose(d, new Quaternionf().rotationX(0.25F), 1F, PLATE, 0);
		double dist = a.distanceTo(b);
		Vec3 ctrl = a.lerp(b, 0.5).add(0, 0.3 + dist * 0.18, 0);
		int n = (int) Math.max(8, Math.min(30, dist / 0.65));
		if (harmless || r.level.random.nextInt(5) < 3) {
			r.sound(ModSounds.PLATE_WHOOSH, a, 1.1F, 0.9F + r.level.random.nextFloat() * 0.3F);
		}
		float spin = (0.5F + r.level.random.nextFloat() * 0.4F) * (r.level.random.nextBoolean() ? 1 : -1);
		return new Plate(actor, a, ctrl, b, n, spin, harmless);
	}

	private static void flyPlates(Run r, BlockState state, List<Plate> air) {
		for (Iterator<Plate> it = air.iterator(); it.hasNext(); ) {
			Plate p = it.next();
			if (!(r.actor(p.actor) instanceof Display d)) {
				it.remove();
				continue;
			}
			p.t++;
			double u = Math.min(1.0, p.t / (double) p.n);
			double v = 1 - u;
			Vec3 next = p.from.scale(v * v).add(p.ctrl.scale(2 * v * u)).add(p.to.scale(u * u));
			if (!p.harmless && p.t > 2) {
				BlockHitResult hit = r.level.clip(new ClipContext(p.pos, next, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, d));
				if (hit.getType() != HitResult.Type.MISS) {
					smash(r, state, p.actor, hit.getLocation());
					it.remove();
					continue;
				}
				ServerPlayer victim = null;
				for (ServerPlayer h : r.hunters()) {
					if (h.getBoundingBox().inflate(0.15).clip(p.pos, next).isPresent()) {
						victim = h;
						break;
					}
				}
				if (victim != null) {
					victim.hurtServer(r.level, r.level.damageSources().magic(), 1.5F);
					Fx.shake(victim, 0.4F, 8);
					Fx.redFlash(victim, 0.3F);
					smash(r, state, p.actor, next);
					it.remove();
					continue;
				}
			}
			p.pos = next;
			move(d, next);
			if (p.t % 2 == 0) {
				pose(d, new Quaternionf().rotationY(p.spin * p.t).rotateX(0.3F), 1F, PLATE, 2);
			}
			if (u >= 1) {
				smash(r, state, p.actor, next);
				it.remove();
			}
		}
	}

	private static void smash(Run r, BlockState state, String actor, Vec3 at) {
		r.level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state), at.x, at.y, at.z, 18, 0.15, 0.1, 0.15, 0.15);
		r.sound(ModSounds.PLATE_SHATTER, at, 1.2F, 0.85F + r.level.random.nextFloat() * 0.3F);
		r.despawn(actor);
	}

	// ------------------------------------------------------------------ the unseen and the house
	/**
	 * Moves an actor to a point only while no hunter sees where it is nor where it goes (Ofelia's seats); the first time
	 * someone then looks at it, a DOLL_TURN accent plays and "visto:&lt;actor&gt;" is posted.
	 */
	public static Exec unseenSwap(Run r, String actor, String point) {
		Vec3 dest = r.at(point).add(0, 0.5, 0);
		Step swap = e -> {
			Entity a = r.actor(actor);
			if (a == null) {
				return true;
			}
			Vec3 c = a.position().add(0, a.getBbHeight() * 0.5, 0);
			e.n = seen(r, c, 50F, 64) || seen(r, dest, 50F, 64) ? 0 : e.n + 1;
			if (e.n < 6) {
				return false;
			}
			Props.place(r, actor, point, false);
			if (a instanceof Mob m) {
				m.getNavigation().stop();
			}
			return true;
		};
		Step found = e -> {
			Entity a = r.actor(actor);
			if (a == null || e.t > 2400) {
				return true;
			}
			Vec3 c = a.position().add(0, a.getBbHeight() * 0.5, 0);
			if (seen(r, c, 22F, 40)) {
				r.sound(ModSounds.DOLL_TURN, c, 1.2F, 0.8F);
				r.post("visto:" + actor);
				return true;
			}
			return false;
		};
		return r.start("casa:swap:" + actor, r.star(), List.of(swap, found));
	}

	/**
	 * Slams a row of doors one after another, every `every` ticks, from the farthest to the nearest to the protagonist.
	 * Short gaps play the cascade sound once; long gaps slam each door. Posts "puertas:fin".
	 */
	public static Exec doorCascade(Run r, List<String> doors, int every) {
		ServerPlayer star = r.star();
		List<String> order = new ArrayList<>();
		for (String d : doors) {
			if (r.def.doors.containsKey(d)) {
				order.add(d);
			}
		}
		if (order.isEmpty()) {
			DeadLine.LOGGER.warn("Site {}: none of {} is a door", r.def.key, doors);
		} else if (star != null) {
			Vec3 s = star.position();
			order.sort(Comparator.comparingDouble((String d) -> -doorAt(r, d).distanceToSqr(s)));
		}
		int gap = Math.max(1, every);
		boolean cascade = gap <= 8;
		return r.start("casa:puertas", star, List.of(e -> {
			if (order.isEmpty()) {
				r.post("puertas:fin");  // nothing to slam: still end, so a step waiting on it does not hang
				return true;
			}
			if (e.t == 0 && cascade) {
				r.sound(ModSounds.DOOR_SLAM_CASCADE, doorAt(r, order.get(0)), 1.8F, 1.0F);
			}
			if (e.t % gap == 0 && e.t / gap < order.size()) {
				String d = order.get(e.t / gap);
				r.door(d, false, !cascade);
				Vec3 at = doorAt(r, d);
				r.level.sendParticles(ParticleTypes.POOF, at.x, at.y - 0.4, at.z, 6, 0.3, 0.6, 0.3, 0.01);
				shakeNear(r, at, 12, 0.35F, 6);
			}
			if (e.t >= (order.size() - 1) * gap) {
				r.post("puertas:fin");
				return true;
			}
			return false;
		}));
	}

	private static Vec3 doorAt(Run r, String door) {
		return Vec3.atCenterOf(r.origin.offset(r.def.doors.get(door))).add(0, 0.5, 0);
	}

	/** The lamps of a group pop one by one (6 ticks apart), from the farthest to the nearest. Posts "focos:fin". */
	public static Exec bulbPop(Run r, String group) {
		return bulbPop(r, group, 6);
	}

	public static Exec bulbPop(Run r, String group, int every) {
		List<BlockPos> g = r.def.group(group);
		List<Integer> order = new ArrayList<>();
		for (int i = 0; i < g.size(); i++) {
			order.add(i);
		}
		ServerPlayer star = r.star();
		if (order.isEmpty()) {
			DeadLine.LOGGER.warn("Site {} has no group '{}'", r.def.key, group);
		} else if (star != null) {
			Vec3 s = star.position();
			order.sort(Comparator.comparingDouble((Integer i) -> -Vec3.atCenterOf(r.origin.offset(g.get(i))).distanceToSqr(s)));
		}
		int gap = Math.max(1, every);
		BlockState glass = Blocks.GLASS.defaultBlockState();
		return r.start("casa:focos", star, List.of(e -> {
			if (order.isEmpty()) {
				r.post("focos:fin");  // nothing to pop: still end, so a step waiting on it does not hang
				return true;
			}
			if (e.t % gap == 0 && e.t / gap < order.size()) {
				int idx = order.get(e.t / gap);
				Vec3 c = Vec3.atCenterOf(r.origin.offset(g.get(idx)));
				r.light(group, idx, false);
				r.sound(ModSounds.BULB_POP, c, 1.3F, 0.85F + r.level.random.nextFloat() * 0.3F);
				r.level.sendParticles(ParticleTypes.ELECTRIC_SPARK, c.x, c.y, c.z, 8, 0.15, 0.15, 0.15, 0.2);
				r.level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, glass), c.x, c.y - 0.2, c.z, 10, 0.15, 0.1, 0.15, 0.1);
				shakeNear(r, c, 8, 0.2F, 4);
			}
			if (e.t >= (order.size() - 1) * gap) {
				r.post("focos:fin");
				return true;
			}
			return false;
		}));
	}
}
