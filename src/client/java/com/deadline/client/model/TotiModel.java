package com.deadline.client.model;

import com.deadline.casa.FamilyEntity;
import com.deadline.client.casa.FamilyRenderer;
import com.deadline.client.model.gen.TotiModelBase;
import com.deadline.client.render.HauntRenderState;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Toti, 15, in ranked: mashes the gamepad (thumbs tapping independently), bobs to the game, leans into the turns and
 * twitches with rage; crouched in the wardrobe he only looks up to shout, slams the door without looking, and at
 * breakfast stands and shrugs. No looks and no toggles (the RGB lives on the emissive layer). Follows the ANIM_NOTES
 * of tools/models/ent_toti.py.
 */
public class TotiModel extends TotiModelBase {
	private static final int CROUCH = FamilyEntity.POSE_CROUCH_CLOSET, SLAM = FamilyEntity.POSE_SLAM, STAND = FamilyEntity.POSE_STAND;
	/** Blend rates: poses ~5 ticks; the slam SNAPS in (3 ticks) and eases back (8). */
	private static final float RATE = 0.35F, SLAM_IN = 0.6F, SLAM_OUT = 0.25F, TALK_RATE = 0.4F;
	/** The concentration tongue (crouch_closet's 'tongue' row): pulled back in whenever he talks. */
	private static final float[] TONGUE = POSE_CROUCH_CLOSET.getOrDefault("tongue", new float[6]);
	/**
	 * 'slam' minus 'crouch_closet': the slam repeats the whole crouch (body, legs, feet), so it is laid on top of the
	 * crouch as its difference and the two weights can never add up to more than one crouch.
	 */
	private static final Map<String, float[]> SLAM_OVER_CROUCH = minus(POSE_SLAM, POSE_CROUCH_CLOSET);

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

		// ---- pose weights (the idle stance is the rest pose: standing, playing). 'crouch' is the shared crouch of
		// crouch_closet AND slam; 'slam' (never above it) moves him from the crouch into the slam on top of it, and
		// 'hunched' is crouch_closet's own share.
		float crouch = blend(s, 0, a == CROUCH || a == SLAM ? 1F : 0F, fresh ? 1F : RATE);
		float slam = Math.min(crouch, blend(s, 1, a == SLAM ? 1F : 0F, fresh ? 1F : a == SLAM ? SLAM_IN : SLAM_OUT));
		float hunched = crouch - slam;
		float stand = blend(s, 2, a == STAND ? 1F : 0F, fresh ? 1F : RATE);
		float talk = blend(s, 3, talking ? 1F : 0F, TALK_RATE);
		// looks up at whoever he is shouting at (SNAP), back down to the pad over ~6 ticks
		float up = blend(s, 4, talking ? 1F : 0F, talking ? 0.6F : 0.17F);
		// slam impact: a fast and a slow copy of the slam; their gap is the hit (shakes the headphones)
		float hitFast = blend(s, 5, a == SLAM ? 1F : 0F, fresh ? 1F : 0.8F);
		float hitSlow = blend(s, 6, a == SLAM ? 1F : 0F, fresh ? 1F : 0.3F);
		float impact = Mth.clamp((hitFast - hitSlow) * 2.5F, 0F, 1F);
		float play = blend(s, 8, a == STAND ? 0F : 1F, fresh ? 1F : RATE);

		apply(POSE_CROUCH_CLOSET, crouch);
		apply(SLAM_OVER_CROUCH, slam);
		apply(POSE_STAND, stand);

		// ---- playing: thumbs mash the buttons independently (3-4 Hz, random holds); the right one stops in the slam
		rot("right_thumb", 0F, 0F, -tap(t, seed, 0F) * play * (1F - slam));
		rot("left_thumb", 0F, 0F, tap(t, seed * 7 + 3, 0.43F) * play);
		// steering: both hands and the shoulders follow the stick a little
		float steer = Mth.sin(t * 0.13F + Math.floorMod(seed, 11));
		rot("right_hand", 0F, 0F, 0.05F * steer * play * (1F - slam));
		rot("left_hand", 0F, 0F, 0.05F * steer * play);
		rot("right_arm", 0F, 0.03F * steer * play * (1F - slam), 0F);
		rot("left_arm", 0F, 0.03F * steer * play, 0F);
		// bobbing to the game's music (2 Hz) and leaning into a turn every 4-7 s
		float bob = 1F - up;
		rot("head", 0.03F * Mth.sin(t * 0.628F) * play * bob, 0F, 0F);
		float turn = FamilyRenderer.pulse(t, seed, 110F, 4F, 14F, 6F) * FamilyRenderer.side(t, seed, 110F) * play * (1F - slam);
		rot("head", 0F, 0F, 0.08F * turn);
		rot("body", 0F, 0F, 0.04F * turn);
		// losing the match: a 3-tick rage twitch of the brows toward the angry V every 3-6 s
		float rage = FamilyRenderer.pulse(t, seed + 5, 90F, 1F, 1F, 1F) * play;
		rot("right_brow", 0F, 0F, 0.15F * rage);
		rot("left_brow", 0F, 0F, -0.15F * rage);
		// breathing and chewing gum
		offset("body", 0F, 0.125F * (1F + Mth.sin(t * 0.105F)), 0F);
		rot("jaw", 0.03F * (1F + Mth.sin(t * 0.785F)) * play * (1F - talk), 0F, 0F);

