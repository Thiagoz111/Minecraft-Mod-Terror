package com.deadline.client.render;

import com.deadline.entity.AnchorEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemDisplayContext;

/** The cursed object of a case: floats and turns slowly, waiting for holy water. */
public class AnchorRenderer extends EntityRenderer<AnchorEntity, AnchorRenderer.State> {
	public static class State extends EntityRenderState {
		public final ItemStackRenderState item = new ItemStackRenderState();
		public float spin;
	}

	private final ItemModelResolver resolver;

	public AnchorRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		this.resolver = ctx.getItemModelResolver();
		this.shadowRadius = 0.3F;
	}

	@Override
	public State createRenderState() {
		return new State();
	}

	@Override
	protected int getBlockLightLevel(AnchorEntity entity, BlockPos pos) {
		return Math.max(6, super.getBlockLightLevel(entity, pos));
	}

	@Override
	public void extractRenderState(AnchorEntity entity, State s, float pt) {
		super.extractRenderState(entity, s, pt);
		resolver.updateForNonLiving(s.item, entity.getItem(), ItemDisplayContext.GROUND, entity);
		s.spin = entity.tickCount + pt;
	}

	@Override
	public void submit(State s, PoseStack ps, SubmitNodeCollector collector, CameraRenderState cam) {
		ps.pushPose();
		ps.translate(0.0F, 0.45F + (float) Math.sin(s.spin * 0.08F) * 0.08F, 0.0F);
		ps.mulPose(Axis.YP.rotationDegrees(s.spin * 1.6F));
		ps.mulPose(Axis.ZP.rotationDegrees((float) Math.sin(s.spin * 0.05F) * 8F));
		ps.scale(1.5F, 1.5F, 1.5F);
		s.item.submit(ps, collector, s.lightCoords, OverlayTexture.NO_OVERLAY, s.outlineColor);
		ps.popPose();
		super.submit(s, ps, collector, cam);
	}
}
