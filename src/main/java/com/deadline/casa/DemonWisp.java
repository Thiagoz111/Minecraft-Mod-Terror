package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.site.Fixtures;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Azamel's wisp: an invisible entity with no model that travels a Catmull-Rom curve trailing black smoke and embers with
 * a whistle, making the lamps it passes flicker. It can hesitate between two points and dive into a mouth. Never saved.
 * Events (when attached to a run): "voluta:llego", "voluta:duda", "voluta:entro".
 */
public class DemonWisp extends Entity {
	private static final int IDLE = 0, FLY = 1, HOVER = 2, ENTER = 3;
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;

	private int mode = IDLE;
	private int t;
	private int duration;
	private Vec3[] path;
	private double[] cum;
	private Vec3 anchor;
	private Vec3 other;
	private Vec3 enterFrom;
	private Entity host;
	private Consumer<DemonWisp> onDone;
	private Run run;
	private int idle;
	private int whistle;
	private final Map<BlockPos, Flick> flicker = new HashMap<>();

	private record Flick(BlockState lit, BlockState dark, int until) {
	}

	public DemonWisp(EntityType<? extends DemonWisp> type, Level level) {
		super(type, level);
		this.noPhysics = true;
		this.setNoGravity(true);
	}

	// ------------------------------------------------------------------ API
	/** A wisp that bursts out of nothing at a point and waits there (Choripán's vomit). */
	public static DemonWisp spawn(ServerLevel level, Vec3 at) {
		DemonWisp w = CasaSetEntities.DEMON_WISP.create(level, EntitySpawnReason.EVENT);
		if (w == null) {
			return null;
		}
		w.snapTo(at.x, at.y, at.z, 0F, 0F);
		w.anchor = at;
		level.addFreshEntity(w);
		level.sendParticles(ModParticles.DEMON_SMOKE, at.x, at.y, at.z, 30, 0.25, 0.25, 0.25, 0.03);
		level.sendParticles(ParticleTypes.LARGE_SMOKE, at.x, at.y, at.z, 12, 0.2, 0.2, 0.2, 0.02);
		return w;
	}

	/** Spawns a wisp on the first point and flies it along the curve in `ticks`; onArrive (may be null) runs at the end. */
	public static DemonWisp fly(ServerLevel level, List<Vec3> path, int ticks, Consumer<DemonWisp> onArrive) {
		if (path.isEmpty()) {
			return null;
		}
		DemonWisp w = spawn(level, path.get(0));
		if (w != null) {
			w.follow(new ArrayList<>(path), ticks, onArrive);
		}
		return w;
	}

	/** Same, registered as a run actor (removed on a chapter replay) and posting its events to the run. */
	public static DemonWisp fly(Run r, String actor, List<Vec3> path, int ticks, Consumer<DemonWisp> onArrive) {
		DemonWisp w = fly(r.level, path, ticks, onArrive);
		if (w != null) {
			w.attach(r, actor);
		}
		return w;
	}

	/** The wisp closest to a point within a radius (to pick up the one Choripán spat out), or null. */
	public static DemonWisp nearest(ServerLevel level, Vec3 at, double radius) {
		DemonWisp best = null;
		double bd = Double.MAX_VALUE;
		for (DemonWisp w : level.getEntitiesOfClass(DemonWisp.class, new AABB(at, at).inflate(radius))) {
			double d = w.position().distanceToSqr(at);
			if (!w.isRemoved() && d < bd) {
				bd = d;
				best = w;
			}
		}
		return best;
	}

	/** Registers the wisp as a run actor and posts its events there. */
	public DemonWisp attach(Run r, String actor) {
		this.run = r;
		if (actor != null) {
			r.actor(actor, this);
		}
		return this;
	}

	/** Flies from where it is through the points in `ticks`. */
	public void flyTo(List<Vec3> points, int ticks, Consumer<DemonWisp> onArrive) {
		List<Vec3> p = new ArrayList<>();
		p.add(this.position());
		p.addAll(points);
		follow(p, ticks, onArrive);
	}

	/** Hesitates for `ticks`, darting from where it is toward `other` and back ("dudando"). */
	public void hover(Vec3 other, int ticks) {
		hover(other, ticks, null);
	}

	public void hover(Vec3 other, int ticks, Consumer<DemonWisp> onDone) {
		this.anchor = this.position();
		this.other = other;
		this.duration = Math.max(1, ticks);
		this.t = 0;
		this.mode = HOVER;
		this.onDone = onDone;
	}

	/** Dives into an entity's mouth (smoke streaming into the head) and disappears; the wisp is discarded after. */
	public void enter(Entity host) {
		enter(host, null);
	}

