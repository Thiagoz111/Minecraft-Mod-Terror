package com.deadline.client.model;

import com.deadline.client.model.gen.AlumnaModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.entity.ApparitionEntity;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** The choir girls: mouthless, dead still between sudden snaps; they sing, sit, face the wall, turn their heads round and run. */
public class AlumnaModel extends AlumnaModelBase {
	/** Hairstyle per variant, in the order of HAIRS in tools/models/ent_alumna.py. */
	private static final String[] HAIRS = {"paloma", "mecha", "rocio", "chela", "ofelia", "anasofia", "lola"};
	/** 'cover_ears' with the arms re-solved for the wider hairstyles, else the plain one. */
	private static final List<Map<String, float[]>> COVER_EARS = Arrays.stream(HAIRS)
			.map(h -> POSES.getOrDefault("cover_ears_" + h, POSE_COVER_EARS)).toList();
	private static final int STAND = ApparitionEntity.POSE_STAND, SING = ApparitionEntity.POSE_SING, SIT = ApparitionEntity.POSE_SIT,
			WALL = ApparitionEntity.POSE_FACE_WALL, POINT = ApparitionEntity.POSE_POINT, EARS = ApparitionEntity.POSE_COVER_EARS,
			HEAD_180 = ApparitionEntity.POSE_HEAD_180, RUN = ApparitionEntity.POSE_RUN, PEEK = ApparitionEntity.POSE_PEEK,
			TURN = ApparitionEntity.POSE_TURN, FREED = ApparitionEntity.POSE_FREED;
	/** Swinging a limb pair by these mirrors the exported 'run' contact frame (right foot forward) into the other step. */
	private static final float LEG_SWING = mirror("right_leg", "left_leg"), SHOE_SWING = mirror("right_shoe", "left_shoe"),
			ARM_SWING = mirror("right_arm", "left_arm");

	private final ModelPart[] hairs = new ModelPart[HAIRS.length];
	private final float restPitch;
	/** Written by {@link #snap}: ticks since the last snap and how far it moved. */
	private float snapAge, snapStep;