		// ---- talking: looks up (full face in the wardrobe light), jaw per syllable, the tongue goes back in
		float syl = FamilyRenderer.syllable(t, seed) * talk;
		rot("head", -0.25F * up * (1F - slam), 0F, 0F);
		rot("neck", -0.15F * up * (1F - slam), 0F, 0F);
		rot("jaw", 0.3F * syl, 0F, 0F);
		float tongueIn = hunched * Math.max(up, talk);  // the slam already drops the tongue row
		rot("tongue", -TONGUE[0] * tongueIn, -TONGUE[1] * tongueIn, -TONGUE[2] * tongueIn);
		offset("tongue", -TONGUE[3] * tongueIn, -TONGUE[4] * tongueIn, -TONGUE[5] * tongueIn);

		// ---- slam impact: the headphones shake; the fringe springs behind the head's pitch
		rot("headphones", 0F, 0F, 0.04F * Mth.sin(t * 2.5F) * impact);
		float pitchNow = head.xRot + neck.xRot;
		float pitchLag = blend(s, 7, pitchNow, 0.5F);
		rot("fringe", Mth.clamp((pitchNow - pitchLag) * 0.8F, -0.1F, 0.05F), 0F, 0F);

		// ---- breakfast: the mic boom swings up out of the way
		rot("mic", -1.2F * stand, 0F, 0F);

		// ---- walking: no arm swing (the pad stays in front of him), soles kept flat
		float legs = Math.max(0F, 1F - crouch);
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
		offset("body", 0F, Math.abs(Mth.sin(pos)) * 0.6F * spd, 0F);

		// ---- head look (neck 35 %, head 65 %): absorbed in the game unless he talks; never in the slam; free at breakfast
		float absorbed = 0.35F * (1F - crouch) + up * (1F - 0.35F * (1F - crouch));
		float lookW = (stand + (1F - stand) * absorbed) * (1F - slam);
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -75F, 75F) * Mth.DEG_TO_RAD * lookW;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD * lookW;
		rot("neck", pitch * 0.35F, yaw * 0.35F, 0F);
		rot("head", pitch * 0.65F, yaw * 0.65F, 0F);
	}

	/** to - from, row by row (rows missing on one side count as zero); all-zero rows are dropped. */
	private static Map<String, float[]> minus(Map<String, float[]> to, Map<String, float[]> from) {
		Map<String, float[]> out = new LinkedHashMap<>();
		for (Map.Entry<String, float[]> e : to.entrySet()) {
			float[] f = from.get(e.getKey());
			float[] d = new float[6];
			boolean any = false;
			for (int i = 0; i < 6; i++) {
				d[i] = e.getValue()[i] - (f != null ? f[i] : 0F);
				any |= Math.abs(d[i]) > 1.0E-5F;
			}
			if (any) {
				out.put(e.getKey(), d);
			}
		}
		for (Map.Entry<String, float[]> e : from.entrySet()) {
			if (!to.containsKey(e.getKey())) {
				float[] d = new float[6];
				for (int i = 0; i < 6; i++) {
					d[i] = -e.getValue()[i];
				}
				out.put(e.getKey(), d);
			}
		}
		return out;
	}

	/** One thumb's button mashing: ~3.6 taps a second, a seeded random hold now and then; returns the lift (rad). */
	private static float tap(float t, int seed, float phase) {
		float u = t * 0.18F + phase + Math.floorMod(seed, 13) * 0.37F;
		int n = Mth.floor(u);
		float h = FamilyRenderer.noise(seed, n);
		if (h < -0.35F) {
			return 0F;  // holding the button down
		}
		return Mth.sin((u - n) * Mth.PI) * (0.12F + 0.04F * (h + 1F));
	}
}
