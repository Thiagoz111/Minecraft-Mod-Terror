package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.client.mixin.GameRendererAccessor;
import com.deadline.client.screen.PhoneScreen;
import com.deadline.net.FxPayload;
import com.deadline.net.PhoneDataPayload;
import com.deadline.registry.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/** Applies server effect packets and runs the client-side horror ambience (heartbeat, ringing...). */
public final class ClientFx {
	private ClientFx() {
	}

	private static final RandomSource RNG = RandomSource.create();
	private static int heartbeatCooldown;
	private static String postEffect = null;
	private static int postCheck;
	private static int ringCooldown;

	public static void onFx(FxPayload p) {
		Minecraft mc = Minecraft.getInstance();
		switch (p.kind()) {
			case FxPayload.SHAKE -> shake(p.a(), p.b());
			case FxPayload.FLASH -> ClientState.flash = Math.max(ClientState.flash, p.a());
			case FxPayload.RED_FLASH -> ClientState.redFlash = Math.max(ClientState.redFlash, p.a());
			case FxPayload.STATIC -> {
				ClientState.staticStrength = p.a();
				ClientState.staticTicks = ClientState.staticTotal = Math.max(1, p.b());
			}
			case FxPayload.FADE -> ClientState.fadeTicks = ClientState.fadeTotal = Math.max(1, p.b());
			case FxPayload.JUMPSCARE -> {
				ClientState.jumpscareKey = p.s();
				ClientState.jumpscareTicks = ClientState.JUMPSCARE_LEN;
				shake(2.6F, 24);
				ClientState.redFlash = 0.6F;
				mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.JUMPSCARE, 1.0F, 1.0F));
			}
			case FxPayload.SOUND_AT -> {
				SoundEvent ev = BuiltInRegistries.SOUND_EVENT.getValue(Identifier.parse(p.s()));
				if (ev != null && mc.level != null) {
					mc.level.playLocalSound(p.x(), p.y(), p.z(), ev, SoundSource.HOSTILE, p.a(), 0.9F + RNG.nextFloat() * 0.2F, false);
				}
			}
			case FxPayload.TITLE -> {
				ClientState.titleKey = p.s();
				ClientState.titleTicks = ClientState.titleTotal = Math.max(1, p.b());
			}
			case FxPayload.INCOMING_CALL -> {
				ClientState.callCase = p.s();
				ClientState.callCaller = p.b();
				ClientState.callTicks = 20 * 20;
				ringCooldown = 0;
			}
			case FxPayload.HALLUCINATION -> hallucination(p.s());
			case FxPayload.SANITY -> ClientState.sanity = p.a();
			case FxPayload.OBJECTIVE -> {
				ClientState.objCase = p.s();
				ClientState.objStage = p.b();
				ClientState.objFlash = 50;
			}
			case FxPayload.CASE_END -> {
				ClientState.endSolved = p.a() > 0.5F;
				ClientState.endReward = p.b();
				ClientState.endTicks = 120;
				ClientState.objCase = "";
				ClientState.objStage = -1;
				if (ClientState.endSolved) {
					mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.CASE_SOLVED, 1.0F, 0.8F));
				}
			}
			default -> {
			}
		}
	}

	public static void onPhoneData(PhoneDataPayload p) {
		ClientState.phone = p;
		ClientState.sanity = p.sanity();
		Minecraft mc = Minecraft.getInstance();
		if (p.open() && !(mc.screen instanceof PhoneScreen) && mc.screen == null) {
			mc.setScreen(new PhoneScreen());
		}
	}

	public static void shake(float intensity, int ticks) {
		if (intensity >= ClientState.shakeIntensity * (ClientState.shakeTicks / (float) Math.max(1, ClientState.shakeTotal))) {
			ClientState.shakeIntensity = intensity;
			ClientState.shakeTicks = ClientState.shakeTotal = Math.max(1, ticks);
		}
	}

	private static void hallucination(String kind) {
		Minecraft mc = Minecraft.getInstance();
		Player pl = mc.player;
		if (pl == null || mc.level == null) {
			return;
		}
		Vec3 look = pl.getLookAngle();
		Vec3 behind = pl.position().subtract(look.x * 3.0, 0, look.z * 3.0)
				.add((RNG.nextFloat() - 0.5) * 2.0, 1.0, (RNG.nextFloat() - 0.5) * 2.0);
		switch (kind) {
			case "whisper" -> {
				Vec3 ear = pl.getEyePosition().add(look.z * (RNG.nextBoolean() ? 1.2 : -1.2), 0, -look.x * 1.2);
				mc.level.playLocalSound(ear.x, ear.y, ear.z, ModSounds.SANITY_WHISPER, SoundSource.AMBIENT, 0.9F, 0.9F + RNG.nextFloat() * 0.2F, false);
			}
			case "footsteps" -> mc.level.playLocalSound(behind.x, behind.y, behind.z, ModSounds.SANITY_FOOTSTEPS, SoundSource.AMBIENT, 1.0F, 1.0F, false);
			case "knock" -> {
				Vec3 at = pl.position().add((RNG.nextFloat() - 0.5) * 12, 1.5, (RNG.nextFloat() - 0.5) * 12);
				mc.level.playLocalSound(at.x, at.y, at.z, ModSounds.SANITY_KNOCK, SoundSource.AMBIENT, 1.2F, 1.0F, false);
			}
			case "figure" -> {
				ClientState.figureTicks = 34;
				ClientState.figureLeft = RNG.nextBoolean();
				mc.level.playLocalSound(behind.x, behind.y, behind.z, ModSounds.SANITY_BREATH, SoundSource.AMBIENT, 0.8F, 0.8F, false);
			}
			default -> {
			}
		}
	}

	public static void tick(Minecraft mc) {
		ClientState.ticks++;
		ClientState.sanityShown += (ClientState.sanity - ClientState.sanityShown) * 0.15F;
		if (ClientState.shakeTicks > 0) {
			ClientState.shakeTicks--;
		}
		ClientState.flash = Math.max(0F, ClientState.flash - 0.06F);
		ClientState.redFlash = Math.max(0F, ClientState.redFlash - 0.04F);
		if (ClientState.fadeTicks > 0) {
			ClientState.fadeTicks--;
		}
		if (ClientState.staticTicks > 0) {
			ClientState.staticTicks--;
		}
		if (ClientState.jumpscareTicks > 0) {
			ClientState.jumpscareTicks--;
		}
		if (ClientState.titleTicks > 0) {
			ClientState.titleTicks--;
		}
		if (ClientState.endTicks > 0) {
			ClientState.endTicks--;
		}
		if (ClientState.figureTicks > 0) {
			ClientState.figureTicks--;
		}
		if (ClientState.objFlash > 0) {
			ClientState.objFlash--;
		}
		if (mc.player == null || mc.level == null) {
			return;
		}

		updatePostEffect(mc);

		// the phone keeps ringing until it is picked up
		if (ClientState.callTicks > 0) {
			ClientState.callTicks--;
			if (mc.screen instanceof PhoneScreen) {
				ClientState.callTicks = 0;
			} else if (--ringCooldown <= 0) {
				ringCooldown = 60;
				mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.PHONE_RING, 1.0F, 0.9F));
				shake(0.25F, 10);
			}
		}

		// heartbeat speeds up as sanity drains
		float s = ClientState.sanityShown;
		if (s < 40F && !mc.isPaused()) {
			if (--heartbeatCooldown <= 0) {
				float t = Mth.clamp(s / 40F, 0F, 1F);
				heartbeatCooldown = (int) Mth.lerp(t, 13F, 30F);
				float vol = Mth.lerp(t, 1.0F, 0.35F);
				mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.SANITY_HEARTBEAT, 1.0F + (1F - t) * 0.12F, vol));
				if (s < 20F) {
					ClientState.redFlash = Math.max(ClientState.redFlash, 0.18F * (1F - s / 20F));
				}
			}
		}
	}

	/** Screen shader: VHS camera look, or a failing mind (desaturation + red fringing). */
	private static void updatePostEffect(Minecraft mc) {
		float s = ClientState.sanityShown;
		String want = ClientState.vhs ? "vhs" : s < 15F ? "insanity_2" : s < 30F ? "insanity_1" : null;
		Identifier current = mc.gameRenderer.currentPostEffect();
		boolean ours = current != null && DeadLine.MOD_ID.equals(current.getNamespace());
		if (want == null) {
			if (postEffect != null && ours) {
				mc.gameRenderer.clearPostEffect();
			}
			postEffect = null;
			return;
		}
		Identifier id = DeadLine.id(want);
		if (!want.equals(postEffect) || (++postCheck % 40 == 0 && !id.equals(current))) {
			if (current == null || ours) {
				((GameRendererAccessor) mc.gameRenderer).deadline$setPostEffect(id);
			}
			postEffect = want;
		}
	}

	/** Camera shake offset in degrees for this frame: (yaw, pitch). */
	public static float[] shakeOffset(float partial) {
		float amount = 0F;
		if (ClientState.shakeTicks > 0) {
			float k = (ClientState.shakeTicks - partial) / ClientState.shakeTotal;
			amount = ClientState.shakeIntensity * Mth.clamp(k, 0F, 1F);
		}
		float s = ClientState.sanityShown;
		if (s < 25F) {
			amount += (25F - s) / 25F * 0.35F;
		}
		if (amount <= 0.001F) {
			return null;
		}
		float t = (ClientState.ticks + partial);
		float yaw = (float) (Math.sin(t * 2.31) * 0.6 + Math.sin(t * 5.7 + 1.3) * 0.4) * amount;
		float pitch = (float) (Math.sin(t * 2.93 + 0.7) * 0.6 + Math.sin(t * 6.1 + 2.1) * 0.4) * amount;
		return new float[] {yaw, pitch};
	}
}
