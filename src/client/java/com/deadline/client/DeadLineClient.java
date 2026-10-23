package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.client.hud.DeadLineHud;
import com.deadline.client.particle.DeadParticle;
import com.deadline.client.render.ModRenderers;
import com.deadline.net.FxPayload;
import com.deadline.net.PhoneDataPayload;
import com.deadline.registry.ModBlocks;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.BlockRenderLayerMap;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.renderer.chunk.ChunkSectionLayer;

public class DeadLineClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		DeadLineKeys.init();
		DeadParticle.registerAll();
		ModRenderers.init();
		com.deadline.client.casa.CasaRenderers.init();
		BlockRenderLayerMap.putBlocks(ChunkSectionLayer.CUTOUT, ModBlocks.SALT_LINE, ModBlocks.BLOOD_STAIN, ModBlocks.RITUAL_CANDLE);
		com.deadline.registry.gen.ModBlocksGen.CUTOUT.forEach(b -> BlockRenderLayerMap.putBlock(b, ChunkSectionLayer.CUTOUT));
		com.deadline.registry.gen.ModBlocksGen.TRANSLUCENT.forEach(b -> BlockRenderLayerMap.putBlock(b, ChunkSectionLayer.TRANSLUCENT));
		ClientSmoke.register();

		ClientPlayNetworking.registerGlobalReceiver(FxPayload.TYPE, (payload, ctx) -> ClientFx.onFx(payload));
		ClientPlayNetworking.registerGlobalReceiver(PhoneDataPayload.TYPE, (payload, ctx) -> ClientFx.onPhoneData(payload));
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> {
			ClientState.reset();
			ClientAmbience.reset();
		});
		ClientTickEvents.END_CLIENT_TICK.register(mc -> {
			DeadLineKeys.tick(mc);
			ClientFx.tick(mc);
			ClientAmbience.tick(mc);
		});

		HudElementRegistry.attachElementAfter(VanillaHudElements.MISC_OVERLAYS, DeadLine.id("backdrop"), DeadLineHud::renderBackdrop);
		HudElementRegistry.addLast(DeadLine.id("front"), DeadLineHud::renderFront);
	}
}
