package com.deadline.client.casa;

import com.deadline.DeadLine;
import com.deadline.casa.FamilyEntity;
import com.deadline.client.render.HauntRenderState;
import com.deadline.client.render.HauntRenderer;
import com.deadline.entity.HauntEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.Arrays;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * {@link HauntRenderer} with looks: the entity's variant picks {@code textures/entity/<key>.png} or
 * {@code <key>_<look>.png} and the matching emissive {@code ..._eyes.png} layer. Written for the Morales family
 * (Jorge 'poseido', the Nona 'poseida') and generic enough for any haunt with looks (Lucía normal / poseida, Ofelia
 * cortada / cosida): {@code new FamilyRenderer<>(ctx, model, shadow, "muneca", true, "", "cosida")}.
 * <p>The render state is a {@link State} (a {@link HauntRenderState}, so every existing haunt model works with it); a
 * {@link FamilyEntity} also fills in whether it is talking and floating. The static helpers are shared by the family
 * animators.
 */
public class FamilyRenderer<T extends HauntEntity, M extends EntityModel<HauntRenderState>> extends HauntRenderer<T, M> {
	/** HauntRenderState + the look index and the family's synced extras. */
	public static class State extends HauntRenderState {
		public int look;
		public boolean talking;
		public boolean floating;
		public boolean wet;
		public int stun;
		/** C: the expression bits of a {@link FamilyEntity} (EXPR_STARE, EXPR_SMILE). */
		public int expr;
	}

	/** C: how far round (degrees off the body) a staring head is drawn (FamilyEntity.EXPR_STARE). */
	public static final float STARE_MAX = 170F;

	private final Identifier[] textures;
	private final Identifier[] eyes;
	private final LookGlow<M> glow;
	private boolean glowAttached;

	/**
	 * looks[v] = texture suffix of variant v ("" = the plain {@code <key>.png}); none = a single look. glow: every look
	 * has its {@code <texture>_eyes.png} emissive layer.
	 */
	public FamilyRenderer(EntityRendererProvider.Context ctx, M model, float shadow, String key, boolean glow, String... looks) {
		this(ctx, model, shadow, key, looks.length == 0 ? new String[] {""} : looks, filled(Math.max(1, looks.length), glow));
	}

	/** Full control: glow[v] false = look v has no emissive layer (no {@code _eyes.png} for it). */
	public FamilyRenderer(EntityRendererProvider.Context ctx, M model, float shadow, String key, String[] looks, boolean[] glow) {
		super(ctx, model, shadow, key, false);
		int n = Math.max(1, looks.length);
		this.textures = new Identifier[n];
		this.eyes = new Identifier[n];
		RenderType[] types = new RenderType[n];
		boolean any = false;
		for (int i = 0; i < n; i++) {
			String look = i < looks.length ? looks[i] : null;
			String base = look == null || look.isEmpty() ? key : key + "_" + look;
			this.textures[i] = DeadLine.id("textures/entity/" + base + ".png");
			if (i < glow.length && glow[i]) {
				this.eyes[i] = DeadLine.id("textures/entity/" + base + "_eyes.png");
				types[i] = RenderTypes.eyes(this.eyes[i]);
				any = true;
			}
		}
		if (any) {
			this.glow = new LookGlow<>(this, types);
			this.addLayer(this.glow);
			this.glowAttached = true;
		} else {
			this.glow = null;
		}
	}

	private static boolean[] filled(int n, boolean v) {
		boolean[] b = new boolean[n];
		Arrays.fill(b, v);
		return b;
	}

	private int lookOf(int variant) {
		return Mth.clamp(variant, 0, this.textures.length - 1);
	}

	@Override
	public HauntRenderState createRenderState() {
		return new State();
	}

	@Override
	public void extractRenderState(T entity, HauntRenderState s, float pt) {
		super.extractRenderState(entity, s, pt);
		if (s instanceof State f) {
			f.look = lookOf(entity.variant());
			f.wet = entity.isInWater();
			f.stun = entity.stunTicks();
			if (entity instanceof FamilyEntity fam) {
				f.talking = fam.isTalking();
				f.floating = fam.isFloating();
				f.expr = fam.expression();
			} else {
				f.talking = false;
				f.floating = false;
				f.expr = 0;
			}
		}
	}

	@Override
	public Identifier getTextureLocation(HauntRenderState s) {
		return this.textures[lookOf(s.variant)];
	}

