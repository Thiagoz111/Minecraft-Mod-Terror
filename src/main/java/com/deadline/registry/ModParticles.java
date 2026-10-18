package com.deadline.registry;

import com.deadline.DeadLine;
import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;

public final class ModParticles {
	public static final SimpleParticleType ECTOPLASM = register("ectoplasm", false);
	public static final SimpleParticleType HOLY_SPARK = register("holy_spark", true);
	public static final SimpleParticleType DEMON_SMOKE = register("demon_smoke", false);
	public static final SimpleParticleType WISP = register("wisp", true);
	public static final SimpleParticleType SALT_SPARKLE = register("salt_sparkle", false);
	public static final SimpleParticleType BLOOD_DRIP = register("blood_drip", false);
	public static final SimpleParticleType HANDPRINT = register("handprint", true);
	public static final SimpleParticleType COLD_BREATH = register("cold_breath", false);

	private ModParticles() {
	}

	private static SimpleParticleType register(String name, boolean alwaysShow) {
		return Registry.register(BuiltInRegistries.PARTICLE_TYPE, DeadLine.id(name), FabricParticleTypes.simple(alwaysShow));
	}

	public static void init() {
	}
}
