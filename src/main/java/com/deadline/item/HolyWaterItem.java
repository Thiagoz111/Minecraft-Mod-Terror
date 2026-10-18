package com.deadline.item;

import com.deadline.entity.HolyWaterEntity;
import com.deadline.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public class HolyWaterItem extends Item {
	public HolyWaterItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.HOLY_WATER_THROW, SoundSource.PLAYERS, 0.7F, 0.9F + level.getRandom().nextFloat() * 0.2F);
		if (level instanceof ServerLevel server) {
			Projectile.spawnProjectileFromRotation(HolyWaterEntity::new, server, stack, player, -10.0F, 1.1F, 1.0F);
		}
		player.getCooldowns().addCooldown(stack, 15);
		stack.consume(1, player);
		return InteractionResult.SUCCESS;
	}
}
