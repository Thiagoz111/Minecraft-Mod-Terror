package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.JorgeModelBase;
import com.deadline.client.render.HauntRenderState;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Jorge Morales, quiet and broken: he stands swaying slowly from foot to foot, breathing heavily; points; sits in his
 * armchair or at the table (C: FamilyEntity.POSE_SIT); possessed (look 1: the grin, black eyes, the angry V) or the
 * copy (look 2). Follows the ANIM_NOTES of tools/models/ent_jorge.py (lean rule: leans go on 'chest', 'body' only
 * bobs; apron rule: the skirt hangs). The old comic beats -- the grill flip, the knife conducting, the fall into the
 * pool, the charcoal sack, the barbecue tongs -- were cut: their props stay hidden.
 */
public class JorgeModel extends JorgeModelBase {
	private static final int POINT = FamilyEntity.POSE_POINT, SIT = FamilyEntity.POSE_SIT;
	/** VARIANT_POSES['poseido']: the brows drop into an angry V, the grin shoves the moustache up. */
	private static final Map<String, float[]> POSEIDO = table(
			"right_brow", new float[] {0F, 0F, 0.42F, 0F, 1.4F, 0F},
			"left_brow", new float[] {0F, 0F, -0.34F, 0F, 0.5F, 0F},
			"moustache", new float[] {-0.08F, 0F, 0F, 0F, -0.8F, 0F});
	/** The salt-hit flinch (chest back, head back, jaw open; the apron flaps, minus the apron-rule share of the lean). */
	private static final Map<String, float[]> FLINCH = table(
			"chest", new float[] {-0.15F, 0F, 0F, 0F, 0F, 0F},
			"head", new float[] {-0.3F, 0F, 0F, 0F, 0F, 0F},
			"jaw", new float[] {0.5F, 0F, 0F, 0F, 0F, 0F},
			"apron_skirt", new float[] {-0.1F, 0F, 0F, 0F, 0F, 0F});
	private static final float RATE = 0.35F, TALK_RATE = 0.4F, POSSESS_RATE = 0.6F;

	public JorgeModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		boolean fresh = t < 4F;
		boolean possessed = s.variant == FamilyEntity.LOOK_POSSESSED;
		// B3: the copy (look 2, FamilyEntity.LOOK_COPIA): Jorge's body, perfectly still -- no sway
		boolean copy = s.variant == FamilyEntity.LOOK_COPIA;
		// B3: POSE_CORNER(_TURN) (facing a wall, perfectly still; then the head comes all the way round, the body does not)
		boolean corner = a == FamilyEntity.POSE_CORNER || a == FamilyEntity.POSE_CORNER_TURN;
		float twist = blend(s, 14, a == FamilyEntity.POSE_CORNER_TURN ? 1F : 0F, fresh ? 1F : 0.05F);
		boolean known = a == POINT;

		// ---- pose weights (the seat is its own channel under the idle upper body)
		float rate = fresh ? 1F : RATE;
		float idle = blend(s, 0, known ? 0F : 1F, rate);
		float fidget = copy || corner ? 0F : idle;
		float point = blend(s, 1, a == POINT ? 1F : 0F, rate);
		float sit = blend(s, 2, a == SIT ? 1F : 0F, fresh ? 1F : 0.2F);
		float poseido = blend(s, 6, possessed ? 1F : 0F, fresh ? 1F : POSSESS_RATE);
		float talk = blend(s, 7, FamilyRenderer.talking(s) ? 1F : 0F, TALK_RATE);
		// salt hit: the stun counter jumping up = a hit; a lagging copy turns the jump into a ~4-tick flinch
		float stun = FamilyRenderer.stun(s);
		float stunLag = blend(s, 8, stun, 0.5F);
		float flinch = Mth.clamp((stun - stunLag) / 12F, 0F, 1F);

		apply(POSE_IDLE, idle);
		apply(POSE_POINT, point);
		apply(POSE_SIT_CHAIR, sit);
		apply(POSEIDO, poseido);
		apply(FLINCH, flinch);

