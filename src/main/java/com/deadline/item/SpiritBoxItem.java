package com.deadline.item;

import com.deadline.caseload.CaseManager;
import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
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

/** Sweeps radio frequencies. Hold it near an entity and something answers. */
public class SpiritBoxItem extends Item {
	public static final int PHRASES = 12;

	public SpiritBoxItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (player.getCooldowns().isOnCooldown(stack)) {
			return InteractionResult.FAIL;
		}
		player.startUsingItem(hand);
		return InteractionResult.CONSUME;
	}

	@Override
	public ItemUseAnimation getUseAnimation(ItemStack stack) {
		return ItemUseAnimation.TOOT_HORN;
	}

	@Override
	public int getUseDuration(ItemStack stack, LivingEntity user) {
		return 120;
	}

	@Override
	public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
		if (!(level instanceof ServerLevel server) || !(user instanceof ServerPlayer p)) {
			return;
		}
		int used = getUseDuration(stack, user) - remaining;
		if (used % 25 == 0) {
			server.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.SPIRIT_BOX_STATIC, SoundSource.PLAYERS, 0.8F, 0.9F + server.getRandom().nextFloat() * 0.2F);
		}
		if (used == 50) {
			HauntEntity near = null;
			for (HauntEntity e : server.getEntitiesOfClass(HauntEntity.class, p.getBoundingBox().inflate(18))) {
				near = e;
				break;
			}
			if (near != null) {
				int phrase = server.getRandom().nextInt(PHRASES);
				server.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.SPIRIT_BOX_VOICE, SoundSource.PLAYERS, 1.2F, 1.0F);
				Fx.title(p, "deadline.spiritbox." + phrase, 70);
				Fx.staticNoise(p, 0.5F, 25);
				SanityManager.add(p, -4.0F);
				CaseManager.evidence(p, 2);
			}
		}
	}

	@Override
	public boolean releaseUsing(ItemStack stack, Level level, LivingEntity user, int remaining) {
		if (user instanceof Player p) {
			p.getCooldowns().addCooldown(stack, 40);
		}
		return true;
	}

	@Override
	public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
		if (user instanceof Player p) {
			p.getCooldowns().addCooldown(stack, 60);
		}
		return stack;
	}
}
