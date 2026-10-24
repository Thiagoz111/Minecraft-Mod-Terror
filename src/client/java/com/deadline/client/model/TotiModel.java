package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.TotiModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Toti, the youngest: quiet, arms hanging at his sides, his eyes on whoever is near; crouched in the wardrobe, standing
 * in a corner with his face to the wall (B3), seated at the table or drawing at the kitchen table (C:
 * FamilyEntity.POSE_SIT). Follows the ANIM_NOTES of tools/models/ent_toti.py; the old comic beats (the gamepad
 * mashing, the ranked-match rage, the door slam, the breakfast shrug) were cut: the gamepad stays hidden.
 */
public class TotiModel extends TotiModelBase {
	private static final int CROUCH = FamilyEntity.POSE_CROUCH_CLOSET, SIT = FamilyEntity.POSE_SIT;
	/** B3 (toti_rincon): in the corner, facing the wall; the turn = the head goes all the way round, the body does not. */
	private static final int CORNER = FamilyEntity.POSE_CORNER, CORNER_TURN = FamilyEntity.POSE_CORNER_TURN;
	/** Blend rates: poses ~5 ticks. */
	private static final float RATE = 0.35F, TALK_RATE = 0.4F;
	/** The concentration tongue (crouch_closet's 'tongue' row): kept in (he does not play any more). */
	private static final float[] TONGUE = POSE_CROUCH_CLOSET.getOrDefault("tongue", new float[6]);

	public TotiModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		boolean fresh = t < 4F;
		boolean talking = FamilyRenderer.talking(s);

		float crouch = blend(s, 0, a == CROUCH ? 1F : 0F, fresh ? 1F : RATE);
		float sit = blend(s, 2, a == SIT ? 1F : 0F, fresh ? 1F : 0.2F);
		float talk = blend(s, 3, talking ? 1F : 0F, TALK_RATE);
		boolean copy = s.variant == FamilyEntity.LOOK_COPIA;
		boolean corner = a == CORNER || a == CORNER_TURN;
		float twist = blend(s, 10, a == CORNER_TURN ? 1F : 0F, fresh ? 1F : 0.05F);

		apply(POSE_CROUCH_CLOSET, crouch);
		apply(POSE_SIT_CHAIR, sit);
		// the tongue stays in
		rot("tongue", -TONGUE[0] * crouch, -TONGUE[1] * crouch, -TONGUE[2] * crouch);
		offset("tongue", -TONGUE[3] * crouch, -TONGUE[4] * crouch, -TONGUE[5] * crouch);

		// breathing (in the corner he does not breathe)
		offset("body", 0F, 0.125F * (1F + Mth.sin(t * 0.105F)) * (corner ? 0F : 1F), 0F);
		// arms down at his sides (the rest pose holds the pad): undo the rest rotations of arm, forearm and hand
		rot("right_arm", 0.2443F, 0.1396F, -0.1396F);
		rot("right_forearm", 0.9774F, 0.3142F, 0F);
		rot("right_hand", -0.5258F, -0.3499F, -0.3548F);
		rot("left_arm", 0.2443F, -0.1396F, 0.1396F);
		rot("left_forearm", 0.9774F, -0.3142F, 0F);
		rot("left_hand", -0.5258F, 0.3499F, 0.3548F);
		hide("gamepad", true);

		// ---- the jaw (only ever moves if something drives it: nobody speaks)
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("jaw", 0.3F * syl, 0F, 0F);
		float pitchNow = head.xRot + neck.xRot;
		float pitchLag = blend(s, 7, pitchNow, 0.5F);
		rot("fringe", Mth.clamp((pitchNow - pitchLag) * 0.8F, -0.1F, 0.05F), 0F, 0F);

		// ---- walking: a small arm swing, soles kept flat
		float legs = Math.max(0F, 1F - crouch - sit);
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed) * legs;
		float leg = Mth.sin(pos) * 0.45F * spd;
		float shinR = Math.max(0F, Mth.sin(pos + 1.2F)) * 0.5F * spd;
		float shinL = Math.max(0F, Mth.sin(pos + Mth.PI + 1.2F)) * 0.5F * spd;
		rot("right_leg", leg, 0F, 0F);
		rot("left_leg", -leg, 0F, 0F);
		rot("right_shin", shinR, 0F, 0F);
		rot("left_shin", shinL, 0F, 0F);
		rot("right_foot", -(leg + shinR) * 0.5F, 0F, 0F);
		rot("left_foot", -(-leg + shinL) * 0.5F, 0F, 0F);
		rot("right_arm", -leg * 0.4F, 0F, 0F);
		rot("left_arm", leg * 0.4F, 0F, 0F);
		offset("body", 0F, Math.abs(Mth.sin(pos)) * 0.6F * spd, 0F);

		// ---- head look (neck 35 %, head 65 %); C: with the stare it follows far further round than it should
		boolean stare = FamilyRenderer.staring(s);
		float lookW = corner ? 0F : 1F;
		float max = stare ? FamilyRenderer.STARE_MAX : 75F;
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -max, max) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.35F, yaw * 0.35F, 0F);
		rot("head", pitch * 0.65F, yaw * 0.65F, 0F);

		// ---- B3: the turn -- the head comes all the way round (neck 35 %, head 65 %) with two small hitches, the body
		// does not move; it ends tipped a little onto one shoulder
		if (twist > 0.001F) {
			float e = twist * twist * (3F - 2F * twist);
			float hitch = Mth.sin(t * 9F) * 0.035F * Mth.clamp(twist * (1F - twist) * 4F, 0F, 1F);
			rot("neck", 0F, Mth.PI * 0.35F * e + hitch, 0F);
			rot("head", 0.1F * e, Mth.PI * 0.65F * e + hitch, 0.22F * e);
		}
		if (copy) {
			// the copy: brows level over the wide-open eyes, the painted grin keeps the jaw shut
			rightBrow.zRot = 0F;
			leftBrow.zRot = 0F;
			jaw.xRot = 0F;
		}
	}
}
