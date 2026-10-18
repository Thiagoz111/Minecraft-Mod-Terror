package com.deadline.client.particle;

import com.deadline.registry.ModParticles;
import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/** One configurable particle class for every DEAD LINE effect. */
public class DeadParticle extends SingleQuadParticle {
	/** Per-type behaviour. */
	public record Style(int minLife, int maxLife, float minSize, float maxSize, float gravity, float friction,
			boolean glow, boolean animate, float growth, float fadeIn, float r, float g, float b, float wobble) {
	}

	private final SpriteSet sprites;
	private final Style style;
	private final float baseSize;
	private final float baseAlpha;
	private final float phase;

	protected DeadParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, SpriteSet sprites, Style style, RandomSource rnd) {
		super(level, x, y, z, 0, 0, 0, sprites.first());
		this.sprites = sprites;
		this.style = style;
		this.xd = dx;
		this.yd = dy;
		this.zd = dz;
		this.gravity = style.gravity;
		this.friction = style.friction;
		this.hasPhysics = style.gravity > 0.05F;
		this.lifetime = style.minLife + rnd.nextInt(Math.max(1, style.maxLife - style.minLife + 1));
		this.baseSize = Mth.lerp(rnd.nextFloat(), style.minSize, style.maxSize);
		this.quadSize = baseSize;
		float tint = 0.85F + rnd.nextFloat() * 0.15F;
		this.setColor(style.r * tint, style.g * tint, style.b * tint);
		this.baseAlpha = 1.0F;
		this.phase = rnd.nextFloat() * 6.28F;
		this.roll = this.oRoll = rnd.nextFloat() * 0.6F - 0.3F;
		if (style.animate) {
			this.setSpriteFromAge(sprites);
		} else {
			this.setSprite(sprites.get(rnd));
		}
	}

	@Override
	public void tick() {
		super.tick();
		if (removed) {
			return;
		}
		float k = age / (float) lifetime;
		if (style.animate) {
			setSpriteFromAge(sprites);
		}
		if (style.wobble > 0F) {
			xd += Math.sin(age * 0.21F + phase) * style.wobble;
			zd += Math.cos(age * 0.17F + phase) * style.wobble;
		}
		quadSize = baseSize * (1F + style.growth * k);
		float in = style.fadeIn > 0F ? Mth.clamp(k / style.fadeIn, 0F, 1F) : 1F;
		float out = Mth.clamp((1F - k) / 0.35F, 0F, 1F);
		alpha = baseAlpha * in * out;
	}

	@Override
	protected Layer getLayer() {
		return Layer.TRANSLUCENT;
	}

	@Override
	public int getLightColor(float pt) {
		return style.glow ? LightTexture.FULL_BRIGHT : super.getLightColor(pt);
	}

	private static void reg(net.minecraft.core.particles.ParticleType<SimpleParticleType> type, Style style) {
		ParticleFactoryRegistry.getInstance().register(type, sprites -> (ParticleProvider<SimpleParticleType>)
				(opt, level, x, y, z, dx, dy, dz, rnd) -> new DeadParticle(level, x, y, z, dx, dy, dz, sprites, style, rnd));
	}

	public static void registerAll() {
		reg(ModParticles.ECTOPLASM, new Style(24, 44, 0.10F, 0.18F, -0.004F, 0.94F, true, true, 0.3F, 0.15F, 0.55F, 1.0F, 0.6F, 0.002F));
		reg(ModParticles.HOLY_SPARK, new Style(10, 22, 0.05F, 0.10F, 0.15F, 0.9F, true, true, -0.5F, 0F, 1.0F, 0.92F, 0.6F, 0F));
		reg(ModParticles.DEMON_SMOKE, new Style(30, 56, 0.18F, 0.32F, -0.012F, 0.93F, false, true, 1.2F, 0.2F, 0.32F, 0.12F, 0.14F, 0.003F));
		reg(ModParticles.WISP, new Style(40, 70, 0.08F, 0.14F, -0.002F, 0.96F, true, true, 0F, 0.2F, 0.7F, 0.95F, 1.0F, 0.006F));
		reg(ModParticles.SALT_SPARKLE, new Style(8, 16, 0.04F, 0.07F, 0.02F, 0.9F, true, true, 0F, 0F, 1.0F, 1.0F, 1.0F, 0F));
		reg(ModParticles.BLOOD_DRIP, new Style(30, 44, 0.06F, 0.09F, 0.6F, 0.98F, false, true, 0F, 0F, 0.75F, 0.05F, 0.06F, 0F));
		reg(ModParticles.HANDPRINT, new Style(90, 120, 0.22F, 0.26F, 0F, 0F, true, false, 0F, 0.2F, 0.75F, 0.45F, 1.0F, 0F));
		reg(ModParticles.COLD_BREATH, new Style(26, 40, 0.10F, 0.16F, -0.003F, 0.92F, false, true, 1.0F, 0.1F, 0.88F, 0.94F, 1.0F, 0.002F));
	}
}
