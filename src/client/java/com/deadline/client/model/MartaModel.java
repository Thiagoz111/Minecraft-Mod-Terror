package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.MartaModelBase;
import com.deadline.client.render.HauntRenderState;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Marta Morales, the comic guide (never possessed): wrings her hands round the phone while she talks, glances about,
 * lifts her worried brows; points, panics, shows the family chat, throws the chorizo (or hands it over) and shouts.
 * Follows the ANIM_NOTES of tools/models/ent_marta.py.
 */
public class MartaModel extends MartaModelBase {
	private static final int IDLE = FamilyEntity.POSE_IDLE, POINT = FamilyEntity.POSE_POINT, SCARED = FamilyEntity.POSE_SCARED,
			PHONE = FamilyEntity.POSE_SHOW_PHONE, PHONE_SCARED = FamilyEntity.POSE_SHOW_PHONE_SCARED, THROW = FamilyEntity.POSE_THROW,
			THROW_BREAD = FamilyEntity.POSE_THROW_BREAD, SHOUT = FamilyEntity.POSE_SHOUT, HAND_OVER = FamilyEntity.POSE_HAND_OVER;
	/**
	 * Blend rates per tick: poses ~6 ticks, into 'scared' 3 (a jolt), the throw's release 3. Every pose channel moves at
	 * the same rate on a given tick (the one the incoming pose sets), so the weights keep summing to 1 mid-blend.
	 */
	private static final float RATE = 0.3F, SCARED_RATE = 0.55F, RELEASE_RATE = 0.6F, TALK_RATE = 0.4F;
	/**
	 * The hand-over beat ("¡Tomá!", chorizo shown): the right fist held out in front and to her right, the chorizo
	 * pointing out of it; a slight lean in, head cocked, brows up, mouth open. Solved with ent_marta.py's solve_arm()
	 * like the generated poses: right wrist (-7, -1, -19), palm (0.9, 0, -0.4), fingers (0, -0.7, -0.7), elbow hint
	 * (-15, 0, -3); fist as in 'throw'; max delta 74 deg.
	 */
	private static final Map<String, float[]> POSE_HAND_OVER = table(
			"body", new float[] {0.0698F, 0F, 0F, 0F, 0F, 0F},
			"right_leg", new float[] {-0.0698F, 0F, 0F, 0F, 0F, 0F},
			"left_leg", new float[] {-0.0698F, 0F, 0F, 0F, 0F, 0F},
			"head", new float[] {0.0698F, 0F, 0.1047F, 0F, 0F, 0F},
			"jaw", new float[] {0.1745F, 0F, 0F, 0F, 0F, 0F},
			"right_brow", new float[] {0F, 0F, 0F, 0F, -0.8F, 0F},
			"left_brow", new float[] {0F, 0F, 0.0698F, 0F, -1.0F, 0F},
			"right_arm", new float[] {-1.2830F, -0.7261F, 0.7592F, 0F, 0F, 0F},
			"right_forearm", new float[] {-0.0751F, 1.0482F, 0F, 0F, 0F, 0F},
			"right_hand", new float[] {-1.2666F, 0.8015F, 0.6145F, 0F, 0F, 0F},
			"right_index", new float[] {0F, 0F, -1.0472F, 0F, 0F, 0F},
			"right_fingers", new float[] {0F, 0F, -0.9599F, 0F, 0F, 0F});
	/** The scared face (jaw + brows) laid over show_phone at 0.6 for "...Lucía no tiene celular". */
	private static final String[] FACE = {"jaw", "right_brow", "left_brow"};

