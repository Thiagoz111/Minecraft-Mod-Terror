package com.deadline.horror.casa;

import com.deadline.DeadLine;
import com.deadline.entity.ApparitionEntity;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * The small props-that-are-alive of the Casa apparitions: both are {@link ApparitionEntity} (no AI, no collision,
 * invulnerable, never pushed; the event moves them and sets their state with setAction):
 * <ul>
 *   <li>{@link #MANO} -- event 39 'bajo_cama': the grey hand (and two blocks of arm) that comes out from under a bed.
 *   The entity is the HAND; it faces where it crawls and the arm trails behind it under the bed.
 *   Actions: {@link #MANO_CREEP} (fingers walking), {@link #MANO_GRIP} (digging into the boards), {@link #MANO_RETRACT}
 *   (yanked back).</li>
 *   <li>{@link #SABANA} -- event 44 'sabana': the bedsheet of the patio line. Actions: {@link #SABANA_HANG} (flat, on
 *   the line), {@link #SABANA_FLY} (full of somebody who is not there), {@link #SABANA_COLLAPSE} (emptied in the air),
 *   {@link #SABANA_FLAT} (lying empty on the ground).</li>
 * </ul>
 */
public final class ApparitionEntities {
	public static final int MANO_CREEP = 0, MANO_GRIP = 1, MANO_RETRACT = 2;
	public static final int SABANA_HANG = 0, SABANA_FLY = 1, SABANA_COLLAPSE = 2, SABANA_FLAT = 3;

	public static final EntityType<ApparitionEntity> MANO = register("mano", 0.5F, 0.25F, 10);
	public static final EntityType<ApparitionEntity> SABANA = register("sabana", 0.9F, 1.9F, 12);

	private static boolean done;

	private ApparitionEntities() {
	}

	private static EntityType<ApparitionEntity> register(String name, float w, float h, int range) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		EntityType.Builder<ApparitionEntity> b = EntityType.Builder.<ApparitionEntity>of(ApparitionEntity::new, MobCategory.MISC)
				.sized(w, h).fireImmune().clientTrackingRange(range);
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, b.build(key));
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		FabricDefaultAttributeRegistry.register(MANO, ApparitionEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(SABANA, ApparitionEntity.createAttributes());
	}
}
