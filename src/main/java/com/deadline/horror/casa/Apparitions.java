package com.deadline.horror.casa;

import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HouseQuery;
import com.deadline.registry.ModParticles;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Shared stagecraft of the Casa apparitions (catalogue 33-45 of docs/design/casa_terror.md 5): marker guards, actors
 * that belong to one event run (spawned here, always removed by {@link #despawnAll} in the event's stop()), "is he
 * looking at it" tests and the one rule every visual scare obeys: never on a hunter who is hidden ({@link #hidden}).
 */
public final class Apparitions {
	private static final String SPAWNED = "b3:spawned";

	private Apparitions() {
	}

	// ------------------------------------------------------------------ markers (never throw: a missing point = cannot run)
	public static boolean has(Run r, String point) {
		return r != null && r.def.points.containsKey(point);
	}

	public static boolean hasAll(Run r, String... points) {
		for (String p : points) {
			if (!has(r, p)) {
				return false;
			}
		}
		return true;
	}

	public static boolean hasArea(Run r, String area) {
		return r != null && r.def.areas.containsKey(area);
	}

	/** World position of a point, or null when the site does not have it. */
	public static Vec3 at(Run r, String point) {
		return has(r, point) ? r.at(point) : null;
	}

	// ------------------------------------------------------------------ the hunter
	/**
	 * True when no visual scare may target this hunter: hidden in a hiding spot (the hunt: B2's
	 * {@code com.deadline.horror.casa.hunt.HideSpots}), a spectator, or dead.
	 */
	public static boolean hidden(ServerPlayer p) {
		if (p == null || p.isSpectator() || !p.isAlive()) {
			return true;
		}
		return com.deadline.horror.casa.hunt.HideSpots.hidden(p);
	}

	/** A loud thing happened here: in the hunt (Act 5) the Nona hears it (0-100: 15 a creak, 40 a plate, 70 a slam). */
	public static void noise(Ctx c, Vec3 at, float loudness) {
		com.deadline.horror.casa.hunt.Hunt.noise(c.run, at, loudness);
	}

	/** Common precondition of every visual apparition: a hunter inside the house who is not hidden. */
	public static boolean canScare(Ctx c) {
		return !hidden(c.p) && HouseQuery.inHouse(c.run, c.p);
	}

	/** The player has this spot on screen (within deg of the centre) with a clear line of sight. */
	public static boolean sees(Ctx c, Vec3 at, float deg) {
		return c.run.looking(c.p, at, deg, 64.0);
	}

	/** The player sees the entity: its head or the middle of its body, within deg of the centre, line of sight. */
	public static boolean watches(Ctx c, Entity e, float deg) {
		if (e == null || e.isRemoved()) {
			return false;
		}
		Vec3 base = e.position();
		double h = e.getBbHeight();
		return c.run.looking(c.p, base.add(0, h * 0.85, 0), deg, 64.0) || c.run.looking(c.p, base.add(0, h * 0.5, 0), deg, 64.0);
	}

	/** Like {@link #watches(Ctx, Entity, float)} but for a body whose visible part is not its hitbox (a ceiling, a floor). */
	public static boolean seesAny(Ctx c, float deg, Vec3... points) {
		for (Vec3 v : points) {
			if (c.run.looking(c.p, v, deg, 64.0)) {
				return true;
			}
		}
		return false;
	}

	public static double dist(Ctx c, Vec3 v) {
		return c.p.position().distanceTo(v);
	}

	public static float yawTo(Vec3 from, Vec3 to) {
		return Props.yawTowards(from, to);
	}

	// ------------------------------------------------------------------ actors of one event run
	/**
	 * Spawns a director actor for this event run: scripted, no AI, invulnerable, never saved, never pushed. It is
	 * tracked in the event's data and removed by {@link #despawnAll}.
	 */
	public static <T extends Entity> T spawn(Ctx c, EntityType<T> type, Vec3 pos, float yaw) {
		T e = type.create(c.level(), EntitySpawnReason.EVENT);
		if (e == null) {
			return null;
		}
		e.snapTo(pos.x, pos.y, pos.z, yaw, 0F);
		if (e instanceof LivingEntity l) {
			l.setYHeadRot(yaw);
			l.setYBodyRot(yaw);
		}
		if (e instanceof HauntEntity h) {
			h.scripted = true;
			h.directorActor = true;
			h.setNoAi(true);
			h.setInvulnerable(true);
			h.setSiteIndex(c.run.site);
			h.setPersistenceRequired();
		}
		c.level().addFreshEntity(e);
		spawned(c).add(e);
		return e;
	}

	@SuppressWarnings("unchecked")
	private static List<Entity> spawned(Ctx c) {
		Object o = c.data.get(SPAWNED);
		if (o instanceof List<?> l) {
			return (List<Entity>) l;
		}
		List<Entity> l = new ArrayList<>();
		c.data.put(SPAWNED, l);
		return l;
	}

	/** Removes everything this event run spawned (call it from stop(): it runs exactly once, aborted or not). */
	public static void despawnAll(Ctx c) {
		for (Entity e : spawned(c)) {
			if (e != null && !e.isRemoved()) {
				e.discard();
			}
		}
		spawned(c).clear();
	}

	/** Removes one actor with a breath of black smoke (a ghost going out, not a body vanishing in a puff). */
	public static void vanish(Entity e, boolean smoke) {
		if (e == null || e.isRemoved()) {
			return;
		}
		if (smoke && e.level() instanceof ServerLevel level) {
			level.sendParticles(ModParticles.DEMON_SMOKE, e.getX(), e.getY() + e.getBbHeight() * 0.6, e.getZ(), 14,
					0.2, e.getBbHeight() * 0.3, 0.2, 0.01);
		}
		e.discard();
	}

	public static boolean gone(Entity e) {
		return e == null || e.isRemoved();
	}

	// ------------------------------------------------------------------ sound
	/** Positional, in the world (everyone near hears it): a sound always comes FROM the apparition. */
	public static void sound(Ctx c, SoundEvent s, Vec3 at, float volume, float pitch) {
		c.run.sound(s, at, volume, pitch);
	}

	public static float pitch(Ctx c, float lo, float hi) {
		return lo + c.rnd.nextFloat() * (hi - lo);
	}

	// ------------------------------------------------------------------ geometry
	/** Height of the floor surface at or under a block position (the top of its collision shape), searching down 2. */
	public static double floorY(Run r, BlockPos feet) {
		for (int dy = 0; dy >= -2; dy--) {
			BlockPos p = feet.above(dy);
			VoxelShape s = r.level.getBlockState(p).getCollisionShape(r.level, p);
			if (!s.isEmpty()) {
				return p.getY() + s.max(Direction.Axis.Y);
			}
		}
		return feet.getY();
	}

	/** The underside of the ceiling over a position (first solid block up to 6 above), or NaN if open sky. */
	public static double ceilingY(Run r, Vec3 at) {
		BlockPos p = BlockPos.containing(at);
		for (int dy = 0; dy <= 6; dy++) {
			BlockPos q = p.above(dy);
			BlockState s = r.level.getBlockState(q);
			VoxelShape v = s.getCollisionShape(r.level, q);
			if (!v.isEmpty()) {
				return q.getY() + v.min(Direction.Axis.Y);
			}
		}
		return Double.NaN;
	}

	/** True when nothing solid is between the two points (eye-level line, blocks only). */
	public static boolean clear(Run r, Vec3 a, Vec3 b, Entity viewer) {
		BlockHitResult hit = r.level.clip(new ClipContext(a, b, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, viewer));
		return hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(a) >= a.distanceTo(b) - 0.3;
	}

	/** The dark corners of a room area: 4 floor spots 0.7 block in from the walls, standable, darkest first. */
	public static List<Vec3> corners(Run r, String area, double floorY) {
		List<Vec3> out = new ArrayList<>();
		if (!hasArea(r, area)) {
			return out;
		}
		AABB box = r.area(area);
		double[] xs = {box.minX + 0.7, box.maxX - 0.7};
		double[] zs = {box.minZ + 0.7, box.maxZ - 0.7};
		for (double x : xs) {
			for (double z : zs) {
				BlockPos feet = BlockPos.containing(x, floorY + 0.1, z);
				if (HouseQuery.standable(r, feet)) {
					out.add(new Vec3(x, floorY(r, feet), z));
				}
			}
		}
		out.sort((a, b) -> Integer.compare(light(r, a), light(r, b)));
		return out;
	}

	public static int light(Run r, Vec3 v) {
		BlockPos p = BlockPos.containing(v.x, v.y + 1.0, v.z);
		return r.level.getBrightness(net.minecraft.world.level.LightLayer.BLOCK, p);
	}

	/** Moves an actor smoothly one step (the tracker interpolates setPos moves) and points it along the motion. */
	public static void glide(Entity e, Vec3 to, boolean face) {
		Vec3 from = e.position();
		e.setPos(to.x, to.y, to.z);
		if (face && from.distanceToSqr(to) > 1.0E-6) {
			float yaw = yawTo(from, to);
			e.setYRot(yaw);
			if (e instanceof LivingEntity l) {
				l.setYHeadRot(yaw);
				l.setYBodyRot(yaw);
			}
		}
	}

	/** Turns a living actor (body and head) to a yaw at once. */
	public static void face(Entity e, float yaw) {
		e.setYRot(yaw);
		if (e instanceof LivingEntity l) {
			l.setYHeadRot(yaw);
			l.setYBodyRot(yaw);
		}
	}

	public static float wrap(float deg) {
		return Mth.wrapDegrees(deg);
	}

	// ------------------------------------------------------------------ gaze: has he seen it, has he looked away
	/** Counts how long the hunter has been looking at an apparition and how long since he looked away. */
	public static final class Gaze {
		/** Consecutive ticks seen / not seen; total ticks seen; ever = seen for at least {@link #MIN} ticks once. */
		public int seen, lost, total;
		public boolean ever;
		public static final int MIN = 4;

		public void update(boolean sees) {
			if (sees) {
				this.seen++;
				this.total++;
				this.lost = 0;
				if (this.seen >= MIN) {
					this.ever = true;
				}
			} else {
				this.lost++;
				this.seen = 0;
			}
		}

		/** He saw it, and has now been looking elsewhere for `ticks`. */
		public boolean lookedAway(int ticks) {
			return this.ever && this.lost >= ticks;
		}
	}

	public static Gaze gaze(Ctx c) {
		Object o = c.data.get("b3:gaze");
		if (o instanceof Gaze g) {
			return g;
		}
		Gaze g = new Gaze();
		c.data.put("b3:gaze", g);
		return g;
	}
}
