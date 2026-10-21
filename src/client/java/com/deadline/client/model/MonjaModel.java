package com.deadline.client.model;

import com.deadline.client.model.gen.MonjaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Sor Agonía: glides without steps, robe trailing; claws rise in the dark, she cowers and burns in the light. */
public class MonjaModel extends MonjaModelBase {
	/** Scripted actions (MonjaEntity.ACT_*) that have their own pose, by blend channel 4..10. */
	private static final String[] SCRIPTED = {"conduct", "sit", "ceiling", "blow", "wet", "kneel_wall", "reveal"};

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
		float[] scripted = new float[SCRIPTED.length];
		float still = 0F;
		for (int i = 0; i < SCRIPTED.length; i++) {
			scripted[i] = blend(s, 4 + i, s.action == 4 + i ? 1F : 0F, i == 2 || i == 6 ? 0.12F : 0.2F);
			still = Math.max(still, scripted[i]);
		}
		float idle = 1F - still;

		offset("body", 0F, (Mth.sin(t * 0.07F) * 0.8F - 0.6F) * idle, 0F);
		rot("body", glide * 0.15F, 0F, Mth.sin(t * 0.04F) * 0.02F * idle);
		ripple("robe", t, 0.1F, 0.9F, 0.05F, 0.03F, glide * 0.3F);
		ripple("scapular", t, 0.1F, 1.1F, 0.04F, 0.02F, glide * 0.25F);
		ripple("sleeve", t, 0.12F, 1.1F, 0.04F, 0.03F, glide * 0.15F);
		rot("veil", Mth.sin(t * 0.08F) * 0.05F + glide * 0.35F, 0F, 0F);
		rot("veil_lower", glide * 0.35F, 0F, 0F);
		rot("veil_right", 0F, 0F, Mth.sin(t * 0.07F) * 0.05F);
		rot("veil_left", 0F, 0F, -Mth.sin(t * 0.07F + 1.3F) * 0.05F);
		rot("hood_right", glide * 0.2F, 0F, 0F);
		rot("hood_left", glide * 0.2F, 0F, 0F);
		rot("chest", Mth.sin(t * 0.06F) * 0.03F, 0F, 0F);
		rot("rosary", Mth.sin(t * 0.09F - 0.6F) * 0.06F + glide * 0.2F, 0F, Mth.sin(t * 0.07F) * 0.04F);
		rot("cross", Mth.sin(t * 0.08F - 0.4F) * 0.05F + glide * 0.15F, 0F, 0F);
		rot("keys", 0F, 0F, Mth.sin(t * 0.9F) * 0.06F * glide + 0.25F * atk);
		look(s, 0.5F * idle);
		// neck snaps sideways now and then (never while a scripted pose holds her still)
		float window = (t + (s.seed % 23)) % 53F;
		float snap = window < 4F ? (1F - window / 4F) : 0F;
		rot("head", 0F, 0F, (0.22F * snap + Mth.sin(t * 0.03F) * 0.06F) * idle);
		rot("jaw", (Mth.sin(t * 0.06F) * 0.5F + 0.5F) * 0.06F, 0F, 0F);
		ripple("right_finger", t, 0.3F, 1.2F, 0.08F, 0F, 0.03F);
		ripple("left_finger", t, 0.28F, 1.1F, 0.08F, 0F, 0.03F);

		apply(pose("attack"), Math.max(Math.max(atk, hunt * 0.35F), scream) * idle);
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

		for (int i = 0; i < SCRIPTED.length; i++) {
			if (scripted[i] > 0.001F) {
				apply(pose(SCRIPTED[i]), scripted[i]);
			}
		}
		float conduct = scripted[0];
		if (conduct > 0.05F) {
			// the index finger beats time; the bell trembles in the other hand
			rot("right_forearm", Mth.sin(t * 0.42F) * 0.18F * conduct, 0F, 0F);
			rot("right_hand", Mth.sin(t * 0.42F - 0.5F) * 0.12F * conduct, 0F, 0F);
			rot("bell", 0F, 0F, Mth.sin(t * 0.84F) * 0.05F * conduct);
		}
		float ceiling = scripted[2];
		if (ceiling > 0.05F) {
			rot("left_arm", 0F, 0F, Mth.sin(t * 0.21F) * 0.08F * ceiling);
			rot("right_arm", 0F, 0F, -Mth.sin(t * 0.23F + 1F) * 0.08F * ceiling);
			rot("head", 0F, Mth.sin(t * 0.05F) * 0.3F * ceiling, 0F);
		}
		float wet = scripted[4];
		if (wet > 0.05F) {
			rot("head", Mth.sin(t * 0.11F) * 0.04F * wet, Mth.sin(t * 0.05F) * 0.25F * wet, 0F);
		}
	}
}
