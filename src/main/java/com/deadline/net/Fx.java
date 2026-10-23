package com.deadline.net;

import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/** Server-side helpers to trigger client effects. */
public final class Fx {
	private Fx() {
	}

	private static void send(ServerPlayer p, int kind, float a, int b, double x, double y, double z, String s) {
		if (ServerPlayNetworking.canSend(p, FxPayload.TYPE)) {
			ServerPlayNetworking.send(p, new FxPayload(kind, a, b, x, y, z, s));
		}
	}

	public static void shake(ServerPlayer p, float intensity, int ticks) {
		send(p, FxPayload.SHAKE, intensity, ticks, 0, 0, 0, "");
	}

	public static void flash(ServerPlayer p, float strength) {
		send(p, FxPayload.FLASH, strength, 0, 0, 0, 0, "");
	}

	public static void redFlash(ServerPlayer p, float strength) {
		send(p, FxPayload.RED_FLASH, strength, 0, 0, 0, 0, "");
	}

	public static void jumpscare(ServerPlayer p, String entityKey) {
		send(p, FxPayload.JUMPSCARE, 1.0F, 0, 0, 0, 0, entityKey);
	}

	public static void staticNoise(ServerPlayer p, float strength, int ticks) {
		send(p, FxPayload.STATIC, strength, ticks, 0, 0, 0, "");
	}

	public static void fade(ServerPlayer p, int ticks) {
		send(p, FxPayload.FADE, 1.0F, ticks, 0, 0, 0, "");
	}

	public static void title(ServerPlayer p, String key, int ticks) {
		send(p, FxPayload.TITLE, 1.0F, ticks, 0, 0, 0, key);
	}

	public static void hallucination(ServerPlayer p, String kind) {
		send(p, FxPayload.HALLUCINATION, 1.0F, 0, 0, 0, 0, kind);
	}

	public static void sanity(ServerPlayer p, float value) {
		send(p, FxPayload.SANITY, value, 0, 0, 0, 0, "");
	}

	public static void objective(ServerPlayer p, String caseKey, int stage) {
		send(p, FxPayload.OBJECTIVE, 1.0F, stage, 0, 0, 0, caseKey);
	}

	public static void caseEnd(ServerPlayer p, boolean solved, int reward) {
		send(p, FxPayload.CASE_END, solved ? 1.0F : 0.0F, reward, 0, 0, 0, "");
	}

	/**
	 * Objective checklist of a scripted chapter. Text format: place key, chapter title key, then one
	 * "objective_key=0|1" per line.
	 */
	public static void checklist(ServerPlayer p, String placeKey, String chapterKey, int chapter, java.util.List<String> objectives) {
		StringBuilder sb = new StringBuilder(placeKey).append('\n').append(chapterKey);
		for (String o : objectives) {
			sb.append('\n').append(o);
		}
		send(p, FxPayload.CHECKLIST, 1.0F, chapter, 0, 0, 0, sb.toString());
	}

	/** Caption bar (hints, signs): name key + text key (either may be "" ; a leading '#' means literal text). */
	public static void subtitle(ServerPlayer p, String speakerKey, String lineKey, int ticks) {
		send(p, FxPayload.SUBTITLE, 1.0F, ticks, 0, 0, 0, speakerKey + "\n" + lineKey);
	}

	/** Reprimand stamp ("AMONESTACIÓN") with its reason and the new total. */
	public static void stamp(ServerPlayer p, String reasonKey, int total) {
		send(p, FxPayload.STAMP, 1.0F, total, 0, 0, 0, reasonKey);
	}

	/** Noise meter: level 0-100; flags bit0 = the nun heard you, bit1 = microphone active. */
	public static void noise(ServerPlayer p, float level, int flags) {
		send(p, FxPayload.NOISE, level, flags, 0, 0, 0, "");
	}

	/** Big centred text (prayers, the file, the diary). progress in 0..1 draws a bar, negative hides it; ticks 0 clears. */
	public static void bigText(ServerPlayer p, String key, int ticks, float progress) {
		send(p, FxPayload.BIG_TEXT, progress, ticks, 0, 0, 0, key);
	}

	/** Chapter title card (title key + subtitle key). */
	public static void chapterCard(ServerPlayer p, String titleKey, String subKey, int ticks) {
		send(p, FxPayload.CHAPTER, 1.0F, ticks, 0, 0, 0, titleKey + "\n" + subKey);
	}

	/** Plays a sound for one player only, at a world position. */
	public static void soundAt(ServerPlayer p, SoundEvent sound, Vec3 pos, float volume) {
		send(p, FxPayload.SOUND_AT, volume, 0, pos.x, pos.y, pos.z, BuiltInRegistries.SOUND_EVENT.getKey(sound).toString());
	}

	/**
	 * Distance-inverted sound: the farther the source is the closer it sounds, and when it is near
	 * it seems to come from far away.
	 */
	public static void invertedSound(ServerPlayer p, Entity source, SoundEvent sound, float volume) {
		Vec3 eye = p.getEyePosition();
		Vec3 dir = source.position().subtract(eye);
		double dist = dir.length();
		Vec3 n = dist > 0.01 ? dir.scale(1.0 / dist) : new Vec3(0, 0, 1);
		Vec3 heard;
		float vol;
		if (dist > 20) {
			heard = eye.add(n.scale(2.0));
			vol = volume;
		} else if (dist < 10) {
			heard = eye.add(n.scale(40.0));
			vol = volume * 2.5F;
		} else {
			heard = eye.add(n.scale(14.0));
			vol = volume * 1.5F;
		}
		soundAt(p, sound, heard, vol);
	}
}
