package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.registry.ModItems;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.ItemStack;

/**
 * Casa Morales set pieces (P4): the demon wisp entity type and the server hooks the set pieces listen to (salt throws,
 * camera flashes and dagger cuts through item use; the yarn and the remembered-block guard every tick; blocks put back
 * before the world is saved on shutdown). The client must give {@link #DEMON_WISP} a renderer (it draws nothing).
 */
public final class CasaSetEntities {
	public static final EntityType<DemonWisp> DEMON_WISP = register("demon_wisp",
			EntityType.Builder.<DemonWisp>of(DemonWisp::new, MobCategory.MISC).sized(0.3F, 0.3F).fireImmune().clientTrackingRange(10).updateInterval(1));

	private static boolean hooked;

	private CasaSetEntities() {
	}

	private static <T extends Entity> EntityType<T> register(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	public static void init() {
		if (hooked) {
			return;
		}
		hooked = true;
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			CasaProps.tickGuard(server);
			YarnWeb.tickAll(server);
		});
		UseItemCallback.EVENT.register((player, world, hand) -> {
			if (player instanceof ServerPlayer sp) {
				ItemStack stack = sp.getItemInHand(hand);
				if (stack.is(ModItems.SALT)) {
					if (!sp.isShiftKeyDown()) {  // sneak + use pours a protective circle instead
						SaltHits.onThrow(sp, hand);
					}
				} else if (stack.is(ModItems.CAMERA)) {
					if (!sp.getCooldowns().isOnCooldown(stack)) {
						DollShelf.onFlash(sp);
					}
				} else if (stack.is(ModItems.SILVER_DAGGER)) {
					YarnWeb.onDagger(sp);
				}
			}
			return InteractionResult.PASS;
		});
		ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
			CasaProps.restoreAll();
			YarnWeb.clearAll();
			DollShelf.clearAll();
			SaltHits.clearAll();
		});
	}
}
