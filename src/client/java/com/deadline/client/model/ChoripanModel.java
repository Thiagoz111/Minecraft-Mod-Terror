package com.deadline.client.model;

import com.deadline.client.model.gen.ChoripanModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.dog.ChoripanEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Choripán (tools/models/ent_choripan.py, ANIM_NOTES): the family dachshund -- asleep, sitting, growling low at the
 * Nona, trotting and running with his ears streaming -- and the dead one standing on his hind legs, perfectly still,
 * the head tilted, staring ({@link ChoripanEntity#POSE_STAND}, look {@link ChoripanEntity#LOOK_MUERTO}). Looks pick the
 * texture in the renderer; this model shows the look's toggles (the scarf of 'bufanda') and never blinks a dead dog.
 */
public class ChoripanModel extends ChoripanModelBase {
	private static final int SIT = ChoripanEntity.POSE_SIT, SLEEP = ChoripanEntity.POSE_SLEEP, GROWL = ChoripanEntity.POSE_GROWL,
			STAND = ChoripanEntity.POSE_STAND, WALK = ChoripanEntity.POSE_WALK, RUN = ChoripanEntity.POSE_RUN;

	public ChoripanModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		boolean dead = s.variant == ChoripanEntity.LOOK_MUERTO;
		boolean fresh = t < 4F;

		// ---- pose weights: the stand SNAPS in (he is already up when you see him), the rest blend over ~5 ticks
		float sit = blend(s, 0, a == SIT ? 1F : 0F, fresh ? 1F : 0.22F);
		float sleep = blend(s, 1, a == SLEEP ? 1F : 0F, fresh ? 1F : 0.12F);
		float growl = blend(s, 2, a == GROWL ? 1F : 0F, fresh ? 1F : 0.2F);
		float stand = blend(s, 3, a == STAND ? 1F : 0F, fresh ? 1F : 0.6F);
		float run = blend(s, 4, a == RUN ? 1F : 0F, 0.25F);
		apply(POSE_SIT, sit);
		apply(POSE_SLEEP, sleep);
		apply(POSE_GROWL, growl);
		apply(POSE_STAND, stand);
		float still = Math.max(stand, sleep);
		float upright = 1F - Math.max(stand, Math.max(sit, sleep));

		// ---- toggles: TOGGLE_DEFAULT -> look -> pose
		hide("scarf", s.variant != ChoripanEntity.LOOK_BUFANDA);
		hide("wrong_face", true);
		hide("neck_twist", true);
		boolean blink = !dead && sleep < 0.5F && Math.floorMod((int) t + seed * 13, 97) < 2;
		hide("eyelids", !(sleep > 0.5F || blink));

		// ---- gait: a quick dachshund trot (diagonal pairs) or a gallop (front pair / back pair), ears and tag flapping
		float spd = Math.min(1F, s.walkAnimationSpeed) * upright;
		float pos = s.walkAnimationPos;
		boolean moving = spd > 0.05F || a == WALK || a == RUN;
		if (moving) {
			float trot = 1F - run;
			float w = pos * 1.3F;
			float g = pos * 0.95F;
			float front = Mth.sin(w) * 0.7F * spd * trot + Mth.sin(g) * 0.9F * spd * run;
			float back = Mth.sin(w) * 0.6F * spd * trot + Mth.sin(g + 1.6F) * 0.85F * spd * run;
			rot("right_front_leg", front, 0F, 0F);
			rot("left_front_leg", trot > 0.5F ? -front : front, 0F, 0F);
			rot("left_back_leg", -back, 0F, 0F);
			rot("right_back_leg", trot > 0.5F ? back : -back, 0F, 0F);
			rot("right_front_paw", Math.max(0F, -front) * 0.8F, 0F, 0F);
			rot("left_front_paw", Math.max(0F, front) * 0.8F, 0F, 0F);
			offset("body", 0F, -Math.abs(Mth.sin(w * 2F)) * 0.35F * spd * trot - Math.abs(Mth.sin(g)) * 0.8F * spd * run, 0F);
			rot("body", Mth.sin(g) * 0.08F * spd * run + Mth.sin(w * 2F) * 0.02F * spd * trot, 0F, Mth.sin(w) * 0.035F * spd * trot);
			rot("right_ear", -0.9F * run * spd, 0F, -0.12F * Mth.sin(w) * spd);
			rot("left_ear", -0.9F * run * spd, 0F, 0.12F * Mth.sin(w) * spd);
		}

		// ---- breathing (not in the stand: he does not breathe), the growl's lip tremble
		if (stand < 0.5F) {
			offset("body", 0F, Mth.sin(t * (sleep > 0.5F ? 0.06F : 0.09F)) * (sleep > 0.5F ? 0.2F : 0.12F), 0F);
		}
		offset("lips", 0F, Mth.sin(t * 2.8F) * 0.15F * growl, 0F);

		// ---- the tail: it wags (it is how you read him) -- never in the stand, never asleep, stiff in the growl
		float wagAmp = (moving ? 0.6F : 0.35F) * (1F - still) * (1F - growl) * (dead ? 0F : 1F);
		float wagSpd = moving ? 0.95F : 0.55F;
		rot("tail", 0F, Mth.sin(t * wagSpd) * wagAmp, 0F);
		rot("tail_tip", 0F, Mth.sin(t * wagSpd - 0.7F) * wagAmp * 1.4F, 0F);

		// ---- head look (neck 30 %, head 70 %); none in the stand (the pose aims the face) or asleep
		float lookW = 1F - still;
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -70F, 70F) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -40F, 40F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.3F, yaw * 0.3F, 0F);
		rot("head", pitch * 0.7F, yaw * 0.7F, 0F);
		// asleep: an ear twitch every few seconds
		rot("right_ear", 0F, 0F, 0.2F * sleep * Math.max(0F, Mth.sin(t * 0.7F)) * (Math.floorMod((int) t + seed, 140) < 9 ? 1F : 0F));
	}
}
