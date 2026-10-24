package com.deadline.client.hunt;

import com.deadline.client.model.gen.NonaModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.hunt.NonaRotaEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The broken Nona (B2, the hunt of Act 5) on the Nona's own geometry (tools/models/ent_nona.py, look 'rota'): the hunt
 * poses of the module (crawl_spider, stand_tall, listen, neck_twist, ceiling_hang, jumpscare) cross-faded, plus what a
 * pose table cannot do: the STRETCH (legs, spine, neck and arms scaled up to ~2.5 blocks, the hips lifted to match),
 * the two gaits (the spider scuttle, belly up, the head upside down in front; the upright walker-less stumble) and the
 * TRANSFORM timeline of "La Nona se rompe" (trembling 0-30, the neck turning 180 in jerks 30-90 while the jaw unhinges,
 * the stretch to the ceiling 90-120, the drop onto all fours 120-150).
 * The normal Nona (FamilyEntity, NonaModel) is untouched: this model only exists for NonaRotaEntity and the jumpscare.
 */
public class NonaRotaModel extends NonaModelBase {
	/**
	 * The stretch: the legs grow by LEG_GROW of their 15 texels (the hips rise to match), the neck and the arms by
	 * NECK_GROW / ARM_GROW, and the whole body by GROW about the floor. Nothing above the neck is scaled on its own
	 * (children inherit the scale: a stretched chest would stretch the face too).
	 */
	private static final float LEG_GROW = 0.9F, LEG_LEN = 15F, NECK_GROW = 0.5F, ARM_GROW = 0.5F, GROW = 0.2F;
	/** hair_loose_0..4: added rotation (rad, x / z) that makes the white locks hang down lank when she stands. */
	private static final float[][] HANG = {{-0.6769F, 2.0935F}, {0.2428F, -0.4164F}, {0.2639F, 0.4601F}, {-0.3515F, -0.3402F},
			{-0.3305F, 0.2867F}};
	private static final float RATE = 0.22F, FAST = 0.5F;

	private final ModelPart[] loose;

