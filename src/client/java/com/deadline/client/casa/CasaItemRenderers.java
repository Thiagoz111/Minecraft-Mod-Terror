package com.deadline.client.casa;

import com.deadline.casa.CasaItems;
import com.deadline.casa.ChancletaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/** Renderers of the Casa Morales thrown items: the blessed choripán and the Nona's slipper. */
public final class CasaItemRenderers {
	private CasaItemRenderers() {
	}

	public static void init() {
		EntityRendererRegistry.register(CasaItems.CHORIPAN_BENDITO_ENTITY, ThrownItemRenderer::new);
		EntityRendererRegistry.register(CasaItems.CHANCLETA_ENTITY, ChancletaRenderer::new);
	}

	/** The slipper tumbling end over end along its flight. */
	public static class ChancletaRenderer extends EntityRenderer<ChancletaEntity, ChancletaRenderer.State> {
		public static class State extends EntityRenderState {
			public final ItemStackRenderState item = new ItemStackRenderState();
			public float spin;
			public float yaw;
		}

		private final ItemModelResolver resolver;
		private final ItemStack stack = new ItemStack(CasaItems.CHANCLETA);

		public ChancletaRenderer(EntityRendererProvider.Context ctx) {
			super(ctx);
			this.resolver = ctx.getItemModelResolver();
			this.shadowRadius = 0.15F;
		}

		@Override
		public State createRenderState() {
			return new State();
		}

		@Override
		public void extractRenderState(ChancletaEntity entity, State s, float pt) {
			super.extractRenderState(entity, s, pt);
			resolver.updateForNonLiving(s.item, stack, ItemDisplayContext.GROUND, entity);
			s.spin = entity.tickCount + pt;
			s.yaw = entity.getYRot();
		}

		@Override
		public void submit(State s, PoseStack ps, SubmitNodeCollector collector, CameraRenderState cam) {
			ps.pushPose();
			ps.translate(0.0F, 0.12F, 0.0F);
			ps.mulPose(Axis.YP.rotationDegrees(-s.yaw));
			ps.mulPose(Axis.XP.rotationDegrees(s.spin * 48F));
			ps.scale(1.4F, 1.4F, 1.4F);
			s.item.submit(ps, collector, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor);
			ps.popPose();
			super.submit(s, ps, collector, cam);
		}
	}
}
