package com.deadline.car;

import com.deadline.DeadLine;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;

/**
 * The car (entity "deadline:auto"), its keys ("deadline:car_keys") and their network payloads. One call to
 * {@link #init()} from the mod initializer. Client side: com.deadline.client.car.CarClient.
 */
public final class Cars {
	public static final EntityType<CarEntity> CAR = register("auto", EntityType.Builder.<CarEntity>of(CarEntity::new, MobCategory.MISC)
			.sized(2.4F, 2.0F).eyeHeight(1.2F).fireImmune().clientTrackingRange(10));
	public static final Item CAR_KEYS = item("car_keys");

	private static final List<CarEntity> LOADED = new ArrayList<>();
	private static boolean done;

	private Cars() {
	}

	private static <T extends net.minecraft.world.entity.Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	private static Item item(String name) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, DeadLine.id(name));
		Item item = new CarKeysItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).setId(key));
		return Registry.register(BuiltInRegistries.ITEM, key, item);
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		FabricDefaultAttributeRegistry.register(CAR, CarEntity.createAttributes());
		PayloadTypeRegistry.playS2C().register(GpsPayload.TYPE, GpsPayload.CODEC);
		PayloadTypeRegistry.playC2S().register(CarInputPayload.TYPE, CarInputPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(CarInputPayload.TYPE, (payload, ctx) -> {
			if (ctx.player().getVehicle() instanceof CarEntity car) {
				car.input(ctx.player(), payload.action(), payload.value());
			}
		});
		ItemGroupEvents.modifyEntriesEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, DeadLine.id("deadline")))
				.register(entries -> entries.accept(CAR_KEYS));
		// a car replaced by the keys (it was far/unloaded) goes away the moment it loads again (next tick, not inside the event)
		ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
			if (entity instanceof CarEntity car) {
				LOADED.add(car);
			}
		});
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (LOADED.isEmpty()) {
				return;
			}
			for (CarEntity car : new ArrayList<>(LOADED)) {
				if (!car.isRemoved() && CarKeysItem.stale(car)) {
					car.ejectPassengers();
					car.discard();
				}
			}
			LOADED.clear();
		});
	}
}
