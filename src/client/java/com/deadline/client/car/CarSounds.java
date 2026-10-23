package com.deadline.client.car;

import com.deadline.car.CarEntity;
import com.deadline.registry.ModSounds;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

/**
 * The car's continuous sounds, per car near the player: engine idle + rev loops (pitch and mix by speed), tyres on
 * gravel/dirt, and the radio (static, or the loop a story event put on it).
 */
public final class CarSounds {
	private static final double RANGE = 48.0;

	private enum Kind {
		IDLE, REV, GRAVEL, RADIO
	}

	private static final Map<Integer, Map<Kind, Loop>> LOOPS = new HashMap<>();

	private CarSounds() {
	}

	/** A loop that follows its car, eases its volume/pitch to targets and fades out when no longer wanted. */
	static final class Loop extends AbstractTickableSoundInstance {
		final CarEntity car;
		final Kind kind;
		final SoundEvent event;
		float targetVolume;
		float targetPitch = 1F;
		boolean fading;

		Loop(CarEntity car, Kind kind, SoundEvent event, SoundSource source) {
			super(event, source, SoundInstance.createUnseededRandom());
			this.car = car;
			this.kind = kind;
			this.event = event;
			this.looping = true;
			this.delay = 0;
			this.volume = 0.01F;
			this.attenuation = SoundInstance.Attenuation.LINEAR;
			this.x = car.getX();
			this.y = car.getY() + 0.8;
			this.z = car.getZ();
		}

		@Override
		public boolean canStartSilent() {
			return true;
		}

		@Override
		public void tick() {
			if (car.isRemoved()) {
				this.stop();
				return;
			}
			this.x = car.getX();
			this.y = car.getY() + 0.8;
			this.z = car.getZ();
			if (fading) {
				volume -= 0.06F;
				if (volume <= 0.01F) {
					this.stop();
				}
				return;
			}
			volume += (Math.max(0.01F, targetVolume) - volume) * 0.25F;
			pitch += (targetPitch - pitch) * 0.3F;
		}
	}

	public static void tick(Minecraft mc) {
		if (mc.level == null || mc.player == null) {
			clear();
			return;
		}
		for (Entity e : mc.level.entitiesForRendering()) {
			if (e instanceof CarEntity car && car.distanceToSqr(mc.player) < RANGE * RANGE) {
				update(mc, car);
			}
		}
		Iterator<Map.Entry<Integer, Map<Kind, Loop>>> it = LOOPS.entrySet().iterator();
		while (it.hasNext()) {
			Map<Kind, Loop> m = it.next().getValue();
			m.values().removeIf(l -> {
				if (l.car.isRemoved() || l.car.distanceToSqr(mc.player) > RANGE * RANGE * 1.2) {
					l.fading = true;
				}
				return l.isStopped();
			});
			if (m.isEmpty()) {
				it.remove();
			}
		}
	}

	private static void update(Minecraft mc, CarEntity car) {
		float sp = Math.abs(car.clientSpeed());
		float k = Mth.clamp(sp / CarEntity.MAX_SPEED, 0F, 1F);
		boolean engine = car.isEngineOn();
		// idle: strongest standing still, rev: takes over with the speed, rising in pitch
		want(mc, car, Kind.IDLE, ModSounds.CAR_IDLE, SoundSource.NEUTRAL, engine, 0.75F * (1F - k * 0.8F) + 0.05F, 0.95F + k * 0.25F);
		want(mc, car, Kind.REV, ModSounds.CAR_REV, SoundSource.NEUTRAL, engine && sp > 0.02F, Math.min(1F, sp * 3.5F) * 0.85F, 0.6F + k * 1.05F);
		want(mc, car, Kind.GRAVEL, ModSounds.CAR_GRAVEL, SoundSource.NEUTRAL, car.onUnpaved() && sp > 0.03F, Math.min(1F, sp * 1.6F) * 0.7F,
				0.75F + k * 0.45F);
		SoundEvent radio = car.radioLoop();
		want(mc, car, Kind.RADIO, radio != null ? radio : ModSounds.CAR_RADIO_STATIC, SoundSource.RECORDS, car.isRadioOn(), 0.55F, 1F);
	}

	private static void want(Minecraft mc, CarEntity car, Kind kind, SoundEvent ev, SoundSource src, boolean on, float vol, float pitch) {
		Map<Kind, Loop> m = LOOPS.computeIfAbsent(car.getId(), id -> new HashMap<>());
		Loop l = m.get(kind);
		if (l != null && (l.event != ev || !on)) {
			l.fading = true;  // switched off, or the radio changed station
			if (l.event != ev && on) {
				m.remove(kind);
				l = null;
			} else {
				return;
			}
		}
		if (!on) {
			return;
		}
		if (l == null || l.isStopped()) {
			l = new Loop(car, kind, ev, src);
			m.put(kind, l);
			mc.getSoundManager().play(l);
		}
		l.fading = false;
		l.targetVolume = vol;
		l.targetPitch = pitch;
	}

	public static void clear() {
		LOOPS.clear();
	}
}
