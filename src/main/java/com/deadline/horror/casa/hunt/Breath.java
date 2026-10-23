package com.deadline.horror.casa.hunt;

import com.deadline.director.Director;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import com.deadline.voice.NoiseMeter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;

/**
 * Holding the breath (key B by default; docs/design/casa_terror.md 6.1, 6.2): 100 -> 0 in 8 s while the key is held,
 * back to full in 5 s once released. While held the player makes no vocal noise (his breathing, the microphone: see
 * NoiseMeter) and his noise fades faster; it costs a little sanity. At 0 he gasps: a loud noise spike she hears from
 * across the house, and the key does nothing until he has caught some breath again.
 */
public final class Breath {
	/** Ticks of a full hold, of a full refill; breath needed to hold again after a gasp. */
	private static final float HOLD_TICKS = 160F, REFILL_TICKS = 100F, AFTER_GASP = 35F;

	static final class State {
		float breath = 100F;
		boolean want;
		boolean holding;
		boolean spent;
	}

	private static final Map<UUID, State> STATES = new HashMap<>();

	private Breath() {
	}

	/** True while the player holds his breath. */
	public static boolean holding(ServerPlayer p) {
		State s = STATES.get(p.getUUID());
		return s != null && s.holding;
	}

	/** 0-100. */
	public static float breath(ServerPlayer p) {
		State s = STATES.get(p.getUUID());
		return s == null ? 100F : s.breath;
	}

	static boolean spent(ServerPlayer p) {
		State s = STATES.get(p.getUUID());
		return s != null && s.spent;
	}

	static void touch(ServerPlayer p) {
		STATES.computeIfAbsent(p.getUUID(), k -> new State());
	}

	/** The key went down / up. */
	static void onKey(ServerPlayer p, boolean hold) {
		State s = STATES.computeIfAbsent(p.getUUID(), k -> new State());
		s.want = hold;
	}

	/** Back to normal breathing (after a capture). */
	static void reset(ServerPlayer p) {
		State s = STATES.get(p.getUUID());
		if (s != null) {
			s.holding = false;
			s.want = false;
			s.spent = false;
			s.breath = 100F;
		}
	}

	static void forget(ServerPlayer p) {
		STATES.remove(p.getUUID());
	}

	static void tick(MinecraftServer server) {
		if (STATES.isEmpty()) {
			return;
		}
		for (Map.Entry<UUID, State> e : STATES.entrySet()) {
			ServerPlayer p = server.getPlayerList().getPlayer(e.getKey());
			State s = e.getValue();
			if (p == null || !p.isAlive() || p.isSpectator()) {
				s.holding = false;
				s.want = false;
				continue;
			}
			if (s.spent && s.breath >= AFTER_GASP) {
				s.spent = false;
			}
			if (s.want && !s.holding && !s.spent && s.breath > 5F) {
				s.holding = true;
				p.level().playSound(null, p.getX(), p.getEyeY(), p.getZ(), ModSounds.HUNT_BREATH_IN, SoundSource.PLAYERS, 0.25F, 1.0F);
			} else if (!s.want && s.holding) {
				s.holding = false;
				p.level().playSound(null, p.getX(), p.getEyeY(), p.getZ(), ModSounds.HUNT_BREATH_OUT, SoundSource.PLAYERS, 0.3F, 1.0F);
			}
			if (s.holding) {
				s.breath -= 100F / HOLD_TICKS;
				if (p.tickCount % 10 == 0) {
					SanityManager.add(p, -0.3F);
				}
				if (s.breath <= 0F) {
					gasp(p, s);
				}
			} else {
				s.breath = Math.min(100F, s.breath + 100F / REFILL_TICKS);
			}
		}
	}

	/** Out of air: a desperate gasp everyone hears. He must let go of the key and press it again to hold once more. */
	private static void gasp(ServerPlayer p, State s) {
		s.breath = 0F;
		s.holding = false;
		s.want = false;
		s.spent = true;
		p.level().playSound(null, p.getX(), p.getEyeY(), p.getZ(), ModSounds.HUNT_GASP, SoundSource.PLAYERS, 1.6F, 0.95F + p.getRandom().nextFloat() * 0.1F);
		NoiseMeter.add(p, 55F);
		com.deadline.net.Fx.shake(p, 0.5F, 10);
		if (Director.of(p) == null) {
			return;
		}
		SanityManager.add(p, -2F);
	}
}
