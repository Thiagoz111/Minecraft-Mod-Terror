package com.deadline.client.model;

import com.deadline.client.model.gen.ClaraModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.entity.ApparitionEntity;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Clara, the freed soul of Sor María: floats in her own light, opens her arms (then her eyes) to rise, bows with palms joined. */
public class ClaraModel extends ClaraModelBase {
	/** Per-tick blend rates: nothing about her snaps (rise ~2 s, bow ~2.5 s, look-at 0.08 as in the art notes). */
	private static final float RISE_RATE = 0.05F, BOW_RATE = 0.045F, IDLE_RATE = 0.05F, LOOK_RATE = 0.08F, SPEAK_RATE = 0.08F;
	/** The bells find gravity ~8 ticks after the arms move. */
	private static final float SLEEVE_LAG = 0.12F;
	/** A slow per-entity blend toward 1 while in RISE, inverted back into ticks since the pose began. */
	private static final float CLOCK_RATE = 0.01F;
	private static final double LOG_CLOCK = Math.log(1F - CLOCK_RATE);
	/** RISE: the lids lift ~2 s into the pose (ease-out over ~8 ticks); they close more slowly as she bows. */
	private static final float EYES_AT = 40F, LIDS_OPEN = 0.25F, LIDS_CLOSE = 0.12F;
	/** ColegioScript (lauds) plays "colegio.clara.gracias" (~10 s) 40 ticks after setting RISE: her lips move then. */
	private static final float TALK_FROM = 42F, TALK_LEN = 200F, SYLLABLE = 4.5F, TALK_SPEAK = 0.6F;
	/** STAND keeps a light 'speak' (face lifted and tilted, eyes open) over the floating idle. */
	private static final float STAND_SPEAK = 0.35F;
	/** While the eyes are open: a blink every 80-140 ticks, ~2 ticks shut. */
	private static final float BLINK_EVERY = 110F, BLINK_LEN = 4F;
	/** Look-at limits (rad) and the neck's share of the pitch. */
	private static final float YAW_MAX = 0.6F, PITCH_MAX = 0.35F, NECK_SHARE = 0.3F;
	/** Ring centre in the halo's own space (its pivot is the centre of the head): it breathes about this point. */
	private static final float HALO_CY = -5F, HALO_CZ = 9.5F;
	/** Added flare allowed on a gore, so the diagonal gores stay outside the others. */
	private static final float GORE_MIN = -0.3F, GORE_MAX = 0.25F;

	private static final float RISE_HEAD = rowOf(POSE_RISE, "head")[0];
	private static final float RISE_NECK = rowOf(POSE_RISE, "neck")[0];
	private static final float BOW_CHEST = rowOf(POSE_BOW, "chest")[0];
	private static final float MOUTH_DZ = rowOf(POSE_SPEAK, "mouth")[5];
	private static final float[] RISE_SLEEVE_R = rowOf(POSE_RISE, "right_sleeve");
	private static final float[] RISE_SLEEVE_L = rowOf(POSE_RISE, "left_sleeve");
	private static final float[] BOW_SLEEVE_R = rowOf(POSE_BOW, "right_sleeve");
	private static final float[] BOW_SLEEVE_L = rowOf(POSE_BOW, "left_sleeve");

	/** The eight gores in order round the hull (front, front-left ... front-right), so the ripple travels round her. */
	private final ModelPart[] gores;
	private final float[] goreRest;

