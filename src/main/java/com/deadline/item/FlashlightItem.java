package com.deadline.item;

import com.deadline.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * A real flashlight: the beam lights the blocks it points at. Sneak + use switches to UV, which
 * reveals hidden souls and handprints. It flickers when something is close.
 */
public class FlashlightItem extends Item {
	public FlashlightItem(Properties props) {
		super(props);
	}

	public static boolean isOn(ItemStack stack) {
		return ItemUtil.getFlag(stack, 0);
	}

	public static boolean isUv(ItemStack stack) {
		return ItemUtil.getFlag(stack, 1);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		boolean on = isOn(stack);
		boolean uv = isUv(stack);
		if (player.isShiftKeyDown() && on) {
			uv = !uv;
			if (player instanceof ServerPlayer sp) {
				sp.displayClientMessage(Component.translatable(uv ? "deadline.msg.uv_on" : "deadline.msg.uv_off"), true);
			}
		} else {
			on = !on;
		}
		if (on && stack.getDamageValue() >= stack.getMaxDamage() - 1) {
			on = false;
			if (player instanceof ServerPlayer sp) {
				sp.displayClientMessage(Component.translatable("deadline.msg.no_battery"), true);
			}
		}
		ItemUtil.setFlags(stack, on, uv);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.FLASHLIGHT_CLICK, SoundSource.PLAYERS, 0.7F, on ? 1.2F : 0.9F);
		return InteractionResult.SUCCESS;
	}

	@Override
	public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, EquipmentSlot slot) {
		if (!(entity instanceof ServerPlayer p) || !isOn(stack)) {
			return;
		}
		boolean held = p.getMainHandItem() == stack || p.getOffhandItem() == stack;
		if (held && p.tickCount % 20 == 0 && !p.isCreative()) {
			if (stack.getDamageValue() >= stack.getMaxDamage() - 1) {
				ItemUtil.setFlags(stack, false, isUv(stack));
				p.displayClientMessage(Component.translatable("deadline.msg.no_battery"), true);
			} else {
				stack.setDamageValue(stack.getDamageValue() + 1);
			}
		}
	}
}
