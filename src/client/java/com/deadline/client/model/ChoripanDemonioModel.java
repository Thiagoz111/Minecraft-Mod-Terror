package com.deadline.client.model;

import com.deadline.client.horror.ChoripanDemonioRenderer;
import com.deadline.client.model.gen.ChoripanDemonioModelBase;
import com.deadline.client.render.HauntRenderState;
import com.deadline.horror.casa.dog.ChoripanDemonioEntity;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * The long dog (tools/models/ent_choripan_demonio.py ANIM_NOTES). The renderer lays the chain out along the head's path
 * ({@link ChoripanDemonioRenderer.DemonState}); this model puts the links there, aims the neck at the chest, hides the
 * arms of the links still inside the doghouse, walks the six human hands in a tripod gait driven by the distance the
 * head has travelled, opens the muzzle "flower" while it comes out and chases, sucks the tongue in when it is pulled
 * back -- and the tail never stops wagging.
 */
public class ChoripanDemonioModel extends ChoripanDemonioModelBase {
	private static final float[] REST_ZROT = {0F, -0.0873F, 0F, 0F, 0F, 0F, 0F, 0F};
	/** The arm bones of each link (front legs on link_1; arm pairs on links 3, 5, 7). */
	private static final String[][] ARMS = {{}, {"front_right_leg", "front_left_leg"}, {}, {"arm_1_right", "arm_1_left"}, {},
			{"arm_2_right", "arm_2_left"}, {}, {"arm_3_right", "arm_3_left"}};
	private static final Set<String> HEAD_KEYS = Set.of("head", "jaw_upper_right", "jaw_upper_left", "jaw_lower_right", "jaw_lower_left",
			"right_brow", "left_brow", "tongue", "tongue_tip", "right_ear", "left_ear", "right_ear_tip", "left_ear_tip", "tag");
	private static final Map<String, float[]> RUN_HEAD = only(POSE_RUN, HEAD_KEYS);
	private static final Map<String, float[]> LUNGE_HEAD = only(POSE_LUNGE, HEAD_KEYS);
	@SuppressWarnings("unchecked")
	private static final Map<String, float[]>[] GAIT = new Map[] {POSE_WALK_1, POSE_WALK_2, POSE_WALK_3, POSE_WALK_4};

	public ChoripanDemonioModel(ModelPart root) {
		super(root);
	}

	private static Map<String, float[]> only(Map<String, float[]> pose, Set<String> keys) {
		Map<String, float[]> out = new LinkedHashMap<>();
		for (Map.Entry<String, float[]> e : pose.entrySet()) {
			if (keys.contains(e.getKey())) {
				out.put(e.getKey(), e.getValue());
			}
		}
		return out;
	}

	@Override
	public void setupAnim(HauntRenderState s) {
		super.setupAnim(s);
		float t = s.ageInTicks;
		hide("vomit", true);
		hide("choripan", true);
		if (!(s instanceof ChoripanDemonioRenderer.DemonState d) || !d.trail) {
			apply(POSE_UNSPOOL, 1F);
			return;
		}
		int state = d.state;
		boolean retract = state == ChoripanDemonioEntity.STATE_RETRACT;
		boolean crawl = state == ChoripanDemonioEntity.STATE_CRAWL;

		// ---- the chain, where the renderer laid it
		for (int k = 0; k < 8; k++) {
			ModelPart p = get("link_" + k);
			if (p == null) {
				continue;
			}
			p.x = d.x[k];
			p.y = d.y[k];
			p.z = d.z[k];
			p.xRot = d.pitch[k];
			p.yRot = d.yaw[k];
			p.zRot = REST_ZROT[k];
			for (String arm : ARMS[k]) {
				hide(arm, d.inside[k]);
			}
			// a slow peristaltic breath running toward the tail
			if (k >= 2) {
				p.y += Mth.sin(t * 0.12F + k * 0.7F) * 0.4F;
			}
		}
		// ---- the neck reaches back down to the chest socket
		ModelPart neck = get("neck");
		if (neck != null) {
			float vx = d.x[1] - d.x[0];
			float vy = d.y[1] - 2F - d.y[0];
			float vz = d.z[1] - d.z[0];
			neck.yRot = (float) Mth.atan2(vx, vz);
			neck.xRot = (float) Mth.atan2(-vy, Mth.sqrt(vx * vx + vz * vz)) + Mth.sin(t * 0.08F) * 0.03F;
		}

		// ---- six hands: a tripod gait, one key every half block the head travels
		float phase = d.odo * 2F;
		int key = Math.floorMod(Mth.floor(phase), 4);
		float u = phase - Mth.floor(phase);
		u = u * u * (3F - 2F * u);
		apply(GAIT[key], 1F - u);
		apply(GAIT[(key + 1) % 4], u);
		// idle: one hand twitches now and then
		if (!crawl && Math.floorMod((int) t + s.seed * 7, 37) < 3) {
			rot("hand_" + (1 + Math.floorMod(s.seed + (int) (t / 37F), 3)) + "_right", -0.15F, 0F, 0F);
		}

		// ---- the head: it locks on (head look), the muzzle parts into the flower; pulled back: shut, tongue sucked in
		float out = retract ? 0F : crawl ? 1F : state == ChoripanDemonioEntity.STATE_EMERGE ? Mth.clamp(d.stateTicks / 60F, 0F, 1F) : 0.7F;
		apply(RUN_HEAD, out * (crawl ? 1F : 0.4F));
		if (state == ChoripanDemonioEntity.STATE_HOLD) {
			// waiting, staring: the flower breathes half open
			apply(LUNGE_HEAD, 0.35F + 0.08F * Mth.sin(t * 0.2F));
		}
		float yaw = Mth.clamp(Mth.wrapDegrees(s.yRot) * Mth.DEG_TO_RAD, -0.7F, 0.7F);
		float pitch = Mth.clamp(s.xRot * Mth.DEG_TO_RAD, -0.5F, 0.6F);
		rot("head", pitch, yaw, 0F);
		// the curious-dog head tilt, every few seconds
		float tilt = Math.max(0F, Mth.sin(t * 0.035F + s.seed)) > 0.92F ? 0.35F : 0F;
		rot("head", 0F, 0F, tilt * (crawl ? 0F : 1F));
		if (crawl) {
			rot("tongue", 0F, Mth.sin(t * 0.7F) * 0.3F, 0F);
			rot("tongue_tip", Mth.sin(t * 0.7F - 1F) * 0.4F, 0F, 0F);
		}
		if (retract) {
			offset("tongue", 0F, 0F, 12F);
			rot("right_ear", 0F, 0F, -0.3F);
			rot("left_ear", 0F, 0F, 0.3F);
		}
		// the flaps quiver
		for (String flap : new String[] {"jaw_upper_right", "jaw_upper_left", "jaw_lower_right", "jaw_lower_left"}) {
			rot(flap, Mth.sin(t * 1.7F + flap.length()) * 0.03F * out, 0F, 0F);
		}

		// ---- THE TAIL NEVER STOPS WAGGING (slower while it unspools)
		float ws = state == ChoripanDemonioEntity.STATE_EMERGE ? 0.7F : 1.1F;
		rot("tail", 0F, Mth.sin(t * ws) * 0.55F, 0F);
		rot("tail_tip", 0F, Mth.sin(t * ws - 0.9F) * 0.45F, 0F);
		// sweater shreds
		for (int k = 1; k <= 4; k++) {
			rot("shred_" + k, crawl ? 0.25F : 0F, 0F, Mth.sin(t * 0.15F + k) * 0.06F);
		}
	}
}
