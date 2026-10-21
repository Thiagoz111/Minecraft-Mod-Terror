package com.deadline.client.casa;

import com.deadline.DeadLine;
import com.deadline.casa.CasaNet;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.minecraft.client.Minecraft;

/** Client side of {@link CasaNet}: the chat, the stitch ring, the name screen and the spirit box wheel. */
public final class CasaClientNet {
	private CasaClientNet() {
	}

	/** One call from DeadLineClient.onInitializeClient. */
	public static void init() {
		ClientPlayNetworking.registerGlobalReceiver(CasaNet.ChatPayload.TYPE, (payload, ctx) -> ChatScreen.onPayload(payload));
		ClientPlayNetworking.registerGlobalReceiver(CasaNet.StitchPayload.TYPE, (payload, ctx) -> StitchOverlay.onPayload(payload));
		ClientPlayNetworking.registerGlobalReceiver(CasaNet.ChoicePayload.TYPE, (payload, ctx) -> onChoice(payload));
		HudElementRegistry.addLast(DeadLine.id("casa_stitch"), StitchOverlay::render);
		ClientTickEvents.END_CLIENT_TICK.register(mc -> {
			StitchOverlay.tick();
			ChatScreen.tickAlways(mc);
		});
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> {
			StitchOverlay.reset();
			ChatScreen.reset();
		});
	}

	private static void onChoice(CasaNet.ChoicePayload p) {
		Minecraft mc = Minecraft.getInstance();
		switch (p.kind()) {
			case CasaNet.ChoicePayload.NAME -> {
				// asked again while the old one is up: the new screen answers the same question
				NameScreen.silentClose = mc.screen instanceof NameScreen;
				mc.setScreen(new NameScreen(p.options(), p.ticks()));
			}
			case CasaNet.ChoicePayload.SPIRIT -> mc.setScreen(new SpiritWheelScreen(p.options(), p.flags()));
			case CasaNet.ChoicePayload.CLOSE -> {
				if (mc.screen instanceof NameScreen || mc.screen instanceof SpiritWheelScreen) {
					NameScreen.silentClose = mc.screen instanceof NameScreen;
					mc.setScreen(null);
				}
			}
			default -> {
			}
		}
	}

	/** Sends an answer to the server. */
	static void send(int action, String arg) {
		if (ClientPlayNetworking.canSend(CasaNet.ActionPayload.TYPE)) {
			ClientPlayNetworking.send(new CasaNet.ActionPayload(action, arg));
		}
	}
}