	@Override
	public void submit(HauntRenderState s, PoseStack ps, SubmitNodeCollector collector, CameraRenderState cam) {
		if (this.glow != null) {
			int look = lookOf(s.variant);
			this.glow.current = look;
			// a look without an emissive texture: take the layer out for this entity (single-threaded submit)
			boolean want = this.eyes[look] != null;
			if (want != this.glowAttached) {
				if (want) {
					this.layers.add(this.glow);
				} else {
					this.layers.remove(this.glow);
				}
				this.glowAttached = want;
			}
		}
		super.submit(s, ps, collector, cam);
	}

	/** Full-bright overlay whose texture follows the look of the entity being submitted. */
	private static final class LookGlow<M extends EntityModel<HauntRenderState>> extends EyesLayer<HauntRenderState, M> {
		private final RenderType[] types;
		private final RenderType fallback;
		int current;

		LookGlow(RenderLayerParent<HauntRenderState, M> parent, RenderType[] types) {
			super(parent);
			this.types = types;
			RenderType first = null;
			for (RenderType t : types) {
				if (t != null) {
					first = t;
					break;
				}
			}
			this.fallback = first;
		}

		@Override
		public RenderType renderType() {
			RenderType t = this.current >= 0 && this.current < this.types.length ? this.types[this.current] : null;
			return t != null ? t : this.fallback;
		}
	}

	// ------------------------------------------------------------------ helpers for the family animators
	public static boolean talking(HauntRenderState s) {
		return s instanceof State f && f.talking;
	}

	public static boolean floating(HauntRenderState s) {
		return s instanceof State f && f.floating;
	}

	public static boolean wet(HauntRenderState s) {
		return s instanceof State f && f.wet;
	}

	public static int stun(HauntRenderState s) {
		return s instanceof State f ? f.stun : 0;
	}

	/** C: the head follows round much further than a neck should (FamilyEntity.EXPR_STARE). */
	public static boolean staring(HauntRenderState s) {
		return s instanceof State f && (f.expr & FamilyEntity.EXPR_STARE) != 0;
	}

	/** C: the Nona's grin, the dentures shown (FamilyEntity.EXPR_SMILE). */
	public static boolean smiling(HauntRenderState s) {
		return s instanceof State f && (f.expr & FamilyEntity.EXPR_SMILE) != 0;
	}

	/** 0..1 mouth opening of a talking face: syllables (~3 a second) beating against slower phrases. */
	public static float syllable(float t, int seed) {
		float k = Math.floorMod(seed, 17);
		float v = Mth.sin(t * 1.1F + k) * 0.65F + Mth.sin(t * 0.43F + k * 0.7F) * 0.45F;
		return Mth.clamp(v * 1.1F + 0.15F, 0F, 1F);
	}

	/** Deterministic -1..1 per (seed, n). */
	public static float noise(int seed, int n) {
		int h = seed * 0x9E3779B1 + n * 0x85EBCA6B;
		h ^= h >>> 15;
		h *= 0x2C1B3C6D;
		h ^= h >>> 12;
		return (h & 0xFFFF) / 32767.5F - 1F;
	}

	/**
	 * A gesture that comes back now and then: once per `period` ticks (starting at a seeded random point of the first
	 * 40 % of it, so the gaps vary) it ramps up over `in` ticks, holds `hold`, ramps down over `out`. Returns 0..1.
	 */
	public static float pulse(float t, int seed, float period, float in, float hold, float out) {
		float u = t + Math.floorMod(seed * 31, 97);
		int n = Mth.floor(u / period);
		float w = u - n * period - (noise(seed, n) * 0.5F + 0.5F) * period * 0.4F;
		if (w < 0F) {
			return 0F;
		}
		if (w < in) {
			return in <= 0F ? 1F : w / in;
		}
		w -= in;
		if (w < hold) {
			return 1F;
		}
		w -= hold;
		if (w < out) {
			return out <= 0F ? 0F : 1F - w / out;
		}
		return 0F;
	}

	/** -1 or +1 for the current cycle of {@link #pulse} with the same seed and period (which way a glance goes). */
	public static float side(float t, int seed, float period) {
		float u = t + Math.floorMod(seed * 31, 97);
		return noise(seed + 101, Mth.floor(u / period)) >= 0F ? 1F : -1F;
	}
}
