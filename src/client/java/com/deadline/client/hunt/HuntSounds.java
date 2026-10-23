package com.deadline.client.hunt;

import com.deadline.horror.casa.hunt.HuntHudPayload;
import com.deadline.registry.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

/**
 * The hunt's loops, in the player's head: the heartbeat (while hidden, and when she is close) that beats harder and
 * louder the closer she is, and the chase music while she chases him (dissonant strings and a pounding drum).
 */
final class HuntSounds {
	/** A non-positional loop that eases to a target volume / pitch and fades out when no longer wanted. */
	static final class Loop extends AbstractTickableSoundInstance {
		float targetVolume;
		float targetPitch = 1F;
		final float fade;

		Loop(SoundEvent event, SoundSource source, float fade) {
			super(event, source, SoundInstance.createUnseededRandom());
			this.fade = fade;
			this.looping = true;
			this.delay = 0;
			this.volume = 0.01F;
			this.relative = true;
			this.attenuation = SoundInstance.Attenuation.NONE;
			this.x = 0.0;
			this.y = 0.0;
			this.z = 0.0;
		}

		@Override
		public boolean canStartSilent() {
			return true;
		}

		@Override
		public void tick() {
			float k = targetVolume > volume ? 0.2F : fade;
			volume += (targetVolume - volume) * k;
			pitch += (targetPitch - pitch) * 0.15F;
			if (targetVolume <= 0.001F && volume < 0.01F) {
				this.stop();
			}
		}

		void finish() {
			this.stop();
		}
	}

	private static Loop heart;
	private static Loop chase;

	private HuntSounds() {
	}

	static void tick(Minecraft mc) {
		if (mc.player == null || mc.level == null) {
			reset();
			return;
		}
		float d = HuntClient.nonaShown;
		float close = d < 0F ? 0F : Mth.clamp(1F - (d - 2F) / 14F, 0F, 1F);
		boolean hidden = HuntClient.hidden();
		boolean holding = HuntClient.flag(HuntHudPayload.HOLDING);
		float heartVol = 0F;
		if (hidden) {
			heartVol = 0.3F + 0.7F * close + (holding ? 0.12F : 0F);
		} else if (close > 0.35F) {
			heartVol = 0.55F * (close - 0.35F) / 0.65F;
		}
		if (HuntClient.flag(HuntHudPayload.SEARCHED)) {
			heartVol = 1F;
		}
		heart = drive(mc, heart, ModSounds.HUNT_HEARTBEAT, SoundSource.PLAYERS, Math.min(1F, heartVol), 0.85F + 0.5F * close, 0.06F);
		boolean chased = HuntClient.flag(HuntHudPayload.CHASED);
		chase = drive(mc, chase, ModSounds.HUNT_CHASE, SoundSource.MUSIC, chased ? 0.9F : 0F, 1F, 0.025F);
	}

	private static Loop drive(Minecraft mc, Loop loop, SoundEvent event, SoundSource source, float volume, float pitch, float fade) {
		if (loop != null && loop.isStopped()) {
			loop = null;
		}
		if (loop == null) {
			if (volume <= 0.01F) {
				return null;
			}
			loop = new Loop(event, source, fade);
			mc.getSoundManager().play(loop);
		}
		loop.targetVolume = volume;
		loop.targetPitch = pitch;
		return loop;
	}

	static void reset() {
		if (heart != null) {
			heart.finish();
			heart = null;
		}
		if (chase != null) {
			chase.finish();
			chase = null;
		}
	}
}