	public NonaRotaModel(ModelPart root) {
		super(root);
		this.loose = new ModelPart[] {hairLoose0, hairLoose1, hairLoose2, hairLoose3, hairLoose4};
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		int a = s.action;
		int seed = s.seed;
		float at = s instanceof NonaRotaRenderer.State st ? st.actionTime : 1000F;
		boolean fresh = t < 4F;
		boolean before = s.variant == NonaRotaEntity.LOOK_BEFORE;

		// ---------------------------------------------------------------- the transformation timeline
		boolean tf = a == NonaRotaEntity.ACT_TRANSFORM;
		float tfTwist = 0F, tfJaw = 0F, tfTall = 0F, tfDrop = 0F, tfShake = 0F;
		if (tf) {
			tfShake = Mth.clamp(at / 30F, 0F, 1F);
			// the neck turns in jerks: five snaps between 30 and 90, each one eased over 5 ticks
			if (at > 30F) {
				float u = Mth.clamp((at - 30F) / 60F, 0F, 1F) * 5F;
				int step = Mth.floor(u);
				float frac = Mth.clamp((u - step) * 2.4F, 0F, 1F);
				tfTwist = Math.min(1F, (step + frac * frac * (3F - 2F * frac)) / 5F);
			}
			tfJaw = Mth.clamp((at - 60F) / 30F, 0F, 1F);
			tfTall = smooth(Mth.clamp((at - 90F) / 30F, 0F, 1F));
			tfDrop = smooth(Mth.clamp((at - 120F) / 14F, 0F, 1F));
			tfTall *= 1F - tfDrop;
			tfTwist *= 1F - tfDrop;
		}

		// ---------------------------------------------------------------- pose weights (one shared rate per tick)
		float rate = fresh ? 1F : a == NonaRotaEntity.ACT_GRAB || a == NonaRotaEntity.ACT_RECOIL ? FAST : RATE;
		boolean crawlAct = a == NonaRotaEntity.ACT_CRAWL || a == NonaRotaEntity.ACT_FLEE || a == NonaRotaEntity.ACT_SEARCH_LOW;
		boolean tallAct = a == NonaRotaEntity.ACT_UPRIGHT || a == NonaRotaEntity.ACT_SEARCH || a == NonaRotaEntity.ACT_RECOIL;
		float crawl = blend(s, 0, crawlAct ? 1F : tf ? tfDrop : 0F, tf ? 1F : rate);
		float tall = blend(s, 1, tallAct ? 1F : a == NonaRotaEntity.ACT_LISTEN ? 0.7F : tf ? tfTall : 0F, tf ? 1F : rate);
		float listen = blend(s, 2, a == NonaRotaEntity.ACT_LISTEN ? 1F : 0F, rate);
		float grab = blend(s, 3, a == NonaRotaEntity.ACT_GRAB ? 1F : 0F, fresh ? 1F : 0.6F);
		float ceiling = blend(s, 4, a == NonaRotaEntity.ACT_CEILING ? 1F : 0F, rate);
		float search = blend(s, 5, a == NonaRotaEntity.ACT_SEARCH ? 1F : 0F, rate);
		float searchLow = blend(s, 6, a == NonaRotaEntity.ACT_SEARCH_LOW ? 1F : 0F, rate);
		float recoil = blend(s, 7, a == NonaRotaEntity.ACT_RECOIL ? 1F : 0F, rate);
		float twist = tf ? tfTwist : blend(s, 8, 0F, rate);
		// the crawl and the hang own the whole body: the upright poses fade under them
		float up = Math.max(0F, 1F - crawl - ceiling);
		tall *= up;
		listen *= up;
		search *= up;
		recoil *= up;

		apply(POSE_CRAWL_SPIDER, crawl);
		apply(POSE_CEILING_HANG, ceiling);
		apply(POSE_STAND_TALL, tall);
		apply(POSE_LISTEN, listen * (1F - grab));
		apply(POSE_NECK_TWIST, twist);
		apply(POSE_JUMPSCARE, grab * up);

		// ---------------------------------------------------------------- toggles
		walker.visible = false;
		rocker.visible = false;
		bun.visible = false;
		yarnBall.visible = false;
		mate.visible = false;
		chancleta.visible = false;
		needleRight.visible = false;
		needleLeft.visible = false;
		yarnRight.visible = false;
		yarnLeft.visible = false;
		dentures.visible = false;
		glasses.visible = before;
		boolean bones = !before || tf && at > 60F;
		jawLong.visible = bones;
		teethUpper.visible = bones;
		rightTalons.visible = !before || tf && at > 90F;
		leftTalons.visible = rightTalons.visible;
		spine.visible = !before || tf && at > 96F;
		for (ModelPart p : loose) {
			p.visible = true;
		}

		// ---------------------------------------------------------------- the stretch
		float stretch = Math.max(tall, tf ? tfTall : 0F);
		float legs = 1F + LEG_GROW * stretch;
		float grow = 1F + GROW * stretch;
		scale("base", grow, grow, grow);
		scale("right_leg", 1F, legs, 1F);
		scale("left_leg", 1F, legs, 1F);
		offset("body", 0F, -LEG_LEN * LEG_GROW * stretch, 0F);
		scale("neck", 1F, 1F + NECK_GROW * Math.max(stretch, 0.6F * crawl), 1F);
		float arms = 1F + ARM_GROW * Math.max(stretch, 0.6F * crawl + 0.6F * ceiling);
		scale("right_arm", 1F, arms, 1F);
		scale("left_arm", 1F, arms, 1F);
		// the longer arms in the crawl push the hands through the floor: lift the bridge to match
		offset("base", 0F, -4.5F * crawl * (arms - 1F) / ARM_GROW, 0F);

		// ---------------------------------------------------------------- breathing, the tremor, the jaw
		float spd = Math.min(1F, s.walkAnimationSpeed);
		float pos = s.walkAnimationPos;
		rot("chest", 0.04F * Mth.sin(t * 0.11F + Math.floorMod(seed, 13)), 0F, 0F);
		float jitter = tf ? tfShake * (1F - tfDrop) : 0.25F;
		rot("head", jitter * 0.05F * FamilyNoise.n(seed, (int) (t * 1.7F)), jitter * 0.07F * FamilyNoise.n(seed + 3, (int) (t * 1.3F)), 0F);
		rot("chest", jitter * 0.03F * FamilyNoise.n(seed + 5, (int) (t * 2.1F)), 0F, jitter * 0.03F * FamilyNoise.n(seed + 7, (int) (t * 1.9F)));
		// the jaw hangs open; it clacks now and then, and drops all the way when she lunges or screams
		float clack = Math.max(0F, Mth.sin(t * 0.21F + seed)) > 0.97F ? 0.25F : 0F;
		float jawOpen = (before && !tf ? 0.05F : 0.3F) + 0.35F * tfJaw + clack - 0.15F * listen;
		rot("jaw", jawOpen, 0F, 0F);
		rot("jaw_long", 0.12F * Mth.sin(t * 0.07F), 0F, 0F);
		// the talons twitch, one finger at a time
		rot("right_talons", 0.2F * Math.max(0F, Mth.sin(t * 0.3F + seed)), 0F, 0F);
		rot("left_talons", 0.2F * Math.max(0F, Mth.sin(t * 0.27F + seed * 2F)), 0F, 0F);

		// ---------------------------------------------------------------- gaits
		// the spider scuttle: diagonal pairs (right hand + left foot, left hand + right foot), quick and jerky, the
		// bridge bobbing and rocking, the upside-down head snapping side to side
		float c = crawl * spd;
		if (c > 0.01F) {
			float ph = pos * 1.25F;
			float sw = Mth.sin(ph);
			float lift = Math.max(0F, Mth.cos(ph));
			float lift2 = Math.max(0F, -Mth.cos(ph));
			rot("right_arm", 0.55F * sw * c, 0F, -0.35F * lift * c);
			rot("left_leg", 0.5F * sw * c, 0F, 0.3F * lift * c);
			rot("left_arm", -0.55F * sw * c, 0F, 0.35F * lift2 * c);
			rot("right_leg", -0.5F * sw * c, 0F, -0.3F * lift2 * c);
			rot("right_forearm", -0.4F * lift * c, 0F, 0F);
			rot("left_forearm", -0.4F * lift2 * c, 0F, 0F);
			offset("base", 0F, -1.2F * Math.abs(Mth.sin(ph)) * c, 0F);
			rot("base", 0F, 0F, 0.08F * Mth.sin(ph) * c);
			rot("head", 0F, 0F, 0.35F * FamilyNoise.n(seed + 11, (int) (t * 0.45F)) * c);
		}
		// at rest in the crawl she is never still: the fingers drum, the head turns as if counting
		float crawlIdle = crawl * (1F - spd);
		rot("head", 0F, 0.25F * Mth.sin(t * 0.05F) * crawlIdle, 0F);
		rot("right_hand", 0.15F * Math.max(0F, Mth.sin(t * 0.6F)) * crawlIdle, 0F, 0F);
		rot("left_hand", 0.15F * Math.max(0F, Mth.sin(t * 0.6F + 1.7F)) * crawlIdle, 0F, 0F);
		// the upright stumble: long stiff legs, a lurch on every step, the head lolling, the arms dangling
		float u = tall * (1F - search) * (1F - recoil) * spd;
		if (u > 0.01F) {
			float ph = pos * 0.55F;
			rot("right_leg", 0.45F * Mth.cos(ph) * u, 0F, 0F);
			rot("left_leg", -0.45F * Mth.cos(ph) * u, 0F, 0F);
			rot("body", 0F, 0.1F * Mth.sin(ph) * u, 0.12F * Mth.sin(ph) * u);
			rot("chest", 0.08F * Math.abs(Mth.sin(ph)) * u, 0F, -0.1F * Mth.sin(ph) * u);
			rot("head", 0F, 0F, 0.25F * Mth.sin(ph * 0.5F + 0.6F) * u);
			rot("right_arm", -0.2F * Mth.cos(ph) * u, 0F, 0.05F * u);
			rot("left_arm", 0.2F * Mth.cos(ph) * u, 0F, -0.05F * u);
			offset("body", 0F, 1.0F * Math.abs(Mth.sin(ph)) * u, 0F);
		}

		// ---------------------------------------------------------------- listen: frozen, the head cocked, sniffing
		if (listen > 0.01F) {
			float sniff = Math.max(0F, Mth.sin(t * 0.9F)) * Math.max(0F, Mth.sin(t * 0.13F));
			rot("head", 0.06F * sniff * listen, 0F, 0F);
			rot("neck", 0.03F * sniff * listen, 0F, 0F);
		}

		// ---------------------------------------------------------------- search: leaning in, the face at the slats
		if (search > 0.01F) {
			rot("chest", 0.55F * search, 0F, 0F);
			rot("neck", 0.5F * search, 0F, 0F);
			rot("head", -0.8F * search, 0F, 0.35F * search);
			offset("body", 0F, 4F * search, -3F * search);
		}
		if (searchLow > 0.01F) {
			rot("neck", -0.35F * searchLow, 0F, 0F);
			rot("head", 0F, 0F, 0.4F * Mth.sin(t * 0.08F) * searchLow);
		}

		// ---------------------------------------------------------------- recoil: arms over the face, shaking, hissing
		if (recoil > 0.01F) {
			rot("chest", -0.45F * recoil, 0F, 0F);
			rot("head", -0.5F * recoil, 0F, 0F);
			rot("right_arm", -2.2F * recoil, 0F, 0.5F * recoil);
			rot("left_arm", -2.0F * recoil, 0F, -0.6F * recoil);
			rot("right_forearm", -1.0F * recoil, 0F, 0F);
			rot("left_forearm", -1.1F * recoil, 0F, 0F);
			rot("body", 0.1F * Mth.sin(t * 3.1F) * recoil, 0F, 0.08F * Mth.sin(t * 2.7F) * recoil);
			rot("jaw", 0.4F * recoil, 0F, 0F);
		}

		// ---------------------------------------------------------------- grab / jumpscare: the lunge
		if (grab > 0.01F) {
			rot("head", 0.06F * Mth.sin(t * 4.3F) * grab, 0.05F * Mth.sin(t * 5.1F) * grab, 0F);
			rot("jaw", 0.25F * grab, 0F, 0F);
		}

		// ---------------------------------------------------------------- the white hair: lank and hanging when she stands,
		// falling to the floor round her upside-down head in the crawl (the module's rest), swaying slowly
		float hang = Math.max(0F, up - grab);
		for (int k = 0; k < loose.length; k++) {
			loose[k].xRot += HANG[k][0] * hang;
			loose[k].zRot += HANG[k][1] * hang;
			loose[k].yRot += 0.05F * Mth.sin(t * 0.03F + 2.1F * k);
		}
		ripple("hair_loose_", t, 0.04F, 1.3F, 0.06F, 0.08F, 0F);

		// ---------------------------------------------------------------- the head follows you only when she stands
		float lookW = Math.max(0F, up - search - grab - recoil) * (1F - listen * 0.6F) * (tf ? 0F : 1F);
		if (lookW > 0.01F) {
			float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot), -70F, 70F) * Mth.DEG_TO_RAD * lookW;
			float pitch = Mth.clamp(s.xRot, -40F, 40F) * Mth.DEG_TO_RAD * lookW;
			rot("neck", pitch * 0.35F, yaw * 0.35F, 0F);
			rot("head", pitch * 0.65F, yaw * 0.65F, 0F);
		}
	}

	private static float smooth(float x) {
		return x * x * (3F - 2F * x);
	}

	/** Deterministic -1..1 noise per (seed, n) for jerky, unrepeating twitches. */
	static final class FamilyNoise {
		private FamilyNoise() {
		}

		static float n(int seed, int n) {
			int h = seed * 0x9E3779B1 + n * 0x85EBCA6B;
			h ^= h >>> 15;
			h *= 0x2C1B3C6D;
			h ^= h >>> 12;
			return (h & 0xFFFF) / 32767.5F - 1F;
		}
	}
}
