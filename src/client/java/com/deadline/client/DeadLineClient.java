package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.client.hud.DeadLineHud;
import com.deadline.client.particle.DeadParticle;
import com.deadline.client.render.ModRenderers;
import com.deadline.net.FxPayload;
import com.deadline.net.PhoneDataPayload;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;

public class DeadLineClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		DeadLineKeys.init();
		DeadParticle.registerAll();
		ModRenderers.init();

		ClientPlayNetworking.registerGlobalReceiver(FxPayload.TYPE, (payload, ctx) -> ClientFx.onFx(payload));
		ClientPlayNetworking.registerGlobalReceiver(PhoneDataPayload.TYPE, (payload, ctx) -> ClientFx.onPhoneData(payload));
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> ClientState.reset());
		ClientTickEvents.END_CLIENT_TICK.register(mc -> {
			DeadLineKeys.tick(mc);
			ClientFx.tick(mc);
		});

		HudElementRegistry.attachElementAfter(VanillaHudElements.MISC_OVERLAYS, DeadLine.id("backdrop"), DeadLineHud::renderBackdrop);
		HudElementRegistry.addLast(DeadLine.id("front"), DeadLineHud::renderFront);
	}
}
