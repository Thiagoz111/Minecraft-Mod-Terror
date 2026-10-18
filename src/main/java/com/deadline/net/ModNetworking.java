package com.deadline.net;

import com.deadline.caseload.CaseManager;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;

public final class ModNetworking {
	private ModNetworking() {
	}

	public static void init() {
		PayloadTypeRegistry.playS2C().register(FxPayload.TYPE, FxPayload.CODEC);
		PayloadTypeRegistry.playS2C().register(PhoneDataPayload.TYPE, PhoneDataPayload.CODEC);
		PayloadTypeRegistry.playC2S().register(PhoneActionPayload.TYPE, PhoneActionPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(PhoneActionPayload.TYPE, (payload, ctx) -> CaseManager.handlePhoneAction(ctx.player(), payload));
	}
}
