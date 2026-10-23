package com.deadline.client.model;

import com.deadline.client.model.gen.ManoModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.ApparitionEntities;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The grey hand under the bed (tools/models/ent_mano.py ANIM_NOTES): the fingers walk it out, dig into the boards with
 * a scratching tremor, then splay and drag as it is yanked back. The arm trails behind under the bed.
 */
public class ManoModel extends ManoModelBase {
	private static final String[] FINGERS = {"finger_4", "finger_3", "finger_2", "finger_1"};

	public ManoModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		float creep = blend(s, 0, a == ApparitionEntities.MANO_CREEP ? 1F : 0F, 0.4F);
		float grip = blend(s, 1, a == ApparitionEntities.MANO_GRIP ? 1F : 0F, 0.35F);
		float back = blend(s, 2, a == ApparitionEntities.MANO_RETRACT ? 1F : 0F, 0.6F);

		apply(POSE_REACH, creep * 0.35F + back);
		apply(POSE_GRIP, grip);
		for (int k = 0; k < FINGERS.length; k++) {
			// crawling: each finger lifts and plants in a wave from the little finger to the index
			float lift = Math.max(0F, Mth.sin(t * 0.55F + k * 1.3F)) * 0.45F * creep;
			// gripping: the nails scratch at the boards
			float scratch = Mth.sin(t * 2.2F + k) * 0.05F * grip;
			rot(FINGERS[k], -lift + scratch, 0F, 0F);
			rot(FINGERS[k] + "_tip", -lift * 0.6F + scratch, 0F, 0F);
			// dragged back: the tips trail
			rot(FINGERS[k] + "_tip", -0.2F * back, 0F, 0F);
		}
		rot("thumb", -Math.max(0F, Mth.sin(t * 0.55F + 5.2F)) * 0.3F * creep, 0F, 0F);
		offset("hand", 0F, -0.3F * Math.max(0F, Mth.sin(t * 1.1F)) * creep, 0F);
		// the elbow bends a little as the arm slides
		rot("upper_arm", 0F, Mth.sin(t * 0.08F) * 0.12F, 0F);
		rot("forearm", 0F, Mth.sin(t * 0.05F + 1F) * 0.04F, 0F);
	}
}
