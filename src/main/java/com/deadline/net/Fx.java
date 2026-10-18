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

	public static void incomingCall(ServerPlayer p, String caseKey, int caller) {
		send(p, FxPayload.INCOMING_CALL, 1.0F, caller, 0, 0, 0, caseKey);
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

	/** Plays a sound for one player only, at a world position. */
	public static void soundAt(ServerPlayer p, SoundEvent sound, Vec3 pos, float volume) {
		send(p, FxPayload.SOUND_AT, volume, 0, pos.x, pos.y, pos.z, BuiltInRegistries.SOUND_EVENT.getKey(sound).toString());
	}

	/**
	 * La Llorona's curse: the farther she is the closer she sounds, and when she is near
	 * her cry seems to come from far away.
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
