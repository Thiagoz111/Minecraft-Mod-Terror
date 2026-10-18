package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.registry.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/** Per-case soundscape: looping ambience + score, random stingers, whispers when the mind starts to slip. */
public final class ClientAmbience {
	private ClientAmbience() {
	}

	private static final RandomSource RNG = RandomSource.create();
	private static Loop ambience;
	private static Loop music;
	private static String current = "";
	private static int stingerCooldown = 600;
	private static int whisperCooldown = 400;

	/** A non-positional loop that fades in, and fades out when asked to stop. */
	static final class Loop extends AbstractTickableSoundInstance {
		private final float target;
		private boolean fading;

		Loop(SoundEvent ev, SoundSource src, float target) {
			super(ev, src, SoundInstance.createUnseededRandom());
			this.target = target;
			this.looping = true;
			this.delay = 0;
			this.volume = 0.01F;
			this.relative = true;
			this.attenuation = SoundInstance.Attenuation.NONE;
		}

		void fadeOut() {
			fading = true;
		}

		@Override
		public void tick() {
			if (fading) {
				volume -= 0.02F;
				if (volume <= 0.01F) {
					this.stop();
				}
			} else if (volume < target) {
				volume = Math.min(target, volume + 0.01F);
			}
		}
	}

	private static SoundEvent ambienceFor(String key) {
		return switch (key) {
			case "rio" -> ModSounds.AMBIENT_RIO;
			case "bosque" -> ModSounds.AMBIENT_BOSQUE;
			case "parque" -> ModSounds.AMBIENT_PARQUE;
			case "convento" -> ModSounds.AMBIENT_CONVENTO;
			default -> ModSounds.AMBIENT_CASA;
		};
	}

	public static void tick(Minecraft mc) {
		Player pl = mc.player;
		String key = "";
		if (pl != null && mc.level != null) {
			var id = mc.level.dimension().identifier();
			if (DeadLine.MOD_ID.equals(id.getNamespace()) && id.getPath().startsWith("caso_")) {
				key = id.getPath().substring(5);
			}
		}
		if (!key.equals(current)) {
			if (ambience != null) {
				ambience.fadeOut();
				ambience = null;
			}
			if (music != null) {
				music.fadeOut();
				music = null;
			}
			current = key;
			if (!key.isEmpty()) {
				ambience = new Loop(ambienceFor(key), SoundSource.AMBIENT, 0.85F);
				music = new Loop(ModSounds.MUSIC_CASE, SoundSource.MUSIC, 0.45F);
				mc.getSoundManager().play(ambience);
				mc.getSoundManager().play(music);
				stingerCooldown = 400 + RNG.nextInt(400);
			}
		}
		if (pl == null || mc.level == null || mc.isPaused()) {
			return;
		}
		if (!current.isEmpty() && --stingerCooldown <= 0) {
			stingerCooldown = 900 + RNG.nextInt(900);
			playAround(mc, pl, ModSounds.AMBIENT_STINGER, 6.0, 0.8F);
		}
		if (ClientState.sanityShown < 45F && --whisperCooldown <= 0) {
			whisperCooldown = 300 + RNG.nextInt((int) Math.max(60, ClientState.sanityShown * 12));
			playAround(mc, pl, ModSounds.AMBIENT_WHISPERS, 3.0, 0.6F);
		}
	}

	private static void playAround(Minecraft mc, Player pl, SoundEvent ev, double dist, float vol) {
		double a = RNG.nextDouble() * Math.PI * 2;
		Vec3 p = pl.getEyePosition().add(Math.cos(a) * dist, (RNG.nextDouble() - 0.3) * 2, Math.sin(a) * dist);
		mc.level.playLocalSound(p.x, p.y, p.z, ev, SoundSource.AMBIENT, vol, 0.9F + RNG.nextFloat() * 0.2F, false);
	}

	public static void reset() {
		current = "";
		ambience = null;
		music = null;
	}
}
