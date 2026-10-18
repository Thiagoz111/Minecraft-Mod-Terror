package com.deadline.client.model;

import com.deadline.client.model.gen.AnimaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** The lost soul: drifts, its tail undulating, and every few seconds lets out a silent scream. */
public class AnimaModel extends AnimaModelBase {
	public AnimaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float cycle = (t + s.seed * 13) % 120F;
		float scream = blend(s, 0, cycle < 35F ? 1F : 0F, 0.2F);

		offset("body", 0F, Mth.sin(t * 0.09F) * 2.2F - 1F, 0F);
		rot("body", 0.08F + Mth.sin(t * 0.05F) * 0.04F, 0F, Mth.sin(t * 0.04F) * 0.05F);
		ripple("tail", t, 0.16F, -0.7F, 0.18F, 0.1F, 0F);
		ripple("hair", t, 0.13F, 0.9F, 0.08F, 0.06F, 0F);
		rot("right_arm", Mth.sin(t * 0.08F) * 0.15F, 0F, Mth.cos(t * 0.06F) * 0.08F);
		rot("left_arm", Mth.sin(t * 0.08F + 1.6F) * 0.15F, 0F, Mth.cos(t * 0.06F + 1.6F) * 0.08F);
		look(s, 0.3F);
		apply(pose("scream"), Math.max(scream, atk));
		if (scream > 0.05F) {
			rot("head", Mth.sin(t * 2.9F) * 0.05F * scream, Mth.sin(t * 2.3F) * 0.06F * scream, 0F);
		}
	}
}
