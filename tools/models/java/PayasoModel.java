package com.deadline.client.model;

import com.deadline.client.model.gen.PayasoModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Sonrisas: lurching gait, slow head tilt, the balloon bobbing on its string, a laugh that shakes the whole body. */
public class PayasoModel extends PayasoModelBase {
	public PayasoModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float frenzy = blend(s, 0, s.action == 2 ? 1F : 0F, 0.15F);
		float laugh = blend(s, 1, s.action == 3 ? 1F : 0F, 0.3F);
		float weak = blend(s, 2, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed);

		walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.75F, 0.55F);
		rot("body", 0F, Mth.sin(pos) * 0.1F * spd, Mth.sin(pos) * 0.09F * spd);
		offset("body", 0F, -Math.abs(Mth.cos(pos)) * 1.2F * spd, 0F);
		look(s, 0.35F);
		rot("head", 0F, 0F, Mth.sin(t * 0.035F) * 0.28F * (1F - laugh));
		rot("hair_left", Mth.sin(t * 0.2F) * 0.05F, 0F, Mth.sin(t * 0.17F) * 0.06F);
		rot("hair_right", Mth.sin(t * 0.2F + 1F) * 0.05F, 0F, Mth.sin(t * 0.17F + 1F) * 0.06F);
		rot("hat", 0F, 0F, Mth.sin(t * 0.05F) * 0.04F);
		rot("balloon_string", Mth.sin(t * 0.07F) * 0.1F, 0F, Mth.sin(t * 0.05F) * 0.09F);
		rot("balloon", -Mth.sin(t * 0.07F) * 0.06F, Mth.sin(t * 0.03F) * 0.3F, 0F);

		apply(pose("attack"), Math.max(atk, frenzy * 0.3F));
		apply(pose("laugh"), laugh);
		if (laugh > 0.05F) {
			rot("head", 0F, Mth.sin(t * 2.2F) * 0.14F * laugh, Mth.sin(t * 1.7F) * 0.1F * laugh);
			rot("jaw", (Mth.sin(t * 1.6F) * 0.5F + 0.5F) * 0.35F * laugh, 0F, 0F);
			rot("body", Mth.sin(t * 3.2F) * 0.04F * laugh, 0F, 0F);
		}
		if (weak > 0.01F) {
			rot("body", 0.3F * weak, 0F, 0F);
		}
	}
}
