package com.deadline.client.render;

import com.deadline.registry.ModEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.entity.NoopRenderer;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;

public final class ModRenderers {
	private ModRenderers() {
	}

	public static void init() {
		EntityRendererRegistry.register(ModEntities.POSEIDA, NoopRenderer::new);
		EntityRendererRegistry.register(ModEntities.MONJA, NoopRenderer::new);
		EntityRendererRegistry.register(ModEntities.SOMBRA, NoopRenderer::new);
		EntityRendererRegistry.register(ModEntities.MUNECA, NoopRenderer::new);
		EntityRendererRegistry.register(ModEntities.ANIMA, NoopRenderer::new);
		EntityRendererRegistry.register(ModEntities.ANCHOR, AnchorRenderer::new);
		EntityRendererRegistry.register(ModEntities.HOLY_WATER, ThrownItemRenderer::new);
		EntityRendererRegistry.register(ModEntities.FLARE, ctx -> new ThrownItemRenderer<>(ctx, 1.0F, true));
	}
}
