package com.deadline.client.model;

import com.deadline.client.model.gen.MadreModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.entity.ApparitionEntity;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** La Madre Remedios: a rigid column that never walks; only head, arms, ledger and rosary move as she writes, stares, points. */
public class MadreModel extends MadreModelBase {
	/** STAND is the stare held at a fraction: chin a little up, the column barely rocked back, spectacles untouched. */
	private static final float STAND_STARE = 0.35F;
	/** One written line: scribble (3 strokes), firm tick, "Aja." (head dip, two jaw opens), lift back to the margin. */
	private static final float LINE = 64F, SCRIBBLE = 42F, AJA = 44F, AJA_END = 50F;
	/** The first tick lands one tick after she appears, matching the "Aja." the script says when it spawns her. */
	private static final float LINE_PHASE = 41F;
	/** Half the sideways travel of the nib along a line (rad). */
	private static final float DRIFT = 0.06F;

	private static final float HEAD_WRITE = rowOf(POSE_WRITE, "head")[0];
	private static final float HEAD_STARE = rowOf(POSE_STARE, "head")[0];
	private static final float HEAD_POINT = rowOf(POSE_POINT, "head")[0];
	private static final float BACK_R_WRITE = rowOf(POSE_WRITE, "veil_back_right")[5];
	private static final float BACK_R_STARE = rowOf(POSE_STARE, "veil_back_right")[5];
	private static final float BACK_R_POINT = rowOf(POSE_POINT, "veil_back_right")[5];
	private static final float BACK_L_WRITE = rowOf(POSE_WRITE, "veil_back_left")[5];
	private static final float BACK_L_STARE = rowOf(POSE_STARE, "veil_back_left")[5];
	private static final float BACK_L_POINT = rowOf(POSE_POINT, "veil_back_left")[5];
	private static final float[] GLASSES_STARE = rowOf(POSE_STARE, "glasses");
	private static final float[] POINT_FOREARM = rowOf(POSE_POINT, "right_forearm");
	private static final float[] POINT_HAND = rowOf(POSE_POINT, "right_hand");
	private static final float[] POINT_INDEX = rowOf(POSE_POINT, "right_index");
	private static final float[] POINT_PEN = rowOf(POSE_POINT, "pen");

	public MadreModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		boolean writing = s.action == ApparitionEntity.POSE_WRITE;
		boolean staring = s.action == ApparitionEntity.POSE_STARE;
		boolean pointing = s.action == ApparitionEntity.POSE_POINT;
		boolean standing = !writing && !staring && !pointing;

		// pose weights: write in over ~6 ticks, stare over ~10, point snaps in over ~3 (arm, then forearm, then hand)
		// and eases out over ~12; the pen flips into the sleeve in the first 2 ticks
		float write = blend(s, 0, writing ? 1F : 0F, 0.35F);
		float stare = blend(s, 1, staring ? 1F : standing ? STAND_STARE : 0F, 0.25F);
		float point = blend(s, 2, pointing ? 1F : 0F, pointing ? 0.6F : 0.22F);
		float pointFore = blend(s, 3, pointing ? 1F : 0F, pointing ? 0.45F : 0.24F);
		float pointHand = blend(s, 4, pointing ? 1F : 0F, pointing ? 0.35F : 0.26F);
		float pen = blend(s, 5, pointing ? 1F : 0F, pointing ? 0.75F : 0.3F);
		float idle = blend(s, 6, standing ? 1F : 0F, 0.2F);
		float glasses = blend(s, 7, staring && stare > 0.5F ? 1F : 0F, staring ? 0.35F : 0.5F);
		float settle = blend(s, 8, pointing ? 1F : 0F, 0.1F);
		float yaw = blend(s, 9, Mth.clamp(s.yRot * Mth.DEG_TO_RAD, -0.6F, 0.6F) * (1F - 0.8F * write), 0.07F);
		float pitch = blend(s, 10, s.xRot * Mth.DEG_TO_RAD * (1F - write), 0.07F);

		apply(POSE_WRITE, write);
		apply(POSE_STARE, stare);
		apply(POSE_POINT, point);
		// the spectacles are pushed up only once the stare has set in (never in STAND)
		addRow("glasses", GLASSES_STARE, glasses - stare);
		addRow("right_forearm", POINT_FOREARM, pointFore - point);
		addRow("right_hand", POINT_HAND, pointHand - point);
		addRow("right_index", POINT_INDEX, pointHand - point);
		addRow("pen", POINT_PEN, pen - point);
		float twirl = Math.max(0F, pen - point) * 4F;
		rot("pen", twirl, 0F, twirl * 0.3F);