	public void enter(Entity host, Consumer<DemonWisp> onEnter) {
		if (host == null) {
			return;
		}
		this.host = host;
		this.enterFrom = this.position();
		this.duration = (int) Math.max(12, Math.min(30, this.position().distanceTo(mouth(host)) * 3));
		this.t = 0;
		this.mode = ENTER;
		this.onDone = onEnter;
		this.whistle = 0;
	}

	/** Moving (flying, hesitating or diving). */
	public boolean busy() {
		return mode != IDLE;
	}

	// ------------------------------------------------------------------ motion
	private void follow(List<Vec3> points, int ticks, Consumer<DemonWisp> done) {
		this.path = points.toArray(new Vec3[0]);
		this.cum = new double[path.length];
		for (int i = 1; i < path.length; i++) {
			cum[i] = cum[i - 1] + path[i].distanceTo(path[i - 1]);
		}
		this.duration = Math.max(1, ticks);
		this.t = 0;
		this.mode = FLY;
		this.onDone = done;
		this.whistle = 0;
	}

	/** A point at fraction u of the curve's length (uniform Catmull-Rom through every point). */
	private Vec3 along(double u) {
		int n = path.length;
		if (n == 1 || cum[n - 1] <= 1e-6) {
			return path[n - 1];
		}
		double target = u * cum[n - 1];
		int i = 0;
		while (i < n - 2 && cum[i + 1] < target) {
			i++;
		}
		double len = cum[i + 1] - cum[i];
		double s = len <= 1e-6 ? 0 : Math.min(1.0, Math.max(0.0, (target - cum[i]) / len));
		return catmull(path[Math.max(0, i - 1)], path[i], path[i + 1], path[Math.min(n - 1, i + 2)], s);
	}

	private static Vec3 catmull(Vec3 p0, Vec3 p1, Vec3 p2, Vec3 p3, double t) {
		double t2 = t * t;
		double t3 = t2 * t;
		return new Vec3(cr(p0.x, p1.x, p2.x, p3.x, t, t2, t3), cr(p0.y, p1.y, p2.y, p3.y, t, t2, t3), cr(p0.z, p1.z, p2.z, p3.z, t, t2, t3));
	}

	private static double cr(double a, double b, double c, double d, double t, double t2, double t3) {
		return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
	}

