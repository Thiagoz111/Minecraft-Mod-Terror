package com.deadline.item;

import com.deadline.entity.PoseidaEntity;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
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

/** Rituale Romanum. Hold use near a bound, weakened possessed soul to perform the exorcism. */
public class RitualBookItem extends Item {
	public RitualBookItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		player.startUsingItem(hand);
		if (level instanceof ServerLevel server) {
			server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.RITUAL_CHANT, SoundSource.PLAYERS, 1.2F, 1.0F);
		}
		return InteractionResult.CONSUME;
	}

	@Override
	public ItemUseAnimation getUseAnimation(ItemStack stack) {
		return ItemUseAnimation.BLOCK;
	}

	@Override
	public int getUseDuration(ItemStack stack, LivingEntity user) {
		return 72000;
	}

	@Override
	public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
		if (!(level instanceof ServerLevel server) || !(user instanceof ServerPlayer p)) {
			return;
		}
		int used = getUseDuration(stack, user) - remaining;
		if (used > 0 && used % 100 == 0) {
			server.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.RITUAL_CHANT, SoundSource.PLAYERS, 1.2F, 1.0F);
		}
		PoseidaEntity target = null;
		for (PoseidaEntity e : server.getEntitiesOfClass(PoseidaEntity.class, p.getBoundingBox().inflate(10))) {
			if (e.isWeakened()) {
				target = e;
				break;
			}
		}
		if (target == null) {
			if (used == 20) {
				p.displayClientMessage(Component.translatable("deadline.msg.nothing_to_exorcise"), true);
			}
			return;
		}
		target.chant(p);
		if (used % 3 == 0) {
			server.sendParticles(ModParticles.HOLY_SPARK, p.getX(), p.getEyeY() - 0.3, p.getZ(), 2, 0.3, 0.2, 0.3, 0.02);
			server.sendParticles(ModParticles.DEMON_SMOKE, target.getX(), target.getY() + 1, target.getZ(), 3, 0.3, 0.6, 0.3, 0.04);
		}
	}
}
