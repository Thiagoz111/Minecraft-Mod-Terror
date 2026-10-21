package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Exec;
import com.deadline.director.Run;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;

/**
 * Lucía's shelf of ten porcelain dolls (item displays, three variants in turn): every doll nobody is looking at turns
 * to stare at the nearest hunter (DOLL_TURN), and while nobody watches the shelf they hop down one at a time and creep
 * across the floor (they do not cross salt). You cannot watch them and Ofelia at once. A camera flash on them freezes them for 6 seconds.
 * Ticks itself through a run sequence; {@link #tick()} may also be called (once per tick).
 * Events: "munecas:piso" (one reached the floor), "munecas:toque" (one touched a hunter), "munecas:flash".
 */
public final class DollShelf {
	/** Fallback doll prop for a variant without its own item: the cursed doll's sprite. */
	public static Supplier<ItemStack> DOLL = () -> new ItemStack(ModItems.CURSED_DOLL);
	/** Relative size of each of the three doll variants (handed out in turn along the shelves). */
	private static final float[] SIZES = {1.0F, 0.84F, 1.14F};
	private static final float SCALE = 0.42F;
	private static final int SHELF = 0, HOP = 1, FLOOR = 2;
	private static final List<DollShelf> ACTIVE = new ArrayList<>();
	/** Doll seats of the three kit shelves, in pixels of the north-facing model: {x, y} (z is 10.5). */
	private static final double[][][] SLOTS = {
		{{4.6, 11.6}, {11.4, 11.6}, {4.6, 21.6}, {11.4, 21.6}},
		{{4.6, 11.6}, {11.4, 11.6}, {8.0, 21.6}},
		{{11.4, 11.6}, {4.6, 21.6}, {11.4, 21.6}},
	};

	private final Run r;
	private final List<Doll> dolls = new ArrayList<>();
	private final List<BlockPos> shelves = new ArrayList<>();
	private Vec3 center;
	private Exec exec;
	private int unseen;
	private int frozen;
	private int advanceEvery = 60;
	private int landed;
	private long lastTurnSound;
	private long lastTick = Long.MIN_VALUE;
	private boolean active;

	private static final class Doll {
		final String actor;
		final BlockPos shelf;
		final Direction front;
		final float scale;
		Vec3 pos;
		float yaw;
		float tilt;
		int state = SHELF;
		int hop;
		int step;
		int cooldown;
		Vec3 from;
		Vec3 to;

		Doll(String actor, BlockPos shelf, Direction front, Vec3 pos, float yaw, float tilt, float scale) {
			this.actor = actor;
			this.shelf = shelf;
			this.front = front;
			this.scale = scale;
			this.pos = pos;
			this.yaw = yaw;
			this.tilt = tilt;
		}
	}

	private DollShelf(Run r) {
		this.r = r;
	}

	/** Takes the dolls off the kit shelf at `shelf` and its neighbours (up to 2 blocks away, same height). */
	public static DollShelf start(Run r, BlockPos shelf) {
		List<BlockPos> around = new ArrayList<>();
		for (int dx = -2; dx <= 2; dx++) {
			for (int dz = -2; dz <= 2; dz++) {
				around.add(shelf.offset(dx, 0, dz));
			}
		}
		return begin(r, around);
	}

	/** Takes the dolls off every shelf block of a site group (e.g. "estante_munecas"). */
	public static DollShelf start(Run r, String group) {
		return begin(r, CasaProps.abs(r, group));
	}

	private static DollShelf begin(Run r, List<BlockPos> candidates) {
		CasaProps.sweep(r);  // after a chapter replay the shelves are still the empty ones until put back
		prune();
		DollShelf s = new DollShelf(r);
		for (BlockPos pos : candidates) {
			BlockState st = r.level.getBlockState(pos);
			String path = CasaProps.path(st);
			if (!path.startsWith("casa_estante_munecas_") || path.endsWith("vacio")) {
				continue;
			}
			int kind = path.endsWith("1") ? 0 : path.endsWith("2") ? 1 : 2;
			s.fill(pos.immutable(), st, SLOTS[kind]);
		}
		if (s.dolls.isEmpty()) {
			DeadLine.LOGGER.warn("DollShelf: no doll shelf found in {}", r.def.key);
			return s;
		}
		s.center = CasaProps.centroid(s.shelves).add(0, 0.6, 0);
		s.active = true;
		ACTIVE.add(s);
		s.exec = r.start("casa:munecas", r.star(), List.of(e -> {
			s.tick();
			return !s.active;
		}));
		return s;
	}