	public ClaraModel(ModelPart root) {
		super(root);
		this.gores = new ModelPart[] {skirtFront, skirtFrontLeft, skirtLeft, skirtBackLeft, skirtBack, skirtBackRight, skirtRight, skirtFrontRight};
		this.goreRest = new float[gores.length];
		for (int k = 0; k < gores.length; k++) {
			goreRest[k] = gores[k].xRot;
		}
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		boolean rising = s.action == ApparitionEntity.POSE_RISE;
		boolean bowing = s.action == ApparitionEntity.POSE_BOW;
		boolean standing = !rising && !bowing;

		float rise = blend(s, 0, rising ? 1F : 0F, RISE_RATE);
		float bow = blend(s, 1, bowing ? 1F : 0F, BOW_RATE);
		float idle = blend(s, 2, standing ? 1F : 0F, IDLE_RATE);
		float clock = blend(s, 3, rising ? 1F : 0F, CLOCK_RATE);
		float since = clock >= 0.9999F ? Float.MAX_VALUE : (float) (Math.log(1F - clock) / LOG_CLOCK);
		boolean talking = rising && since >= TALK_FROM && since < TALK_FROM + TALK_LEN;
		// eyes: closed at first in RISE, open ~2 s in; open in STAND once it has settled (never on a spawn blip); shut in BOW
		boolean eyesOpen = rising ? since >= EYES_AT : standing && idle > 0.6F;
		float open = blend(s, 4, eyesOpen ? 1F : 0F, eyesOpen ? LIDS_OPEN : LIDS_CLOSE);
		float lookW = 1F - 0.7F * bow;
		float yaw = blend(s, 5, Mth.clamp(s.yRot * Mth.DEG_TO_RAD, -YAW_MAX, YAW_MAX) * lookW, LOOK_RATE);
		float pitch = blend(s, 6, Mth.clamp(s.xRot * Mth.DEG_TO_RAD, -PITCH_MAX, PITCH_MAX) * lookW, LOOK_RATE);
		float sleeveRise = blend(s, 7, rise, SLEEVE_LAG);
		float sleeveBow = blend(s, 8, bow, SLEEVE_LAG);
		float speak = blend(s, 9, talking ? TALK_SPEAK : standing ? STAND_SPEAK : 0F, SPEAK_RATE);

		// poses (the lids and lips are driven below by scale / visibility, not by the tables' slide-behind offsets)
		float lidZ = eyelids.z;
		float mouthZ = mouth.z;
		apply(POSE_RISE, rise);
		apply(POSE_BOW, bow);
		apply(POSE_SPEAK, speak);
		eyelids.z = lidZ;
		mouth.z = mouthZ;
		addRow("right_sleeve", RISE_SLEEVE_R, sleeveRise - rise);
		addRow("left_sleeve", RISE_SLEEVE_L, sleeveRise - rise);
		addRow("right_sleeve", BOW_SLEEVE_R, sleeveBow - bow);
		addRow("left_sleeve", BOW_SLEEVE_L, sleeveBow - bow);

		// she floats: slow hover, the faintest sway, breathing; the back veil hangs with gravity
		float swayX = Mth.sin(t * 0.045F) * 0.02F;
		float swayY = Mth.sin(t * 0.02F) * 0.04F;
		float breath = Mth.sin(t * 0.05F) * 0.015F;
		float tilt = Mth.sin(t * 0.03F) * 0.05F;
		offset("body", 0F, -1F + Mth.sin(t * 0.06F), 0F);
		rot("body", swayX, swayY, 0F);
		rot("chest", breath, 0F, 0F);
		rot("veil", -0.6F * (swayX + breath + BOW_CHEST * bow) + Mth.sin(t * 0.05F - 1.2F) * 0.03F, 0F, 0F);
		rot("veil_drape_right", Mth.sin(t * 0.05F + 0.6F) * 0.03F, NECK_SHARE * yaw, 0F);
		rot("veil_drape_left", Mth.sin(t * 0.05F + 0.6F) * 0.03F, NECK_SHARE * yaw, 0F);
		rot("veil_right", 0F, 0F, Mth.sin(t * 0.05F) * 0.02F);
		rot("veil_left", 0F, 0F, -Mth.sin(t * 0.05F + 1F) * 0.02F);

		// robe: an underwater ripple travelling round the eight gores
		for (int k = 0; k < gores.length; k++) {
			ModelPart g = gores[k];
			g.xRot += Mth.sin(t * 0.07F + k * 0.785F) * 0.05F;
			g.zRot += Mth.cos(t * 0.058F + k) * 0.015F;
			g.xRot = goreRest[k] + Mth.clamp(g.xRot - goreRest[k], GORE_MIN, GORE_MAX);
		}

		// look-at with easing; when the player is below her in RISE the look pitch takes over the pose's lift
		float down = Mth.clamp(pitch / PITCH_MAX, 0F, 1F) * rise;
		float lift = -(RISE_HEAD + RISE_NECK) * down;
		rot("neck", pitch * NECK_SHARE - RISE_NECK * down, 0F, 0F);
		rot("head", pitch * (1F - NECK_SHARE) - RISE_HEAD * down, yaw, tilt);

		// arms: a breath of sway (barely any with the palms joined), the open arms of RISE lift and settle
		float armSway = Mth.sin(t * 0.05F) * 0.03F * (1F - 0.7F * bow);
		float orans = Mth.sin(t * 0.04F) * 0.03F * rise;
		rot("right_arm", armSway, 0F, orans);
		rot("left_arm", armSway, 0F, -orans);
		rot("right_sleeve", Mth.sin(t * 0.06F) * 0.04F, 0F, 0F);
		rot("left_sleeve", Mth.sin(t * 0.06F + 0.7F) * 0.04F, 0F, 0F);
		rot("right_hand", Mth.sin(t * 0.07F) * 0.04F * (1F - bow), 0F, 0F);
		rot("left_hand", Mth.sin(t * 0.07F + 0.5F) * 0.04F * (1F - bow), 0F, 0F);
		boolean palms = rise > 0.5F;
		hide("right_hand_light", !palms);
		hide("left_hand_light", !palms);

		// eyelids: closed at rest; they lift (yScale 1 -> 0 about their top edge) and are hidden once open
		float lid = Math.max(1F - open, open > 0.95F ? blink(t, s.seed) : 0F);
		hide("eyelids", lid < 0.03F);
		scale("eyelids", 1F, Math.max(lid, 0.03F), 1F);
		// lips: the speech frame only shows on an open syllable
		boolean lips = talking && syllable(since - TALK_FROM);
		hide("mouth", !lips);
		if (lips) {
			offset("mouth", 0F, 0F, MOUTH_DZ);
		}

		// halo: the tables keep it upright for a camera in front; cancel the idle sway / breath / tilt (not the look-at),
		// then let it breathe about the ring centre
		rot("halo", -(swayX + breath + lift), -swayY, -tilt);
		float hs = 1F + Mth.sin(t * 0.08F) * 0.03F;
		scale("halo", hs, hs, hs);
		float a = halo.xRot;
		float k = 1F - hs;
		offset("halo", 0F, k * (HALO_CY * Mth.cos(a) - HALO_CZ * Mth.sin(a)), k * (HALO_CY * Mth.sin(a) + HALO_CZ * Mth.cos(a)));
	}

