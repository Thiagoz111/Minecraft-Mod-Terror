package com.deadline.horror.casa.dog;

import com.deadline.DeadLine;
import com.deadline.casa.FamilyEntity;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * Choripán's two bodies: {@link #CHORIPAN} the dachshund (0.6 x 0.7; standing on his hind legs he is a block tall but
 * the box stays a dog's) and {@link #CHORIPAN_DEMONIO} the long dog (the 0.8 x 0.8 box is its HEAD; the chain is drawn
 * behind it by the client). Call {@link #init()} once from the mod initializer.
 */
public final class DogEntities {
	public static final EntityType<ChoripanEntity> CHORIPAN = register("choripan",
			EntityType.Builder.<ChoripanEntity>of(ChoripanEntity::new, MobCategory.MISC).sized(0.6F, 0.7F).fireImmune().clientTrackingRange(12));
	public static final EntityType<ChoripanDemonioEntity> CHORIPAN_DEMONIO = register("choripan_demonio",
			EntityType.Builder.<ChoripanDemonioEntity>of(ChoripanDemonioEntity::new, MobCategory.MISC).sized(0.8F, 0.8F).fireImmune()
					.clientTrackingRange(16).updateInterval(1));

	private static boolean done;

	private DogEntities() {
	}

	private static <T extends net.minecraft.world.entity.Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		FabricDefaultAttributeRegistry.register(CHORIPAN, FamilyEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(CHORIPAN_DEMONIO, ChoripanDemonioEntity.createAttributes());
	}
}
