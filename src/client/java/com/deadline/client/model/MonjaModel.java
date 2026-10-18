package com.deadline.client.model;

import com.deadline.client.model.gen.MonjaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Sor Agonía: glides without steps, robe trailing; claws rise in the dark, she cowers and burns in the light. */
public class MonjaModel extends MonjaModelBase {
	public MonjaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float hunt = blend(s, 0, s.action == 1 ? 1F : 0F, 0.1F);
		float burn = blend(s, 1, s.action == 2 ? 1F : 0F, 0.25F);
		float scream = blend(s, 2, s.action == 3 ? 1F : 0F, 0.3F);
		float weak = blend(s, 3, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float glide = Math.min(1F, s.speed * 6F);

		offset("body", 0F, Mth.sin(t * 0.07F) * 0.8F - 0.6F, 0F);
		rot("body", glide * 0.15F, 0F, Mth.sin(t * 0.04F) * 0.02F);
		ripple("robe", t, 0.1F, 0.9F, 0.05F, 0.03F, glide * 0.3F);
		ripple("skirt", t, 0.1F, 0.9F, 0.05F, 0.03F, glide * 0.3F);
		ripple("sleeve", t, 0.12F, 1.1F, 0.04F, 0.03F, glide * 0.15F);
		rot("veil", Mth.sin(t * 0.08F) * 0.05F + glide * 0.35F, 0F, 0F);
		look(s, 0.5F);
		// neck snaps sideways now and then
		float window = (t + (s.seed % 23)) % 53F;
		float snap = window < 4F ? (1F - window / 4F) : 0F;
		rot("head", 0F, 0F, 0.22F * snap + Mth.sin(t * 0.03F) * 0.06F);
		rot("jaw", (Mth.sin(t * 0.06F) * 0.5F + 0.5F) * 0.06F, 0F, 0F);
		ripple("right_finger", t, 0.3F, 1.2F, 0.08F, 0F, 0.03F);
		ripple("left_finger", t, 0.28F, 1.1F, 0.08F, 0F, 0.03F);

		apply(pose("attack"), Math.max(Math.max(atk, hunt * 0.35F), scream));
		if (scream > 0.05F) {
			rot("jaw", 0.3F * scream + Mth.sin(t * 3.7F) * 0.06F * scream, 0F, 0F);
			rot("head", Mth.sin(t * 3.1F) * 0.06F * scream, Mth.sin(t * 2.3F) * 0.08F * scream, 0F);
		}
		apply(pose("burn"), burn);
		if (burn > 0.05F) {
			rot("body", Mth.sin(t * 6.1F) * 0.05F * burn, 0F, Mth.sin(t * 5.3F) * 0.05F * burn);
		}
		if (weak > 0.01F) {
			rot("body", 0.35F * weak, 0F, 0F);
		}
	}
}
