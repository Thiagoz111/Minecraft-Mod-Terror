package com.deadline.item;

import com.deadline.entity.FlareEntity;
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

public class FlareItem extends Item {
	public FlareItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.FLARE_IGNITE, SoundSource.PLAYERS, 1.0F, 1.0F);
		if (level instanceof ServerLevel server) {
			Projectile.spawnProjectileFromRotation(FlareEntity::new, server, stack, player, -5.0F, 1.0F, 1.0F);
		}
		player.getCooldowns().addCooldown(stack, 20);
		stack.consume(1, player);
		return InteractionResult.SUCCESS;
	}
}
