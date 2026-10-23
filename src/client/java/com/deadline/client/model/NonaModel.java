package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.client.render.HauntRenderState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * La Nona Pocha: shuffles behind her squeaky walker, offers mate, knits rocking in her chair, throws the chancleta,
 * and possessed (look 1: bun undone into floating white tresses) floats in the rocker in the 1961 room, casts the red
 * yarn and screams with her dentures floating. Follows the ANIM_NOTES of tools/models/ent_nona.py: one cross-faded
 * pose at a time, toggles start from the default look, then the look, then the pose.
 */
public class NonaModel extends NonaModelBase {
	private static final int STAND_WALKER = FamilyEntity.POSE_STAND_WALKER, OFFER_MATE = FamilyEntity.POSE_OFFER_MATE,
			KNIT = FamilyEntity.POSE_KNIT_SIT, NO_WALKER = FamilyEntity.POSE_STAND_NO_WALKER, THROW = FamilyEntity.POSE_THROW_CHANCLETA,
			FLOAT = FamilyEntity.POSE_FLOAT_ROCK, YARN = FamilyEntity.POSE_YARN_CAST, SCREAM = FamilyEntity.POSE_SCREAM_DENTURES,
			SEW = FamilyEntity.POSE_SEW_CALM;
	/**
	 * Blend rates: poses ~6 ticks; into the throw and the scream ~3; the throw's release 3. Every pose channel moves at
	 * the same rate on a given tick (the one the incoming pose sets, or the release's while the throw fades out), so the
	 * weights keep summing to 1 mid-blend as the ANIM_NOTES ask.
	 */
	private static final float RATE = 0.3F, FAST_RATE = 0.55F, RELEASE_RATE = 0.6F, TALK_RATE = 0.4F;
	/** Height of the floating rocker (texels; the float poses carry it in their 'base' row). */
	private static final float FLOAT_DY = -14F;
	/** How fast the rocker rises, and how slowly it comes down into 'sew_calm' (~60 ticks) or anything else. */
	private static final float RISE_RATE = 0.15F, LAND_CALM_RATE = 0.05F, LAND_RATE = 0.2F;

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
		boolean known = a == OFFER_MATE || a == KNIT || a == NO_WALKER || a == THROW || a == FLOAT || a == YARN || a == SCREAM || a == SEW;
		boolean floatPose = FamilyEntity.floatPose(a);

		// ---- pose weights (mutually exclusive, cross-faded at one shared rate); anything unknown is the walker stance
		float rate = fresh ? 1F : a == THROW || a == SCREAM ? FAST_RATE : RATE;
		float release = Math.max(rate, RELEASE_RATE);
		float throwW = blend(s, 4, a == THROW ? 1F : 0F, a == THROW ? rate : release);
		if (a != THROW && throwW > 0.02F) {
			rate = release;
		}
		float stand = blend(s, 0, known && a != STAND_WALKER ? 0F : 1F, rate);
		float offer = blend(s, 1, a == OFFER_MATE ? 1F : 0F, rate);
		float knit = blend(s, 2, a == KNIT ? 1F : 0F, rate);
		float noWalker = blend(s, 3, a == NO_WALKER ? 1F : 0F, rate);
		float floatW = blend(s, 5, a == FLOAT ? 1F : 0F, rate);
		float yarn = blend(s, 6, a == YARN ? 1F : 0F, rate);
		float scream = blend(s, 7, a == SCREAM ? 1F : 0F, rate);
		float sew = blend(s, 8, a == SEW ? 1F : 0F, rate);
		float talk = blend(s, 9, FamilyRenderer.talking(s) ? 1F : 0F, TALK_RATE);
		// the rocker's height has its own (slower) channel: she rises with the pose and comes down slowly into sew_calm
		float height = blend(s, 10, floatPose ? 1F : 0F, fresh ? 1F : floatPose ? RISE_RATE : a == SEW ? LAND_CALM_RATE : LAND_RATE);
		float relFast = blend(s, 11, a == THROW ? 1F : 0F, fresh ? 1F : 0.8F);
		float relSlow = blend(s, 12, a == THROW ? 1F : 0F, fresh ? 1F : 0.4F);
		float snap = Mth.clamp((relSlow - relFast) * 4F, 0F, 1F);
		// the yarn shoots out of her hands over ~4 ticks when the cast starts
		float shoot = blend(s, 13, a == YARN ? 1F : 0F, a == YARN ? (fresh ? 1F : 0.45F) : 1F);

		apply(POSE_STAND_WALKER, stand);
		apply(POSE_OFFER_MATE, offer);
		apply(POSE_KNIT_SIT, knit);
		apply(POSE_STAND_NO_WALKER, noWalker);
		apply(POSE_THROW_CHANCLETA, throwW);
		apply(POSE_FLOAT_ROCK, floatW);
		apply(POSE_YARN_CAST, yarn);
		apply(POSE_SCREAM_DENTURES, scream);
		apply(POSE_SEW_CALM, sew);
		// swap the tables' built-in float (base dy -14) for the height channel
		offset("base", 0F, -FLOAT_DY * (floatW + yarn + scream) + FLOAT_DY * height, 0F);

		// ---- toggles: default look -> look -> pose; the walker and the rocker swap at the middle of the sit / stand
		float seatedW = knit + floatW + yarn + scream + sew;
		walker.visible = stand + offer > 0.5F;
		rocker.visible = seatedW > 0.5F;
		bun.visible = !possessed;
		for (ModelPart p : loose) {
			p.visible = possessed;
		}
		dentures.visible = a == SCREAM;  // the pose wins over the look (scream_dentures is staged 'poseida' anyway)
		rightSlipper.visible = a != THROW;
		chancleta.visible = a == THROW;
		mate.visible = a == OFFER_MATE;
		needleRight.visible = a == KNIT;
		needleLeft.visible = a == KNIT;
		yarnRight.visible = a == YARN;
		yarnLeft.visible = a == YARN;

