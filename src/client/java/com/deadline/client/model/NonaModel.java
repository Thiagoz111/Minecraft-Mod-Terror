package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * La Nona Pocha: shuffles behind her squeaky walker, knits rocking in her chair, sits at the head of the table (C:
 * FamilyEntity.POSE_SIT -- seated with nothing under her but the chair she is on), stares with her head turned far
 * further round than a neck should (EXPR_STARE) and grins with her too-white dentures (EXPR_SMILE); possessed (look 1:
 * the bun undone into floating white tresses) she floats in the rocker in the 1961 room and screams with her dentures
 * floating. Follows the ANIM_NOTES of tools/models/ent_nona.py: one cross-faded pose at a time, toggles start from the
 * default look, then the look, then the pose. The old comic beats (the mate, the chancleta, the yarn) were cut: their
 * props stay hidden.
 */
public class NonaModel extends NonaModelBase {
	private static final int STAND_WALKER = FamilyEntity.POSE_STAND_WALKER, KNIT = FamilyEntity.POSE_KNIT_SIT,
			FLOAT = FamilyEntity.POSE_FLOAT_ROCK, SCREAM = FamilyEntity.POSE_SCREAM_DENTURES, SEW = FamilyEntity.POSE_SEW_CALM,
			SIT = FamilyEntity.POSE_SIT;
	/** Blend rates: poses ~6 ticks; into the scream ~3. Every pose channel moves at the same rate on a given tick. */
	private static final float RATE = 0.3F, FAST_RATE = 0.55F, TALK_RATE = 0.4F;
	/** Height of the floating rocker (texels; the float poses carry it in their 'base' row). */
	private static final float FLOAT_DY = -14F;
	/** How fast the rocker rises, and how slowly it comes down into 'sew_calm' (~60 ticks) or anything else. */
	private static final float RISE_RATE = 0.15F, LAND_CALM_RATE = 0.05F, LAND_RATE = 0.2F;
	/**
	 * C, the grin: the floating dentures brought back from in front of her face (parked 8 texels out at nose height)
	 * into her mouth, the lower plate closed up, the jaw a little dropped.
	 */
	private static final float[] GRIN_DENTURES = {0.21F, 0F, 0F, 0F, 3.5F, 7.5F};
	private static final float GRIN_LOWER = -0.45F, GRIN_JAW = 0.14F;

	private final ModelPart[] loose;

