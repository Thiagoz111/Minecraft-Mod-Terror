package com.deadline.item;

import com.deadline.registry.ModBlocks;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Bag of consecrated salt. Click the floor to pour a line; sneak + use to draw a protective circle
 * around yourself. Entities cannot cross salt.
 */
public class SaltItem extends Item {
	public SaltItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult useOn(UseOnContext ctx) {
		Player player = ctx.getPlayer();
		if (player != null && player.isShiftKeyDown()) {
			return InteractionResult.PASS;
		}
		if (ctx.getClickedFace() != Direction.UP) {
			return InteractionResult.PASS;
		}
		BlockPos pos = ctx.getClickedPos().above();
		Level level = ctx.getLevel();
		if (place(level, pos)) {
			if (level instanceof ServerLevel server) {
				pour(server, pos);
				if (player != null) {
					ctx.getItemInHand().hurtAndBreak(1, player, ctx.getHand());
				}
			}
			return InteractionResult.SUCCESS;
		}
		return InteractionResult.FAIL;
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		if (!player.isShiftKeyDown()) {
			return InteractionResult.PASS;
		}
		ItemStack stack = player.getItemInHand(hand);
		if (!(level instanceof ServerLevel server)) {
			return InteractionResult.SUCCESS;
		}
		BlockPos c = player.blockPosition();
		int placed = 0;
		for (int a = 0; a < 360; a += 15) {
			int x = (int) Math.round(Math.cos(Math.toRadians(a)) * 2.5);
			int z = (int) Math.round(Math.sin(Math.toRadians(a)) * 2.5);
			BlockPos p = c.offset(x, 0, z);
			for (int dy = 1; dy >= -2; dy--) {
				BlockPos q = p.above(dy);
				if (place(level, q)) {
					pour(server, q);
					placed++;
					break;
				}
			}
		}
		if (placed > 0) {
			stack.hurtAndBreak(Math.max(1, placed / 2), player, hand);
			player.getCooldowns().addCooldown(stack, 40);
		}
		return InteractionResult.SUCCESS;
	}

	private static boolean place(Level level, BlockPos pos) {
		BlockState here = level.getBlockState(pos);
		BlockState salt = ModBlocks.SALT_LINE.defaultBlockState();
		if (!here.canBeReplaced() || here.is(ModBlocks.SALT_LINE) || !salt.canSurvive(level, pos)) {
			return false;
		}
		if (!level.isClientSide()) {
			level.setBlock(pos, salt, 3);
		}
		return true;
	}

	private static void pour(ServerLevel level, BlockPos pos) {
		level.sendParticles(ModParticles.SALT_SPARKLE, pos.getX() + 0.5, pos.getY() + 0.1, pos.getZ() + 0.5, 6, 0.25, 0.05, 0.25, 0.01);
		level.playSound(null, pos, ModSounds.SALT_PLACE, SoundSource.BLOCKS, 0.6F, 0.9F + level.getRandom().nextFloat() * 0.3F);
	}
}