		// ---- idle on every pose: breathing, the deaf "¿qué?" tilt, a quick glance aside every 4-6 s
		float still = 1F - Math.max(scream, throwW);
		rot("chest", 0.025F * Mth.sin(t * 0.08F + Math.floorMod(seed, 23)), 0F, 0F);
		rot("head", 0F, 0F, 0.06F * Mth.sin(t * 0.035F) * still);
		float glance = FamilyRenderer.pulse(t, seed, 100F, 3F, 8F, 3F) * FamilyRenderer.side(t, seed, 100F);
		rot("head", 0F, 0.2F * glance * still * (1F - knit), 0F);

		// ---- per pose
		// knit_sit: the needles work, the chair rocks slowly
		rot("right_hand", 0.18F * Mth.sin(t * 0.5F) * knit, 0F, 0F);
		rot("left_hand", 0.12F * Mth.sin(t * 0.5F + 1.6F) * knit, 0F, 0F);
		rot("base", 0.06F * Mth.sin(t * 0.07F) * knit, 0F, 0F);
		// stand_no_walker: the scolding head shake
		rot("head", 0F, 0.12F * Mth.sin(t * 0.6F) * noWalker, 0F);
		// offer_mate: the gourd bobs while she talks
		offset("mate", 0F, 0.3F * Mth.sin(t * 0.5F) * talk * offer, 0F);
		// throw_chancleta release: the arm snaps over
		rot("right_arm", -1.6F * snap, 0F, 0F);
		rot("right_forearm", 0.8F * snap, 0F, 0F);
		// floating in the rocker: the bob and the rock about the floor contact
		float afloat = Math.max(height, FamilyRenderer.floating(s) ? 1F : 0F);
		offset("base", 0F, 0.8F * Mth.sin(t * 0.06F) * afloat, 0F);
		rot("base", 0.09F * Mth.sin(t * 0.08F) * height, 0F, 0F);
		// yarn_cast: the strands shoot out, the clawed hands tremble
		if (yarnRight.visible) {
			scale("yarn_right", 1F, Math.max(0.02F, shoot), 1F);
			scale("yarn_left", 1F, Math.max(0.02F, shoot), 1F);
		}
		rot("right_hand", 0F, 0F, 0.05F * Mth.sin(t * 1.7F) * yarn);
		rot("left_hand", 0F, 0F, -0.05F * Mth.sin(t * 1.7F + 0.8F) * yarn);
		// scream_dentures: the dentures drift and clack in front of the dislocated jaw
		if (dentures.visible) {
			rot("dentures_lower", 0.35F * Math.abs(Mth.sin(t * 0.45F)), 0F, 0F);
			offset("dentures", 0F, 0.6F * Mth.sin(t * 0.1F), 0F);
			rot("dentures", 0F, 0.15F * Mth.sin(t * 0.07F), 0F);
		}
		// sew_calm: the hands work the last stitch, small and tender
		rot("right_hand", 0.05F * Mth.sin(t * 0.3F) * sew, 0F, 0F);
		rot("left_hand", -0.04F * Mth.sin(t * 0.3F + 0.7F) * sew, 0F, 0F);
		// possessed: the loose tresses drift slowly as if under water, out of phase per strand
		if (possessed) {
			ripple("hair_loose_", t, 0.05F, 1.3F, 0.10F, 0.14F, 0F);
			for (int k = 0; k < loose.length; k++) {
				loose[k].yRot += 0.06F * Mth.sin(t * 0.03F + 2.1F * k);
			}
		}

		// ---- talking
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("jaw", 0.04F * talk + 0.18F * syl, 0F, 0F);

		// ---- walking (standing poses only): she shuffles; arms push the walker (no swing) or swing a little without
		float legs = Math.max(0F, 1F - seatedW);
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed) * legs;
		float swing = Mth.cos(pos) * 0.35F * spd;
		rot("right_leg", swing, 0F, 0F);
		rot("left_leg", -swing, 0F, 0F);
		float armAmp = walker.visible ? 0F : 0.2F;
		rot("right_arm", -Mth.cos(pos) * armAmp * spd * (1F - throwW), 0F, 0F);
		rot("left_arm", Mth.cos(pos) * armAmp * spd, 0F, 0F);
		rot("body", 0F, 0F, 0.03F * Mth.sin(pos) * spd);
		float forward = Math.min(swing, -swing);  // the forward leg's swing (negative)
		rot("skirt_front", 0.25F * forward, 0F, 0F);
		rot("skirt_hem", 0.125F * forward, 0F, 0F);
		rot("skirt_back", 0.2F * Math.abs(swing), 0F, 0F);
		rot("glasses", 0F, 0F, 0.05F * Mth.sin(pos * 2F) * spd);
		offset("yarn_ball", 0F, 0.3F * Math.abs(Mth.sin(pos)) * spd, 0F);
		// the squeaky wheel turns with the distance walked
		rot("walker_wheel", s.walkAnimationPos * 3.2F, 0F, 0F);

		// ---- head look (neck 35 %, head 65 %): she looks up at you even while knitting
		float lookW = 1F - 0.7F * scream - 0.5F * yarn - 0.5F * knit - 0.6F * sew - 0.4F * throwW;
		lookW = Math.max(0F, lookW);
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -75F, 75F) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.35F, yaw * 0.35F, 0F);
		rot("head", pitch * 0.65F, yaw * 0.65F, 0F);
	}
}
