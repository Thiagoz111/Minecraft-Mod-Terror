package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Exec;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.net.Fx;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * Jorge's six asado knives: they lift off the rack (KNIFE_LIFT), orbit around the holder and fly at a target one at a
 * time (KNIFE_WHOOSH; 3 damage on a hunter, KNIFE_IMPACT and stuck in a wall). A knife that crosses a salt line drops
 * to the floor as an item. Ticks itself through a run sequence; {@link #tick()} may also be called (once per tick).
 * Events: "cuchillo:lanzado", "cuchillo:golpe", "cuchillo:clavado", "cuchillo:sal", "cuchillos:fin".
 */
public final class KnifeOrbit {
	public static final int KNIVES = 6;
	private static final int LIFT = 0, ORBIT = 1, AIM = 2, FLY = 3, STUCK = 4, GONE = 5;
	private static final Vector3f PIVOT = new Vector3f(0.5F, 0.03F, 0.5F);
	private static final float ROLL = (float) (Math.PI / 2);
	private static final double RADIUS = 1.6, SPEED = 1.05;

	private final Run r;
	private final Entity holder;
	private final BlockPos rack;
	private final Knife[] knives = new Knife[KNIVES];
	private Exec exec;
	private int t;
	private int auto;
	private int autoTimer;
	private long lastTick = Long.MIN_VALUE;
	private boolean active;
	private boolean finished;

	private static final class Knife {
		final String actor;
		final int index;
		int state = LIFT;
		int t;
		Vec3 pos;
		Vec3 from;
		Vec3 vel;
		Vec3 dir;
		Entity target;

		Knife(String actor, int index, Vec3 pos) {
			this.actor = actor;
			this.index = index;
			this.pos = pos;
			this.from = pos;
		}
	}

	private KnifeOrbit(Run r, Entity holder, BlockPos rack) {
		this.r = r;
		this.holder = holder;
		this.rack = rack.immutable();
	}

	/** Lifts the knives off the rack block (swapped to its empty version) and sets them orbiting the holder. */
	public static KnifeOrbit start(Run r, Entity holder, BlockPos rack) {
		KnifeOrbit k = new KnifeOrbit(r, holder, rack);
		k.begin();
		return k;
	}

	private void begin() {
		CasaProps.sweep(r);  // after a chapter replay the rack may still be the empty one until the guard runs
		BlockState rs = r.level.getBlockState(rack);
		Direction f = CasaProps.facing(rs);
		Direction side = f.getClockWise();
		Vec3 c = Vec3.atBottomCenterOf(rack).add(-f.getStepX() * 0.3, 0.45, -f.getStepZ() * 0.3);
		BlockState knife = CasaProps.kitOr("casa_cuchillo", Blocks.TRIPWIRE_HOOK.defaultBlockState());
		List<String> actors = new ArrayList<>();
		for (int i = 0; i < KNIVES; i++) {
			String actor = CasaProps.uid("cuchillo");
			double off = (i - 2.5) * 0.12;
			Vec3 p = c.add(side.getStepX() * off, 0, side.getStepZ() * off);
			Display.BlockDisplay d = CasaProps.block(r, actor, p, knife);
			CasaProps.pose(d, CasaProps.alongX(new Vec3(0, -1, 0), ROLL), 1F, PIVOT, 0);
			knives[i] = new Knife(actor, i, p);
			actors.add(actor);
		}
		if (CasaProps.path(rs).equals("casa_cuchillos")) {
			CasaProps.swap(r, rack, CasaProps.kit("casa_cuchillos_vacio", rs), actors);
		}
		r.sound(ModSounds.KNIFE_LIFT, c, 1.4F, 1.0F);
		active = true;
		exec = r.start("casa:cuchillos", r.star(), List.of(e -> {
			tick();
			return !active;
		}));
	}

	/** Launches one orbiting knife (the lowest still circling) at a target; false when none is ready. */
	public boolean launch(Entity target) {
		if (!active || target == null) {
			return false;
		}
		for (Knife k : knives) {
			if (k != null && k.state == ORBIT) {
				k.state = AIM;
				k.t = 0;
				k.target = target;
				k.from = k.pos;
				return true;
			}
		}
		return false;
	}

	/** Launches a knife at the nearest visible hunter every `every` ticks by itself (0 turns it off). */
	public KnifeOrbit autoLaunch(int every) {
		this.auto = Math.max(0, every);
		this.autoTimer = this.auto;
		return this;
	}

	/** Knives not launched yet (lifting, orbiting or aiming). */
	public int remaining() {
		int n = 0;
		for (Knife k : knives) {
			if (k != null && k.state <= AIM) {
				n++;
			}
		}
		return n;
	}

	public boolean active() {
		return active;
	}

	/** The holder is freed: every knife still in the air clatters to the floor (the ones stuck in walls stay). */
	public void stop() {
		for (Knife k : knives) {
			if (k != null && k.state <= FLY) {
				drop(k, k.pos);
			}
		}
		active = false;
		finished = true;
		if (exec != null) {
			exec.cancel();
		}
	}

	/** Removes every knife (stuck or dropped too) and puts the full rack back. */
	public void clear() {
		stop();
		for (Knife k : knives) {
			if (k != null) {
				r.despawn(k.actor);
			}
		}
		CasaProps.settleAt(r, rack);
	}

	public void tick() {
		if (!active || lastTick == r.now()) {
			return;
		}
		lastTick = r.now();
		t++;
		if (holder == null || holder.isRemoved()) {
			stop();
			return;
		}
		Vec3 center = holder.position().add(0, holder.getBbHeight() * 0.9, 0);
		boolean busy = false;
		for (Knife k : knives) {
			if (k == null) {
				continue;
			}
			Display d = r.actor(k.actor) instanceof Display.BlockDisplay bd ? bd : null;
			if (d == null) {
				if (k.state <= FLY) {
					k.state = GONE;
				}
				continue;
			}
			switch (k.state) {
				case LIFT -> lift(k, d, center);
				case ORBIT -> orbit(k, d, center);
				case AIM -> aim(k, d, center);
				case FLY -> fly(k, d);
				case STUCK -> quiver(k, d);
				default -> {
				}
			}
			if (k.state <= FLY) {
				busy = true;
			}
		}
		if (auto > 0 && --autoTimer <= 0) {
			autoTimer = auto;
			ServerPlayer p = visibleHunter(center);
			if (p != null) {
				launch(p);
			}
		}
		if (!busy && !finished) {
			finished = true;
			active = false;
			r.post("cuchillos:fin");
		}
	}

	private Vec3 slot(int i, Vec3 center) {
		double a = t * 0.09 + i * (Math.PI * 2 / KNIVES);
		return center.add(Math.cos(a) * RADIUS, 0.12 * Math.sin(t * 0.13 + i), Math.sin(a) * RADIUS);
	}

	private void lift(Knife k, Display d, Vec3 center) {
		k.t++;
		int delay = k.index * 4;
		if (k.t <= delay) {
			return;
		}
		double u = Math.min(1.0, (k.t - delay) / 20.0);
		double e = CasaProps.ease(u);
		Vec3 slot = slot(k.index, center);
		k.pos = k.from.lerp(slot, e).add(0, Math.sin(u * Math.PI) * 0.8, 0);
		CasaProps.move(d, k.pos);
		if (k.t % 2 == 0 || u >= 1) {
			Vec3 out = slot.subtract(center).normalize();
			CasaProps.pose(d, CasaProps.alongX(new Vec3(0, -1, 0).lerp(out, e), ROLL), 1F, PIVOT, 2);
		}
		if (u >= 1) {
			k.state = ORBIT;
			k.t = 0;
		}
	}

	private void orbit(Knife k, Display d, Vec3 center) {
		k.pos = slot(k.index, center);
		CasaProps.move(d, k.pos);
		if (t % 2 == 0) {
			CasaProps.pose(d, CasaProps.alongX(k.pos.subtract(center).add(0, -0.15, 0), ROLL), 1F, PIVOT, 2);
		}
		if (t % 30 == k.index * 5) {
			r.sound(ModSounds.KNIFE_WHOOSH, k.pos, 0.35F, 1.5F);
		}
	}

	private void aim(Knife k, Display d, Vec3 center) {
		k.t++;
		Entity tg = k.target;
		if (tg == null || tg.isRemoved()) {
			k.state = ORBIT;
			return;
		}
		Vec3 aimAt = tg.getBoundingBox().getCenter().add(0, tg.getBbHeight() * 0.15, 0);
		Vec3 to = aimAt.subtract(center).normalize();
		Vec3 hold = center.add(to.scale(1.2)).add(0, 0.2, 0);
		double u = Math.min(1.0, k.t / 8.0);
		k.pos = k.from.lerp(hold, CasaProps.ease(u)).add(CasaProps.rnd(r.level, 0.03), CasaProps.rnd(r.level, 0.03), CasaProps.rnd(r.level, 0.03));
		CasaProps.move(d, k.pos);
		Vec3 dir = aimAt.subtract(k.pos);
		CasaProps.pose(d, CasaProps.alongX(dir, ROLL), 1F, PIVOT, 1);
		if (k.t >= 10) {
			k.vel = dir.normalize().scale(SPEED);
			k.dir = dir.normalize();
			k.state = FLY;
			k.t = 0;
			r.sound(ModSounds.KNIFE_WHOOSH, k.pos, 1.3F, 0.9F + r.level.random.nextFloat() * 0.2F);
			r.post("cuchillo:lanzado");
		}
	}

	private void fly(Knife k, Display d) {
		k.t++;
		Vec3 p0 = k.pos;
		Vec3 p1 = p0.add(k.vel);
		for (int s = 1; s <= 4; s++) {
			Vec3 q = p0.lerp(p1, s / 4.0);
			if (CasaProps.saltAt(r.level, q)) {
				r.level.sendParticles(ModParticles.SALT_SPARKLE, q.x, q.y, q.z, 12, 0.15, 0.15, 0.15, 0.05);
				drop(k, q);
				r.post("cuchillo:sal");
				return;
			}
		}
		for (ServerPlayer p : r.hunters()) {
			if (p != holder && !p.isSpectator() && p.getBoundingBox().inflate(0.15).clip(p0, p1).isPresent()) {
				p.hurtServer(r.level, r.level.damageSources().magic(), 3.0F);
				Fx.shake(p, 0.5F, 8);
				Fx.redFlash(p, 0.5F);
				SanityManager.add(p, -3F);
				r.sound(ModSounds.KNIFE_IMPACT, p.position().add(0, 1, 0), 1.2F, 1.3F);
				drop(k, p.position().add(0, 0.6, 0));
				r.post("cuchillo:golpe");
				return;
			}
		}
		BlockHitResult hit = r.level.clip(new ClipContext(p0, p1, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, d));
		if (hit.getType() != HitResult.Type.MISS) {
			k.pos = hit.getLocation().subtract(k.dir.scale(0.32));
			CasaProps.move(d, k.pos);
			k.state = STUCK;
			k.t = 0;
			r.sound(ModSounds.KNIFE_IMPACT, hit.getLocation(), 1.4F, 0.9F + r.level.random.nextFloat() * 0.2F);
			r.post("cuchillo:clavado");
			return;
		}
		k.pos = p1;
		CasaProps.move(d, p1);
		if (k.t > 40) {
			drop(k, p1);
		}
	}

	private void quiver(Knife k, Display d) {
		k.t++;
		if (k.t <= 8 && k.dir != null) {
			double a = (8 - k.t) * 0.012;
			Vec3 wob = k.dir.add(CasaProps.rnd(r.level, a), CasaProps.rnd(r.level, a), CasaProps.rnd(r.level, a));
			CasaProps.pose(d, CasaProps.alongX(wob, ROLL), 1F, PIVOT, 1);
		}
	}

	/** The knife falls as an item that cannot be picked up (same actor name, so a replay removes it). */
	private void drop(Knife k, Vec3 at) {
		k.state = GONE;
		ItemStack stack = new ItemStack(BuiltInRegistries.ITEM.getValue(DeadLine.id("casa_cuchillo")));
		if (stack.isEmpty() || at == null) {
			r.despawn(k.actor);
			return;
		}
		ItemEntity it = new ItemEntity(r.level, at.x, at.y, at.z, stack);
		it.setPickUpDelay(32767);
		it.setDeltaMovement(CasaProps.rnd(r.level, 0.08), 0.05, CasaProps.rnd(r.level, 0.08));
		it.addTag(Props.ACTOR_TAG);
		r.level.addFreshEntity(it);
		r.actor(k.actor, it);
		r.sound(ModSounds.KNIFE_IMPACT, at, 0.6F, 1.5F);
	}

	private ServerPlayer visibleHunter(Vec3 from) {
		ServerPlayer best = null;
		double bd = 18 * 18;
		for (ServerPlayer p : r.hunters()) {
			double d = p.getEyePosition().distanceToSqr(from);
			if (p.isSpectator() || d >= bd) {
				continue;
			}
			BlockHitResult hit = r.level.clip(new ClipContext(from, p.getEyePosition(), ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, holder));
			if (hit.getType() == HitResult.Type.MISS) {
				bd = d;
				best = p;
			}
		}
		return best;
	}
}
