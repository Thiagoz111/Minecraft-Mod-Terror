package com.deadline.casa;

import com.deadline.registry.ModItems;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;

/**
 * Server hooks of the Casa Morales set pieces: the remembered-block guard every tick, the camera flash the doll
 * shelves react to, and the blocks put back before the world is saved on shutdown. (The demon wisp, the salt hits
 * and the yarn webs of the old comedy design were cut: docs/design/casa_terror.md 9.)
 */
public final class CasaSetEntities {
	private static boolean hooked;

	private CasaSetEntities() {
	}

	public static void init() {
		if (hooked) {
			return;
		}
		hooked = true;
		ServerTickEvents.END_SERVER_TICK.register(CasaProps::tickGuard);
		UseItemCallback.EVENT.register((player, world, hand) -> {
			if (player instanceof ServerPlayer sp) {
				ItemStack stack = sp.getItemInHand(hand);
				if (stack.is(ModItems.CAMERA) && !sp.getCooldowns().isOnCooldown(stack)) {
					DollShelf.onFlash(sp);
				}
			}
			return InteractionResult.PASS;
		});
		ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
			CasaProps.restoreAll();
			DollShelf.clearAll();
		});
	}
}