	public NonaModel(ModelPart root) {
		super(root);
		this.loose = new ModelPart[] {hairLoose0, hairLoose1, hairLoose2, hairLoose3, hairLoose4};
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		boolean fresh = t < 4F;
		boolean possessed = s.variant == FamilyEntity.LOOK_POSSESSED;
		boolean known = a == KNIT || a == FLOAT || a == SCREAM || a == SEW || a == SIT;
		boolean floatPose = FamilyEntity.floatPose(a);
		boolean grin = FamilyRenderer.smiling(s) && a != SCREAM;

		// ---- pose weights (mutually exclusive, cross-faded at one shared rate); anything unknown is the walker stance.
		// POSE_SIT is sew_calm's seated body without the rocker (the chair, the car seat is under her).
		float rate = fresh ? 1F : a == SCREAM ? FAST_RATE : RATE;
		float stand = blend(s, 0, known && a != STAND_WALKER ? 0F : 1F, rate);
		float knit = blend(s, 2, a == KNIT ? 1F : 0F, rate);
		float floatW = blend(s, 5, a == FLOAT ? 1F : 0F, rate);
		float scream = blend(s, 7, a == SCREAM ? 1F : 0F, rate);
		float sew = blend(s, 8, a == SEW || a == SIT ? 1F : 0F, rate);
		float chair = blend(s, 4, a == SIT ? 1F : 0F, rate);
		float talk = blend(s, 9, FamilyRenderer.talking(s) ? 1F : 0F, TALK_RATE);
		// the rocker's height has its own (slower) channel: she rises with the pose and comes down slowly into sew_calm
		float height = blend(s, 10, floatPose ? 1F : 0F, fresh ? 1F : floatPose ? RISE_RATE : a == SEW ? LAND_CALM_RATE : LAND_RATE);
		float grinW = blend(s, 13, grin ? 1F : 0F, fresh ? 1F : 0.35F);

		apply(POSE_STAND_WALKER, stand);
		apply(POSE_KNIT_SIT, knit);
		apply(POSE_FLOAT_ROCK, floatW);
		apply(POSE_SCREAM_DENTURES, scream);
		apply(POSE_SEW_CALM, sew);
		// swap the tables' built-in float (base dy -14) for the height channel
		offset("base", 0F, -FLOAT_DY * (floatW + scream) + FLOAT_DY * height, 0F);

		// ---- toggles: default look -> look -> pose; the walker and the rocker swap at the middle of the sit / stand
		float seatedW = knit + floatW + scream + sew;
		walker.visible = stand > 0.5F;
		rocker.visible = seatedW - chair > 0.5F;
		bun.visible = !possessed;
		// B2: the bones of the 'rota' look (the hunt, client/hunt/NonaRotaModel) never show on the family's Nona
		jawLong.visible = false;
		teethUpper.visible = false;
		rightTalons.visible = false;
		leftTalons.visible = false;
		spine.visible = false;
		for (ModelPart p : loose) {
			p.visible = possessed;
		}
		dentures.visible = a == SCREAM || grinW > 0.05F;  // floating in the scream; in her mouth in the grin
		rightSlipper.visible = true;
		chancleta.visible = false;
		mate.visible = false;
		needleRight.visible = a == KNIT;
		needleLeft.visible = a == KNIT;
		yarnRight.visible = false;
		yarnLeft.visible = false;

		// ---- idle on every pose: breathing, the deaf "¿qué?" tilt, a quick glance aside every 4-6 s (never in a stare)
		boolean stare = FamilyRenderer.staring(s);
		float still = (1F - scream) * (stare ? 0F : 1F);
		rot("chest", 0.025F * Mth.sin(t * 0.08F + Math.floorMod(seed, 23)), 0F, 0F);
		rot("head", 0F, 0F, 0.06F * Mth.sin(t * 0.035F) * still);
		float glance = FamilyRenderer.pulse(t, seed, 100F, 3F, 8F, 3F) * FamilyRenderer.side(t, seed, 100F);
		rot("head", 0F, 0.2F * glance * still * (1F - knit), 0F);

		// ---- per pose
		// knit_sit: the needles work, the chair rocks slowly
		rot("right_hand", 0.18F * Mth.sin(t * 0.5F) * knit, 0F, 0F);
		rot("left_hand", 0.12F * Mth.sin(t * 0.5F + 1.6F) * knit, 0F, 0F);
		rot("base", 0.06F * Mth.sin(t * 0.07F) * knit, 0F, 0F);
		// floating in the rocker: the bob and the rock about the floor contact
		float afloat = Math.max(height, FamilyRenderer.floating(s) ? 1F : 0F);
		offset("base", 0F, 0.8F * Mth.sin(t * 0.06F) * afloat, 0F);
		rot("base", 0.09F * Mth.sin(t * 0.08F) * height, 0F, 0F);
		// scream_dentures: the dentures drift and clack in front of the dislocated jaw
		if (a == SCREAM) {
			rot("dentures_lower", 0.35F * Math.abs(Mth.sin(t * 0.45F)), 0F, 0F);
			offset("dentures", 0F, 0.6F * Mth.sin(t * 0.1F), 0F);
			rot("dentures", 0F, 0.15F * Mth.sin(t * 0.07F), 0F);
		}
		// C, the grin: the dentures in her mouth, too white, the jaw just open
		if (grinW > 0.001F) {
			rot("dentures", GRIN_DENTURES[0] * grinW, 0F, 0F);
			offset("dentures", 0F, GRIN_DENTURES[4] * grinW, GRIN_DENTURES[5] * grinW);
			rot("dentures_lower", GRIN_LOWER * grinW, 0F, 0F);
			rot("jaw", GRIN_JAW * grinW, 0F, 0F);
		}
		// sew_calm: the hands work the last stitch, small and tender (seated on a chair: hands still in her lap)
		rot("right_hand", 0.05F * Mth.sin(t * 0.3F) * (sew - chair), 0F, 0F);
		rot("left_hand", -0.04F * Mth.sin(t * 0.3F + 0.7F) * (sew - chair), 0F, 0F);
		// possessed: the loose tresses drift slowly as if under water, out of phase per strand
		if (possessed) {
			ripple("hair_loose_", t, 0.05F, 1.3F, 0.10F, 0.14F, 0F);
			for (int k = 0; k < loose.length; k++) {
				loose[k].yRot += 0.06F * Mth.sin(t * 0.03F + 2.1F * k);
			}
		}

		// ---- the jaw (only ever moves if something drives it: nobody speaks)
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("jaw", 0.04F * talk + 0.18F * syl, 0F, 0F);

		// ---- walking (standing poses only): she shuffles; arms push the walker (no swing)
		float legs = Math.max(0F, 1F - seatedW);
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed) * legs;
		float swing = Mth.cos(pos) * 0.35F * spd;
		rot("right_leg", swing, 0F, 0F);
		rot("left_leg", -swing, 0F, 0F);
		float armAmp = walker.visible ? 0F : 0.2F;
		rot("right_arm", -Mth.cos(pos) * armAmp * spd, 0F, 0F);
		rot("left_arm", Mth.cos(pos) * armAmp * spd, 0F, 0F);
		rot("body", 0F, 0F, 0.03F * Mth.sin(pos) * spd);
		float forward = Math.min(swing, -swing);  // the forward leg's swing (negative)
		rot("skirt_front", 0.25F * forward, 0F, 0F);
		rot("skirt_hem", 0.125F * forward, 0F, 0F);
		rot("skirt_back", 0.2F * Math.abs(swing), 0F, 0F);
		rot("glasses", 0F, 0F, 0.05F * Mth.sin(pos * 2F) * spd);
		// the squeaky wheel turns with the distance walked
		rot("walker_wheel", s.walkAnimationPos * 3.2F, 0F, 0F);

		// ---- head look (neck 35 %, head 65 %): she looks up at you even while knitting; C: the stare follows round to
		// 170 degrees off the body, the neck taking its share of the impossible turn
		float lookW = 1F - 0.7F * scream - 0.5F * knit - 0.6F * (sew - chair);
		lookW = stare ? 1F : Math.max(0F, lookW);
		float max = stare ? FamilyRenderer.STARE_MAX : 75F;
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -max, max) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.35F, yaw * 0.35F, 0F);
		rot("head", pitch * 0.65F, yaw * 0.65F, 0F);
	}
}
