package com.deadline.client.render;

import com.deadline.DeadLine;
import com.deadline.client.model.AnimaModel;
import com.deadline.client.model.MonjaModel;
import com.deadline.client.model.MunecaModel;
import com.deadline.client.model.PoseidaModel;
import com.deadline.client.model.SombraModel;
import com.deadline.client.model.gen.AnimaModelBase;
import com.deadline.client.model.gen.MonjaModelBase;
import com.deadline.client.model.gen.MunecaModelBase;
import com.deadline.client.model.gen.PoseidaModelBase;
import com.deadline.client.model.gen.SombraModelBase;
import com.deadline.registry.ModEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;

public final class ModRenderers {
	private ModRenderers() {
	}

	private static ModelLayerLocation layer(String key) {
		return new ModelLayerLocation(DeadLine.id(key), "main");
	}

	public static final ModelLayerLocation MONJA = layer("monja");
	public static final ModelLayerLocation POSEIDA = layer("poseida");
	public static final ModelLayerLocation SOMBRA = layer("sombra");
	public static final ModelLayerLocation MUNECA = layer("muneca");
	public static final ModelLayerLocation ANIMA = layer("anima");

	public static void init() {
		EntityModelLayerRegistry.registerModelLayer(MONJA, MonjaModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(POSEIDA, PoseidaModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(SOMBRA, SombraModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(MUNECA, MunecaModelBase::createBodyLayer);
		EntityModelLayerRegistry.registerModelLayer(ANIMA, AnimaModelBase::createBodyLayer);

		EntityRendererRegistry.register(ModEntities.MONJA, ctx -> new HauntRenderer<>(ctx, new MonjaModel(ctx.bakeLayer(MONJA)), 0.5F, "monja", true));
		EntityRendererRegistry.register(ModEntities.POSEIDA, ctx -> new HauntRenderer<>(ctx, new PoseidaModel(ctx.bakeLayer(POSEIDA)), 0.4F, "poseida", false));
		EntityRendererRegistry.register(ModEntities.SOMBRA, ctx -> new HauntRenderer<>(ctx, new SombraModel(ctx.bakeLayer(SOMBRA)), 0.0F, "sombra", true));
		EntityRendererRegistry.register(ModEntities.MUNECA, ctx -> new HauntRenderer<>(ctx, new MunecaModel(ctx.bakeLayer(MUNECA)), 0.3F, "muneca", true));
		EntityRendererRegistry.register(ModEntities.ANIMA, ctx -> new HauntRenderer<>(ctx, new AnimaModel(ctx.bakeLayer(ANIMA)), 0.0F, "anima", true));
		// placeholders until the alumna / madre / clara models ship (tools/models/ent_*.py)
		EntityRendererRegistry.register(ModEntities.ALUMNA, ctx -> new HauntRenderer<>(ctx, new AnimaModel(ctx.bakeLayer(ANIMA)), 0.0F, "anima", true));
		EntityRendererRegistry.register(ModEntities.MADRE, ctx -> new HauntRenderer<>(ctx, new MonjaModel(ctx.bakeLayer(MONJA)), 0.0F, "monja", true));
		EntityRendererRegistry.register(ModEntities.CLARA, ctx -> new HauntRenderer<>(ctx, new AnimaModel(ctx.bakeLayer(ANIMA)), 0.0F, "anima", true));
		EntityRendererRegistry.register(ModEntities.ANCHOR, AnchorRenderer::new);
		EntityRendererRegistry.register(ModEntities.HOLY_WATER, ThrownItemRenderer::new);
		EntityRendererRegistry.register(ModEntities.FLARE, ctx -> new ThrownItemRenderer<>(ctx, 1.0F, true));
	}
}
