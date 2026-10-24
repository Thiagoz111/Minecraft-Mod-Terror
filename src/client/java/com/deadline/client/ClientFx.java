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

/** Applies server effect packets and runs the client-side screen effects (shake, flashes, the VHS shader...). */
public final class ClientFx {
	private ClientFx() {
	}

	private static final RandomSource RNG = RandomSource.create();
	private static String postEffect = null;
	private static int postCheck;

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
				// B2: the creatures of the Casa get a 3D face in the camera (client/hunt/Jumpscare3D); the rest the picture
				if (com.deadline.client.hunt.Jumpscare3D.start(p.s())) {
					return;
				}
				ClientState.jumpscareKey = p.s();
				ClientState.jumpscareTicks = ClientState.JUMPSCARE_LEN;
				shake(2.6F, 24);
				ClientState.redFlash = 0.6F;
				mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.JUMPSCARE, 1.0F, 1.0F));
			}
			case FxPayload.SOUND_AT -> {
				SoundEvent ev = BuiltInRegistries.SOUND_EVENT.getValue(Identifier.parse(p.s()));
				if (ev != null && mc.level != null) {
					if (p.b() == 1) {  // heard in the head: steady pitch, stays with the player
						mc.getSoundManager().play(SimpleSoundInstance.forUI(ev, 1.0F, p.a()));
					} else {
						mc.level.playLocalSound(p.x(), p.y(), p.z(), ev, SoundSource.HOSTILE, p.a(), 0.9F + RNG.nextFloat() * 0.2F, false);
					}
				}
			}
			case FxPayload.TITLE -> {
				ClientState.titleKey = p.s();
				ClientState.titleTicks = ClientState.titleTotal = Math.max(1, p.b());
			}
			case FxPayload.OBJECTIVE -> {
				ClientState.objCase = p.s();
				ClientState.objStage = p.b();
				ClientState.objFlash = 50;
			}
			case FxPayload.CHECKLIST -> com.deadline.client.hud.StoryHud.onChecklist(p.s(), p.b());
			case FxPayload.SUBTITLE -> {
				String[] sp = p.s().split("\n", 2);
				com.deadline.client.hud.StoryHud.speakerKey = sp[0];
				com.deadline.client.hud.StoryHud.lineKey = sp.length > 1 ? sp[1] : "";
				com.deadline.client.hud.StoryHud.subTicks = com.deadline.client.hud.StoryHud.subTotal = Math.max(1, p.b());
			}
			case FxPayload.STAMP -> {
				com.deadline.client.hud.StoryHud.stampKey = p.s();
				com.deadline.client.hud.StoryHud.stampTotal = p.b();
				com.deadline.client.hud.StoryHud.stampTicks = com.deadline.client.hud.StoryHud.STAMP_LEN;
			}
			case FxPayload.NOISE -> {
				com.deadline.client.hud.StoryHud.noise = p.a();
				com.deadline.client.hud.StoryHud.noiseFlags = p.b();
				com.deadline.client.hud.StoryHud.noiseTicks = 40;
			}
			case FxPayload.BIG_TEXT -> {
				int t = Math.max(0, p.b());
				if (p.s().equals(com.deadline.client.hud.StoryHud.bigKey) && com.deadline.client.hud.StoryHud.bigTicks > 0 && t > 0) {
					// a refresh of the same text (prayer, silence): keep its fade-in, just extend it
					com.deadline.client.hud.StoryHud.bigTotal += t - com.deadline.client.hud.StoryHud.bigTicks;
					com.deadline.client.hud.StoryHud.bigTicks = t;
				} else {
					com.deadline.client.hud.StoryHud.bigKey = p.s();
					com.deadline.client.hud.StoryHud.bigTicks = com.deadline.client.hud.StoryHud.bigTotal = t;
				}
				com.deadline.client.hud.StoryHud.bigProgress = p.a();
			}
			case FxPayload.CHAPTER -> {
				String[] sp = p.s().split("\n", 2);
				com.deadline.client.hud.StoryHud.cardTitle = sp[0];
				com.deadline.client.hud.StoryHud.cardSub = sp.length > 1 ? sp[1] : "";
				com.deadline.client.hud.StoryHud.cardTicks = com.deadline.client.hud.StoryHud.cardTotal = Math.max(1, p.b());
			}
			case FxPayload.CASE_END -> {
				com.deadline.client.hud.StoryHud.reset();
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

	public static void tick(Minecraft mc) {
		ClientState.ticks++;
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
		com.deadline.client.hud.StoryHud.tick();
		if (ClientState.objFlash > 0) {
			ClientState.objFlash--;
		}
		if (mc.player == null || mc.level == null) {
			return;
		}

		updatePostEffect(mc);
	}

	/** Screen shader: the VHS camera look while recording. */
	private static void updatePostEffect(Minecraft mc) {
		String want = ClientState.vhs ? "vhs" : null;
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
		if (amount <= 0.001F) {
			return null;
		}
		float t = (ClientState.ticks + partial);
		float yaw = (float) (Math.sin(t * 2.31) * 0.6 + Math.sin(t * 5.7 + 1.3) * 0.4) * amount;
		float pitch = (float) (Math.sin(t * 2.93 + 0.7) * 0.6 + Math.sin(t * 6.1 + 2.1) * 0.4) * amount;
		return new float[] {yaw, pitch};
	}
}
