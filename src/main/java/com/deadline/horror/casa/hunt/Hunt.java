package com.deadline.horror.casa.hunt;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.horror.Haunt;
import com.deadline.horror.HouseQuery;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Act 5 of Casa Morales, "Ella escucha todo" (docs/design/casa_terror.md 2, 6.1, 6.2, 7): the possessed Nona
 * ({@link NonaRotaEntity}) hunts the hunters by ear. One hunt per {@link Run}, kept beside it like {@link Haunt}.
 * <ul>
 *   <li>{@link #transform} plays the set piece "La Nona se rompe" (back turned, bones cracking, the neck turning 180, the
 *   jaw unhinging, stretching to the ceiling, dropping to all fours) and then starts the hunt; posts
 *   {@code hunt:transformed}.</li>
 *   <li>{@link #start} starts it without the set piece (she is simply out there, somewhere you are not looking).</li>
 *   <li>{@link #stop} despawns her, pulls every hunter out of his hiding place and clears the state.</li>
 *   <li>{@link #noise} lets any event make a sound she hears (a plate that shatters, a door slammed by the house).</li>
 *   <li>A capture never kills: jumpscare, black, and the hunter wakes up on the guest bed with the taste of blood
 *   (blindness, nausea); posts {@code hunt:captured}; {@link #captures} counts them.</li>
 * </ul>
 * Debug: these static methods are what {@code /deadline horror} sub-commands should call.
 */
public final class Hunt {
	/** Actor name of the hunter in the run (Run.end and checkpoints discard it with the other actors). */
	public static final String ACTOR = "hunt_nona";
	/** Ticks the hunter is deaf after a capture (the hunter wakes up and gets his breath back). */
	static final int GRACE_AFTER_CAPTURE = 20 * 25;
	/** Room markers she prowls between (design 11); only the ones the site has and that stand inside the house. */
	private static final String[] ROOMS = {"hall", "living", "comedor", "cocina", "despensa", "lavadero", "bano_pb",
			"nona_cuarto", "costurero", "escritorio", "pasillo_pb", "pasillo_pb_fondo", "esc_principal_pie",
			"esc_principal_arriba", "esc_servicio_pie", "esc_servicio_arriba", "pasillo_1p", "pasillo_1p_fondo", "lucia_cuarto",
			"toti_cuarto", "matrimonial", "huespedes", "bano_1p", "cuarto_nono", "telefono_fijo", "mesada", "heladera", "tv",
			"mecedora", "aparador", "tocador", "caja_musica", "estante_munecas", "maquina_coser"};

	private static final Map<Run, State> STATES = new WeakHashMap<>();

	/** A sound somewhere in the house (thrown objects, the house itself) waiting to be heard. */
	record Noise(Vec3 pos, float loudness, long at) {
	}

	/** One capture in progress: jumpscare -> black -> waking up on the bed. */
	static final class Capture {
		final UUID player;
		final long start;

		Capture(UUID player, long start) {
			this.player = player;
			this.start = start;
		}
	}

	static final class State {
		final Run run;
		boolean active;
		boolean transforming;
		int captures;
		long missingSince = -1;
		long deafUntil;
		final List<Noise> noises = new ArrayList<>();
		final List<Capture> capturing = new ArrayList<>();
		final Map<UUID, Long> lastCaptured = new HashMap<>();
		List<String> rooms;

		State(Run run) {
			this.run = run;
		}
	}

	private Hunt() {
	}

	private static State state(Run run) {
		return STATES.computeIfAbsent(run, State::new);
	}

	static State peek(Run run) {
		return run == null ? null : STATES.get(run);
	}

	// ------------------------------------------------------------------ public API
	/** Starts the hunt without the set piece: she appears where no hunter is looking, far from them. */
	public static void start(Run run) {
		if (run == null) {
			return;
		}
		State s = state(run);
		NonaRotaEntity e = nona(run);
		if (e != null && s.active) {
			return;  // already hunting (or transforming)
		}
		s.active = true;
		s.transforming = false;
		s.missingSince = -1;
		if (e == null) {
			e = spawnHidden(run, s);
		}
		if (e != null && !e.isTransforming()) {
			e.beginHunt(false);
		}
	}

	/**
	 * The set piece "La Nona se rompe": spawns her at `at` facing `yaw` (her back to the room) and plays the
	 * transformation (~7.5 s); then the hunt starts and the run gets {@code hunt:transformed}.
	 */
	public static void transform(Run run, Vec3 at, float yaw) {
		if (run == null || at == null) {
			return;
		}
		State s = state(run);
		s.active = true;
		s.transforming = true;
		s.missingSince = -1;
		NonaRotaEntity e = spawn(run, at, yaw);
		if (e != null) {
			e.startTransform();
		}
	}

	/** Ends the hunt: she is gone, every hidden hunter of the run is let out, captures in progress are finished. */
	public static void stop(Run run) {
		if (run == null) {
			return;
		}
		State s = STATES.remove(run);
		run.despawn(ACTOR);
		HideSpots.releaseAll(run);
		if (s != null) {
			for (Capture c : s.capturing) {
				ServerPlayer p = player(run, c.player);
				if (p != null) {
					wakeUp(run, p);
				}
			}
		}
		for (ServerPlayer p : run.hunters()) {
			HuntHud.clear(p);
		}
	}

	/** True from the start of the transformation (or {@link #start}) until {@link #stop}. */
	public static boolean active(Run run) {
		State s = peek(run);
		return s != null && s.active;
	}

	/** True while "La Nona se rompe" is playing. */
	public static boolean transforming(Run run) {
		State s = peek(run);
		return s != null && s.transforming;
	}

	/** Times she caught a hunter in this run. */
	public static int captures(Run run) {
		State s = peek(run);
		return s == null ? 0 : s.captures;
	}

	/** A noise in the house she may hear (0-100 like the noise meter: 15 a creak, 40 a plate, 70 a slam, 100 a scream). */
	public static void noise(Run run, Vec3 pos, float loudness) {
		State s = peek(run);
		if (s == null || !s.active || pos == null || loudness <= 0F) {
			return;
		}
		if (s.noises.size() > 24) {
			s.noises.remove(0);
		}
		s.noises.add(new Noise(pos, Math.min(100F, loudness), run.now()));
	}

	/** The hunter entity of a run (null when there is none right now). */
	public static NonaRotaEntity nona(Run run) {
		return run != null && run.actor(ACTOR) instanceof NonaRotaEntity n ? n : null;
	}

	// ------------------------------------------------------------------ spawning
	static NonaRotaEntity spawn(Run run, Vec3 at, float yaw) {
		NonaRotaEntity e = HuntEntities.NONA_ROTA.create(run.level, EntitySpawnReason.EVENT);
		if (e == null) {
			return null;
		}
		e.snapTo(at.x, at.y, at.z, yaw, 0F);
		e.setYHeadRot(yaw);
		e.setYBodyRot(yaw);
		e.bind(run);
		run.level.addFreshEntity(e);
		run.actor(ACTOR, e);
		return e;
	}

	/** She appears in a room out of every hunter's view, as far as possible from them (12+ blocks when it can). */
	private static NonaRotaEntity spawnHidden(Run run, State s) {
		String best = null;
		double bestD = -1;
		List<ServerPlayer> hs = run.hunters();
		for (String k : rooms(run)) {
			Vec3 v = run.at(k);
			double d = Double.MAX_VALUE;
			boolean seen = false;
			for (ServerPlayer p : hs) {
				d = Math.min(d, p.position().distanceTo(v));
				seen |= HouseQuery.sees(run, p, v.add(0, 1.0, 0));
			}
			if (seen) {
				continue;
			}
			double score = d >= 12 && d <= 40 ? 100 + run.level.getRandom().nextDouble() * 20 : Math.min(d, 60);
			if (score > bestD) {
				bestD = score;
				best = k;
			}
		}
		if (best == null) {
			best = run.def.points.containsKey("pasillo_pb_fondo") ? "pasillo_pb_fondo" : "spawn";
		}
		Vec3 v = run.at(best);
		return spawn(run, v, run.yaw(best));
	}

	/** Patrol markers: the room points of {@link #ROOMS} plus the outside of every hiding place, inside the house. */
	static List<String> rooms(Run run) {
		State s = state(run);
		if (s.rooms != null) {
			return s.rooms;
		}
		List<String> out = new ArrayList<>();
		AABB house = run.def.areas.containsKey("casa") ? run.area("casa").inflate(0.5) : null;
		for (String k : ROOMS) {
			if (run.def.points.containsKey(k)) {
				out.add(k);
			}
		}
		for (String k : HouseQuery.points(run, "hide_")) {
			if (k.endsWith("_out")) {
				out.add(k);
			}
		}
		out.removeIf(k -> {
			Vec3 v = run.at(k);
			return (house != null && !house.contains(v)) || !HouseQuery.standable(run, BlockPos.containing(v));
		});
		if (out.isEmpty()) {
			out.add("spawn");
		}
		s.rooms = out;
		return out;
	}

	// ------------------------------------------------------------------ capture (fail forward, never a death)
	/** She got him: jumpscare, black, and he wakes up on the guest bed. Called by the hunter entity. */
	static void capture(Run run, ServerPlayer p) {
		State s = state(run);
		for (Capture c : s.capturing) {
			if (c.player.equals(p.getUUID())) {
				return;
			}
		}
		long now = run.now();
		Long last = s.lastCaptured.get(p.getUUID());
		if (last != null && now - last < 20 * 8) {
			return;
		}
		s.lastCaptured.put(p.getUUID(), now);
		HideSpots.drag(p);
		Breath.reset(p);
		s.capturing.add(new Capture(p.getUUID(), now));
		s.captures++;
		Fx.jumpscare(p, "nona_rota");
		Fx.shake(p, 2.2F, 26);
		Haunt h = Haunt.peek(run);
		if (h != null) {
			h.jumpscared();
		}
		run.level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.HUNT_GRAB, SoundSource.HOSTILE, 2.2F, 1.0F);
		run.post("hunt:captured");
		run.inc("hunt_captures");
		DeadLine.LOGGER.info("Hunt: {} captured ({} so far)", p.getName().getString(), s.captures);
	}

	private static void tickCaptures(Run run, State s) {
		long now = run.now();
		for (Iterator<Capture> it = s.capturing.iterator(); it.hasNext();) {
			Capture c = it.next();
			ServerPlayer p = player(run, c.player);
			if (p == null) {
				it.remove();
				continue;
			}
			long t = now - c.start;
			if (t == 14) {
				Fx.fade(p, 70);  // black at ~t 49, back by t 84
			}
			if (t >= 14 && t < 50) {
				p.setDeltaMovement(Vec3.ZERO);
				p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 10, 6, false, false));
			}
			if (t == 48) {
				wakeUp(run, p);
				it.remove();
			}
		}
	}

	/** Teleport to the guest bed (huespedes_cama) in the dark of the fade, blind and sick. */
	private static void wakeUp(Run run, ServerPlayer p) {
		String bed = run.def.points.containsKey("huespedes_cama") ? "huespedes_cama"
				: run.def.points.containsKey("huespedes") ? "huespedes" : "spawn";
		Vec3 v = run.at(bed);
		if (p.isPassenger()) {
			p.stopRiding();
		}
		p.teleportTo(run.level, v.x, v.y + 0.6, v.z, java.util.Set.of(), run.yaw(bed), 30F, false);
		p.setDeltaMovement(Vec3.ZERO);
		p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0));
		p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 200, 0));
		p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 100, 1, false, false));
		Fx.redFlash(p, 0.5F);
		run.level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.HUNT_GASP, SoundSource.PLAYERS, 0.9F, 0.8F);
		State s = peek(run);
		if (s != null) {
			s.deafUntil = run.now() + GRACE_AFTER_CAPTURE;
			NonaRotaEntity n = nona(run);
			if (n != null) {
				n.afterCapture(p);
			}
		}
	}

	private static ServerPlayer player(Run run, UUID id) {
		Entity e = run.level.getEntity(id);
		return e instanceof ServerPlayer sp && !sp.isRemoved() ? sp : null;
	}

	// ------------------------------------------------------------------ ticking (from HuntEntities' server tick)
	static void tickAll(MinecraftServer server) {
		if (STATES.isEmpty()) {
			return;
		}
		for (Map.Entry<Run, State> en : new ArrayList<>(STATES.entrySet())) {
			Run run = en.getKey();
			State s = en.getValue();
			if (run == null) {
				continue;
			}
			if (Director.get(run.type, run.site) != run) {
				stop(run);  // the case ended or the site restarted under us
				continue;
			}
			try {
				tick(run, s);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Hunt tick failed", ex);
			}
		}
	}

	private static void tick(Run run, State s) {
		long now = run.now();
		s.noises.removeIf(n -> now - n.at() > 10);
		tickCaptures(run, s);
		if (!s.active) {
			return;
		}
		NonaRotaEntity n = nona(run);
		if (n == null) {
			// a checkpoint or a chunk unload took her: she comes back from somewhere else after a few seconds
			if (s.missingSince < 0) {
				s.missingSince = now;
			} else if (now - s.missingSince > 20 * 6 && !run.hunters().isEmpty()) {
				s.missingSince = -1;
				s.transforming = false;
				NonaRotaEntity e = spawnHidden(run, s);
				if (e != null) {
					e.beginHunt(false);
				}
			}
		} else {
			s.missingSince = -1;
			if (s.transforming && !n.isTransforming()) {
				s.transforming = false;
			}
		}
	}

	/** Called by the hunter when the transformation is over. */
	static void transformed(Run run) {
		State s = peek(run);
		if (s != null) {
			s.transforming = false;
		}
		run.post("hunt:transformed");
	}

	static boolean deaf(Run run) {
		State s = peek(run);
		return s != null && run.now() < s.deafUntil;
	}

	static List<Noise> noises(Run run) {
		State s = peek(run);
		return s == null ? List.of() : s.noises;
	}

	static boolean capturing(Run run, ServerPlayer p) {
		State s = peek(run);
		if (s == null) {
			return false;
		}
		for (Capture c : s.capturing) {
			if (c.player.equals(p.getUUID())) {
				return true;
			}
		}
		return false;
	}
}
