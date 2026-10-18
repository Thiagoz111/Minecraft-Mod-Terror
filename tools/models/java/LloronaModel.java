package com.deadline.client.model;

import com.deadline.client.model.gen.LloronaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** La Llorona: floats, hair and torn hem drift as if underwater; reaches out when chasing, wails when watched. */
public class LloronaModel extends LloronaModelBase {
	public LloronaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float chase = blend(s, 0, s.action == 1 ? 1F : 0F, 0.12F);
		float scream = blend(s, 1, s.action == 2 ? 1F : 0F, 0.3F);
		float weak = blend(s, 2, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float drift = Math.min(1F, s.speed * 6F);

		offset("body", 0F, Mth.sin(t * 0.08F) * 1.6F - 1.2F, 0F);
		rot("body", 0.05F + drift * 0.18F + weak * 0.35F, 0F, Mth.sin(t * 0.045F) * 0.03F);
		ripple("skirt_", t, 0.11F, 0.8F, 0.06F, 0.04F, drift * 0.35F + chase * 0.1F);
		ripple("hair_front_", t, 0.09F, 1.1F, 0.04F, 0.05F, 0F);
		ripple("hair_side_", t, 0.08F, 1.7F, 0.05F, 0.04F, drift * 0.2F);
		rot("hair_back", Mth.sin(t * 0.08F) * 0.05F + drift * 0.3F, 0F, 0F);
		rot("hair_back_lower", Mth.sin(t * 0.08F - 0.7F) * 0.08F + drift * 0.25F, 0F, 0F);
		rot("veil", Mth.sin(t * 0.1F) * 0.06F + drift * 0.35F, 0F, Mth.sin(t * 0.07F) * 0.04F);
		rot("veil_lower", Mth.sin(t * 0.1F - 0.9F) * 0.09F + drift * 0.3F, 0F, 0F);

		rot("right_arm", Mth.sin(t * 0.06F) * 0.05F, 0F, -0.03F);
		rot("left_arm", Mth.sin(t * 0.06F + 1.4F) * 0.05F, 0F, 0.03F);
		ripple("right_finger_", t, 0.3F, 1.2F, 0.08F, 0F, 0.04F);
		ripple("left_finger_", t, 0.27F, 1.4F, 0.08F, 0F, 0.04F);

		// eerie idle head tilt, eternal slow wail
		look(s, 0.45F);
		rot("head", 0F, 0F, (0.16F + Mth.sin(t * 0.03F) * 0.05F) * (1F - scream));
		rot("jaw", (Mth.sin(t * 0.05F) * 0.5F + 0.5F) * 0.14F, 0F, 0F);

		apply(pose("attack"), Math.max(chase * 0.55F, atk));
		apply(pose("scream"), scream);
		if (scream > 0.05F) {
			rot("head", 0F, Mth.sin(t * 2.7F) * 0.06F * scream, Mth.sin(t * 3.1F) * 0.07F * scream);
			rot("jaw", Mth.sin(t * 4.3F) * 0.05F * scream, 0F, 0F);
		}
		if (weak > 0.01F) {
			rot("neck", 0.35F * weak, 0F, 0F);
			rot("right_arm", 0.2F * weak, 0F, 0.1F * weak);
			rot("left_arm", 0.2F * weak, 0F, -0.1F * weak);
		}
	}
}