		// the column: barely breathing; the slabs, back veil and wings only stir in the draught (and flare as she appears)
		float gust = t < 2F ? t * 0.5F : Math.max(0F, 1F - (t - 2F) * 0.1F);
		gust = gust * gust * (3F - 2F * gust);
		rot("body", Mth.sin(t * 0.05F) * 0.006F, 0F, 0F);
		rot("skirt_front", Mth.sin(t * 0.03F) * 0.008F - 0.06F * gust, 0F, 0F);
		rot("skirt_back", Mth.sin(t * 0.03F + 1F) * 0.008F + 0.06F * gust, 0F, 0F);
		rot("skirt_right", 0F, 0F, Mth.sin(t * 0.03F + 2F) * 0.008F + 0.06F * gust);
		rot("skirt_left", 0F, 0F, Mth.sin(t * 0.03F + 3F) * 0.008F - 0.06F * gust);
		rot("veil_back_right", Mth.sin(t * 0.04F) * 0.01F, 0F, 0.05F * gust);
		rot("veil_back_left", Mth.sin(t * 0.04F + 1.3F) * 0.01F, 0F, -0.05F * gust);
		rot("veil_right", 0F, 0F, 0.08F * gust);
		rot("veil_left", 0F, 0F, -0.08F * gust);
		// rosary pendulum, kicked when the arm snaps out (decays over ~20 ticks)
		float kick = Math.max(0F, point - settle) * 1.5F;
		rot("rosary", 0F, 0F, Mth.sin(t * 0.06F) * 0.04F - 0.15F * kick);

		// idle: every 80-140 ticks the nib taps towards the ledger
		float u = t + (s.seed & 63) * 7F;
		int n = (int) (u / 110F);
		float tap = hump(u - n * 110F - ((n * 73 + s.seed * 31) & 31), 0F, 3F);
		rot("right_hand", 0.12F * tap * idle, 0F, 0F);

		// write: the pen scratches along a line, ticks it, "Aja." (head dip, two short jaw opens, deeper scowl)
		float dip = 0F;
		if (write > 0.001F) {
			float ph = (t + LINE_PHASE) % LINE;
			float stroke = 0F;
			float lift = 0F;
			float drift;
			if (ph < SCRIBBLE) {
				float p = ph / SCRIBBLE;
				stroke = Math.abs(Mth.sin(p * 3F * Mth.PI));
				drift = (p - 0.5F) * 2F * DRIFT;
			} else if (ph < AJA_END) {
				drift = DRIFT;
			} else {
				float q = (ph - AJA_END) / (LINE - AJA_END);
				drift = DRIFT - 2F * DRIFT * q * q * (3F - 2F * q);
				lift = Mth.sin(q * Mth.PI);
			}
			float tick = hump(ph, SCRIBBLE, 2F);
			float aja = hump(ph, AJA, 6F);
			float sc = stroke * write;
			rot("right_arm", 0F, 0F, drift * 0.5F * write);
			rot("right_forearm", Mth.sin(t * 0.6F) * 0.012F * sc, drift * 0.5F * write, 0F);
			rot("right_hand", Mth.sin(t * 1.2F + 0.8F) * 0.03F * sc - 0.05F * lift * write, 0F, Mth.cos(t * 1.2F) * 0.02F * sc);
			rot("pen", Mth.sin(t * 1.2F) * 0.05F * sc + 0.08F * tick * write, 0F, Mth.cos(t * 1.2F) * 0.04F * sc);
			rot("book", 0.03F * aja * write, 0F, 0F);
			rot("jaw", (hump(ph, AJA, 2.5F) * 0.1F + hump(ph, AJA + 3F, 2F) * 0.06F) * write, 0F, 0F);
			rot("right_brow", 0F, 0F, 0.06F * hump(ph, AJA, 8F) * write);
			rot("head", 0F, drift * 0.5F * write, 0F);
			dip = 0.1F * aja * write;
		}

		// head: slow clamped tracking (eyes stay in the ledger while writing) and the VEIL RULE on its own pitch
		float headPose = HEAD_WRITE * write + HEAD_STARE * stare + HEAD_POINT * point;
		float headExtra = Mth.clamp(headPose + pitch + dip, -0.3F, 0.35F) - headPose;
		rot("head", headExtra, yaw, 0F);
		rot("veil_right", -0.85F * headExtra, 0F, 0F);
		rot("veil_left", -0.85F * headExtra, 0F, 0F);
		float backDz = -2F * Math.max(headPose + headExtra, 0F);
		offset("veil_back_right", 0F, 0F, backDz - (BACK_R_WRITE * write + BACK_R_STARE * stare + BACK_R_POINT * point));
		offset("veil_back_left", 0F, 0F, backDz - (BACK_L_WRITE * write + BACK_L_STARE * stare + BACK_L_POINT * point));
	}

	/** Adds one bone's row of a pose table scaled by w (w may be negative to take part of an applied pose back). */
	private void addRow(String bone, float[] v, float w) {
		if (w > 0.001F || w < -0.001F) {
			rot(bone, v[0] * w, v[1] * w, v[2] * w);
			offset(bone, v[3] * w, v[4] * w, v[5] * w);
		}
	}

	/** A sine bump 0 -> 1 -> 0 while x runs from start to start + len, 0 outside. */
	private static float hump(float x, float start, float len) {
		return x >= start && x < start + len ? Mth.sin((x - start) / len * Mth.PI) : 0F;
	}

	private static float[] rowOf(Map<String, float[]> pose, String bone) {
		float[] v = pose.get(bone);
		return v != null && v.length >= 6 ? v : new float[6];
	}
}
