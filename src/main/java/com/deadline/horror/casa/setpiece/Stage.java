package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.director.Director;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.dog.Choripan;
import com.deadline.horror.casa.dog.ChoripanEntity;
import com.deadline.registry.ModEntities;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;

/**
 * Stagecraft shared by the Casa set pieces (C): the family as RUN actors (they outlive one set piece: the dinner hands
 * them to the first hour, the first hour to bedtime), seats, walking routes, and "chores" -- small orders that finish on
 * their own after the set piece that gave them has ended (sit down when you get to the armchair, go away once nobody
 * sees you). Actor names are the ones the act script uses: {@link #NONA}, {@link #MARTA}, {@link #JORGE}, {@link #TOTI},
 * plus {@link #LUCIA} (a {@link PoseidaEntity}) and the dog ({@link Choripan#ACTOR}).
 */
public final class Stage {
	public static final String NONA = "nona", MARTA = "marta", JORGE = "jorge", TOTI = "toti", LUCIA = "lucia";
	/** The four {@link FamilyEntity} members, in seat order. */
	public static final List<String> MEMBERS = List.of(NONA, MARTA, JORGE, TOTI);
	/** Dinner seats (docs/design/casa_terror.md 11: silla_1 the Nona at the head, 2 Marta, 3 Jorge, 4 Lucía, 5 Toti). */
	public static final Map<String, String> SEATS = Map.of(NONA, "silla_1", MARTA, "silla_2", JORGE, "silla_3", LUCIA, "silla_4",
			TOTI, "silla_5");

	private static final Map<Run, List<Chore>> CHORES = new WeakHashMap<>();

	private Stage() {
	}

	// ------------------------------------------------------------------ markers
	public static boolean has(Run r, String point) {
		return Apparitions.has(r, point);
	}

	public static Vec3 at(Run r, String point) {
		return Apparitions.at(r, point);
	}

	public static boolean hasArea(Run r, String area) {
		return Apparitions.hasArea(r, area);
	}

	public static boolean in(Run r, Entity e, String area) {
		return e != null && hasArea(r, area) && r.area(area).contains(e.position());
	}

	/** Room areas that are outside the walls (the front garden, the yard, the balcony). */
	private static final List<String> OUTDOORS = List.of("jardin", "patio", "balcon", "cucha", "galpon");

	/**
	 * Past the front door: inside the house and in one of its rooms. The recess in front of the door and the door block
	 * are inside the 'casa' box but in no room (the hall starts behind the door), so stepping up to knock does not count.
	 */
	public static boolean pastThreshold(Run r, Entity e) {
		if (e == null || !HouseQuery.inHouse(r, e)) {
			return false;
		}
		String room = HouseQuery.room(r, e);
		return room != null && !OUTDOORS.contains(room);
	}

	public static float yawTo(Vec3 from, Vec3 to) {
		return Props.yawTowards(from, to);
	}

	/** Unit vector a yaw looks along (horizontal). */
	public static Vec3 forward(float yaw) {
		double r = Math.toRadians(yaw);
		return new Vec3(-Math.sin(r), 0, Math.cos(r));
	}

	/** Unit vector to the RIGHT hand of something facing yaw. */
	public static Vec3 right(float yaw) {
		double r = Math.toRadians(yaw);
		return new Vec3(-Math.cos(r), 0, -Math.sin(r));
	}

	/** The player's horizontal look direction. */
	public static Vec3 look(ServerPlayer p) {
		return forward(p.getYRot());
	}

	/**
	 * The spot on the floor `out` blocks from a door, on the side of `side` (crossing the door the way it opens: along
	 * the axis its block faces). Null when the site has no such door.
	 */
	public static Vec3 doorStep(Run r, String door, Vec3 side, double out) {
		Vec3 d = HouseQuery.doorPos(r, door);
		if (d == null) {
			return null;
		}
		Vec3 base = new Vec3(d.x, Math.floor(d.y), d.z);
		Vec3 to = side.subtract(base);
		BlockState st = r.level.getBlockState(BlockPos.containing(d));
		Direction.Axis ax = st.hasProperty(BlockStateProperties.HORIZONTAL_FACING)
				? st.getValue(BlockStateProperties.HORIZONTAL_FACING).getAxis()
				: Math.abs(to.x) >= Math.abs(to.z) ? Direction.Axis.X : Direction.Axis.Z;
		double sign = ax == Direction.Axis.X ? Math.signum(to.x) : Math.signum(to.z);
		if (sign == 0.0) {
			sign = 1.0;
		}
		Vec3 axis = ax == Direction.Axis.X ? new Vec3(sign, 0, 0) : new Vec3(0, 0, sign);
		return base.add(axis.scale(out));
	}

