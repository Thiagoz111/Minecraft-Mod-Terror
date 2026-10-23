package com.deadline.client.hunt;

import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.hunt.NonaRotaEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.world.phys.AABB;

/**
 * The broken Nona: look 0 = nona_rota.png (+ nona_rota_eyes.png: the milky cataracts glow faintly in the dark), look
 * 1 = nona_poseida.png (the first seconds of "La Nona se rompe"). A little bigger than the family's Nona; the culling
 * box covers the stretched body (she stands ~2.5 blocks while her hitbox stays door-sized).
 */
public class NonaRotaRenderer extends FamilyRenderer<NonaRotaEntity, NonaRotaModel> {
	/** + ticks since the current action started (the transformation timeline, the search lean...). */
	public static class State extends FamilyRenderer.State {
		public float actionTime;
	}

	public NonaRotaRenderer(EntityRendererProvider.Context ctx) {
		super(ctx, new NonaRotaModel(ctx.bakeLayer(HuntClient.NONA_ROTA_LAYER)), 0.55F, "nona", true, "rota", "poseida");
	}

	@Override
	public HauntRenderState createRenderState() {
		return new State();
	}

	@Override
	public void extractRenderState(NonaRotaEntity entity, HauntRenderState s, float pt) {
		super.extractRenderState(entity, s, pt);
		if (s instanceof State st) {
			st.actionTime = (float) (entity.level().getGameTime() - entity.actionAt()) + pt;
		}
	}

	@Override
	protected void scale(HauntRenderState s, PoseStack poseStack) {
		poseStack.scale(1.12F, 1.12F, 1.12F);
	}

	@Override
	protected AABB getBoundingBoxForCulling(NonaRotaEntity entity) {
		return super.getBoundingBoxForCulling(entity).expandTowards(0.0, 1.4, 0.0).inflate(0.6, 0.0, 0.6);
	}
}