	private void fill(BlockPos pos, BlockState st, double[][] slots) {
		Direction f = CasaProps.facing(st);
		List<String> actors = new ArrayList<>();
		Vec3 corner = Vec3.atLowerCornerOf(pos);
		for (double[] slot : slots) {
			String actor = CasaProps.uid("muneca");
			int v = dolls.size() % SIZES.length;
			float scale = SCALE * SIZES[v];
			Vec3 at = corner.add(CasaProps.local(f, slot[0], slot[1], 10.5)).add(0, scale * 0.5, 0);
			float yaw = (float) (Math.atan2(f.getStepX(), f.getStepZ()) + CasaProps.rnd(r.level, 0.6));
			float tilt = (float) CasaProps.rnd(r.level, 0.2);
			Display.ItemDisplay d = CasaProps.item(r, actor, at, doll(v));
			if (d == null) {
				continue;
			}
			CasaProps.pose(d, new Quaternionf().rotationY(yaw).rotateZ(tilt), scale, CasaProps.ZERO, 0);
			dolls.add(new Doll(actor, pos, f, at, yaw, tilt, scale));
			actors.add(actor);
		}
		shelves.add(pos);
		CasaProps.swap(r, pos, CasaProps.kit("casa_estante_munecas_vacio", st), actors);
	}

	/** Doll variant 0..2: its own item ("casa_muneca_1".."casa_muneca_3") once one exists, else {@link #DOLL}. */
	private static ItemStack doll(int variant) {
		Item it = BuiltInRegistries.ITEM.getOptional(DeadLine.id("casa_muneca_" + (variant + 1))).orElse(null);
		return it != null ? new ItemStack(it) : DOLL.get();
	}

	/** Ticks of nobody watching the shelf before the next doll hops down (default 60). */
	public DollShelf advanceEvery(int ticks) {
		this.advanceEvery = Math.max(10, ticks);
		return this;
	}

	/** The camera flash: nothing moves for `ticks`. */
	public void freeze(int ticks) {
		frozen = Math.max(frozen, ticks);
		for (Doll d : dolls) {
			r.level.sendParticles(ModParticles.HOLY_SPARK, d.pos.x, d.pos.y, d.pos.z, 4, 0.1, 0.15, 0.1, 0.02);
		}
	}

	public int onFloor() {
		return landed;
	}

	public int onShelf() {
		int n = 0;
		for (Doll d : dolls) {
			if (d.state == SHELF) {
				n++;
			}
		}
		return n;
	}

	public boolean active() {
		return active;
	}

	/** Ofelia is purified: the dolls go limp where they are (the ones on the floor fall over) and stay. */
	public void stop() {
		if (!active) {
			return;
		}
		active = false;
		ACTIVE.remove(this);
		if (exec != null) {
			exec.cancel();
		}
		for (Doll d : dolls) {
			Display.ItemDisplay e = display(d);
			if (e == null) {
				continue;
			}
			if (d.state == SHELF) {
				CasaProps.pose(e, new Quaternionf().rotationY(d.yaw).rotateX(0.45F), d.scale, CasaProps.ZERO, 6);
			} else {
				d.pos = new Vec3(d.to.x, d.to.y - d.scale * 0.5 + 0.03, d.to.z);
				CasaProps.move(e, d.pos);
				CasaProps.pose(e, new Quaternionf().rotationY(d.yaw).rotateX((float) (Math.PI / 2)), d.scale, CasaProps.ZERO, 4);
			}
		}
	}

	/** Removes the dolls and puts the full shelves back. */
	public void clear() {
		stop();
		for (Doll d : dolls) {
			r.despawn(d.actor);
		}
		for (BlockPos p : shelves) {
			CasaProps.settleAt(r, p);
		}
	}

	public void tick() {
		if (!active || lastTick == r.now()) {
			return;
		}
		lastTick = r.now();
		if (gone()) {
			active = false;  // removed from outside (a chapter replay, the case ending): nothing left to move
			ACTIVE.remove(this);
			return;
		}
		if (frozen > 0) {
			frozen--;
		}
		for (Doll d : dolls) {
			if (d.state == HOP) {
				hopTick(d);
			}
		}
		if (r.now() % 2 != 0 || r.hunters().isEmpty()) {
			return;
		}
		boolean shelfSeen = CasaProps.seen(r, center, 45F, 40);
		Vec3 turnedAt = null;
		for (Doll d : dolls) {
			Display.ItemDisplay e = display(d);
			if (d.state == HOP || e == null) {
				continue;
			}
			if (d.cooldown > 0) {
				d.cooldown -= 2;
			}
			if (frozen > 0 || CasaProps.seen(r, d.pos, 45F, 40)) {
				continue;
			}
			ServerPlayer p = CasaProps.nearest(r, d.pos);
			if (p == null) {
				continue;
			}
			Vec3 eye = p.getEyePosition();
			float want = (float) Math.atan2(eye.x - d.pos.x, eye.z - d.pos.z);
			if (Math.abs(wrap(want - d.yaw)) > 0.25F || d.tilt != 0F) {
				d.yaw = want;
				d.tilt = 0F;
				CasaProps.pose(e, new Quaternionf().rotationY(want), d.scale, CasaProps.ZERO, 3);
				turnedAt = d.pos;
			}
			if (d.state == FLOOR) {
				creep(d, e, p);
			}
		}
		if (turnedAt != null && r.now() - lastTurnSound > 14) {
			lastTurnSound = r.now();
			r.sound(ModSounds.DOLL_TURN, turnedAt, 0.9F, 0.9F + r.level.random.nextFloat() * 0.3F);
		}
		if (shelfSeen || frozen > 0) {
			unseen = 0;
		} else if ((unseen += 2) >= advanceEvery) {
			unseen = 0;
			hopNext();
		}
	}

