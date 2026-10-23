package com.deadline.casa;

import com.deadline.DeadLine;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * Casa Morales P1: the family's entity types (all {@link FamilyEntity}; the client gives each its own model and
 * textures in {@code client/casa/FamilyRenderers}). Hitboxes: Marta 0.6 x 1.75, Jorge 0.7 x 1.9, the Nona 0.6 x 1.5
 * (hunched), Toti 0.6 x 1.8. Call {@link #init()} once from the mod initializer.
 */
public final class FamilyEntities {
	public static final EntityType<FamilyEntity> MARTA = register("marta", 0.6F, 1.75F);
	public static final EntityType<FamilyEntity> JORGE = register("jorge", 0.7F, 1.9F);
	public static final EntityType<FamilyEntity> NONA = register("nona", 0.6F, 1.5F);
	public static final EntityType<FamilyEntity> TOTI = register("toti", 0.6F, 1.8F);

	private static boolean done;

	private FamilyEntities() {
	}

	private static EntityType<FamilyEntity> register(String name, float width, float height) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		EntityType.Builder<FamilyEntity> builder = EntityType.Builder.<FamilyEntity>of(FamilyEntity::new, MobCategory.MISC)
				.sized(width, height).fireImmune().clientTrackingRange(12);
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		FabricDefaultAttributeRegistry.register(MARTA, FamilyEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(JORGE, FamilyEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(NONA, FamilyEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(TOTI, FamilyEntity.createAttributes());
	}

	public static boolean isFamily(Entity e) {
		return e instanceof FamilyEntity;
	}
}
