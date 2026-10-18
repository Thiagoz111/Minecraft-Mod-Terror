package com.deadline.item;

import com.deadline.entity.AnimaEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.component.DataComponents;
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

/** Spirit jar. Right-click a weakened entity (or a revealed soul) to trap it. */
public class SpiritJarItem extends Item {
	private final boolean full;

	public SpiritJarItem(Properties props, boolean full) {
		super(props);
		this.full = full;
	}

	@Override
	public boolean isFoil(ItemStack stack) {
		return full;
	}

	@Override
	public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
		if (full || !(target instanceof HauntEntity haunt)) {
			return InteractionResult.PASS;
		}
		boolean capturable = (haunt.isWeakened() && !haunt.requiresExorcism()) || (haunt instanceof AnimaEntity a && a.isRevealed());
		if (!capturable) {
			if (player instanceof ServerPlayer sp) {
				sp.displayClientMessage(Component.translatable(haunt.requiresExorcism() ? "deadline.msg.needs_exorcism" : "deadline.msg.too_strong"), true);
			}
			return InteractionResult.FAIL;
		}
		if (player.level() instanceof ServerLevel level && player instanceof ServerPlayer sp) {
			for (int i = 0; i < 20; i++) {
				double t = i / 20.0;
				level.sendParticles(ModParticles.WISP,
						haunt.getX() + (player.getX() - haunt.getX()) * t,
						haunt.getY() + 1 + (player.getEyeY() - 0.5 - haunt.getY() - 1) * t,
						haunt.getZ() + (player.getZ() - haunt.getZ()) * t, 2, 0.1, 0.1, 0.1, 0.01);
			}
			level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.JAR_CAPTURE, SoundSource.PLAYERS, 1.5F, 1.0F);
			ItemStack jar = new ItemStack(ModItems.SPIRIT_JAR_FULL);
			jar.set(DataComponents.CUSTOM_NAME, Component.translatable("item.deadline.spirit_jar_full.named", haunt.getType().getDescription()));
			stack.consume(1, player);
			if (!player.getInventory().add(jar)) {
				player.drop(jar, false);
			}
			if (haunt instanceof AnimaEntity) {
				haunt.discard();
			} else {
				haunt.banish(level, sp);
			}
		}
		return InteractionResult.SUCCESS;
	}
}
