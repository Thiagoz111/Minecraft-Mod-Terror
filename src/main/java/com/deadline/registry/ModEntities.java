package com.deadline.registry;

import com.deadline.DeadLine;
import com.deadline.entity.AnchorEntity;
import com.deadline.entity.AnimaEntity;
import com.deadline.entity.FlareEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.HolyWaterEntity;
import com.deadline.entity.MonjaEntity;
import com.deadline.entity.MunecaEntity;
import com.deadline.entity.PoseidaEntity;
import com.deadline.entity.SombraEntity;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

public final class ModEntities {
	public static final EntityType<PoseidaEntity> POSEIDA = register("poseida",
			EntityType.Builder.of(PoseidaEntity::new, MobCategory.MONSTER).sized(0.6F, 1.5F).fireImmune().clientTrackingRange(12));
	public static final EntityType<MonjaEntity> MONJA = register("monja",
			EntityType.Builder.of(MonjaEntity::new, MobCategory.MONSTER).sized(0.7F, 1.95F).fireImmune().clientTrackingRange(12));
	public static final EntityType<SombraEntity> SOMBRA = register("sombra",
			EntityType.Builder.of(SombraEntity::new, MobCategory.MONSTER).sized(0.8F, 3.4F).fireImmune().clientTrackingRange(16));
	public static final EntityType<MunecaEntity> MUNECA = register("muneca",
			EntityType.Builder.of(MunecaEntity::new, MobCategory.MONSTER).sized(0.45F, 0.8F).fireImmune().clientTrackingRange(10));
	public static final EntityType<AnimaEntity> ANIMA = register("anima",
			EntityType.Builder.of(AnimaEntity::new, MobCategory.MONSTER).sized(0.7F, 1.9F).fireImmune().clientTrackingRange(10));
	public static final EntityType<AnchorEntity> ANCHOR = register("anchor",
			EntityType.Builder.<AnchorEntity>of(AnchorEntity::new, MobCategory.MISC).sized(0.7F, 0.9F).fireImmune().clientTrackingRange(10));
	public static final EntityType<HolyWaterEntity> HOLY_WATER = register("holy_water",
			EntityType.Builder.<HolyWaterEntity>of(HolyWaterEntity::new, MobCategory.MISC).sized(0.25F, 0.25F).clientTrackingRange(4).updateInterval(10));
	public static final EntityType<FlareEntity> FLARE = register("flare",
			EntityType.Builder.<FlareEntity>of(FlareEntity::new, MobCategory.MISC).sized(0.25F, 0.25F).clientTrackingRange(8).updateInterval(5));

	private ModEntities() {
	}

	private static <T extends Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	public static void init() {
		FabricDefaultAttributeRegistry.register(POSEIDA, PoseidaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(MONJA, MonjaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(SOMBRA, SombraEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(MUNECA, MunecaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(ANIMA, AnimaEntity.createAttributes());
	}

	public static boolean isHaunt(Entity e) {
		return e instanceof HauntEntity;
	}
}