	public MartaModel(ModelPart root) {
		super(root);
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		boolean throwing = a == THROW || a == THROW_BREAD;
		boolean phoneUp = a == PHONE || a == PHONE_SCARED;
		boolean known = a == POINT || a == SCARED || phoneUp || throwing || a == SHOUT || a == HAND_OVER;
		boolean fresh = t < 4F;  // just appeared: already in her pose
		// B3: the copy (look 2, FamilyEntity.LOOK_COPIA) never fidgets: no wringing, no glances, no brows shooting up
		// B3: POSE_CORNER(_TURN) (facing a wall, perfectly still; then the head comes all the way round, the body does not)
		boolean corner = a == FamilyEntity.POSE_CORNER || a == FamilyEntity.POSE_CORNER_TURN;
		float twist = blend(s, 14, a == FamilyEntity.POSE_CORNER_TURN ? 1F : 0F, fresh ? 1F : 0.05F);
		float alive = s.variant == FamilyEntity.LOOK_COPIA || corner ? 0F : 1F;

		// ---- pose weights (cross-fade). One rate for every pose channel on a tick: the incoming pose's (the scared jolt
		// fast), or the release's while a throw is still fading out, so the outgoing and incoming weights sum to 1.
		float rate = fresh ? 1F : a == SCARED ? SCARED_RATE : RATE;
		float release = Math.max(rate, RELEASE_RATE);
		float throwW = blend(s, 4, throwing ? 1F : 0F, throwing ? rate : release);
		if (!throwing && throwW > 0.02F) {
			rate = release;
		}
		float idle = blend(s, 0, known ? 0F : 1F, rate);
		float scared = blend(s, 1, a == SCARED ? 1F : 0F, rate);
		float point = blend(s, 2, a == POINT ? 1F : 0F, rate);
		float showPhone = blend(s, 3, phoneUp ? 1F : 0F, rate);
		float shout = blend(s, 5, a == SHOUT ? 1F : 0F, rate);
		float handOver = blend(s, 11, a == HAND_OVER ? 1F : 0F, rate);
		float phoneScare = blend(s, 6, a == PHONE_SCARED ? 0.6F : 0F, fresh ? 1F : SCARED_RATE);
		float talk = blend(s, 7, FamilyRenderer.talking(s) ? 1F : 0F, TALK_RATE);
		// the release: a fast and a slow fade of the throw; their gap is a ~2-tick kick right after the pose ends
		float relFast = blend(s, 8, throwing ? 1F : 0F, fresh ? 1F : 0.8F);
		float relSlow = blend(s, 9, throwing ? 1F : 0F, fresh ? 1F : 0.4F);
		float snap = Mth.clamp((relSlow - relFast) * 4F, 0F, 1F);
		float yawLag = blend(s, 10, Mth.wrapDegrees(s.yRot), 0.5F);

		apply(POSE_IDLE_NERVOUS, idle);
		apply(POSE_SCARED, scared);
		apply(POSE_POINT, point);
		apply(POSE_SHOW_PHONE, showPhone);
		apply(POSE_THROW, throwW);
		apply(POSE_SHOUT, shout);
		apply(POSE_HAND_OVER, handOver);
		applyRows(POSE_SCARED, phoneScare, FACE);

		// ---- toggles: the chorizo / bread only while winding up the throw (hidden on release: the item flies) and the
		// chorizo while holding it out in the hand-over (hidden when the pose ends: the item is handed over)
		chorizo.visible = a == THROW || a == HAND_OVER;
		bread.visible = a == THROW_BREAD;
		phone.visible = true;

		// ---- idle on every pose
		float breath = Mth.sin(t * 0.09F + Math.floorMod(seed, 31));
		rot("body", 0.02F * breath, 0F, 0F);
		// the wring: hands twisting round the phone at her belly
		rot("right_hand", 0F, 0F, 0.25F * Mth.sin(t * 0.25F) * idle * alive);
		rot("left_hand", 0F, 0.12F * Mth.sin(t * 0.25F + 1.4F) * idle * alive, 0F);
		rot("right_fingers", 0F, 0F, -0.08F * (0.5F + 0.5F * Mth.sin(t * 0.25F + 0.6F)) * idle * alive);
		// nervous head: a slow tilt plus a quick glance aside every 3-5 s
		float calm = (1F - Math.max(throwW, scared)) * alive;
		rot("head", 0F, 0F, 0.05F * Mth.sin(t * 0.07F) * calm);
		float glance = FamilyRenderer.pulse(t, seed, 80F, 2F, 6F, 2F) * FamilyRenderer.side(t, seed, 80F);
		rot("head", 0F, 0.15F * glance * calm * Math.max(0F, 1F - point - handOver), 0F);
		// worried brows shoot up now and then
		float lift = FamilyRenderer.pulse(t, seed + 7, 110F, 3F, 10F, 5F) * calm;
		offset("right_brow", 0F, -0.6F * lift, 0F);
		offset("left_brow", 0F, -0.6F * lift, 0F);
		// scared: trembling
		rot("body", 0F, 0F, 0.02F * Mth.sin(t * 2.1F) * scared);

		// ---- talking: jaw on the syllables, the shout bobs her forward on them
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("jaw", 0.05F * talk + 0.25F * syl, 0F, 0F);
		rot("body", 0.05F * syl * shout, 0F, 0F);
		rot("head", 0.03F * syl * (1F - shout), 0F, 0F);

		// ---- the throw's release: the arm snaps through
		rot("right_arm", 1.6F * snap, 0F, 0F);
		rot("right_forearm", 0.4F * snap, 0F, 0F);

		// ---- walking: legs, a small arm swing (the phone arm barely: the screen stays readable), skirt panels
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed);
		float swing = Mth.cos(pos) * 0.5F * spd;
		rot("right_leg", swing, 0F, 0F);
		rot("left_leg", -swing, 0F, 0F);
		rot("right_arm", -Mth.cos(pos) * 0.25F * spd * Math.max(0F, 1F - throwW - handOver), 0F, 0F);
		rot("left_arm", Mth.cos(pos) * 0.25F * 0.3F * spd, 0F, 0F);
		rot("skirt_right", 0.2F * swing, 0F, 0F);
		rot("skirt_left", -0.2F * swing, 0F, 0F);
		rot("skirt_back", 0.25F * Math.abs(swing), 0F, 0F);
		rot("body", 0F, -0.04F * Mth.sin(pos) * spd, 0F);
		rot("belt_tails", 0.12F * Mth.sin(pos * 2F) * spd, 0F, 0F);
		rot("curlers", 0.03F * Mth.sin(pos * 2F) * spd, 0F, 0F);
		float run = Mth.clamp((spd - 0.6F) * 2.5F, 0F, 1F);
		rot("lapel_right", 0F, 0F, 0.05F * Mth.sin(pos * 2F) * run);
		rot("lapel_left", 0F, 0F, -0.05F * Mth.sin(pos * 2F) * run);

