package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.JorgeModelBase;
import com.deadline.client.render.HauntRenderState;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Jorge Morales, "el rey del asado": the "es la humedad, flaco" stance (sways, pats the belly, clacks the tongs), the
 * charcoal sack, and possessed by Azamel (look 1: the grin, black eyes, the angry V) flipping chorizos with his bare
 * hands, conducting the knives, then falling like a sack into the pelopincho. Follows the ANIM_NOTES of
 * tools/models/ent_jorge.py (lean rule: leans go on 'chest', 'body' only bobs; apron rule: the skirt hangs).
 */
public class JorgeModel extends JorgeModelBase {
	private static final int POINT = FamilyEntity.POSE_POINT, GRILL = FamilyEntity.POSE_GRILL_FLIP, KNIFE = FamilyEntity.POSE_KNIFE_CONDUCT,
			LIMP = FamilyEntity.POSE_LIMP_FALL, BAG = FamilyEntity.POSE_CARRY_BAG;
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
	/** limp_fall timing: a slow clock read back as ticks since the pose began; the fall takes 7 ticks, legs 2 behind. */
	private static final float CLOCK_RATE = 0.02F, FALL_TICKS = 7F, LEG_LAG = 2F;
	private static final double LOG_CLOCK = Math.log(1F - CLOCK_RATE);

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
		// B3: the copy (look 2, FamilyEntity.LOOK_COPIA): Jorge's body, perfectly still -- no pats, no clacks, no sway
		boolean copy = s.variant == FamilyEntity.LOOK_COPIA;
		// B3: POSE_CORNER(_TURN) (facing a wall, perfectly still; then the head comes all the way round, the body does not)
		boolean corner = a == FamilyEntity.POSE_CORNER || a == FamilyEntity.POSE_CORNER_TURN;
		float twist = blend(s, 14, a == FamilyEntity.POSE_CORNER_TURN ? 1F : 0F, fresh ? 1F : 0.05F);
		boolean limp = a == LIMP;
		boolean known = a == POINT || a == GRILL || a == KNIFE || limp || a == BAG;

		// ---- pose weights
		float rate = fresh ? 1F : RATE;
		float idle = blend(s, 0, known ? 0F : 1F, rate);
		float fidget = copy || corner ? 0F : idle;
		float point = blend(s, 1, a == POINT ? 1F : 0F, rate);
		float grill = blend(s, 2, a == GRILL ? 1F : 0F, rate);
		float knife = blend(s, 3, a == KNIFE ? 1F : 0F, rate);
		float bagW = blend(s, 5, a == BAG ? 1F : 0F, fresh ? 1F : a == BAG ? RATE : 0.6F);
		// limp_fall: ease-IN over 7 ticks (stiff, then he drops), the last stretch snaps (the thud), legs 2 ticks late
		float clock = blend(s, 4, limp ? 1F : 0F, fresh ? 1F : limp ? CLOCK_RATE : 0.3F);
		float since = clock >= 0.9999F ? Float.MAX_VALUE : (float) (Math.log(1F - clock) / LOG_CLOCK);
		float fall = blend(s, 10, limp ? easeIn(since / FALL_TICKS) : 0F, limp ? 1F : 0.25F);
		float fallLegs = blend(s, 11, limp ? easeIn((since - LEG_LAG) / FALL_TICKS) : 0F, limp ? 1F : 0.25F);
		float poseido = blend(s, 6, possessed ? 1F : 0F, fresh ? 1F : POSSESS_RATE);
		float talk = blend(s, 7, FamilyRenderer.talking(s) ? 1F : 0F, TALK_RATE);
		// salt hit: the stun counter jumping up = a hit; a lagging copy turns the jump into a ~4-tick flinch
		float stun = FamilyRenderer.stun(s);
		float stunLag = blend(s, 8, stun, 0.5F);
		float flinch = Mth.clamp((stun - stunLag) / 12F, 0F, 1F);