	private static Vec3 mouth(Entity e) {
		Vec3 look = e.getLookAngle();
		return e.getEyePosition().add(look.x * 0.25, -0.12, look.z * 0.25);
	}

	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		Vec3 before = this.position();
		switch (mode) {
			case FLY -> tickFly();
			case HOVER -> tickHover();
			case ENTER -> tickEnter(level);
			default -> tickIdle();
		}
		if (this.isRemoved()) {
			return;
		}
		trail(level, before, this.position());
		tickFlicker(level);
		if (--whistle <= 0) {
			boolean moving = mode != IDLE;
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.WISP_WHISTLE, SoundSource.HOSTILE,
					moving ? 1.3F : 0.6F, 0.9F + this.random.nextFloat() * 0.25F);
			whistle = moving ? 45 : 120;
		}
	}

	private void tickFly() {
		t++;
		double u = Math.min(1.0, t / (double) duration);
		double k = 0.5 * u + 0.5 * CasaProps.ease(u);
		Vec3 p = along(k);
		this.setPos(p.x, p.y, p.z);
		if (u >= 1) {
			mode = IDLE;
			anchor = p;
			idle = 0;
			finish("voluta:llego");
		}
	}

	private void tickHover() {
		t++;
		double ph = t * 0.09 + Math.sin(t * 0.031) * 1.7;
		double f = (0.5 - 0.5 * Math.cos(ph)) * 0.8;
		Vec3 p = anchor.lerp(other, f).add(0, 0.1 * Math.sin(t * 0.2), 0);
		this.setPos(p.x, p.y, p.z);
		if (t >= duration) {
			mode = IDLE;
			anchor = p;
			idle = 0;
			finish("voluta:duda");
		}
	}

	private void tickEnter(ServerLevel level) {
		if (host == null || host.isRemoved()) {
			mode = IDLE;
			anchor = this.position();
			return;
		}
		t++;
		Vec3 target = mouth(host);
		double u = Math.min(1.0, t / (double) duration);
		Vec3 ctrl = enterFrom.lerp(target, 0.5).add(0, 0.8, 0);
		double v = 1 - u;
		Vec3 p = enterFrom.scale(v * v).add(ctrl.scale(2 * v * u)).add(target.scale(u * u));
		this.setPos(p.x, p.y, p.z);
		Vec3 dir = target.subtract(p);
		for (int i = 0; i < 3; i++) {
			level.sendParticles(ModParticles.DEMON_SMOKE, p.x + CasaProps.rnd(level, 0.1), p.y + CasaProps.rnd(level, 0.1), p.z + CasaProps.rnd(level, 0.1),
					0, dir.x, dir.y, dir.z, 0.18);
		}
		if (u >= 1) {
			level.sendParticles(ModParticles.DEMON_SMOKE, target.x, target.y, target.z, 30, 0.12, 0.12, 0.12, 0.02);
			level.sendParticles(ParticleTypes.LARGE_SMOKE, target.x, target.y, target.z, 10, 0.1, 0.1, 0.1, 0.01);
			level.playSound(null, target.x, target.y, target.z, ModSounds.WISP_WHISTLE, SoundSource.HOSTILE, 1.6F, 0.5F);
			finish("voluta:entro");
			this.discard();
		}
	}

	private void tickIdle() {
		if (anchor == null) {
			anchor = this.position();
		}
		idle++;
		double a = this.tickCount * 0.11;
		this.setPos(anchor.x + Math.cos(a) * 0.08, anchor.y + 0.12 * Math.sin(this.tickCount * 0.15), anchor.z + Math.sin(a) * 0.08);
		if (run == null && idle > 2400) {
			this.discard();  // nobody claimed it
		}
	}

	private void finish(String event) {
		Consumer<DemonWisp> c = onDone;
		onDone = null;
		if (run != null) {
			run.post(event);
		}
		if (c != null) {
			try {
				c.accept(this);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Demon wisp callback failed", ex);
			}
		}
	}

	// ------------------------------------------------------------------ effects
	private void trail(ServerLevel level, Vec3 a, Vec3 b) {
		boolean moving = mode != IDLE;
		if (!moving && this.tickCount % 2 != 0) {
			return;
		}
		double dist = a.distanceTo(b);
		int n = Math.min(4, 1 + (int) (dist / 0.35));
		for (int i = 1; i <= n; i++) {
			Vec3 p = a.lerp(b, i / (double) n);
			level.sendParticles(ModParticles.DEMON_SMOKE, p.x, p.y, p.z, moving ? 2 : 1, 0.06, 0.06, 0.06, 0.008);
			if (this.random.nextInt(3) == 0) {
				level.sendParticles(ParticleTypes.LARGE_SMOKE, p.x, p.y, p.z, 1, 0.04, 0.04, 0.04, 0.01);
			}
			if (this.random.nextInt(2) == 0) {
				level.sendParticles(new DustParticleOptions(0xFF5A1E, 0.8F), p.x, p.y, p.z, 1, 0.1, 0.1, 0.1, 0.0);
			}
			if (moving && this.random.nextInt(7) == 0) {
				level.sendParticles(ParticleTypes.SMALL_FLAME, p.x, p.y, p.z, 1, 0.05, 0.05, 0.05, 0.005);
			}
		}
	}

	/** Lamps near a moving wisp go dark for a few ticks (kit fixtures with a dark form; not invisible light blocks). */
	private void tickFlicker(ServerLevel level) {
		int now = this.tickCount;
		for (Iterator<Map.Entry<BlockPos, Flick>> it = flicker.entrySet().iterator(); it.hasNext(); ) {
			Map.Entry<BlockPos, Flick> en = it.next();
			if (now >= en.getValue().until()) {
				relight(level, en.getKey(), en.getValue());
				it.remove();
			}
		}
		if (mode == IDLE || now % 4 != 0 || flicker.size() >= 6 || HauntEntity.SHOWCASE) {
			return;
		}
		BlockPos c = this.blockPosition();
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-2, -2, -2), c.offset(2, 2, 2))) {
			BlockState s = level.getBlockState(p);
			if (s.isAir() || s.is(Blocks.LIGHT) || flicker.containsKey(p) || this.random.nextInt(3) != 0) {
				continue;
			}
			BlockState dark = Fixtures.dark(s);
			if (dark == null || dark == s) {
				continue;
			}
			BlockPos k = p.immutable();
			flicker.put(k, new Flick(s, dark, now + 3 + this.random.nextInt(6)));
			level.setBlock(k, dark, FLAGS);
			if (flicker.size() >= 6) {
				break;
			}
		}
	}

	private static void relight(ServerLevel level, BlockPos pos, Flick f) {
		if (level.getBlockState(pos) == f.dark()) {
			level.setBlock(pos, f.lit(), FLAGS);
		}
	}

	@Override
	public void remove(RemovalReason reason) {
		if (this.level() instanceof ServerLevel level) {
			flicker.forEach((pos, f) -> relight(level, pos, f));
			flicker.clear();
		}
		super.remove(reason);
	}

	// ------------------------------------------------------------------ entity plumbing
	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPickable() {
		return false;
	}

	@Override
	public boolean shouldBeSaved() {
		return false;
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
	}
}
