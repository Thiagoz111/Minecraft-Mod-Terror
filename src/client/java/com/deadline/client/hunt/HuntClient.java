package com.deadline.client.hunt;

import com.deadline.DeadLine;
import com.deadline.client.DeadLineKeys;
import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.horror.casa.hunt.BreathPayload;
import com.deadline.horror.casa.hunt.HuntEntities;
import com.deadline.horror.casa.hunt.HuntHudPayload;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.fabricmc.fabric.api.client.rendering.v1.world.WorldRenderEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.NoopRenderer;

/**
 * Client side of B2 (the hunt): the broken Nona's renderer, the hide seat (invisible), the hold-breath key, the
 * hiding-place overlays, the lungs bar, the heartbeat and chase loops, and the 3D jumpscares. Wired from
 * DeadLineClient with {@link #init()}.
 */
public final class HuntClient {
	public static final ModelLayerLocation NONA_ROTA_LAYER = new ModelLayerLocation(DeadLine.id("nona_rota"), "main");

	// ---------------------------------------------------------------- last state from the server (HuntHudPayload)
	static float breath = 100F;
	static float breathShown = 100F;
	static int hide;
	static float nona = -1F;
	static float nonaShown = -1F;
	static int flags;
	/** Ticks since the last payload (the state goes stale when the server stops sending). */
	static int age = 1000;
	/** Ticks the current hiding place has been shown (fade in). */
	static int hideTicks;
	static int searchedTicks;

	private static boolean sentHold;
	private static boolean done;

	private HuntClient() {
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		EntityModelLayerRegistry.registerModelLayer(NONA_ROTA_LAYER, NonaModelBase::createBodyLayer);
		EntityRendererRegistry.register(HuntEntities.NONA_ROTA, NonaRotaRenderer::new);
		EntityRendererRegistry.register(HuntEntities.HIDE_SEAT, NoopRenderer::new);
		ClientPlayNetworking.registerGlobalReceiver(HuntHudPayload.TYPE, (payload, ctx) -> onPayload(payload));
		ClientTickEvents.END_CLIENT_TICK.register(HuntClient::tick);
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> reset());
		HudElementRegistry.attachElementAfter(VanillaHudElements.MISC_OVERLAYS, DeadLine.id("hunt_hide"), HuntOverlay::renderHide);
		HudElementRegistry.addLast(DeadLine.id("hunt_front"), HuntOverlay::renderFront);
		WorldRenderEvents.BEFORE_ENTITIES.register(Jumpscare3D::render);
	}

	static void onPayload(HuntHudPayload p) {
		breath = p.breath();
		if (p.hide() != hide) {
			hideTicks = 0;
		}
		hide = p.hide();
		nona = p.nona();
		flags = p.flags();
		age = 0;
	}

	public static boolean hidden() {
		return hide != 0 && age < 40;
	}

	static boolean flag(int f) {
		return age < 40 && (flags & f) != 0;
	}

	private static void tick(Minecraft mc) {
		age++;
		if (age > 60) {
			hide = 0;
			nona = -1F;
			flags = 0;
			breath = 100F;
		}
		breathShown += (breath - breathShown) * 0.35F;
		nonaShown = nona < 0F ? -1F : nonaShown < 0F ? nona : nonaShown + (nona - nonaShown) * 0.3F;
		hideTicks = hide != 0 ? hideTicks + 1 : 0;
		searchedTicks = flag(HuntHudPayload.SEARCHED) ? searchedTicks + 1 : 0;

		// hold breath: the key state goes to the server on every change (it counts the 8 seconds)
		while (DeadLineKeys.BREATH.consumeClick()) {
			// presses are read as a held state below
		}
		boolean down = mc.player != null && mc.screen == null && DeadLineKeys.BREATH.isDown();
		if (down != sentHold && ClientPlayNetworking.canSend(BreathPayload.TYPE)) {
			sentHold = down;
			ClientPlayNetworking.send(new BreathPayload(down));
		}
		HuntSounds.tick(mc);
		Jumpscare3D.tick(mc);
	}

	static void reset() {
		breath = breathShown = 100F;
		hide = 0;
		nona = nonaShown = -1F;
		flags = 0;
		age = 1000;
		sentHold = false;
		HuntSounds.reset();
		Jumpscare3D.reset();
	}
}
