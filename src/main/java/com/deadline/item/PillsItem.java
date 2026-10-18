package com.deadline.item;

import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.level.Level;

/** Sanity pills: +35 cordura. */
public class PillsItem extends Item {
	public PillsItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		player.startUsingItem(hand);
		return InteractionResult.CONSUME;
	}

	@Override
	public ItemUseAnimation getUseAnimation(ItemStack stack) {
		return ItemUseAnimation.EAT;
	}

	@Override
	public int getUseDuration(ItemStack stack, LivingEntity user) {
		return 24;
	}

	@Override
	public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
		if (user instanceof ServerPlayer p) {
			SanityManager.add(p, 35.0F);
			level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.PILLS_SWALLOW, SoundSource.PLAYERS, 1.0F, 1.0F);
			p.getCooldowns().addCooldown(stack, 100);
		}
		stack.consume(1, user);
		return stack;
	}
}
