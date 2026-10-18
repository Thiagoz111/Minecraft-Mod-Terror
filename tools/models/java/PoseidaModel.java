package com.deadline.client.model;

import com.deadline.client.model.gen.PoseidaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Lucía: spider-walks on walls and ceilings, turns her head all the way round, levitates during the exorcism. */
public class PoseidaModel extends PoseidaModelBase {
	public PoseidaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float crawl = blend(s, 0, s.action == 1 || s.climbing ? 1F : 0F, 0.12F);
		float exo = blend(s, 1, s.action == 2 ? 1F : 0F, 0.08F);
		float spin = blend(s, 2, s.action == 3 ? 1F : 0F, 0.06F);
		float weak = blend(s, 3, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float pos = s.walkAnimationPos * 0.9F;
		float spd = Math.min(1F, s.walkAnimationSpeed);
		float upright = 1F - crawl;

		// normal stiff little walk
		walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.6F * upright, 0.25F * upright);
		look(s, 0.4F * upright);
		rot("head", 0F, 0F, (Mth.sin(t * 0.04F) * 0.25F) * upright * (1F - exo));
		rot("jaw", (Mth.sin(t * 0.07F) * 0.5F + 0.5F) * 0.08F, 0F, 0F);

		// spider-walk: diagonal limb pairs scuttle, head jerks
		apply(pose("spider"), crawl);
		if (crawl > 0.01F) {
			float a = Mth.cos(pos * 1.4F) * 0.45F * spd * crawl;
			rot("right_arm", a, 0F, 0F);
			rot("left_leg", a, 0F, 0F);
			rot("left_arm", -a, 0F, 0F);
			rot("right_leg", -a, 0F, 0F);
			rot("head", 0F, Mth.sin(t * 0.9F) * 0.12F * crawl, 0F);
		}

		// head turned all the way round
		apply(pose("headturn"), spin);

		// exorcism: levitating, convulsing
		apply(pose("float"), exo);
		if (exo > 0.01F) {
			offset("base", 0F, -6F * exo + Mth.sin(t * 0.1F) * 1.5F * exo, 0F);
			rot("body", Mth.sin(t * 5.3F) * 0.05F * exo, 0F, Mth.sin(t * 4.1F) * 0.06F * exo);
			rot("head", Mth.sin(t * 6.7F) * 0.12F * exo, Mth.sin(t * 5.9F) * 0.18F * exo, 0F);
			rot("jaw", (Mth.sin(t * 2.1F) * 0.5F + 0.5F) * 0.5F * exo, 0F, 0F);
		}
		apply(pose("attack"), atk);
		ripple("right_finger", t, 0.4F, 1.3F, 0.07F, 0F, 0F);
		ripple("left_finger", t, 0.37F, 1.1F, 0.07F, 0F, 0F);
		ripple("hair", t, 0.08F, 1.0F, 0.04F, 0.03F, 0F);
		if (weak > 0.01F) {
			rot("neck", 0.4F * weak, 0F, 0F);
		}
	}
}
