package com.deadline.item;

import com.deadline.caseload.CaseManager;
import com.deadline.entity.AnchorEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** EMF reader: five LEDs that light up as paranormal activity gets closer. Level 5 counts as evidence. */
public class EmfItem extends Item {
	public EmfItem(Properties props) {
		super(props);
	}

	public static int readLevel(ServerLevel level, Entity holder) {
		double best = Double.MAX_VALUE;
		for (Entity e : level.getEntities(holder, holder.getBoundingBox().inflate(22), e -> e instanceof HauntEntity || e instanceof AnchorEntity)) {
			best = Math.min(best, e.distanceTo(holder));
		}
		if (best < 3.5) return 5;
		if (best < 7) return 4;
		if (best < 11) return 3;
		if (best < 16) return 2;
		if (best < 22) return 1;
		return 0;
	}

	@Override
	public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, EquipmentSlot slot) {
		if (!(entity instanceof ServerPlayer p)) {
			return;
		}
		boolean held = p.getMainHandItem() == stack || p.getOffhandItem() == stack;
		if (!held) {
			if (p.tickCount % 20 == 0) {
				ItemUtil.setFloat(stack, 0);
			}
			return;
		}
		if (p.tickCount % 4 != 0) {
			return;
		}
		int lvl = readLevel(level, p);
		if (lvl > 0 && lvl < 5 && level.getRandom().nextInt(6) == 0) {
			lvl += level.getRandom().nextBoolean() ? 1 : -1; // natural flicker
		}
		ItemUtil.setFloat(stack, lvl);
		int period = switch (lvl) {
			case 5 -> 4;
			case 4 -> 8;
			case 3 -> 16;
			case 2 -> 28;
			case 1 -> 48;
			default -> 0;
		};
		if (period > 0 && p.tickCount % period == 0) {
			level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.EMF_BEEP, SoundSource.PLAYERS, 0.5F, 0.8F + lvl * 0.15F);
		}
		if (lvl == 5 && p.tickCount % 200 == 0) {
			CaseManager.evidence(p, 1);
		}
	}
}
