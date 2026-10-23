package com.deadline.client.model;

import com.deadline.client.model.gen.PoseidaModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.entity.PoseidaEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Lucía (tools/models/ent_poseida.py ANIM_NOTES). Two looks on one rig, each with its own geometry (toggles):
 * <ul>
 *   <li>look 0 'normal' (the girl at dinner): braids, child hands, the shy stance (stand_normal) or sitting at the table
 *   ({@link PoseidaEntity#ACT_SIT}: sit_chair); the jaw never opens (the smile is painted across the seam).</li>
 *   <li>look 1 'poseida' (the host): the black mane, the claws, the burned sweater. Spider-walks on walls (ACT_CRAWL /
 *   climbing), turns her head all the way round, levitates for the exorcism, and -- scripted -- hangs upside down from
 *   the ceiling with every limb bent the wrong way and her face turned down at you ({@link PoseidaEntity#ACT_CEILING},
 *   {@link PoseidaEntity#ACT_CEILING_RUN}: the fast scuttle).</li>
 * </ul>
 */
public class PoseidaModel extends PoseidaModelBase {
	private static final String[] NORMAL_ONLY = {"braid_right", "braid_left", "right_mitt", "left_mitt"};
	private static final String[] POSSESSED_ONLY = {"hair_back", "hair_right", "hair_left", "right_claw", "left_claw", "sweater_burn"};

	public PoseidaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		boolean possessed = s.variant == PoseidaEntity.LOOK_POSSESSED;
		// ---- toggles: TOGGLE_DEFAULT -> look (-> pose: 'dazed' only, not used here)
		for (String n : NORMAL_ONLY) {
			hide(n, possessed);
		}
		for (String n : POSSESSED_ONLY) {
			hide(n, !possessed);
		}
		hide("dizzy_eyes", true);
		if (possessed) {
			possessed(s);
		} else {
			girl(s);
		}
	}

	/** The girl: shy, still, hands together; seated at the table. Small steps; the jaw never moves. */
	private void girl(HauntRenderState s) {
		float t = s.ageInTicks;
		boolean fresh = t < 4F;
		float sit = blend(s, 0, s.action == PoseidaEntity.ACT_SIT ? 1F : 0F, fresh ? 1F : 0.15F);
		apply(POSE_STAND_NORMAL, 1F - sit);
		apply(POSE_SIT_CHAIR, sit);
		float stand = 1F - sit;
		walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.45F * stand, 0F);
		rot("body", Mth.sin(t * 0.08F) * 0.015F, 0F, 0F);
		// a curious tilt now and then, the head following whoever is near (less while seated: she does not look at you)
		look(s, 0.4F * (1F - 0.7F * sit));
		rot("head", 0F, 0F, Mth.sin(t * 0.03F + s.seed) * 0.08F * stand);
		ripple("hem_", t, 0.09F, 1.2F, 0.02F, 0.015F, 0F);
	}

	private void possessed(HauntRenderState s) {
		float t = s.ageInTicks;
		boolean fresh = t < 4F;
		int a = s.action;
		boolean ceiling = a == PoseidaEntity.ACT_CEILING || a == PoseidaEntity.ACT_CEILING_RUN;
		float ceil = blend(s, 4, ceiling ? 1F : 0F, fresh ? 1F : 0.5F);
		float scuttle = blend(s, 5, a == PoseidaEntity.ACT_CEILING_RUN ? 1F : 0F, 0.4F);
		float crawl = blend(s, 0, (a == PoseidaEntity.ACT_CRAWL || s.climbing) && !ceiling ? 1F : 0F, 0.12F);
		float exo = blend(s, 1, a == PoseidaEntity.ACT_EXORCISM ? 1F : 0F, 0.08F);
		float spin = blend(s, 2, a == PoseidaEntity.ACT_HEADSPIN ? 1F : 0F, 0.06F);
		float weak = blend(s, 3, s.weakened ? 1F : 0F, 0.08F);
		float atk = s.attackAnim > 0F ? Mth.sin(s.attackAnim * Mth.PI) : 0F;
		float pos = s.walkAnimationPos * 0.9F;
		float spd = Math.min(1F, s.walkAnimationSpeed);
		float upright = (1F - crawl) * (1F - ceil);

		// normal stiff little walk
		walk(s, "left_leg", "right_leg", "left_arm", "right_arm", 0.6F * upright, 0.25F * upright);
		look(s, 0.4F * upright);
		rot("head", 0F, 0F, (Mth.sin(t * 0.04F) * 0.25F) * upright * (1F - exo));
		rot("jaw", (Mth.sin(t * 0.07F) * 0.5F + 0.5F) * 0.08F, 0F, 0F);

		// spider-walk: diagonal limb pairs scuttle, head jerks
		apply(pose("spider"), crawl);
		if (crawl > 0.01F) {
			float c = Mth.cos(pos * 1.4F) * 0.45F * spd * crawl;
			rot("right_arm", c, 0F, 0F);
			rot("left_leg", c, 0F, 0F);
			rot("left_arm", -c, 0F, 0F);
			rot("right_leg", -c, 0F, 0F);
			rot("head", 0F, Mth.sin(t * 0.9F) * 0.12F * crawl, 0F);
		}

		// on the ceiling: upside down, limbs bent the wrong way, the face down at you; the scuttle is FAST and twitchy
		apply(POSE_CEILING_CRAWL, ceil);
		if (ceil > 0.01F) {
			float w = t * 1.9F;
			float c = Mth.cos(w) * 0.42F * scuttle * ceil;
			float jerk = Mth.sin(w * 2.3F) * 0.08F * scuttle * ceil;
			rot("right_arm", c, 0F, jerk);
			rot("left_leg", c, 0F, -jerk);
			rot("left_arm", -c, 0F, -jerk);
			rot("right_leg", -c, 0F, jerk);
			rot("right_forearm", Math.max(0F, -c) * 0.6F, 0F, 0F);
			rot("left_forearm", Math.max(0F, c) * 0.6F, 0F, 0F);
			offset("base", 0F, -Math.abs(Mth.sin(w)) * 0.6F * scuttle * ceil, 0F);
			// still: the head twitches, the jaw hangs and shivers
			float still = 1F - scuttle;
			rot("head", 0F, Mth.sin(t * 0.9F) * 0.12F * ceil + (Math.floorMod((int) t + s.seed, 53) < 2 ? 0.3F * still * ceil : 0F), 0F);
			rot("jaw", Mth.sin(t * 3.1F) * 0.04F * ceil, 0F, 0F);
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
		ripple("hem_", t, 0.09F, 1.2F, 0.04F, 0.03F, 0F);
		if (weak > 0.01F) {
			rot("neck", 0.4F * weak, 0F, 0F);
		}
	}
}