	public AlumnaModel(ModelPart root) {
		super(root);
		for (int i = 0; i < HAIRS.length; i++) {
			hairs[i] = get("hair_" + HAIRS[i]);
		}
		restPitch = body.xRot + neck.xRot + head.xRot;
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int hair = Math.floorMod(s.variant, HAIRS.length);
		for (int i = 0; i < hairs.length; i++) {
			if (hairs[i] != null) {
				hairs[i].visible = i == hair;
			}
		}
		// the mouthless face IS the character: the "O" only exists once they are freed (Laudes)
		jaw.visible = a == FREED;

		// pose weights: ~5-tick fades, SNAP into 'point', HOLD the base pose while the head comes round,
		// slow fade off the wall for the turn; a girl that has just appeared is already in her pose
		boolean known = (a >= STAND && a <= TURN) || a == FREED;
		float rate = t < 4F ? 1F : switch (a) {
			case POINT -> 0.6F;
			case HEAD_180 -> 0F;
			case TURN -> 0.12F;
			case RUN -> 0.35F;
			default -> 0.3F;
		};
		float stand = blend(s, 0, a == STAND || !known ? 1F : 0F, rate);
		float sing = blend(s, 1, a == SING || a == FREED ? 1F : 0F, rate);
		float sit = blend(s, 2, a == SIT ? 1F : 0F, rate);
		float wall = blend(s, 3, a == WALL ? 1F : 0F, rate);
		float point = blend(s, 4, a == POINT ? 1F : 0F, rate);
		float ears = blend(s, 5, a == EARS ? 1F : 0F, rate);
		float run = blend(s, 7, a == RUN ? 1F : 0F, rate);
		float peek = blend(s, 8, a == PEEK ? 1F : 0F, rate);
		float freed = blend(s, 9, a == FREED ? 1F : 0F, rate);
		// head_180: two cascaded fades = an eased turn of ~1 s, the neck slightly ahead of the head
		float lead = blend(s, 6, a == HEAD_180 ? 1F : 0F, t < 4F ? 1F : 0.2F);
		float round = blend(s, 10, lead, t < 4F ? 1F : 0.2F);
		float held = blend(s, 11, a == POINT ? 1F : 0F, 0.03F);
		// turn from the wall: remember the yaw she had against it, then bring head, then body, round from there
		boolean facing = a == WALL;
		float turnRate = facing ? 1F : a == TURN ? 0.22F : 0.35F;
		float wallYaw = blend(s, 12, s.bodyRot, facing ? 1F : 0F);
		float turnLead = blend(s, 15, facing ? 1F : 0F, turnRate);
		float headLeft = blend(s, 13, turnLead, turnRate);
		float bodyLeft = blend(s, 14, headLeft, facing ? 1F : a == TURN ? 0.12F : 0.3F);

		apply(pose("stand"), stand);
		apply(pose("sing"), sing);
		apply(pose("sit_desk"), sit);
		apply(pose("face_wall"), wall);
		apply(pose("point"), point);
		apply(COVER_EARS.get(hair), ears);
		apply(pose("run"), run);
		apply(pose("peek"), peek);
		apply(pose("freed"), freed);
		apply(pose("head_180"), round);
		if (round > 0.001F) {
			rot("neck", 0F, (lead - round) * 0.5F, 0F);
			if (round > 0.75F) {
				rot("head", 0F, 0.1F * Mth.sin((round - 0.75F) * 4F * Mth.PI), 0F);
			}
		}

		// idle on every pose: barely breathing, a settle now and then, head tilts that snap and hold
		float still = 1F - Math.max(run, ears);
		float breath = Mth.sin(t * 0.07F + Math.floorMod(s.seed, 64));
		offset("right_arm", 0F, -0.12F * breath, 0F);
		offset("left_arm", 0F, -0.12F * breath, 0F);
		rot("neck", -0.012F * breath, 0F, 0F);
		float settle = snap(t, s.seed * 31 + 7, 0.015F) * still;
		float settleRing = ring(snapAge, snapStep) * still;
		rot("body", 0F, 0F, settle);
		rot("bow", 0F, 0F, Mth.clamp(-settleRing * 3F, -0.08F, 0.08F));
		float tiltLag = snap(t - 3.5F, s.seed, 0.2F);
		float tiltTip = snap(t - 5.5F, s.seed, 0.2F);
		float tilt = snap(t, s.seed, 0.2F);
		float kick = ring(snapAge, snapStep) * still;
		float kickLate = ring(snapAge - 1F, snapStep) * still;
		rot("head", 0F, 0F, tilt * still);
		ripple("skirt_", t, 0.05F, 1.4F, 0.015F, 0.01F, 0F);

		// hair tips: slow sway plus a spring that lags the head snaps (tips 2 ticks behind the uppers)
		float spring = Mth.clamp((tiltLag - tilt) * 0.4F, -0.1F, 0.1F) * still;
		float springTip = Mth.clamp((tiltTip - tiltLag) * 0.4F, -0.1F, 0.1F) * still;
		float sway = Mth.sin(t * 0.045F + Math.floorMod(s.seed, 7)) * 0.03F;
		float swayLate = Mth.sin(t * 0.045F + Math.floorMod(s.seed, 7) - 0.9F) * 0.03F;
		rot("paloma_braid_right", 0F, 0F, spring + sway);
		rot("paloma_braid_left", 0F, 0F, spring + sway);
		rot("paloma_braid_right_tip", 0F, 0F, springTip + swayLate);
		rot("paloma_braid_left_tip", 0F, 0F, springTip + swayLate);
		rot("rocio_tail_tip", 0F, 0F, -kick * 0.6F + swayLate);
		rot("ofelia_curtain", sway * 0.5F, 0F, spring * 0.6F);
		rot("anasofia_tail_right", 0F, 0F, kick * 0.3F);
		rot("anasofia_tail_left", 0F, 0F, kick * 0.3F);
		rot("anasofia_tail_right_tip", 0F, 0F, springTip + swayLate);
		rot("anasofia_tail_left_tip", 0F, 0F, springTip + swayLate);
		rot("lola_bow", 0F, 0F, Mth.clamp(kick * 0.15F, -0.06F, 0.06F));
		float tails = Mth.clamp(kickLate * 0.2F, -0.08F, 0.08F);
		rot("lola_tail_r", 0F, 0F, tails);
		rot("lola_tail_l", 0F, 0F, tails);

		// cold hands: a slow curl that never takes both hands at once, a tremor on one wrist every few seconds
		float curl = Mth.sin(t * 0.035F + Math.floorMod(s.seed, 13));
		rot("right_fingers", 0F, 0F, -0.1F * Math.max(0F, curl));
		rot("left_fingers", 0F, 0F, 0.1F * Math.max(0F, -curl));
		float u = t + Math.floorMod(s.seed * 17, 61);
		int n = Mth.floor(u / 70F);
		float w = u - n * 70F;
		if (w < 12F) {
			rot((n & 1) == 0 ? "right_hand" : "left_hand", 0F, 0F, Mth.sin(t * 2.3F) * 0.04F * Mth.sin(w / 12F * Mth.PI));
		}

		if (sing > 0.001F) {
			rot("head", -0.02F * (0.5F + 0.5F * Mth.sin(t * 0.15F)) * sing, 0F, 0F);
		}
		if (a == FREED) {
			// the "O" is always flush on the face (never seen sliding out), and opens a little on the beat
			float[] slide = pose("freed").get("jaw");
			if (slide != null) {
				float k = 1F - freed;
				offset("jaw", slide[3] * k, slide[4] * k, slide[5] * k);
			}
			offset("jaw", 0F, 0.2F - 0.2F * Mth.cos(t * 0.3F), 0F);
		}
		if (point > 0.001F) {
			// after holding the point for ~2 s the index starts to beckon
			float beckon = Mth.clamp((held - 0.7F) * 6F, 0F, 1F) * point;
			rot("right_index", -0.25F * (1F - Mth.cos(t * 0.16F)) * beckon, 0F, 0F);
		}
		if (ears > 0.001F) {
			rot("neck", Mth.sin(t * 2.1F) * 0.012F * ears, 0F, 0F);
		}
		if (peek > 0.001F) {
			rot("neck", 0F, 0F, (0.5F + 0.5F * Mth.sin(t * 0.03F)) * 0.05F * peek);
		}

		if (run > 0.001F) {
			// scripted slide, so the stride runs on the clock; it mirrors the contact frame every half cycle
			float ph = t * 0.85F + Math.floorMod(s.seed, 11) * 0.57F;
			float c = Mth.sin(ph);
			float swing = (1F - c) * run;
			float foot = 0.5F - 0.5F * Mth.cos(ph * 2F - 1F);
			float flap = Mth.sin(ph * 2F - 1.6F) * run;
			float flapLate = Mth.sin(ph * 2F - 2.6F) * run;
			rot("right_leg", LEG_SWING * swing, 0F, 0F);
			rot("left_leg", -LEG_SWING * swing, 0F, 0F);
			rot("right_shoe", SHOE_SWING * swing, 0F, 0F);
			rot("left_shoe", -SHOE_SWING * swing, 0F, 0F);
			rot("right_arm", ARM_SWING * swing, 0F, 0F);
			rot("left_arm", -ARM_SWING * swing, 0F, 0F);
			// the heel tucks up as the leg comes through, never on a contact frame
			rot("right_shin", Math.max(0F, Mth.cos(ph)) * 0.5F * run, 0F, 0F);
			rot("left_shin", Math.max(0F, -Mth.cos(ph)) * 0.5F * run, 0F, 0F);
			rot("body", 0.08F * foot * run, 0F, 0F);
			ripple("skirt_", t, 0.6F, 1.4F, 0.04F * run, 0.025F * run, 0F);
			rot("skirt_front", -0.12F * Math.abs(c) * run, 0F, 0F);
			rot("skirt_right", 0F, 0F, 0.12F * Math.max(0F, c) * run);
			rot("skirt_left", 0F, 0F, -0.12F * Math.max(0F, -c) * run);
			rot("bow", -0.15F * run, 0F, 0.06F * c * run);
			rot("paloma_braid_right", 0.12F * flap, 0F, 0.05F * c * run);
			rot("paloma_braid_left", 0.12F * flap, 0F, 0.05F * c * run);
			rot("paloma_braid_right_tip", 0.12F * flapLate, 0F, 0F);
			rot("paloma_braid_left_tip", 0.12F * flapLate, 0F, 0F);
			rot("rocio_tail_tip", (0.5F - foot) * 0.3F * run, 0F, 0F);
			rot("ofelia_curtain", 0.08F * flap, 0F, 0F);
			float bob = 0.25F * (2F * foot - 1F) * run;
			rot("anasofia_tail_right", 0F, 0F, bob);
			rot("anasofia_tail_left", 0F, 0F, -bob);
			rot("anasofia_tail_right_tip", 0F, 0F, bob * 0.5F);
			rot("anasofia_tail_left_tip", 0F, 0F, -bob * 0.5F);
			offset("hair_chela", 0F, 0.3F * foot * run, 0F);
			rot("lola_bow", 0F, 0F, 0.06F * flap);
			rot("lola_tail_r", 0F, 0F, 0.06F * flapLate);
			rot("lola_tail_l", 0F, 0F, 0.06F * flapLate);
		}

		// head look (neck 30 %, head 70 %); while turning from the wall the body is held back towards the
		// wall and the head comes round first
		float lookW = 1F - 0.8F * run;
		float yawDeg = Mth.clamp(Mth.wrapDegrees(s.yRot), -75F, 75F) * lookW;
		if (headLeft > 0.0005F || bodyLeft > 0.0005F) {
			float db = Mth.wrapDegrees(s.bodyRot - wallYaw);
			float dh = Mth.wrapDegrees(s.bodyRot + s.yRot - wallYaw);
			rot("body", 0F, -db * bodyLeft * Mth.DEG_TO_RAD, 0F);
			yawDeg += db * bodyLeft - dh * headLeft;
		}
		float yaw = Mth.clamp(yawDeg, -170F, 170F) * Mth.DEG_TO_RAD;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * lookW * Mth.DEG_TO_RAD;
		rot("neck", pitch * 0.3F, yaw * 0.3F, 0F);
		rot("head", pitch * 0.7F, yaw * 0.7F, 0F);

		// gravity: with the chin up (sing, freed) the long back hair would swing into her back; keep it hanging
		// (the bowed poses already carry their own correction)
		float lift = restPitch - (body.xRot + neck.xRot + head.xRot);
		if (lift > 0F) {
			rot("ofelia_curtain", lift * 0.9F, 0F, 0F);
			rot("rocio_tail", lift * 0.3F, 0F, 0F);
			rot("rocio_tail_tip", lift * 0.6F, 0F, 0F);
			rot("paloma_braid_right", lift * 0.6F, 0F, 0F);
			rot("paloma_braid_left", lift * 0.6F, 0F, 0F);
		}
	}