	/** A free standing spot (2 blocks of air over a floor) at or near a position (same block column, one up / down). */
	public static Vec3 stand(Run r, Vec3 v) {
		if (v == null) {
			return null;
		}
		BlockPos feet = BlockPos.containing(v);
		for (int dy : new int[] {0, 1, -1}) {
			BlockPos f = feet.above(dy);
			if (HouseQuery.standable(r, f)) {
				return new Vec3(v.x, Apparitions.floorY(r, f), v.z);
			}
		}
		return null;
	}

	/** The block a chair-like kit block (key contains `part`) nearest to a position within `radius`, or null. */
	public static BlockPos kitNear(Run r, Vec3 at, String part, int radius) {
		BlockPos c = BlockPos.containing(at);
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-radius, -1, -radius), c.offset(radius, 1, radius))) {
			BlockState s = r.level.getBlockState(p);
			if (!s.isAir() && HouseQuery.key(s).contains(part)) {
				double d = Vec3.atCenterOf(p).distanceToSqr(at);
				if (d < bd) {
					bd = d;
					best = p.immutable();
				}
			}
		}
		return best;
	}

	/** Yaw an actor seated on this chair block faces (the chair's own facing), or the fallback. */
	public static float chairYaw(Run r, BlockPos chair, float fallback) {
		BlockState s = r.level.getBlockState(chair);
		if (s.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			Direction f = s.getValue(BlockStateProperties.HORIZONTAL_FACING);
			return f.toYRot();
		}
		return fallback;
	}

	// ------------------------------------------------------------------ the family as run actors
	public static FamilyEntity member(Run r, String who) {
		return r != null && r.actor(who) instanceof FamilyEntity f ? f : null;
	}

	public static PoseidaEntity lucia(Run r) {
		return r != null && r.actor(LUCIA) instanceof PoseidaEntity l ? l : null;
	}

	public static EntityType<FamilyEntity> type(String who) {
		return switch (who) {
			case NONA -> FamilyEntities.NONA;
			case MARTA -> FamilyEntities.MARTA;
			case JORGE -> FamilyEntities.JORGE;
			default -> FamilyEntities.TOTI;
		};
	}

	/**
	 * The family member `who` as a run actor at a position facing yaw: the one already there is moved, otherwise a new
	 * one is spawned (scripted, no AI, invulnerable, never saved).
	 */
	public static FamilyEntity member(Run r, String who, Vec3 at, float yaw) {
		FamilyEntity f = member(r, who);
		if (f == null) {
			f = type(who).create(r.level, EntitySpawnReason.EVENT);
			if (f == null) {
				return null;
			}
			f.snapTo(at.x, at.y, at.z, yaw, 0F);
			setup(r, f, yaw);
			r.level.addFreshEntity(f);
			r.actor(who, f);
		} else {
			f.stopWalking();
			f.teleportTo(at.x, at.y, at.z);
			f.face(yaw);
			f.setYBodyRot(yaw);
		}
		f.setVariant(FamilyEntity.LOOK_NORMAL);
		f.setExpression(0);
		f.watch(null);
		f.lookAt(null);
		f.watchPlayers(true);
		return f;
	}

	/** Lucía as a run actor (the girl: look normal), seated or standing. */
	public static PoseidaEntity lucia(Run r, Vec3 at, float yaw, int look, int action) {
		PoseidaEntity l = lucia(r);
		if (l == null) {
			l = ModEntities.POSEIDA.create(r.level, EntitySpawnReason.EVENT);
			if (l == null) {
				return null;
			}
			l.snapTo(at.x, at.y, at.z, yaw, 0F);
			setup(r, l, yaw);
			r.level.addFreshEntity(l);
			r.actor(LUCIA, l);
		} else {
			l.teleportTo(at.x, at.y, at.z);
			Apparitions.face(l, yaw);
		}
		l.setVariant(look);
		l.setAction(action);
		return l;
	}

	private static void setup(Run r, HauntEntity h, float yaw) {
		h.setYHeadRot(yaw);
		h.setYBodyRot(yaw);
		h.scripted = true;
		h.directorActor = true;
		h.setNoAi(true);
		h.setInvulnerable(true);
		h.setSiteIndex(r.site);
		h.setPersistenceRequired();
	}

	/** Every family member (and Lucía, and the dog) of the run, present right now. */
	public static List<Entity> family(Run r) {
		List<Entity> out = new ArrayList<>();
		for (String who : MEMBERS) {
			FamilyEntity f = member(r, who);
			if (f != null) {
				out.add(f);
			}
		}
		if (lucia(r) != null) {
			out.add(lucia(r));
		}
		if (Choripan.get(r) != null) {
			out.add(Choripan.get(r));
		}
		return out;
	}

	/** They go to bed / away: every family run actor (and the dog) removed, their chores forgotten. */
	public static void dismissFamily(Run r) {
		for (String who : MEMBERS) {
			r.despawn(who);
		}
		r.despawn(LUCIA);
		Choripan.remove(r);
		List<Chore> l = CHORES.get(r);
		if (l != null) {
			l.clear();
		}
	}

	/** Sits a member down on its dinner chair (moving it there), facing the table. */
	public static FamilyEntity seat(Run r, String who) {
		String chair = SEATS.get(who);
		if (chair == null || !has(r, chair)) {
			return null;
		}
		FamilyEntity f = member(r, who, r.at(chair), r.yaw(chair));
		if (f != null) {
			f.setAction(FamilyEntity.POSE_SIT);
			f.propSounds = false;
		}
		return f;
	}

	/** Lucía on her dinner chair (the girl, sitting, hands in her lap). */
	public static PoseidaEntity seatLucia(Run r) {
		String chair = SEATS.get(LUCIA);
		return has(r, chair) ? lucia(r, r.at(chair), r.yaw(chair), PoseidaEntity.LOOK_NORMAL, PoseidaEntity.ACT_SIT) : null;
	}

	/** Choripán under the dinner table (between the chairs of the Nona's end), growling low at her. */
	public static ChoripanEntity dogUnderTable(Run r) {
		if (!has(r, "silla_1") || !has(r, "silla_8")) {
			return null;
		}
		Vec3 a = r.at("silla_1");
		Vec3 b = r.at("silla_8");
		Vec3 under = a.add(b.subtract(a).scale(0.3));
		ChoripanEntity dog = Choripan.get(r);
		if (dog == null) {
			dog = Choripan.spawn(r, "silla_1", ChoripanEntity.POSE_GROWL, ChoripanEntity.LOOK_NORMAL);
		}
		if (dog != null) {
			dog.stopWalking();
			dog.teleportTo(under.x, under.y, under.z);
			dog.face(yawTo(under, a));
			dog.setVariant(ChoripanEntity.LOOK_NORMAL);
			dog.pose(ChoripanEntity.POSE_GROWL);
			FamilyEntity nona = member(r, NONA);
			if (nona != null) {
				dog.watch(nona);
			}
		}
		return dog;
	}

	/** True when any hunter of the run (or the given player) has the point on screen with a clear line of sight. */
	public static boolean seen(Run r, ServerPlayer p, Vec3 at) {
		if (p != null && HouseQuery.sees(r, p, at)) {
			return true;
		}
		for (ServerPlayer h : r.hunters()) {
			if (h != p && HouseQuery.sees(r, h, at)) {
				return true;
			}
		}
		return false;
	}

	public static boolean seen(Run r, ServerPlayer p, Entity e) {
		return e != null && (seen(r, p, e.position().add(0, e.getBbHeight() * 0.85, 0)) || seen(r, p, e.position().add(0, e.getBbHeight() * 0.4, 0)));
	}

	// ------------------------------------------------------------------ routes
	/** A walk through waypoints (one walkTo per leg: stairs and doorways are crossed one at a time). */
	public static final class Route {
		private final List<Vec3> points = new ArrayList<>();
		private final double speed;
		private int index = -1;

		public Route(double speed, Vec3... pts) {
			this.speed = speed;
			for (Vec3 v : pts) {
				if (v != null) {
					this.points.add(v);
				}
			}
		}

		/** Advances the walk; true once the last point is reached (or there was none). */
		public boolean tick(FamilyEntity f) {
			if (f == null || f.isRemoved()) {
				return true;
			}
			if (this.index >= this.points.size()) {
				return true;
			}
			if (this.index < 0 || f.hasArrived() && !f.isWalking()) {
				this.index++;
				if (this.index >= this.points.size()) {
					return true;
				}
				f.walkTo(this.points.get(this.index), this.speed);
			}
			return false;
		}

		public boolean done() {
			return this.index >= this.points.size();
		}

		public Vec3 last() {
			return this.points.isEmpty() ? null : this.points.get(this.points.size() - 1);
		}
	}

	/**
	 * The way from wherever an actor is to a room: up the main stair when the room is on another floor, then the corridor
	 * spot in front of the room's door, then the room point. Null points (missing markers) are skipped.
	 */
	public static Route routeTo(Run r, Entity who, String door, String roomPoint, double speed) {
		List<Vec3> pts = new ArrayList<>();
		Vec3 room = at(r, roomPoint);
		if (room == null) {
			return new Route(speed);
		}
		boolean otherFloor = Math.abs(room.y - who.getY()) > 2.5;
		if (otherFloor) {
			boolean up = room.y > who.getY();
			Vec3 pie = at(r, "esc_principal_pie");
			Vec3 arriba = at(r, "esc_principal_arriba");
			pts.add(up ? pie : arriba);
			pts.add(up ? arriba : pie);
		}
		if (door != null) {
			// the hall on the room's floor (world heights: the floor nearer the room point)
			Vec3 pb = at(r, "pasillo_pb");
			Vec3 p1 = at(r, "pasillo_1p");
			Vec3 corridor = pb == null ? p1 : p1 == null ? pb : Math.abs(p1.y - room.y) < Math.abs(pb.y - room.y) ? p1 : pb;
			pts.add(doorStep(r, door, corridor != null ? corridor : who.position(), 1.2));
			pts.add(doorStep(r, door, room, 1.0));
		}
		pts.add(room);
		return new Route(speed, pts.toArray(new Vec3[0]));
	}

	// ------------------------------------------------------------------ chores (orders that outlive their set piece)
	/** One standing order for an actor, ticked by the server until it is done. */
	public interface Chore {
		/** True when done (it is then dropped). */
		boolean tick(Run r);

		Entity actor();
	}

	/** Gives an actor a standing order (replacing the one it had). */
	public static void chore(Run r, Chore c) {
		if (r == null || c == null || c.actor() == null) {
			return;
		}
		List<Chore> l = CHORES.computeIfAbsent(r, k -> new ArrayList<>());
		l.removeIf(o -> o.actor() == c.actor());
		l.add(c);
	}

	/** Cancels the standing order of an actor (a set piece takes it over). */
	public static void cancelChore(Run r, Entity e) {
		List<Chore> l = CHORES.get(r);
		if (l != null && e != null) {
			l.removeIf(o -> o.actor() == e);
		}
	}

	/** Walk a route, then do something on arrival (sit down, face the sink...). */
	public static void walkThen(Run r, FamilyEntity f, Route route, Consumer<FamilyEntity> then) {
		chore(r, new Chore() {
			@Override
			public boolean tick(Run run) {
				if (f.isRemoved()) {
					return true;
				}
				if (route.tick(f)) {
					if (then != null) {
						then.accept(f);
					}
					return true;
				}
				return false;
			}

			@Override
			public Entity actor() {
				return f;
			}
		});
	}

	/**
	 * When no hunter sees the actor, it is moved to `to` (facing yaw; null: removed from the run) and `then` runs. For the
	 * actors that cannot walk (Lucía) and for exits (the dog gone out, the family gone to bed).
	 */
	public static void whenUnseen(Run r, Entity e, String actorName, Vec3 to, float yaw, Consumer<Entity> then) {
		chore(r, new Chore() {
			private int unseen;

			@Override
			public boolean tick(Run run) {
				if (e.isRemoved()) {
					return true;
				}
				boolean visible = seen(run, null, e) || to != null && seen(run, null, to.add(0, 1.0, 0));
				this.unseen = visible ? 0 : this.unseen + 1;
				if (this.unseen < 10) {
					return false;
				}
				if (to == null) {
					if (actorName != null) {
						run.despawn(actorName);
					} else {
						e.discard();
					}
				} else {
					e.teleportTo(to.x, to.y, to.z);
					if (e instanceof LivingEntity) {
						Apparitions.face(e, yaw);
					}
					if (e instanceof FamilyEntity f) {
						f.face(yaw);
					}
				}
				if (then != null) {
					then.accept(e);
				}
				return true;
			}

			@Override
			public Entity actor() {
				return e;
			}
		});
	}

	/** Server tick (from SetPieces): runs the chores of live runs, drops those of finished ones. */
	public static void tickChores(MinecraftServer server) {
		if (CHORES.isEmpty()) {
			return;
		}
		for (Map.Entry<Run, List<Chore>> en : new ArrayList<>(CHORES.entrySet())) {
			Run r = en.getKey();
			if (r == null || Director.get(r.type, r.site) != r) {
				CHORES.remove(r);
				continue;
			}
			if (r.hunters().isEmpty()) {
				continue;  // nobody here: the house holds its breath
			}
			for (Iterator<Chore> it = new ArrayList<>(en.getValue()).iterator(); it.hasNext();) {
				Chore c = it.next();
				boolean done;
				try {
					done = c.tick(r);
				} catch (RuntimeException ex) {
					com.deadline.DeadLine.LOGGER.error("Casa set piece chore failed", ex);
					done = true;
				}
				if (done) {
					en.getValue().remove(c);
				}
			}
		}
	}

	public static void forget(Run r) {
		CHORES.remove(r);
	}

	// ------------------------------------------------------------------ misc
	/** Vec3 of a block's top centre. */
	public static Vec3 top(Run r, BlockPos p) {
		var shape = r.level.getBlockState(p).getCollisionShape(r.level, p);
		double y = shape.isEmpty() ? p.getY() + 0.5 : p.getY() + shape.max(Direction.Axis.Y);
		return new Vec3(p.getX() + 0.5, y, p.getZ() + 0.5);
	}
}