	private static float wrap(float a) {
		while (a > Math.PI) {
			a -= (float) (Math.PI * 2);
		}
		while (a < -Math.PI) {
			a += (float) (Math.PI * 2);
		}
		return a;
	}

	private Display.ItemDisplay display(Doll d) {
		return r.actor(d.actor) instanceof Display.ItemDisplay e ? e : null;
	}

	/** Every doll display is gone. */
	private boolean gone() {
		for (Doll d : dolls) {
			if (display(d) != null) {
				return false;
			}
		}
		return true;
	}

	/** Forgets shelves that stopped, whose run is over or whose dolls a chapter replay removed (their sequence is gone). */
	private static void prune() {
		ACTIVE.removeIf(s -> {
			if (s.active && Director.get(s.r.type, s.r.site) == s.r && !s.gone()) {
				return false;
			}
			s.active = false;
			return true;
		});
	}

	private void hopNext() {
		List<Doll> left = new ArrayList<>();
		for (Doll d : dolls) {
			if (d.state == SHELF && display(d) != null) {
				left.add(d);
			}
		}
		if (left.isEmpty()) {
			return;
		}
		Doll d = left.get(r.level.random.nextInt(left.size()));
		Direction f = d.front;
		Direction side = f.getClockWise();
		Vec3 base = Vec3.atBottomCenterOf(d.shelf);
		double out = 1.1 + r.level.random.nextDouble() * 0.9;
		double lat = CasaProps.rnd(r.level, 0.8);
		Vec3 target = base.add(f.getStepX() * out + side.getStepX() * lat, d.scale * 0.5, f.getStepZ() * out + side.getStepZ() * lat);
		if (!CasaProps.passable(r.level, target)) {
			target = base.add(f.getStepX() * 1.0, d.scale * 0.5, f.getStepZ() * 1.0);
		}
		d.state = HOP;
		d.hop = 0;
		d.from = d.pos;
		d.to = target;
		r.sound(ModSounds.MUNECA_CREAK, d.pos, 0.9F, 1.2F);
	}

	private void hopTick(Doll d) {
		Display.ItemDisplay e = display(d);
		if (e == null) {
			d.state = FLOOR;
			return;
		}
		d.hop++;
		double u = Math.min(1.0, d.hop / 10.0);
		d.pos = d.from.lerp(d.to, u).add(0, 0.7 * 4 * u * (1 - u), 0);
		CasaProps.move(e, d.pos);
		if (u >= 1) {
			d.state = FLOOR;
			d.pos = d.to;
			landed++;
			r.sound(ModSounds.MUNECA_CREAK, d.pos, 1.0F, 1.4F);
			r.post("munecas:piso");
			if (landed == 1 || onShelf() == 0) {
				r.sound(ModSounds.DOLL_GIGGLE_CHORUS, center, 1.3F, 1.0F);
			}
		}
	}

	private void creep(Doll d, Display.ItemDisplay e, ServerPlayer p) {
		d.step += 2;
		if (d.step < 24) {
			return;
		}
		d.step = 0;
		Vec3 flat = new Vec3(p.getX() - d.pos.x, 0, p.getZ() - d.pos.z);
		double dist = flat.length();
		if (dist < 0.01) {
			return;
		}
		Vec3 dir = flat.scale(1 / dist);
		if (dist <= 1.4) {
			if (d.cooldown <= 0) {
				touch(d, e, p, dir);
			}
			return;
		}
		Vec3 dest = d.pos.add(dir.scale(0.45));
		if (CasaProps.passable(r.level, dest) && !CasaProps.saltAt(r.level, dest) && !CasaProps.saltAt(r.level, d.pos.lerp(dest, 0.5))) {
			d.pos = dest;
			d.to = dest;
			CasaProps.move(e, dest);
		}
	}

	private void touch(Doll d, Display.ItemDisplay e, ServerPlayer p, Vec3 dir) {
		d.cooldown = 60;
		SanityManager.add(p, -5F);
		Fx.redFlash(p, 0.35F);
		Fx.shake(p, 0.3F, 6);
		r.sound(ModSounds.MUNECA_GIGGLE, d.pos, 1.2F, 1.1F);
		r.post("munecas:toque");
		Vec3 back = d.pos.subtract(dir.scale(2.0));
		if (CasaProps.passable(r.level, back) && !CasaProps.saltAt(r.level, back)) {
			d.pos = back;
			d.to = back;
			CasaProps.move(e, back);
		}
	}

	/** Camera flash by a hunter (from the item-use hook): freezes a shelf with a doll in frame within 18 blocks. */
	static void onFlash(ServerPlayer p) {
		prune();
		for (DollShelf s : new ArrayList<>(ACTIVE)) {
			if (s.r.level != p.level()) {
				continue;
			}
			for (Doll d : s.dolls) {
				if (s.display(d) != null && s.r.looking(p, d.pos, 42F, 18)) {
					s.freeze(120);
					s.r.post("munecas:flash");
					break;
				}
			}
		}
	}

	static void clearAll() {
		ACTIVE.clear();
	}
}
