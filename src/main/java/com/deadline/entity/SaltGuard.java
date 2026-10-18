package com.deadline.entity;

import com.deadline.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;

/** Consecrated salt lines are impassable for paranormal entities -- even for their teleports. */
public final class SaltGuard {
	private SaltGuard() {
	}

	public static boolean blocked(Level level, BlockPos pos) {
		return near(level, pos, 2);
	}

	public static boolean near(Level level, BlockPos pos, int r) {
		for (BlockPos p : BlockPos.betweenClosed(pos.offset(-r, -1, -r), pos.offset(r, 1, r))) {
			if (level.getBlockState(p).is(ModBlocks.SALT_LINE)) {
				return true;
			}
		}
		return false;
	}
}