		// ---- head look (neck 30 %, head 70 %); the temple rollers bob a tick after the head turns
		float lookW = corner ? 0F : 1F - 0.5F * throwW;
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -75F, 75F) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.3F, yaw * 0.3F, 0F);
		rot("head", pitch * 0.7F, yaw * 0.7F, 0F);
		float follow = Mth.clamp((Mth.wrapDegrees(s.yRot) - yawLag) * Mth.DEG_TO_RAD * 0.5F, -0.04F, 0.04F);
		rot("curler_right", 0F, 0F, follow);
		rot("curler_left", 0F, 0F, follow);
		if (twist > 0.001F) {
			float e = twist * twist * (3F - 2F * twist);
			float hitch = Mth.sin(t * 9F) * 0.035F * Mth.clamp(twist * (1F - twist) * 4F, 0F, 1F);
			rot("neck", 0F, Mth.PI * 0.3F * e + hitch, 0F);
			rot("head", 0.1F * e, Mth.PI * 0.7F * e + hitch, 0.2F * e);
		}
		if (s.variant == FamilyEntity.LOOK_COPIA) {
			// the copy: the brows lie flat over the wide-open eyes (no worry in that face), the painted grin keeps the jaw shut
			rightBrow.zRot = 0F;
			leftBrow.zRot = 0F;
			jaw.xRot = 0F;
		}
	}

	/** Adds only some bones of a pose table, scaled by w. */
	private void applyRows(Map<String, float[]> pose, float w, String... bones) {
		if (w <= 0.001F) {
			return;
		}
		for (String b : bones) {
			float[] v = pose.get(b);
			if (v != null) {
				rot(b, v[0] * w, v[1] * w, v[2] * w);
				offset(b, v[3] * w, v[4] * w, v[5] * w);
			}
		}
	}
}
