package com.deadline.client.render;

import com.deadline.DeadLine;
import com.deadline.client.model.BalloonModel;
import com.deadline.entity.BalloonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;

/** Draws Sonrisas' balloons. */
public class BalloonRenderer extends EntityRenderer<BalloonEntity, EntityRenderState> {
	private static final Identifier TEXTURE = DeadLine.id("textures/entity/balloon.png");
	private final BalloonModel model;

	public BalloonRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		this.model = new BalloonModel(ctx.bakeLayer(ModRenderers.BALLOON));
		this.shadowRadius = 0.15F;
	}

	@Override
	public EntityRenderState createRenderState() {
		return new EntityRenderState();
	}

	@Override
	public void submit(EntityRenderState s, PoseStack ps, SubmitNodeCollector collector, CameraRenderState cam) {
		ps.pushPose();
		ps.scale(-1.0F, -1.0F, 1.0F);
		ps.translate(0.0F, -1.501F, 0.0F);
		model.setupAnim(s);
		collector.submitModel(model, s, ps, RenderTypes.entityCutoutNoCull(TEXTURE), s.lightCoords, OverlayTexture.NO_OVERLAY, -1, null, s.outlineColor, null);
		ps.popPose();
		super.submit(s, ps, collector, cam);
	}
}
