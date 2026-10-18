package com.deadline.client.render;

import com.deadline.DeadLine;
import com.deadline.entity.AnimaEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.PoseidaEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.Identifier;

/** Generic renderer for the haunts: texture + optional emissive layer + synced behaviour state. */
public class HauntRenderer<T extends HauntEntity, M extends EntityModel<HauntRenderState>> extends MobRenderer<T, HauntRenderState, M> {
	private final Identifier texture;

	public HauntRenderer(EntityRendererProvider.Context ctx, M model, float shadow, String key, boolean glow) {
		super(ctx, model, shadow);
		this.texture = DeadLine.id("textures/entity/" + key + ".png");
		if (glow) {
			this.addLayer(new GlowLayer<>(this, DeadLine.id("textures/entity/" + key + "_eyes.png")));
		}
	}

	@Override
	public HauntRenderState createRenderState() {
		return new HauntRenderState();
	}

	@Override
	public Identifier getTextureLocation(HauntRenderState state) {
		return texture;
	}

	@Override
	public void extractRenderState(T entity, HauntRenderState s, float pt) {
		super.extractRenderState(entity, s, pt);
		s.action = entity.action();
		s.weakened = entity.isWeakened();
		s.stunned = entity.isStunned();
		s.anchored = entity.isAnchored();
		s.attackAnim = entity.getAttackAnim(pt);
		s.climbing = entity instanceof PoseidaEntity p && p.isClimbing();
		s.revealed = entity instanceof AnimaEntity a && a.isRevealed();
		s.speed = (float) entity.getDeltaMovement().horizontalDistance();
		s.seed = entity.getId();
	}

	@Override
	protected boolean isShaking(HauntRenderState s) {
		return s.stunned || s.weakened || super.isShaking(s);
	}
}
