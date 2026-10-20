package com.deadline.voice;

import com.deadline.director.Director;
import com.deadline.director.Run;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * Microphone input for the scares (optional: works only with Simple Voice Chat installed). Keeps a per-player
 * loudness estimate and calibration, feeds the noise meter and the director ("voice" events, "voice_ticks").
 */
public final class Voice {
	/** Installed by the Simple Voice Chat plugin when present. */
	public static volatile VoiceBackend backend;
	private static final Map<UUID, State> STATES = new HashMap<>();
	private static final Set<UUID> OPTED_OUT = new HashSet<>();

	public static final class State {
		/** Smoothed loudness (dBFS) of the latest frames. */
		public float db = -90F;
		public boolean whisper;
		public long lastVoiced = -1000;
		/** Calibrated normal speaking level (dBFS); the first utterances set it. */
		public float base = -32F;
		int calibrationFrames;
		public int shouts;
	}

	private Voice() {
	}

	public static boolean available() {
		return backend != null;
	}

	public static boolean enabled(ServerPlayer p) {
		return backend != null && !OPTED_OUT.contains(p.getUUID());
	}

	public static void optOut(ServerPlayer p, boolean out) {
		if (out) {
			OPTED_OUT.add(p.getUUID());
			if (backend != null) {
				backend.clear(p.getUUID());
			}
		} else {
			OPTED_OUT.remove(p.getUUID());
		}
	}

	public static State state(ServerPlayer p) {
		return STATES.computeIfAbsent(p.getUUID(), k -> new State());
	}

	/** True while the player is talking (voiced frames in the last 6 ticks), whisper excluded. */
	public static boolean speaking(ServerPlayer p, long now) {
		State s = STATES.get(p.getUUID());
		return s != null && now - s.lastVoiced < 6 && !s.whisper;
	}

	/** Loudness relative to the calibrated speaking voice (dB; +12 = a shout). */
	public static float relative(ServerPlayer p) {
		State s = state(p);
		return s.db - s.base;
	}

	public static void tick(MinecraftServer server) {
		VoiceBackend b = backend;
		if (b == null) {
			return;
		}
		long now = server.overworld().getGameTime();
		for (VoiceBackend.Frame f : b.drain()) {
			if (OPTED_OUT.contains(f.player())) {
				continue;
			}
			State s = STATES.computeIfAbsent(f.player(), k -> new State());
			s.db = s.db < f.db() ? f.db() : s.db * 0.6F + f.db() * 0.4F;
			s.whisper = f.whisper();
			if (f.db() > -50F && !f.whisper()) {
				s.lastVoiced = now;
				if (s.calibrationFrames < 150) {
					s.base = s.calibrationFrames == 0 ? f.db() : s.base * 0.97F + f.db() * 0.03F;
					s.calibrationFrames++;
				}
			}
		}
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			State s = STATES.get(p.getUUID());
			if (s == null) {
				continue;
			}
			if (now - s.lastVoiced > 3) {
				s.db = Math.max(-90F, s.db - 4F);
			}
			if (now - s.lastVoiced < 2 && !s.whisper) {
				Run r = Director.of(p);
				if (r != null) {
					r.post("voice");
					r.inc("voice_ticks");
					if (s.db - s.base > 12F) {
						r.post("shout");
					}
				}
			}
		}
	}

	public static void tagNext(ServerPlayer p, String tag, int ms) {
		if (enabled(p)) {
			backend.tagNext(p.getUUID(), tag, ms);
		}
	}

	public static boolean hasClip(ServerPlayer p, String tag) {
		return enabled(p) && backend.hasClip(p.getUUID(), tag);
	}

	/** Plays the player's own captured clip to them (or to another listener). Returns false without a clip. */
	public static boolean play(ServerPlayer listener, ServerPlayer owner, String tag, VoiceBackend.Effect fx, Vec3 at) {
		if (!enabled(owner) || !backend.hasClip(owner.getUUID(), tag)) {
			return false;
		}
		backend.play(listener, owner.getUUID(), tag, fx, at);
		return true;
	}

	public static void clear(ServerPlayer p) {
		STATES.remove(p.getUUID());
		if (backend != null) {
			backend.clear(p.getUUID());
		}
	}
}
