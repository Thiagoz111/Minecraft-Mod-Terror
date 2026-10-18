package com.deadline.caseload.sites;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CrossCollisionBlock;
import net.minecraft.world.level.block.RedStoneWireBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Sites are placed without neighbour updates (fast, and keeps water still). This pass recomputes the
 * connection shapes of fences, panes, walls, stairs and dust so they render joined.
 */
final class ShapeFixer {
	private ShapeFixer() {
	}

	static void refresh(SiteBuilder b, int x0, int y0, int z0, int x1, int y1, int z1) {
		for (int x = x0; x <= x1; x++) {
			for (int y = y0; y <= y1; y++) {
				for (int z = z0; z <= z1; z++) {
					BlockPos pos = b.at(x, y, z);
					BlockState s = b.level.getBlockState(pos);
					Block blk = s.getBlock();
					if (blk instanceof CrossCollisionBlock || blk instanceof WallBlock || blk instanceof StairBlock || blk instanceof RedStoneWireBlock) {
						BlockState n = Block.updateFromNeighbourShapes(s, b.level, pos);
						if (n != s) {
							b.level.setBlock(pos, n, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE);
						}
					}
				}
			}
		}
	}
}
