package com.deadline.client.render;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Base for every generated creature model: name lookup of bones, additive pose tables exported from the
 * art tools, and per-entity smoothed blend weights so actions fade in and out instead of snapping.
 */
public abstract class HauntModel extends EntityModel<HauntRenderState> {
	private static final Map<Integer, float[]> BLEND = new HashMap<>();
	private final Map<String, ModelPart> parts = new HashMap<>();
	private final Map<String, java.util.List<ModelPart>> groups = new HashMap<>();

	protected HauntModel(ModelPart root, Function<Identifier, RenderType> renderType) {
		super(root, renderType);
	}

	protected final void part(String name, ModelPart p) {
		parts.put(name, p);
	}

	public final ModelPart get(String name) {
		return parts.get(name);
	}

	/** All parts whose name starts with prefix, sorted by name (e.g. "skirt_" -> skirt_0..skirt_7). */
	protected final java.util.List<ModelPart> group(String prefix) {
		return groups.computeIfAbsent(prefix, k -> parts.keySet().stream().filter(n -> n.startsWith(k)).sorted()
				.map(parts::get).toList());
	}

	/** Adds a travelling sine wave to every part of a group (cloth, hair, tails). */
	protected final void ripple(String prefix, float t, float freq, float step, float ax, float az, float bias) {
		java.util.List<ModelPart> g = group(prefix);
		for (int i = 0; i < g.size(); i++) {
			ModelPart p = g.get(i);
			p.xRot += Mth.sin(t * freq + i * step) * ax + bias;
			p.zRot += Mth.cos(t * freq * 0.83F + i * step * 1.3F) * az;
		}
	}

	public final boolean has(String name) {
		return parts.containsKey(name);
	}

	/** Pose tables exported by the art tools (overridden by the generated base). */
	protected Map<String, Map<String, float[]>> poses() {
		return Map.of();
	}

	protected final Map<String, float[]> pose(String name) {
		return poses().get(name);
	}

	/** Builds a pose table from ("bone", float[6]) pairs. */
	public static Map<String, float[]> table(Object... kv) {
		Map<String, float[]> m = new LinkedHashMap<>();
		for (int i = 0; i + 1 < kv.length; i += 2) {
			m.put((String) kv[i], (float[]) kv[i + 1]);
		}
		return m;
	}

	protected final void rot(String name, float x, float y, float z) {
		ModelPart p = parts.get(name);
		if (p != null) {
			p.xRot += x;
			p.yRot += y;
			p.zRot += z;
		}
	}

	protected final void offset(String name, float x, float y, float z) {
		ModelPart p = parts.get(name);
		if (p != null) {
			p.x += x;
			p.y += y;
			p.z += z;
		}
	}

	protected final void scale(String name, float x, float y, float z) {
		ModelPart p = parts.get(name);
		if (p != null) {
			p.xScale *= x;
			p.yScale *= y;
			p.zScale *= z;
		}
	}

	protected final void hide(String name, boolean hidden) {
		ModelPart p = parts.get(name);
		if (p != null) {
			p.visible = !hidden;
		}
	}

	/** Adds a pose table scaled by weight w. */
	protected final void apply(Map<String, float[]> pose, float w) {
		if (w <= 0.001F || pose == null) {
			return;
		}
		for (Map.Entry<String, float[]> e : pose.entrySet()) {
			float[] v = e.getValue();
			rot(e.getKey(), v[0] * w, v[1] * w, v[2] * w);
			offset(e.getKey(), v[3] * w, v[4] * w, v[5] * w);
		}
	}

	/** Head tracking spread over neck and head (degrees from the render state). */
	protected final void look(HauntRenderState s, float neckShare) {
		float yaw = Mth.clamp(s.yRot, -75F, 75F) * Mth.DEG_TO_RAD;
		float pitch = Mth.clamp(s.xRot, -45F, 45F) * Mth.DEG_TO_RAD;
		if (has("neck")) {
			rot("neck", pitch * neckShare, yaw * neckShare, 0F);
			rot("head", pitch * (1F - neckShare), yaw * (1F - neckShare), 0F);
		} else {
			rot("head", pitch, yaw, 0F);
		}
	}

	/** Classic limb swing from the walk animation. */
	protected final void walk(HauntRenderState s, String leftLeg, String rightLeg, String leftArm, String rightArm, float legAmp, float armAmp) {
		float pos = s.walkAnimationPos * 0.6662F;
		float spd = Math.min(1F, s.walkAnimationSpeed);
		rot(rightLeg, Mth.cos(pos) * legAmp * spd, 0F, 0F);
		rot(leftLeg, Mth.cos(pos + Mth.PI) * legAmp * spd, 0F, 0F);
		rot(rightArm, Mth.cos(pos + Mth.PI) * armAmp * spd, 0F, 0F);
		rot(leftArm, Mth.cos(pos) * armAmp * spd, 0F, 0F);
	}

	/** Smoothly moves a per-entity weight (channel 0..15) toward target; rate is per tick (0..1). */
	protected static float blend(HauntRenderState s, int channel, float target, float rate) {
		float[] st = BLEND.computeIfAbsent(s.seed, k -> new float[32]);
		float dt = s.ageInTicks - st[16 + channel];
		st[16 + channel] = s.ageInTicks;
		if (dt < 0F || dt > 40F) {
			st[channel] = target;
			return target;
		}
		float k = 1F - (float) Math.pow(1F - rate, dt);
		st[channel] += (target - st[channel]) * k;
		if (BLEND.size() > 1024) {
			BLEND.clear();
		}
		return st[channel];
	}

	protected static float wave(float t, float freq, float phase) {
		return Mth.sin(t * freq + phase);
	}
}
