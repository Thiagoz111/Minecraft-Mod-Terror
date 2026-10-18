package com.deadline.item;

import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
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
import net.minecraft.world.phys.Vec3;

/** Hold it up: a cone of holy light that pushes back, stuns and burns entities. */
public class CrucifixItem extends Item {
	private static final int MAX_HOLD = 100;

	public CrucifixItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (player.getCooldowns().isOnCooldown(stack)) {
			return InteractionResult.FAIL;
		}
		player.startUsingItem(hand);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.CRUCIFIX_ACTIVATE, SoundSource.PLAYERS, 1.0F, 1.0F);
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
		int used = getUseDuration(stack, user) - remaining;
		if (!(level instanceof ServerLevel server) || !(user instanceof ServerPlayer player)) {
			return;
		}
		if (used >= MAX_HOLD) {
			player.stopUsingItem();
			player.getCooldowns().addCooldown(stack, 60);
			return;
		}
		if (used % 4 != 0) {
			return;
		}
		Vec3 eye = player.getEyePosition();
		Vec3 look = player.getLookAngle();
		for (int i = 1; i <= 6; i++) {
			Vec3 p = eye.add(look.scale(i * 1.4));
			server.sendParticles(ModParticles.HOLY_SPARK, p.x, p.y - 0.2, p.z, 2, 0.15 * i, 0.15 * i, 0.15 * i, 0.01);
		}
		boolean hit = false;
		for (HauntEntity e : server.getEntitiesOfClass(HauntEntity.class, player.getBoundingBox().inflate(10))) {
			Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
			double d = to.length();
			if (d > 10 || to.normalize().dot(look) < 0.77 || !player.hasLineOfSight(e)) {
				continue;
			}
			hit = true;
			Vec3 push = to.normalize().scale(0.9 / Math.max(1.0, d * 0.3));
			e.push(push.x, 0.15, push.z);
			e.stun(30);
			if (used % 20 == 0) {
				e.hurtServer(server, server.damageSources().magic(), 1.5F * e.holyWeakness());
				server.playSound(null, e.getX(), e.getY(), e.getZ(), ModSounds.CRUCIFIX_REPEL, SoundSource.PLAYERS, 1.2F, 0.9F + server.getRandom().nextFloat() * 0.2F);
				server.sendParticles(ModParticles.DEMON_SMOKE, e.getX(), e.getY() + 1, e.getZ(), 8, 0.3, 0.5, 0.3, 0.03);
			}
		}
		if (used % 20 == 0) {
			stack.hurtAndBreak(hit ? 3 : 1, player, player.getUsedItemHand());
			SanityManager.add(player, 0.5F);
		}
	}

	@Override
	public boolean releaseUsing(ItemStack stack, Level level, LivingEntity user, int remaining) {
		if (user instanceof Player p) {
			p.getCooldowns().addCooldown(stack, 30);
		}
		return true;
	}
}