	/** 0 -> 1 -> 0 over a few ticks once per 80-140 ticks (per-entity jitter). */
	private static float blink(float t, int seed) {
		float u = t + (seed & 63) * 3F;
		int n = (int) (u / BLINK_EVERY);
		float x = u - n * BLINK_EVERY - ((n * 37 + seed * 11) & 31);
		return x >= 0F && x < BLINK_LEN ? Math.min(1F, Mth.sin(x / BLINK_LEN * Mth.PI) * 1.6F) : 0F;
	}

	/** Lips open ~2.5 of every 4.5 ticks, with a breath every few syllables. */
	private static boolean syllable(float p) {
		int n = (int) (p / SYLLABLE);
		return n % 9 != 8 && n % 14 != 13 && p - n * SYLLABLE < 2.5F;
	}

	/** Adds one bone's row of a pose table scaled by w (negative takes part of an applied pose back). */
	private void addRow(String bone, float[] v, float w) {
		if (w > 0.001F || w < -0.001F) {
			rot(bone, v[0] * w, v[1] * w, v[2] * w);
			offset(bone, v[3] * w, v[4] * w, v[5] * w);
		}
	}

	private static float[] rowOf(Map<String, float[]> pose, String bone) {
		float[] v = pose.get(bone);
		return v != null && v.length >= 6 ? v : new float[6];
	}
}
