package com.deadline.voice;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.net.Fx;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * How loud each hunter is (0-100, decays 8 per second). Running, landing, doors and the voice push it up; the nun
 * hunts towards loud players. Shown next to the sanity ECG while a scripted case runs.
 */
public final class NoiseMeter {
	private static final Map<UUID, Float> LEVEL = new HashMap<>();
	private static final Map<UUID, Boolean> AIRBORNE = new HashMap<>();
	private static final Map<UUID, Integer> HEARD = new HashMap<>();

	private NoiseMeter() {
	}

	public static float get(ServerPlayer p) {
		return LEVEL.getOrDefault(p.getUUID(), 0F);
	}

	public static void add(ServerPlayer p, float amount) {
		float k = p.isShiftKeyDown() ? 0.5F : 1F;
		LEVEL.merge(p.getUUID(), amount * k, (a, b) -> Math.min(100F, a + b));
	}

	/** The nun noticed this player (HUD shows "TE ESCUCHA" for a while). */
	public static void heard(ServerPlayer p) {
		HEARD.put(p.getUUID(), 60);
	}

	public static void tick(MinecraftServer server) {
		long now = server.overworld().getGameTime();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			Run r = Director.of(p);
			if (r == null) {
				continue;
			}
			UUID id = p.getUUID();
			float n = Math.max(0F, LEVEL.getOrDefault(id, 0F) - 0.4F);
			if (p.isSprinting() && p.onGround()) {
				n = Math.min(100F, n + 0.9F);
			}
			boolean air = !p.onGround();
			if (Boolean.TRUE.equals(AIRBORNE.get(id)) && !air && p.fallDistance > 0.5) {
				n = Math.min(100F, n + 8F);
			}
			AIRBORNE.put(id, air);
			if (Voice.enabled(p) && Voice.speaking(p, now)) {
				float rel = Voice.relative(p);
				n = Math.min(100F, n + Math.max(0.6F, 1.2F + rel * 0.25F) * (p.isShiftKeyDown() ? 0.5F : 1F));
			}
			LEVEL.put(id, n);
			int heard = HEARD.getOrDefault(id, 0);
			if (heard > 0) {
				HEARD.put(id, heard - 1);
			}
			if (now % 5 == 0) {
				Fx.noise(p, n, (heard > 0 ? 1 : 0) | (Voice.enabled(p) ? 2 : 0));
			}
		}
	}
}
