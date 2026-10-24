package com.deadline.horror.casa.hunt;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.registry.ModItems;
import com.deadline.voice.NoiseMeter;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

/**
 * B2 (the hunt): entity types, payloads and server hooks of {@link Hunt}, {@link HideSpots} and {@link Breath}.
 * Call {@link #init()} once from the mod initializer, BEFORE {@code Director.register()} so the hiding places get the
 * first look at a right click (the director would otherwise take clicks on marked props).
 */
public final class HuntEntities {
	/** The broken Nona: 0.7 x 1.45 so she fits through doors while crawling; she stands taller only as a model. */
	public static final EntityType<NonaRotaEntity> NONA_ROTA = register("nona_rota",
			EntityType.Builder.<NonaRotaEntity>of(NonaRotaEntity::new, MobCategory.MONSTER).sized(0.7F, 1.45F).fireImmune().clientTrackingRange(16));
	/** The invisible seat inside a hiding place. */
	public static final EntityType<HideSeatEntity> HIDE_SEAT = register("hide_seat",
			EntityType.Builder.<HideSeatEntity>of(HideSeatEntity::new, MobCategory.MISC).sized(0.25F, 0.25F).fireImmune().clientTrackingRange(8)
					.updateInterval(20));

	private static boolean done;

	private HuntEntities() {
	}

	private static <T extends Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		FabricDefaultAttributeRegistry.register(NONA_ROTA, NonaRotaEntity.createAttributes());

		PayloadTypeRegistry.playC2S().register(BreathPayload.TYPE, BreathPayload.CODEC);
		PayloadTypeRegistry.playS2C().register(HuntHudPayload.TYPE, HuntHudPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(BreathPayload.TYPE, (payload, ctx) -> Breath.onKey(ctx.player(), payload.hold()));

		UseBlockCallback.EVENT.register(HideSpots::onUse);
		// the flashlight's click is a noise she hears (design 6.1)
		UseItemCallback.EVENT.register((player, world, hand) -> {
			if (player instanceof ServerPlayer sp && sp.getItemInHand(hand).is(ModItems.FLASHLIGHT) && Director.of(sp) != null) {
				NoiseMeter.add(sp, 14F);
				Hunt.noise(Director.of(sp), sp.position(), 20F);
			}
			return InteractionResult.PASS;
		});
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			Breath.tick(server);
			HideSpots.tick(server);
			Hunt.tickAll(server);
			HuntHud.tick(server);
		});
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> {
			HideSpots.forget(handler.getPlayer());
			Breath.forget(handler.getPlayer());
			HuntHud.forget(handler.getPlayer());
		});
	}
}
