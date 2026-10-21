package com.deadline.casa;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.entity.FlareEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * The Nona's red yarn: threads of red wool (block displays scaled to 0.05 x 0.05 x length) shot from an anchor across
 * the room. Touching one snags you for 2 seconds and costs 8 sanity (YARN_TWANG); a swing or right click of the silver
 * dagger cuts the thread in the crosshair, and a flare burns any thread it touches (YARN_SNAP).
 * Events (when cast for a run): "lana:engancho", "lana:cortada", "lana:quemada", and "lana:fin" once the last thread is
 * cut or burnt. A web {@link #clear}ed, or whose threads were removed from outside (a chapter replay, the case ending),
 * ends silently.
 */
public final class YarnWeb {
	private static final List<YarnWeb> ACTIVE = new ArrayList<>();
	private static final Map<UUID, Float> SWING = new HashMap<>();
	private static final float THICK = 0.05F;
	private static final Vector3f AXIS = new Vector3f(0.5F, 0.5F, 0F);
	private static final double TOUCH = 0.32, REACH = 4.5;

	private final ServerLevel level;
	private final Run run;
	private final List<Seg> segs = new ArrayList<>();
	private final Map<UUID, Hook> hooks = new HashMap<>();
	private final Map<UUID, Integer> free = new HashMap<>();
	private AABB bounds;
	private int age;
	private boolean ended;

	private static final class Seg {
		final Vec3 a;
		final Vec3 b;
		final Display.BlockDisplay d;
		final String actor;
		final int start;
		boolean shot;
		boolean grown;
		boolean cut;

		Seg(Vec3 a, Vec3 b, Display.BlockDisplay d, String actor, int start) {
			this.a = a;
			this.b = b;
			this.d = d;
			this.actor = actor;
			this.start = start;
		}
	}

	private record Hook(Vec3 at, int until) {
	}

	private YarnWeb(ServerLevel level, Run run) {
		this.level = level;
		this.run = run;
	}

	/**
	 * Shoots one thread from `from` to each point (one every 3 ticks). Inside a case site the web joins that site's run
	 * (threads as actors, events posted); elsewhere it stands alone until cut or {@link #clear}ed.
	 */
	public static YarnWeb cast(ServerLevel level, Vec3 from, List<Vec3> to) {
		return begin(new YarnWeb(level, runAt(level, from)), from, to);
	}

	/** Same, with the threads as run actors (removed on a chapter replay) and events posted to the run. */
	public static YarnWeb cast(Run r, Vec3 from, List<Vec3> to) {
		return begin(new YarnWeb(r.level, r), from, to);
	}

	private static Run runAt(ServerLevel level, Vec3 at) {
		for (ServerPlayer p : level.players()) {
			Run r = Director.of(p);
			if (r != null && r.level == level && r.siteBox().contains(at)) {
				return r;
			}
		}
		return null;
	}

	private static YarnWeb begin(YarnWeb w, Vec3 from, List<Vec3> to) {
		for (Vec3 p : to) {
			w.add(from, p, w.segs.size() * 3);
		}
		ACTIVE.add(w);
		return w;
	}

	/** One more thread between two anchors, shot right away. */
	public YarnWeb add(Vec3 a, Vec3 b) {
		return add(a, b, age + 1);
	}

	private YarnWeb add(Vec3 a, Vec3 b, int start) {
		Vec3 dir = b.subtract(a);
		if (dir.lengthSqr() < 1e-4) {
			return this;
		}
		String actor = run != null ? CasaProps.uid("lana") : null;
		Display.BlockDisplay d = run != null ? CasaProps.block(run, actor, a, Blocks.RED_WOOL.defaultBlockState())
				: CasaProps.block(level, a, Blocks.RED_WOOL.defaultBlockState());
		if (d == null) {
			return this;
		}
		CasaProps.pose(d, CasaProps.alongZ(dir), new Vector3f(THICK, THICK, 0.01F), AXIS, 0);
		segs.add(new Seg(a, b, d, actor, start));
		AABB box = new AABB(a, b).inflate(1.0);
		bounds = bounds == null ? box : bounds.minmax(box);
		return this;
	}

	/** Threads still up. */
	public int alive() {
		int n = 0;
		for (Seg s : segs) {
			if (!s.cut) {
				n++;
			}
		}
		return n;
	}

	public boolean hooked(ServerPlayer p) {
		return hooks.containsKey(p.getUUID());
	}

	/** Removes every thread (no event). */
	public void clear() {
		for (Seg s : segs) {
			s.cut = true;
			remove(s);
		}
		hooks.clear();
		ended = true;
		ACTIVE.remove(this);
	}

	private void remove(Seg s) {
		if (run != null && s.actor != null) {
			run.despawn(s.actor);
		} else if (!s.d.isRemoved()) {
			s.d.discard();
		}
	}

	// ------------------------------------------------------------------ ticking
	static void tickAll(MinecraftServer server) {
		if (ACTIVE.isEmpty()) {
			SWING.clear();
			return;
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			float a = p.getAttackAnim(1.0F);
			Float prev = SWING.put(p.getUUID(), a);
			if ((prev == null || prev == 0F) && a > 0F && p.getMainHandItem().is(ModItems.SILVER_DAGGER)) {
				onDagger(p);
			}
		}
		for (YarnWeb w : new ArrayList<>(ACTIVE)) {
			w.tick();
		}
	}

	private void tick() {
		if (run != null && Director.get(run.type, run.site) != run) {
			clear();
			return;
		}
		for (Seg s : segs) {
			if (!s.cut && s.d.isRemoved()) {
				clear();  // a thread vanished without being cut (a chapter replay discards them): end without "lana:fin"
				return;
			}
		}
		age++;
		boolean any = false;
		for (Seg s : segs) {
			if (s.cut) {
				continue;
			}
			any = true;
			if (!s.grown && age >= s.start) {
				if (!s.shot) {
					s.shot = true;
					Vec3 dir = s.b.subtract(s.a);
					CasaProps.pose(s.d, CasaProps.alongZ(dir), new Vector3f(THICK, THICK, (float) dir.length()), AXIS, 5);
					level.playSound(null, s.a.x, s.a.y, s.a.z, ModSounds.YARN_TWANG, SoundSource.HOSTILE, 0.9F, 1.0F + level.random.nextFloat() * 0.3F);
				}
				s.grown = age >= s.start + 5;
			}
		}
		if (!any) {
			ended = true;  // "lana:fin" was posted by the cut that took the last thread
			ACTIVE.remove(this);
			return;
		}
		holdHooked();
		snag();
		if (age % 4 == 0 && bounds != null) {
			for (FlareEntity f : level.getEntitiesOfClass(FlareEntity.class, bounds)) {
				Vec3 fp = f.position();
				for (Seg s : segs) {
					if (!s.cut && s.grown && CasaProps.segDist(fp, fp, s.a, s.b) < 0.7) {
						cut(s, true);
					}
				}
			}
		}
	}

	private void holdHooked() {
		if (hooks.isEmpty()) {
			return;
		}
		for (ServerPlayer p : level.players()) {
			Hook h = hooks.get(p.getUUID());
			if (h == null) {
				continue;
			}
			if (age >= h.until()) {
				hooks.remove(p.getUUID());
				free.put(p.getUUID(), age + 40);
				continue;
			}
			if (p.position().distanceToSqr(h.at()) > 0.02) {
				p.teleportTo(level, h.at().x, h.at().y, h.at().z, Set.of(), p.getYRot(), p.getXRot(), false);
			}
		}
	}

	private void snag() {
		if (bounds == null) {
			return;
		}
		for (ServerPlayer p : level.players()) {
			if (p.isSpectator() || hooks.containsKey(p.getUUID()) || !bounds.contains(p.position())
					|| free.getOrDefault(p.getUUID(), 0) > age) {
				continue;
			}
			Vec3 feet = p.position().add(0, 0.2, 0);
			Vec3 head = p.getEyePosition().add(0, -0.1, 0);
			for (Seg s : segs) {
				if (!s.cut && s.grown && CasaProps.segDist(feet, head, s.a, s.b) < TOUCH) {
					hooks.put(p.getUUID(), new Hook(p.position(), age + 40));
					level.playSound(null, p.getX(), p.getY() + 1, p.getZ(), ModSounds.YARN_TWANG, SoundSource.HOSTILE, 1.3F, 0.8F);
					SanityManager.add(p, -8F);
					Fx.shake(p, 0.4F, 10);
					p.displayClientMessage(Component.translatable("deadline.casa.msg.lana"), true);
					if (run != null) {
						run.post("lana:engancho");
					}
					break;
				}
			}
		}
	}

	private void cut(Seg s, boolean burn) {
		s.cut = true;
		for (int i = 0; i <= 12; i++) {
			Vec3 q = s.a.lerp(s.b, i / 12.0);
			if (burn) {
				level.sendParticles(ParticleTypes.FLAME, q.x, q.y, q.z, 1, 0.03, 0.03, 0.03, 0.01);
				level.sendParticles(ParticleTypes.SMOKE, q.x, q.y, q.z, 1, 0.03, 0.03, 0.03, 0.01);
			} else {
				level.sendParticles(new DustParticleOptions(0xA01828, 1.0F), q.x, q.y, q.z, 1, 0.04, 0.04, 0.04, 0.0);
			}
		}
		Vec3 m = s.a.lerp(s.b, 0.5);
		level.playSound(null, m.x, m.y, m.z, ModSounds.YARN_SNAP, SoundSource.HOSTILE, 1.2F, burn ? 0.8F : 1.1F);
		remove(s);
		for (ServerPlayer p : level.players()) {
			if (hooks.containsKey(p.getUUID()) && CasaProps.segDist(p.position(), p.getEyePosition(), s.a, s.b) < 1.0) {
				hooks.remove(p.getUUID());
				free.put(p.getUUID(), age + 20);
			}
		}
		if (run != null) {
			run.post(burn ? "lana:quemada" : "lana:cortada");
		}
		if (!ended && alive() == 0) {
			ended = true;
			hooks.clear();
			ACTIVE.remove(this);
			if (run != null) {
				run.post("lana:fin");
			}
		}
	}

	/** Silver dagger swung or used (hooks): cuts the nearest thread under the crosshair within reach. */
	static void onDagger(ServerPlayer p) {
		Vec3 eye = p.getEyePosition();
		Vec3 end = eye.add(p.getViewVector(1F).scale(REACH));
		YarnWeb bestWeb = null;
		Seg best = null;
		double bd = 0.3;
		for (YarnWeb w : ACTIVE) {
			if (w.level != p.level()) {
				continue;
			}
			for (Seg s : w.segs) {
				if (s.cut || !s.grown) {
					continue;
				}
				double d = CasaProps.segDist(eye, end, s.a, s.b);
				if (d < bd) {
					bd = d;
					best = s;
					bestWeb = w;
				}
			}
		}
		if (bestWeb != null) {
			bestWeb.cut(best, false);
		}
	}

	static void clearAll() {
		for (YarnWeb w : new ArrayList<>(ACTIVE)) {
			w.clear();
		}
		ACTIVE.clear();
		SWING.clear();
	}
}
