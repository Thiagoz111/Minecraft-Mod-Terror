package com.deadline.item;

import com.deadline.caseload.CaseManager;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModSounds;
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

/** The DEAD LINE phone. Right-click to open it; its screen glows while there are unread text messages. */
public class PhoneItem extends Item {
	public PhoneItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		if (player instanceof ServerPlayer sp) {
			CaseManager.syncPhone(sp, true);
			level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.PHONE_NOTIFY, SoundSource.PLAYERS, 0.4F, 1.0F);
		}
		return InteractionResult.SUCCESS;
	}

	@Override
	public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, EquipmentSlot slot) {
		if (entity instanceof ServerPlayer p && p.tickCount % 10 == 0) {
			ItemUtil.setFlags(stack, com.deadline.phone.PhoneMessages.unread(ModAttachments.get(p)) > 0);
		}
	}
}
