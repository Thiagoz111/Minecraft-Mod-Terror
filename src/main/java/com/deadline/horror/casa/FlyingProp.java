package com.deadline.horror.casa;

import com.deadline.casa.CasaProps;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.net.Fx;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.Display;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * A flying object of the house (docs/design/casa_terror.md 6.4), made of a display entity so it needs nothing on the
 * client: a decorative block taken from the house ({@link #lift}: a chair, a picture, the rocking chair) or a loose prop
 * ({@link #spawn} a plate, a knife; {@link #spawnItem} a book, a glass) flies with physics (directed throw with
 * {@link #throwAt}, gravity, drag, bounces, spin), hurts a hunter it hits a little (never to death), and ends where it
 * lands: as a real block again in the cell it fell into ({@link #asBlock}), lying there as a display, stuck in a wall
 * ({@link #stick}, knives) or broken ({@link #breakable}: shards of its own block and a shatter).
 *
 * <p>The owner ticks it ({@link #tick}, once per tick) and calls {@link #restore} when its event stops: the display goes,
 * the block it became goes, and the original block is back in its place. Every change is remembered through
 * {@link CasaProps#remember} linked to a display, so a chapter replay or the end of the case puts the house back too;
 * {@link #clear(Run)} restores every prop of a run (the case script calls it on leave through
 * {@link PoltergeistEvents#cleanup}).
 */
public final class FlyingProp {
	public enum State {
		HELD, FLYING, SLIDING, RESTING, STUCK, BROKEN, GONE
	}

	/** Pivots in model space: a block's centre; the floor of a flat prop (a plate, a knife lying on its side). */
	public static final Vector3f CENTER = new Vector3f(0.5F, 0.5F, 0.5F);
	public static final Vector3f FLAT = new Vector3f(0.5F, 0.03F, 0.5F);
	/** The kit knife lies along the model's x: this roll stands its blade up (as {@link com.deadline.casa.KnifeOrbit}). */
	private static final float KNIFE_ROLL = (float) (Math.PI / 2);
	private static final List<FlyingProp> ALL = new ArrayList<>();

	public final Run run;
	private final String actor;
	private final BlockState shown;
	private final ItemStack item;
	private final BlockState original;
	private final BlockPos origin;
	private Quaternionf base;
	private Quaternionf spin = new Quaternionf();
	private Vector3f pivot = CENTER;
	private float scale = 1F;
	private Vec3 pos;
	private Vec3 vel = Vec3.ZERO;
	private Vec3 aimAt;
	private Vector3f spinAxis = new Vector3f(0F, 1F, 0F);
	private float spinRate;
	private double gravity = 0.045;
	private double drag = 0.985;
	private double bounce = 0.3;
	private double friction = 0.55;
	private double radius = 0.3;
	private float damage = 1.5F;
	private float loud = 30F;
	private boolean breakable;
	private boolean stick;
	private boolean asBlock;
	private boolean pointAlong;
	private boolean harmless;
	private SoundEvent hitSound = ModSounds.ALACENA_GOLPE;
	private SoundEvent breakSound = ModSounds.PLATE_SHATTER;
	private State state = State.HELD;
	private int age;
	private int bounces;
	private Vec3 slideFrom;
	private Vec3 slideTo;
	private int slideT;
	private int slideN;
	private BlockPos landed;
	private String anchor;
	private ServerPlayer hitWho;
	private final Set<UUID> hurt = new HashSet<>();

	private FlyingProp(Run run, String actor, BlockState shown, ItemStack item, BlockState original, BlockPos origin, Vec3 pos, Quaternionf base) {
		this.run = run;
		this.actor = actor;
		this.shown = shown;
		this.item = item;
		this.original = original;
		this.origin = origin;
		this.pos = pos;
		this.base = base;
		ALL.add(this);
	}

	// ------------------------------------------------------------------ making one
	/**
	 * Takes the block at pos off the house into a display that looks exactly like it (the block becomes air). Null for
	 * air, doors, block entities and blocks another set piece holds. It lands as a block again unless told otherwise.
	 */
	public static FlyingProp lift(Run r, BlockPos pos) {
		CasaProps.sweep(r);
		if (CasaProps.held(r, pos)) {
			return null;
		}
		BlockState s = r.level.getBlockState(pos);
		if (s.isAir() || s.getBlock() instanceof DoorBlock || r.level.getBlockEntity(pos) != null) {
			return null;
		}
		String actor = CasaProps.uid("vuela");
		Vec3 c = Vec3.atCenterOf(pos);
		Display.BlockDisplay d = CasaProps.block(r, actor, c, Polter.north(s));
		if (d == null) {
			return null;
		}
		Quaternionf q = Polter.yaw(Polter.facing(s));
		CasaProps.pose(d, q, 1F, CENTER, 0);
		CasaProps.remember(r, pos, s, List.of(actor));
		r.setBlock(pos, Blocks.AIR.defaultBlockState());
		FlyingProp f = new FlyingProp(r, actor, Polter.north(s), null, s, pos.immutable(), c, q);
		f.asBlock = true;
		return f;
	}

	/** A loose block prop that was not in the house (a plate out of the sideboard, a knife off the rack). */
	public static FlyingProp spawn(Run r, Vec3 at, BlockState state, float yawRad, Vector3f pivot) {
		if (state == null) {
			return null;
		}
		String actor = CasaProps.uid("vuela");
		Display.BlockDisplay d = CasaProps.block(r, actor, at, Polter.north(state));
		if (d == null) {
			return null;
		}
		Quaternionf q = new Quaternionf().rotationY(yawRad);
		CasaProps.pose(d, q, 1F, pivot, 0);
		FlyingProp f = new FlyingProp(r, actor, Polter.north(state), null, null, null, at, q);
		f.pivot = pivot;
		return f;
	}

	/** A loose item (a book, a glass, a jar) shown by an item display centred on `at`. */
	public static FlyingProp spawnItem(Run r, Vec3 at, ItemStack stack, float scale) {
		String actor = CasaProps.uid("vuela");
		Display.ItemDisplay d = CasaProps.item(r, actor, at, stack);
		if (d == null) {
			return null;
		}
		Quaternionf q = new Quaternionf();
		CasaProps.pose(d, q, scale, CasaProps.ZERO, 0);
		FlyingProp f = new FlyingProp(r, actor, null, stack, null, null, at, q);
		f.pivot = CasaProps.ZERO;
		f.scale = scale;
		f.radius = 0.2;
		return f;
	}

	// ------------------------------------------------------------------ how it behaves
	public FlyingProp pivot(Vector3f p) {
		this.pivot = p;
		return this;
	}

	public FlyingProp scale(float s) {
		this.scale = s;
		return this;
	}

	public FlyingProp gravity(double g) {
		this.gravity = g;
		return this;
	}

	public FlyingProp drag(double d) {
		this.drag = d;
		return this;
	}

	/** Fraction of the speed it keeps off a wall or the floor (0 = dead stop). */
	public FlyingProp bounce(double b) {
		this.bounce = b;
		return this;
	}

	public FlyingProp radius(double r) {
		this.radius = r;
		return this;
	}

	/** Damage on a hunter it hits (light: the house never kills, see {@link Polter#hurt}). */
	public FlyingProp damage(float d) {
		this.damage = d;
		return this;
	}

	/** It hits nobody (it is meant to just miss). */
	public FlyingProp harmless() {
		this.harmless = true;
		return this;
	}

	/** How loud its impacts are for the hunt (0-100). */
	public FlyingProp loud(float l) {
		this.loud = l;
		return this;
	}

	/** It shatters at the first hard impact (plates, glasses): shards of its block and this sound. */
	public FlyingProp breakable(SoundEvent shatter) {
		this.breakable = true;
		if (shatter != null) {
			this.breakSound = shatter;
		}
		return this;
	}

	/** It sticks where its point hits a wall (knives), pointing along its flight. */
	public FlyingProp stick() {
		this.stick = true;
		this.pointAlong = true;
		return this;
	}

	/** It flies point first (a knife), oriented along its velocity (or at its aim while held). */
	public FlyingProp pointAlong() {
		this.pointAlong = true;
		return this;
	}

	/** Whether it becomes a real block where it lands (lifted blocks do by default). */
	public FlyingProp asBlock(boolean b) {
		this.asBlock = b && original != null;
		return this;
	}

	public FlyingProp hitSound(SoundEvent s) {
		this.hitSound = s;
		return this;
	}

	public FlyingProp spin(Vec3 axis, float radPerTick) {
		Vec3 a = axis.lengthSqr() < 1e-6 ? new Vec3(0, 1, 0) : axis.normalize();
		this.spinAxis = new Vector3f((float) a.x, (float) a.y, (float) a.z);
		this.spinRate = radPerTick;
		return this;
	}

	// ------------------------------------------------------------------ moving it
	/** Holds it still in the air at a point (aiming at `aim` if it flies point first; null keeps its turn). */
	public FlyingProp hold(Vec3 at, Vec3 aim) {
		this.state = State.HELD;
		this.pos = at;
		this.aimAt = aim;
		this.vel = Vec3.ZERO;
		Display d = display();
		if (d != null) {
			CasaProps.move(d, at);
			CasaProps.pose(d, orientation(), scale, pivot, 3);
		}
		return this;
	}

	public FlyingProp launch(Vec3 velocity) {
		this.vel = velocity;
		this.state = State.FLYING;
		this.age = 0;
		return this;
	}

	/**
	 * Throws it at a point: horizontal speed `speed` blocks/tick and the arc that gravity needs to get there, with a
	 * tumbling spin (unless it flies point first).
	 */
	public FlyingProp throwAt(Vec3 target, double speed) {
		Vec3 d = target.subtract(pos);
		double h = Math.sqrt(d.x * d.x + d.z * d.z);
		double t = Math.max(3.0, h / Math.max(0.05, speed));
		Vec3 v = new Vec3(d.x / t, (d.y + 0.5 * gravity * t * t) / t, d.z / t);
		if (!pointAlong && spinRate == 0F) {
			var rnd = run.level.getRandom();
			spin(new Vec3(rnd.nextDouble() - 0.5, rnd.nextDouble() * 0.6, rnd.nextDouble() - 0.5), 0.25F + rnd.nextFloat() * 0.3F);
		}
		return launch(v);
	}

	/** Drags it along the floor to `to` in `ticks`, in jerks (a chair that moves by itself), then lands there. */
	public FlyingProp slideTo(Vec3 to, int ticks) {
		this.state = State.SLIDING;
		this.slideFrom = pos;
		this.slideTo = to;
		this.slideT = 0;
		this.slideN = Math.max(4, ticks);
		return this;
	}

	/** Puts it at once at `to` and lands it there (what moved while the room was dark). */
	public FlyingProp placeAt(Vec3 to, float yawRad) {
		this.pos = to;
		this.base = new Quaternionf().rotationY(yawRad);
		this.spin = new Quaternionf();
		land();
		return this;
	}

	// ------------------------------------------------------------------ state
	public State state() {
		return state;
	}

	/** Still in the air or sliding (or held). */
	public boolean moving() {
		return state == State.FLYING || state == State.SLIDING || state == State.HELD;
	}

	public boolean flying() {
		return state == State.FLYING || state == State.SLIDING;
	}

	public boolean broken() {
		return state == State.BROKEN;
	}

	public Vec3 pos() {
		return landed != null ? Vec3.atCenterOf(landed) : pos;
	}

	public Vec3 velocity() {
		return vel;
	}

	/** The block it became where it landed (null if it did not). */
	public BlockPos landedBlock() {
		return landed;
	}

	public BlockPos origin() {
		return origin;
	}

	/** Run actor name of its display (to link a remembered block to it, see {@link CasaProps#swap}). */
	public String actor() {
		return actor;
	}

	/** The hunter it hit last (null if none). */
	public ServerPlayer hit() {
		return hitWho;
	}

	/** True when a hunter sees where it is now, or the empty place it came from. */
	public boolean seen(float deg) {
		for (ServerPlayer p : run.hunters()) {
			if (p.isSpectator()) {
				continue;
			}
			if (state != State.BROKEN && state != State.GONE && run.looking(p, pos(), deg, 48)) {
				return true;
			}
			if (origin != null && run.looking(p, Vec3.atCenterOf(origin), deg, 48)) {
				return true;
			}
		}
		return false;
	}

	private Display display() {
		return run.actor(actor) instanceof Display d ? d : null;
	}

	// ------------------------------------------------------------------ ticking
	/** One physics step; true once it has come to rest (landed, stuck, broken or gone). */
	public boolean tick() {
		switch (state) {
			case FLYING -> fly();
			case SLIDING -> slide();
			case HELD -> {
				Display d = display();
				if (d == null) {
					state = State.GONE;
				} else if (aimAt != null && run.now() % 2 == 0) {
					CasaProps.pose(d, orientation(), scale, pivot, 2);
				}
			}
			default -> {
			}
		}
		return !moving();
	}

	private void fly() {
		Display d = display();
		if (d == null) {
			state = State.GONE;
			return;
		}
		age++;
		vel = vel.scale(drag).add(0, -gravity, 0);
		Vec3 next = pos.add(vel);
		double speed = vel.length();
		// consecrated salt on the floor stops what flies over it: it drops dead there
		if (CasaProps.saltAt(run.level, next)) {
			run.level.sendParticles(ModParticles.SALT_SPARKLE, next.x, next.y, next.z, 10, 0.15, 0.15, 0.15, 0.05);
			vel = new Vec3(0, Math.min(0, vel.y), 0);
			next = pos.add(vel);
		}
		if (!harmless) {
			for (ServerPlayer h : run.hunters()) {
				if (h.isSpectator() || hurt.contains(h.getUUID())) {
					continue;
				}
				AABB box = h.getBoundingBox().inflate(Math.min(0.25, radius * 0.6));
				if (box.contains(pos) || box.clip(pos, next).isPresent()) {
					strike(h, speed);
					if (breakable) {
						shatter(next);
						return;
					}
					vel = new Vec3(-vel.x * 0.2, Math.min(vel.y, 0.05), -vel.z * 0.2);
					next = pos.add(vel);
					break;
				}
			}
		}
		Vec3 dir = speed < 1e-6 ? new Vec3(0, -1, 0) : vel.scale(1 / speed);
		Vec3 reach = next.add(dir.scale(stick ? 0.1 : radius));
		BlockHitResult hit = run.level.clip(new ClipContext(pos, reach, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, d));
		if (hit.getType() != HitResult.Type.MISS) {
			Vec3 at = hit.getLocation();
			Direction face = hit.getDirection();
			if (breakable && speed > 0.15) {
				shatter(at);
				return;
			}
			if (stick && face != Direction.UP) {
				pos = at.subtract(dir.scale(0.32));
				CasaProps.move(d, pos);
				CasaProps.pose(d, orientation(), scale, pivot, 1);
				state = State.STUCK;
				run.sound(ModSounds.KNIFE_IMPACT, at, 1.4F, 0.9F + run.level.getRandom().nextFloat() * 0.2F);
				Polter.noise(run, at, loud);
				return;
			}
			Vec3 n = new Vec3(face.getStepX(), face.getStepY(), face.getStepZ());
			double vn = vel.dot(n);
			Vec3 vt = vel.subtract(n.scale(vn));
			vel = vt.scale(friction).subtract(n.scale(vn * bounce));
			pos = at.add(n.scale(radius + 0.01));
			bounces++;
			spinRate *= 0.6F;
			float v = (float) Math.min(1.0, speed * 2.5);
			if (v > 0.15F && hitSound != null) {
				run.sound(hitSound, at, 0.5F + v, 0.7F + run.level.getRandom().nextFloat() * 0.4F);
				Polter.noise(run, at, loud * v);
			}
			if (face == Direction.UP && (vel.length() < 0.09 || bounces > 4) || bounces > 9) {
				land();
				return;
			}
		} else {
			pos = next;
		}
		if (spinRate != 0F && !pointAlong) {
			spin = new Quaternionf().rotationAxis(spinRate, spinAxis.x, spinAxis.y, spinAxis.z).mul(spin);
			spinRate *= 0.995F;
		}
		CasaProps.move(d, pos);
		if (age % 2 == 0) {
			CasaProps.pose(d, orientation(), scale, pivot, 2);
		}
		if (age > 20 * 12 || pos.y < run.origin.getY() - 24) {
			land();
		}
	}

	private void slide() {
		Display d = display();
		if (d == null) {
			state = State.GONE;
			return;
		}
		slideT++;
		double u = Math.min(1.0, slideT / (double) slideN);
		// in jerks: it surges, stops, surges again (a chair dragged by someone you cannot see)
		double k = CasaProps.ease(u) + 0.04 * Math.sin(u * Math.PI * 7) * (1 - u);
		pos = slideFrom.lerp(slideTo, Math.max(0, Math.min(1, k)));
		CasaProps.move(d, pos);
		if (slideT % 3 == 0) {
			float wob = (float) (0.06 * Math.sin(slideT * 0.9) * (1 - u));
			spin = new Quaternionf().rotationY(wob);
			CasaProps.pose(d, orientation(), scale, pivot, 3);
		}
		if (u >= 1) {
			land();
		}
	}

	private Quaternionf orientation() {
		if (pointAlong) {
			Vec3 dir = aimAt != null && state == State.HELD ? aimAt.subtract(pos) : vel;
			if (dir.lengthSqr() < 1e-6) {
				dir = new Vec3(0, -1, 0);
			}
			return CasaProps.alongX(dir, KNIFE_ROLL);
		}
		return new Quaternionf(spin).mul(base);
	}

	// ------------------------------------------------------------------ endings
	private void strike(ServerPlayer h, double speed) {
		hurt.add(h.getUUID());
		hitWho = h;
		Polter.hurt(run, h, (float) (damage * Math.min(1.0, 0.4 + speed * 1.5)));
		Fx.shake(h, 0.45F, 8);
		Fx.redFlash(h, 0.3F);
		SanityManager.add(h, -3F);
		if (hitSound != null) {
			run.sound(hitSound, h.position().add(0, 1.2, 0), 1.2F, 1.1F);
		}
	}

	/** Breaks it: shards of its own block (glass for items) and the shatter; nothing is left. */
	public void shatter(Vec3 at) {
		BlockState shards = shown != null ? shown : Blocks.GLASS.defaultBlockState();
		run.level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, shards), at.x, at.y, at.z, 18, 0.15, 0.1, 0.15, 0.15);
		run.sound(breakSound, at, 1.2F, 0.85F + run.level.getRandom().nextFloat() * 0.3F);
		Polter.noise(run, at, Math.max(40F, loud + 10F));
		run.despawn(actor);
		state = State.BROKEN;
	}

	/** It comes to rest: a real block in the cell it fell into when it can be one, else lying there as a display. */
	private void land() {
		Display d = display();
		vel = Vec3.ZERO;
		if (d == null) {
			state = State.GONE;
			return;
		}
		double fy = Polter.floorAt(run, pos.add(0, 0.3, 0), 4);
		if (Double.isNaN(fy)) {
			fy = pos.y - 0.5 * scale;
		}
		Quaternionf now = orientation();
		Vector3f fwd = now.transform(new Vector3f(0F, 0F, -1F));
		float yaw = (float) Math.atan2(-fwd.x, -fwd.z);
		if (asBlock && original != null && origin != null && settleAsBlock(fy, yaw)) {
			return;
		}
		Quaternionf rest;
		double y;
		if (item != null) {
			rest = new Quaternionf().rotationY(yaw).rotateX((float) (Math.PI / 2));
			y = fy + 0.03 * scale;
		} else if (pivot.y < 0.2F) {
			rest = new Quaternionf().rotationY(yaw);
			y = fy + pivot.y * scale;
		} else {
			// upright, upside down or on its side, whichever it is closest to, turned the way it faces now
			Vector3f up = now.transform(new Vector3f(0F, 1F, 0F));
			rest = new Quaternionf().rotationY(yaw);
			if (up.y < -0.5F) {
				rest.rotateX((float) Math.PI);
			} else if (up.y < 0.5F) {
				Vector3f right = new Quaternionf().rotationY(yaw).transform(new Vector3f(1F, 0F, 0F));
				rest.rotateZ((float) (Math.PI / 2) * (up.dot(right) > 0F ? -1F : 1F));
			}
			y = fy + 0.5 * scale;
		}
		pos = new Vec3(pos.x, y, pos.z);
		spin = new Quaternionf();
		base = rest;
		CasaProps.move(d, pos);
		CasaProps.pose(d, rest, scale, pivot, 3);
		state = State.RESTING;
	}

	/** Becomes the block it was, in the cell under it, turned to the nearest facing; false when the cell is not free. */
	private boolean settleAsBlock(double floorY, float yaw) {
		BlockPos cell = BlockPos.containing(pos.x, floorY + 0.05, pos.z);
		if (!run.level.getBlockState(cell).isAir() || CasaProps.held(run, cell)
				|| run.level.getBlockState(cell.below()).getCollisionShape(run.level, cell.below()).isEmpty()) {
			return false;
		}
		AABB box = new AABB(cell);
		for (ServerPlayer p : run.hunters()) {
			if (p.getBoundingBox().intersects(box)) {
				return false;
			}
		}
		BlockState put = original;
		if (put.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			put = put.setValue(BlockStateProperties.HORIZONTAL_FACING, nearest(yaw));
		}
		anchor = CasaProps.uid("vuela_ancla");
		if (CasaProps.block(run, anchor, Vec3.atCenterOf(cell), Blocks.AIR.defaultBlockState()) == null) {
			anchor = null;
			return false;
		}
		// both changes (the empty place it came from, the block where it fell) now hang on the invisible anchor
		CasaProps.forget(run, origin);
		CasaProps.remember(run, origin, original, List.of(anchor));
		CasaProps.remember(run, cell, run.level.getBlockState(cell), List.of(anchor));
		run.setBlock(cell, put);
		run.despawn(actor);
		landed = cell.immutable();
		state = State.RESTING;
		return true;
	}

	/** The block facing whose north-model yaw is closest to `yaw` (radians, as {@link Polter#yawRad}). */
	private static Direction nearest(float yaw) {
		Direction best = Direction.NORTH;
		double bd = Double.MAX_VALUE;
		for (Direction f : Direction.Plane.HORIZONTAL) {
			double d = Math.abs(Math.atan2(Math.sin(yaw - Polter.yawRad(f)), Math.cos(yaw - Polter.yawRad(f))));
			if (d < bd) {
				bd = d;
				best = f;
			}
		}
		return best;
	}

	/** Puts the house back: the display and the block it became go, the original block is back in its place. */
	public void restore() {
		run.despawn(actor);
		if (anchor != null) {
			run.despawn(anchor);
		}
		if (landed != null) {
			CasaProps.settleAt(run, landed);
		}
		if (origin != null) {
			CasaProps.settleAt(run, origin);
		}
		landed = null;
		anchor = null;
		state = State.GONE;
		ALL.remove(this);
	}

	/** Restores every flying prop of a run (the case is left, a set piece wants the house whole). */
	public static void clear(Run r) {
		for (FlyingProp f : new ArrayList<>(ALL)) {
			if (f.run == r || Director.get(f.run.type, f.run.site) != f.run) {
				f.restore();
			}
		}
	}

	/** Restores a list of props and empties it. */
	public static void restoreAll(List<FlyingProp> props) {
		if (props == null) {
			return;
		}
		for (FlyingProp f : props) {
			if (f != null) {
				f.restore();
			}
		}
		props.clear();
	}
}