		// ---- toggles: TOGGLE_DEFAULT -> look -> pose (a pose wins); the old props never show
		smile.visible = possessed;
		smileJaw.visible = possessed;
		demonEyes.visible = possessed;
		bag.visible = false;
		tongs.visible = false;

		// ---- idle on every pose: breathing (chest + belly), a slow sway of the weight from foot to foot
		float breath = Mth.sin(t * 0.09F + Math.floorMod(seed, 29));
		lean(-0.01F * breath);
		offset("belly", 0F, 0F, -0.2F * (1F + breath));
		float sway = fidget * (1F - sit);
		rot("chest", 0F, 0.02F * Mth.sin(t * 0.03F + 1F) * sway, 0.03F * Mth.sin(t * 0.045F) * sway);
		rot("neck", 0F, 0F, -0.015F * Mth.sin(t * 0.045F) * sway);

		// ---- the jaw (only ever moves if something drives it: nobody speaks); possessed: the grin's halves chatter
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("jaw", (0.22F + 0.23F * poseido) * syl, 0F, 0F);
		offset("moustache", 0F, 0.3F * syl, 0F);
		rot("jaw", 0.03F * (1F + Mth.sin(t * 1.57F)) * poseido * (1F - talk), 0F, 0F);
		// the flinch: the belly is a jelly
		offset("belly", 0F, 0F, 0.8F * flinch * Mth.cos(t * 1.6F));

		// ---- walking (a heavy, slow walk)
		float ph = s.walkAnimationPos * 0.6662F;
		float sp = Math.min(1F, s.walkAnimationSpeed) * (1F - sit);
		float w = Mth.sin(ph);
		offset("body", 0F, Math.abs(w) * 0.8F * sp, 0F);
		rot("chest", 0F, w * 0.05F * sp, w * 0.06F * sp);
		offset("belly", 0F, Mth.sin(2F * ph - 0.6F) * 0.5F * sp, 0F);
		float rightLeg = w * 0.45F * sp;
		rot("right_leg", rightLeg, 0F, 0F);
		rot("left_leg", -rightLeg, 0F, 0F);
		rot("right_shin", Math.max(0F, Mth.sin(ph + 1.2F)) * 0.4F * sp, 0F, 0F);
		rot("left_shin", Math.max(0F, Mth.sin(ph + Mth.PI + 1.2F)) * 0.4F * sp, 0F, 0F);
		rot("right_arm", -w * 0.35F * sp, 0F, 0F);
		rot("left_arm", w * 0.35F * sp, 0F, 0F);
		// apron rule: the forward thigh pushes the hem forward, lagging ~2 ticks behind the legs
		float forwardThigh = Math.max(0F, Math.max(-rightLeg, rightLeg));
		rot("apron_hem", blend(s, 12, -0.6F * forwardThigh, 0.5F), 0F, 0F);

		// ---- head look (neck 30 %, head 70 %); C: with the stare it follows far further round than it should
		boolean stare = FamilyRenderer.staring(s);
		float lookW = corner ? 0F : 1F;
		float max = stare ? FamilyRenderer.STARE_MAX : 75F;
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -max, max) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.3F, yaw * 0.3F, 0F);
		rot("head", pitch * 0.7F, yaw * 0.7F, 0F);
		if (twist > 0.001F) {
			float e = twist * twist * (3F - 2F * twist);
			float hitch = Mth.sin(t * 9F) * 0.035F * Mth.clamp(twist * (1F - twist) * 4F, 0F, 1F);
			rot("neck", 0F, Mth.PI * 0.3F * e + hitch, 0F);
			rot("head", 0.1F * e, Mth.PI * 0.7F * e + hitch, 0.2F * e);
		}
		if (copy) {
			// the copy: brows level over the wide-open eyes, the painted grin keeps the jaw shut
			rightBrow.zRot = 0F;
			leftBrow.zRot = 0F;
			jaw.xRot = 0F;
		}
	}

	/** A chest lean with the apron rule: the skirt keeps hanging plumb. */
	private void lean(float x) {
		rot("chest", x, 0F, 0F);
		rot("apron_skirt", -x, 0F, 0F);
	}
}
