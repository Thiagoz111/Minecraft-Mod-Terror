package com.deadline.registry;

import com.deadline.DeadLine;
import com.deadline.entity.AnchorEntity;
import com.deadline.entity.AnimaEntity;
import com.deadline.entity.BalloonEntity;
import com.deadline.entity.FlareEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.HolyWaterEntity;
import com.deadline.entity.LloronaEntity;
import com.deadline.entity.MonjaEntity;
import com.deadline.entity.MunecaEntity;
import com.deadline.entity.PayasoEntity;
import com.deadline.entity.PoseidaEntity;
import com.deadline.entity.SombraEntity;
import com.deadline.entity.WendigoEntity;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

public final class ModEntities {
	public static final EntityType<LloronaEntity> LLORONA = register("llorona",
			EntityType.Builder.of(LloronaEntity::new, MobCategory.MONSTER).sized(0.7F, 2.4F).fireImmune().clientTrackingRange(12));
	public static final EntityType<WendigoEntity> WENDIGO = register("wendigo",
			EntityType.Builder.of(WendigoEntity::new, MobCategory.MONSTER).sized(0.9F, 3.2F).clientTrackingRange(12));
	public static final EntityType<PoseidaEntity> POSEIDA = register("poseida",
			EntityType.Builder.of(PoseidaEntity::new, MobCategory.MONSTER).sized(0.6F, 1.5F).fireImmune().clientTrackingRange(12));
	public static final EntityType<PayasoEntity> PAYASO = register("payaso",
			EntityType.Builder.of(PayasoEntity::new, MobCategory.MONSTER).sized(0.7F, 2.6F).fireImmune().clientTrackingRange(12));
	public static final EntityType<MonjaEntity> MONJA = register("monja",
			EntityType.Builder.of(MonjaEntity::new, MobCategory.MONSTER).sized(0.7F, 2.4F).fireImmune().clientTrackingRange(12));
	public static final EntityType<SombraEntity> SOMBRA = register("sombra",
			EntityType.Builder.of(SombraEntity::new, MobCategory.MONSTER).sized(0.7F, 2.9F).fireImmune().clientTrackingRange(16));
	public static final EntityType<MunecaEntity> MUNECA = register("muneca",
			EntityType.Builder.of(MunecaEntity::new, MobCategory.MONSTER).sized(0.4F, 0.75F).fireImmune().clientTrackingRange(10));
	public static final EntityType<AnimaEntity> ANIMA = register("anima",
			EntityType.Builder.of(AnimaEntity::new, MobCategory.MONSTER).sized(0.6F, 1.6F).fireImmune().clientTrackingRange(10));
	public static final EntityType<AnchorEntity> ANCHOR = register("anchor",
			EntityType.Builder.<AnchorEntity>of(AnchorEntity::new, MobCategory.MISC).sized(0.7F, 0.9F).fireImmune().clientTrackingRange(10));
	public static final EntityType<BalloonEntity> BALLOON = register("balloon",
			EntityType.Builder.<BalloonEntity>of(BalloonEntity::new, MobCategory.MISC).sized(0.5F, 0.9F).fireImmune().clientTrackingRange(10));
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
		FabricDefaultAttributeRegistry.register(LLORONA, LloronaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(WENDIGO, WendigoEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(POSEIDA, PoseidaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(PAYASO, PayasoEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(MONJA, MonjaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(SOMBRA, SombraEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(MUNECA, MunecaEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(ANIMA, AnimaEntity.createAttributes());
	}

	public static boolean isHaunt(Entity e) {
		return e instanceof HauntEntity;
	}
}
