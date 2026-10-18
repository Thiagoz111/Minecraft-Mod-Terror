package com.deadline.item;

import com.deadline.caseload.CaseManager;
import com.deadline.entity.AnimaEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Spirit camera. The flash stuns entities in frame and reveals the invisible ones. */
public class CameraItem extends Item {
	public CameraItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (player.getCooldowns().isOnCooldown(stack)) {
			return InteractionResult.FAIL;
		}
		player.getCooldowns().addCooldown(stack, 60);
		level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.CAMERA_FLASH, SoundSource.PLAYERS, 1.0F, 1.0F);
		if (level instanceof ServerLevel server && player instanceof ServerPlayer sp) {
			for (ServerPlayer other : server.players()) {
				if (other.distanceToSqr(player) < 16 * 16) {
					Fx.flash(other, other == sp ? 0.55F : 0.9F);
				}
			}
			Vec3 eye = player.getEyePosition();
			Vec3 look = player.getLookAngle();
			boolean captured = false;
			for (HauntEntity e : server.getEntitiesOfClass(HauntEntity.class, player.getBoundingBox().inflate(18))) {
				Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
				if (to.length() > 18 || to.normalize().dot(look) < 0.85) {
					continue;
				}
				if (e instanceof AnimaEntity anima) {
					anima.reveal(240);
				}
				if (player.hasLineOfSight(e)) {
					e.stun(50);
					captured = true;
				}
			}
			if (captured) {
				CaseManager.evidence(sp, 3);
			}
			stack.hurtAndBreak(1, player, hand);
		}
		return InteractionResult.SUCCESS;
	}
}
