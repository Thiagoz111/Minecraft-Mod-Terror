package com.deadline.client.model;

import com.deadline.client.model.gen.BalloonModelBase;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.util.Mth;

/** The red balloon bobs and turns slowly on its string. */
public class BalloonModel extends BalloonModelBase {
	public BalloonModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(EntityRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		this.string.xRot += Mth.sin(t * 0.07F) * 0.08F;
		this.string.zRot += Mth.sin(t * 0.05F + 1F) * 0.08F;
		this.balloon.yRot += t * 0.01F;
	}
}