		apply(POSE_IDLE, idle);
		apply(POSE_POINT, point);
		apply(POSE_GRILL_FLIP, grill);
		apply(POSE_KNIFE_CONDUCT, knife);
		apply(POSE_CARRY_BAG, bagW);
		applySplit(POSE_LIMP_FALL, fall, fallLegs);
		apply(POSEIDO, poseido);
		apply(FLINCH, flinch);

		// ---- toggles: TOGGLE_DEFAULT -> look -> pose (a pose wins)
		smile.visible = possessed;
		smileJaw.visible = possessed;
		demonEyes.visible = possessed;
		bag.visible = a == BAG;
		tongs.visible = a != BAG && a != GRILL && !limp && !copy && !corner;

		// ---- idle on every pose: breathing (chest + belly), a slow sway of the weight from foot to foot
		float upright = 1F - fall;
		float breath = Mth.sin(t * 0.09F + Math.floorMod(seed, 29));
		lean(-0.01F * breath * upright);
		offset("belly", 0F, 0F, -0.2F * (1F + breath));
		rot("chest", 0F, 0.02F * Mth.sin(t * 0.03F + 1F) * fidget, 0.03F * Mth.sin(t * 0.045F) * fidget);
		rot("neck", 0F, 0F, -0.015F * Mth.sin(t * 0.045F) * fidget);
		// a belly pat every 4-8 s (two taps)
		float pat = FamilyRenderer.pulse(t, seed, 120F, 0F, 6F, 0F);
		rot("left_hand", 0.15F * Math.abs(Mth.sin(t * 1.05F)) * pat * fidget, 0F, 0F);
		// the tongs clack every 5-9 s: closed 2 ticks, open over 2, twice
		float clackW = tongs.visible ? 1F - grill : 0F;
		float clack = clack(FamilyRenderer.pulse(t, seed + 3, 140F, 0F, 8F, 0F) > 0F, t, seed);
		rot("tongs_arm", 0F, -0.26F * clack * clackW, 0F);

		// ---- grill_flip: 16-tick cycle; the right hand flips (3 up, 5 back), the left presses on the off-beat
		if (grill > 0.001F) {
			float p = mod(t + Math.floorMod(seed, 16), 16F);
			float flip = p < 3F ? p / 3F : p < 8F ? 1F - (p - 3F) / 5F : 0F;
			rot("right_forearm", -0.35F * flip * grill, 0F, 0F);
			rot("right_hand", -0.6F * flip * grill, 0F, 0F);
			float press = p >= 8F && p < 12F ? Mth.sin((p - 8F) / 4F * Mth.PI) : 0F;
			offset("left_hand", 0F, 0.6F * press * grill, 0F);
			rot("head", 0F, 0F, 0.1F * Mth.sin(t * 0.157F) * grill);
		}
		// ---- knife_conduct: a downbeat every 10 ticks (2 down, 8 back); the left arm on the off-beats
		if (knife > 0.001F) {
			float p = mod(t, 10F);
			float down = p < 2F ? p / 2F : 1F - (p - 2F) / 8F;
			float q = mod(t + 5F, 10F);
			float off = q < 2F ? q / 2F : 1F - (q - 2F) / 8F;
			rot("right_arm", 0.25F * down * knife, 0F, 0F);
			rot("left_arm", 0.1F * off * knife, 0F, 0F);
			offset("body", 0F, 0.3F * down * knife, 0F);
		}

		// ---- talking: jaw per syllable (shouted when possessed), the moustache bobs, tiny nods
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		float loud = Math.max(poseido, knife);
		rot("jaw", (0.22F + 0.23F * loud) * syl, 0F, 0F);
		offset("moustache", 0F, 0.3F * syl, 0F);
		rot("head", 0.05F * Mth.sin(t * 0.3F) * talk * upright, 0F, 0F);
		// possessed: the grin's halves chatter at ~5 Hz when he is not talking
		rot("jaw", 0.03F * (1F + Mth.sin(t * 1.57F)) * poseido * (1F - talk) * upright, 0F, 0F);
		// the flinch: the belly is a jelly
		offset("belly", 0F, 0F, 0.8F * flinch * Mth.cos(t * 1.6F));

