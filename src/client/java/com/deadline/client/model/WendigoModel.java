package com.deadline.client.model;

import com.deadline.client.model.gen.WendigoModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** El Wendigo: digitigrade stalking gait, dragging claws, sudden head twitches, jaw chatter while hunting. */
public class WendigoModel extends WendigoModelBase {
	public WendigoModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		float hunt = blend(s, 0, s.action == 1 ? 1F : 0F, 0.1F);
		float scream = blend(s, 1, s.action == 2 ? 1F : 0F, 0.25F);
		float flee = blend(s, 2, s.action == 3 ? 1F : 0F, 0.2F);
		float weak = blend(s, 3, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float pos = s.walkAnimationPos * 0.55F;
		float spd = Math.min(1F, s.walkAnimationSpeed);

		// gait: thigh swings, shin folds back on the lift, hoof flicks
		for (int side = 0; side < 2; side++) {
			String lr = side == 0 ? "right" : "left";
			float ph = pos + side * Mth.PI;
			rot(lr + "_leg", Mth.cos(ph) * 0.65F * spd, 0F, 0F);
			rot(lr + "_shin", -Math.max(0F, Mth.sin(ph)) * 0.7F * spd, 0F, 0F);
			rot(lr + "_foot", Math.max(0F, Mth.sin(ph)) * 0.5F * spd, 0F, 0F);
			rot(lr + "_arm", Mth.cos(ph + Mth.PI) * 0.45F * spd, 0F, 0F);
			rot(lr + "_forearm", -0.1F - Math.max(0F, Mth.cos(ph)) * 0.35F * spd, 0F, 0F);
		}
		offset("body", 0F, -Math.abs(Mth.sin(pos)) * 1.5F * spd, 0F);

		// breathing, hunger
		rot("chest", Mth.sin(t * 0.09F) * 0.035F + hunt * 0.12F, 0F, 0F);
		rot("tail", Mth.sin(t * 0.07F) * 0.1F, Mth.sin(t * 0.05F) * 0.15F, 0F);
		look(s, 0.5F);
		// sudden head twitch every ~2 s, different per individual
		float window = (t + (s.seed % 17)) % 41F;
		if (window < 3F) {
			float dir = ((int) ((t + s.seed) / 41F) & 1) == 0 ? 1F : -1F;
			rot("head", 0F, 0.35F * dir * (1F - window / 3F), 0.25F * dir * (1F - window / 3F));
		}
		rot("jaw", (Mth.sin(t * 1.9F) * 0.5F + 0.5F) * 0.16F * hunt + 0.05F, 0F, 0F);
		ripple("right_finger", t, 0.25F, 0.9F, 0.06F, 0F, 0F);
		ripple("left_finger", t, 0.23F, 1.1F, 0.06F, 0F, 0F);

		apply(pose("attack"), Math.max(atk, hunt * 0.15F));
		apply(pose("scream"), Math.max(scream, flee * 0.35F));
		if (scream > 0.05F) {
			rot("head", Mth.sin(t * 3.3F) * 0.05F * scream, Mth.sin(t * 2.6F) * 0.08F * scream, 0F);
		}
		if (flee > 0.01F) {
			rot("body", -0.25F * flee, 0F, 0F);
		}
		if (weak > 0.01F) {
			rot("body", 0.3F * weak, 0F, 0F);
			rot("neck", 0.3F * weak, 0F, 0F);
		}
	}
}