	/** A held level that SNAPS (2 ticks) to a new seeded value every 5-12 s; records the snap in snapAge/snapStep. */
	private float snap(float t, int seed, float amp) {
		float period = 100F + Math.floorMod(seed * 7, 8) * 20F;
		float u = t + Math.floorMod(seed * 31, 97);
		int n = Mth.floor(u / period);
		float prev = noise(seed, n - 1) * amp;
		float cur = noise(seed, n) * amp;
		snapAge = u - n * period;
		snapStep = cur - prev;
		return Mth.lerp(Math.min(1F, snapAge / 2F), prev, cur);
	}

	/** Damped ringing that follows a snap of size step, age ticks after it. */
	private static float ring(float age, float step) {
		return age < 0F || age > 40F ? 0F : (float) Math.exp(-age * 0.15F) * Mth.sin(age * 0.9F) * step;
	}

	/** Deterministic -1..1 per (seed, n). */
	private static float noise(int seed, int n) {
		int h = seed * 0x9E3779B1 + n * 0x85EBCA6B;
		h ^= h >>> 15;
		h *= 0x2C1B3C6D;
		h ^= h >>> 12;
		return (h & 0xFFFF) / 32767.5F - 1F;
	}

	private static float mirror(String right, String left) {
		Map<String, float[]> run = POSES.getOrDefault("run", Map.of());
		float[] r = run.get(right);
		float[] l = run.get(left);
		return r == null || l == null ? 0F : (l[0] - r[0]) * 0.5F;
	}
}