		// ---- afloat in the pelopincho (limp_fall in water): bobbing, the belly island, the feet paddling
		if (limp && FamilyRenderer.wet(s)) {
			offset("body", 0F, 0.3F * Mth.sin(t * 0.21F) * fall, 0F);
			offset("belly", 0F, 0F, -0.4F * fall);
			rot("right_shin", 0.1F * Mth.sin(t * 0.3F) * fallLegs, 0F, 0F);
			rot("left_shin", -0.1F * Mth.sin(t * 0.3F) * fallLegs, 0F, 0F);
		}

		// ---- walking (a waddle; with the sack: legs only and a sideways sway)
		float ph = s.walkAnimationPos * 0.6662F;
		float sp = Math.min(1F, s.walkAnimationSpeed) * upright;
		float w = Mth.sin(ph);
		offset("body", 0F, Math.abs(w) * 0.8F * sp, 0F);
		rot("chest", 0F, w * 0.05F * sp * (1F - bagW), w * (0.06F - 0.01F * bagW) * sp);
		offset("belly", 0F, Mth.sin(2F * ph - 0.6F) * 0.5F * sp, 0F);
		float rightLeg = w * 0.45F * sp;
		rot("right_leg", rightLeg, 0F, 0F);
		rot("left_leg", -rightLeg, 0F, 0F);
		rot("right_shin", Math.max(0F, Mth.sin(ph + 1.2F)) * 0.4F * sp, 0F, 0F);
		rot("left_shin", Math.max(0F, Mth.sin(ph + Mth.PI + 1.2F)) * 0.4F * sp, 0F, 0F);
		float arms = sp * (1F - bagW) * (1F - Math.max(grill, knife));
		rot("right_arm", -w * 0.35F * arms, 0F, 0F);
		rot("left_arm", w * 0.35F * arms, 0F, 0F);
		// apron rule: the forward thigh (negative xRot; one leg is always the forward one) pushes the hem forward,
		// -max(0, -legX) * 0.6, lagging ~2 ticks behind the legs
		float forwardThigh = Math.max(0F, Math.max(-rightLeg, rightLeg));
		rot("apron_hem", blend(s, 12, -0.6F * forwardThigh, 0.5F), 0F, 0F);

		// ---- head look (neck 30 %, head 70 %); none while he lies KO'd
		float lookW = corner ? 0F : upright * (1F - 0.5F * grill) * (1F - 0.6F * knife);
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -75F, 75F) * Mth.DEG_TO_RAD * lookW;
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

	/** limp_fall rows: the legs (hips and knees) with their own, lagging weight. */
	private void applySplit(Map<String, float[]> pose, float w, float wLegs) {
		for (Map.Entry<String, float[]> e : pose.entrySet()) {
			String bone = e.getKey();
			float k = bone.endsWith("_leg") || bone.endsWith("_shin") ? wLegs : w;
			if (k <= 0.001F) {
				continue;
			}
			float[] v = e.getValue();
			rot(bone, v[0] * k, v[1] * k, v[2] * k);
			offset(bone, v[3] * k, v[4] * k, v[5] * k);
		}
	}

	/** w = u^2 (stiff, then the drop), the last 10 % snapped. */
	private static float easeIn(float u) {
		if (u <= 0F) {
			return 0F;
		}
		return u >= 0.9F ? 1F : u * u;
	}

	/** "clack clack": closed 2 ticks, open over 2, twice, during an active clack window. */
	private static float clack(boolean on, float t, int seed) {
		if (!on) {
			return 0F;
		}
		float p = mod(t + Math.floorMod(seed, 4), 4F);
		return p < 2F ? 1F : 1F - (p - 2F) / 2F;
	}

	private static float mod(float x, float m) {
		float r = x % m;
		return r < 0F ? r + m : r;
	}
}
