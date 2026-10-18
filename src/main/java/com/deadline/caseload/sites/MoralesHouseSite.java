package com.deadline.caseload.sites;

import com.deadline.registry.ModEntities;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Casa Morales: a two-storey suburban house with a basement. Lucia's bedroom upstairs, a ritual circle
 * in the basement, porcelain dolls everywhere.
 */
public class MoralesHouseSite extends SiteBuilder {
	private static final Block[] SIDING = {Blocks.PALE_OAK_PLANKS, Blocks.PALE_OAK_PLANKS, Blocks.PALE_OAK_PLANKS, Blocks.BIRCH_PLANKS, Blocks.STRIPPED_PALE_OAK_WOOD};
	private static final Block[] STONE = {Blocks.COBBLESTONE, Blocks.MOSSY_COBBLESTONE, Blocks.STONE_BRICKS, Blocks.CRACKED_STONE_BRICKS, Blocks.MOSSY_STONE_BRICKS};

	@Override
	protected Layout generate() {
		clearAbove(26, 20);
		ground(26, new Block[]{Blocks.GRASS_BLOCK, Blocks.GRASS_BLOCK, Blocks.COARSE_DIRT, Blocks.PODZOL, Blocks.DIRT},
				new Block[]{Blocks.SHORT_GRASS, Blocks.DEAD_BUSH, Blocks.SHORT_GRASS, Blocks.FERN}, 0.18F);
		yard();
		basement();
		groundFloor();
		upperFloor();
		roof();
		porch();
		finish();

		extra(ModEntities.MUNECA, -5.5, 5, 0.5);
		extra(ModEntities.MUNECA, -2.5, 5, -3.5);
		extra(ModEntities.MUNECA, -5.5, 0, 2.5);
		extra(ModEntities.ANIMA, 6.5, 1.5, 12.5);
		return layout(v(0.5, 0, -20.5), 0.0F, v(-4.5, 5, -1.5), v(-2.5, -3.9, 0.5));
	}

	private void yard() {
		// broken picket fence around the lot
		for (int x = -17; x <= 17; x++) {
			for (int z : new int[]{-15, 17}) {
				if (rand.nextFloat() < 0.8F && Math.abs(x) > 1) {
					set(x, 0, z, Blocks.SPRUCE_FENCE);
				}
			}
		}
		for (int z = -15; z <= 17; z++) {
			for (int x : new int[]{-17, 17}) {
				if (rand.nextFloat() < 0.8F) {
					set(x, 0, z, Blocks.SPRUCE_FENCE);
				}
			}
		}
		for (int z = -15; z <= -10; z++) {
			set(0, -1, z, rand.nextFloat() < 0.8F ? Blocks.GRAVEL : Blocks.COARSE_DIRT);
		}
		// mailbox
		set(3, 0, -15, Blocks.DARK_OAK_FENCE);
		set(3, 1, -15, dir(Blocks.BARREL, Direction.NORTH));
		deadTree(-12, -9, Blocks.DARK_OAK_LOG, 7);
		deadTree(12, 10, Blocks.DARK_OAK_LOG, 8);
		deadTree(-11, 11, Blocks.DARK_OAK_LOG, 6);
		// rusty swing in the backyard
		for (int y = 0; y <= 3; y++) {
			set(7, y, 12, Blocks.DARK_OAK_FENCE);
			set(11, y, 12, Blocks.DARK_OAK_FENCE);
		}
		for (int x = 7; x <= 11; x++) {
			set(x, 4, 12, log(Blocks.STRIPPED_DARK_OAK_LOG, Direction.Axis.X));
		}
		for (int y = 2; y <= 3; y++) {
			set(8, y, 12, Blocks.IRON_CHAIN);
			set(10, y, 12, Blocks.IRON_CHAIN);
		}
		set(8, 1, 12, slab(Blocks.DARK_OAK_SLAB, true));
		set(10, 1, 12, Blocks.IRON_CHAIN);
		blood(-6, 0, -12);
		blood(5, 0, 9);
	}

	private void basement() {
		fillMix(-8, -7, -6, 8, -1, 6, STONE);
		clear(-7, -5, -5, 7, -2, 5);
		fillMix(-7, -6, -5, 7, -6, 5, Blocks.STONE_BRICKS, Blocks.CRACKED_STONE_BRICKS, Blocks.COBBLESTONE, Blocks.MOSSY_COBBLESTONE);
		// pentagram of red dust with candles at the points
		int cx = -3, cz = 0, r = 3;
		for (int a = 0; a < 360; a += 8) {
			int x = cx + (int) Math.round(Math.cos(Math.toRadians(a)) * r);
			int z = cz + (int) Math.round(Math.sin(Math.toRadians(a)) * r);
			set(x, -5, z, Blocks.REDSTONE_WIRE);
		}
		for (int i = 0; i < 5; i++) {
			double a = Math.toRadians(-90 + i * 72);
			int x = cx + (int) Math.round(Math.cos(a) * (r + 1));
			int z = cz + (int) Math.round(Math.sin(a) * (r + 1));
			candles(x, -5, z, 3, true);
		}
		set(cx, -5, cz, Blocks.DARK_OAK_FENCE);
		set(cx, -4, cz, Blocks.DARK_OAK_PRESSURE_PLATE);
		// shelves, furnace, chains
		for (int z = -4; z <= 3; z += 2) {
			set(7, -5, z, dir(Blocks.BARREL, Direction.UP));
			set(7, -4, z, Blocks.CHISELED_BOOKSHELF);
		}
		set(6, -5, -5, facing(Blocks.BLAST_FURNACE, Direction.WEST));
		set(5, -5, -5, Blocks.BREWING_STAND);
		for (int y = -3; y <= -2; y++) {
			set(-6, y, 4, Blocks.IRON_CHAIN);
			set(1, y, -4, Blocks.IRON_CHAIN);
		}
		bed(-6, -5, -4, Blocks.RED_BED, Direction.EAST);
		decay(-7, -5, -5, 7, -2, 5, 0.35F, 0.05F);
		// stairs down from the kitchen
		clear(1, -5, 5, 5, -1, 5);
		for (int i = 0; i < 5; i++) {
			set(5 - i, -1 - i, 5, stairs(Blocks.DARK_OAK_STAIRS, Direction.EAST, false));
		}
	}

	private void groundFloor() {
		// footprint floor + outer walls
		fill(-8, -1, -6, 8, -1, 6, Blocks.DARK_OAK_PLANKS);
		walls(-8, 0, -6, 8, 8, 6, SIDING);
		for (int y = 0; y <= 8; y++) {
			for (int[] c : new int[][]{{-8, -6}, {8, -6}, {-8, 6}, {8, 6}}) {
				set(c[0], y, c[1], Blocks.STRIPPED_DARK_OAK_LOG);
			}
		}
		clear(-7, 0, -5, 7, 3, 5);
		// windows (some broken, some boarded)
		int[] wx = {-6, -3, 3, 6};
		for (int x : wx) {
			for (int z : new int[]{-6, 6}) {
				window(x, 1, z, Direction.Axis.X);
				window(x, 6, z, Direction.Axis.X);
			}
		}
		for (int z : new int[]{-3, 2}) {
			window(-8, 1, z, Direction.Axis.Z);
			window(8, 1, z, Direction.Axis.Z);
			window(-8, 6, z, Direction.Axis.Z);
			window(8, 6, z, Direction.Axis.Z);
		}
		door(0, 0, -6, Blocks.DARK_OAK_DOOR, Direction.NORTH, true);
		door(4, 0, 6, Blocks.DARK_OAK_DOOR, Direction.SOUTH, false);
		// interior wall with doorway
		for (int z = -5; z <= 5; z++) {
			for (int y = 0; y <= 3; y++) {
				set(0, y, z, Blocks.PALE_OAK_PLANKS);
			}
		}
		clear(0, 0, -1, 0, 1, 0);
		clear(0, 0, 3, 0, 1, 3);
		// living room
		for (int z = -3; z <= -1; z++) {
			set(-7, 0, z, stairs(Blocks.SPRUCE_STAIRS, Direction.WEST, false));
		}
		set(-3, 0, -2, Blocks.DARK_OAK_PLANKS);
		set(-3, 1, -2, Blocks.BLACK_CONCRETE);
		fill(-5, 0, -5, -1, 3, -5, Blocks.BRICKS);
		set(-3, 0, -5, Blocks.CAMPFIRE.defaultBlockState().setValue(BlockStateProperties.LIT, false));
		clear(-3, 1, -5, -3, 1, -5);
		set(-7, 0, 2, Blocks.BOOKSHELF);
		set(-7, 1, 2, Blocks.BOOKSHELF);
		set(-5, 0, -4, stairs(Blocks.OAK_STAIRS, Direction.SOUTH, false));
		for (int x = -6; x <= -4; x++) {
			for (int z = -2; z <= 1; z++) {
				set(x, 0, z, Blocks.RED_CARPET);
			}
		}
		// staircase up along the back wall
		for (int i = 0; i < 4; i++) {
			set(-7 + i, i, 5, stairs(Blocks.DARK_OAK_STAIRS, Direction.EAST, false));
			for (int y = i + 1; y <= 3; y++) {
				set(-7 + i, y, 5, Blocks.AIR);
			}
		}
		// kitchen
		for (int z = -4; z <= 1; z++) {
			set(7, 0, z, z == -1 ? Blocks.WATER_CAULDRON.defaultBlockState().setValue(BlockStateProperties.LEVEL_CAULDRON, 3)
					: dir(Blocks.BARREL, Direction.UP));
		}
		set(7, 0, -5, facing(Blocks.SMOKER, Direction.WEST));
		set(7, 0, 2, Blocks.WHITE_CONCRETE);
		set(7, 1, 2, Blocks.WHITE_CONCRETE);
		set(3, 0, -1, Blocks.DARK_OAK_FENCE);
		set(3, 1, -1, Blocks.DARK_OAK_PRESSURE_PLATE);
		set(2, 0, -1, stairs(Blocks.DARK_OAK_STAIRS, Direction.WEST, false));
		set(4, 0, -2, stairs(Blocks.DARK_OAK_STAIRS, Direction.NORTH, false));
		decay(-7, 0, -5, 7, 3, 5, 0.25F, 0.025F);
		// trail of blood toward the stairs
		for (int x = -2; x <= 3; x++) {
			if (rand.nextBoolean()) {
				blood(x, 0, 4);
			}
		}
	}

	private void window(int x, int y, int z, Direction.Axis axis) {
		float r = rand.nextFloat();
		Block b = r < 0.25F ? Blocks.AIR : (r < 0.45F ? Blocks.DARK_OAK_PLANKS : Blocks.GLASS_PANE);
		set(x, y, z, b);
		set(x, y + 1, z, r < 0.45F && r >= 0.25F ? Blocks.AIR : b);
		if (axis == Direction.Axis.X) {
			set(x + 1, y, z, b == Blocks.DARK_OAK_PLANKS ? Blocks.AIR : b);
			set(x + 1, y + 1, z, b);
		} else {
			set(x, y, z + 1, b == Blocks.DARK_OAK_PLANKS ? Blocks.AIR : b);
			set(x, y + 1, z + 1, b);
		}
	}

	private void upperFloor() {
		fill(-7, 4, -5, 7, 4, 5, Blocks.DARK_OAK_PLANKS);
		clear(-7, 4, 5, -4, 4, 5);
		for (int x = -7; x <= -4; x++) {
			set(x, 5, 4, Blocks.DARK_OAK_FENCE);
		}
		clear(-7, 5, -5, 7, 8, 5);
		fill(-7, 9, -5, 7, 9, 5, Blocks.DARK_OAK_PLANKS);
		for (int z = -5; z <= 3; z++) {
			for (int y = 5; y <= 8; y++) {
				set(0, y, z, Blocks.PALE_OAK_PLANKS);
			}
		}
		door(0, 5, -2, Blocks.SPRUCE_DOOR, Direction.EAST, true);
		set(-1, 5, 3, Blocks.PALE_OAK_PLANKS);
		door(-3, 5, 3, Blocks.SPRUCE_DOOR, Direction.SOUTH, true);
		for (int x = -7; x <= -1; x++) {
			if (x != -3) {
				for (int y = 5; y <= 8; y++) {
					set(x, y, 3, Blocks.PALE_OAK_PLANKS);
				}
			}
		}
		// Lucia's bedroom
		for (int x = -7; x <= -1; x++) {
			for (int z = -5; z <= 2; z++) {
				set(x, 5, z, Blocks.PINK_CARPET);
			}
		}
		bed(-6, 5, -3, Blocks.WHITE_BED, Direction.NORTH);
		set(-2, 5, -5, facing(Blocks.CHEST, Direction.SOUTH));
		set(-7, 5, 0, Blocks.DARK_OAK_FENCE);
		set(-7, 6, 0, Blocks.DARK_OAK_PRESSURE_PLATE);
		candles(-7, 6, 1, 1, true);
		for (int i = 0; i < 6; i++) {
			blood(-6 + rand.nextInt(5), 5, -4 + rand.nextInt(6));
		}
		decay(-7, 5, -5, -1, 8, 2, 0.4F, 0.0F);
		// parents' bedroom
		bed(5, 5, -3, Blocks.RED_BED, Direction.NORTH);
		bed(6, 5, -3, Blocks.RED_BED, Direction.NORTH);
		set(1, 5, -5, Blocks.SPRUCE_PLANKS);
		set(1, 6, -5, Blocks.SPRUCE_PLANKS);
		set(2, 5, -5, Blocks.SPRUCE_PLANKS);
		set(2, 6, -5, Blocks.SPRUCE_PLANKS);
		// bathroom
		for (int x = 1; x <= 7; x++) {
			for (int y = 5; y <= 8; y++) {
				set(x, y, 2, x == 3 && y <= 6 ? Blocks.AIR : Blocks.PALE_OAK_PLANKS);
			}
		}
		set(6, 5, 4, Blocks.WATER_CAULDRON.defaultBlockState().setValue(BlockStateProperties.LEVEL_CAULDRON, 3));
		set(7, 5, 4, Blocks.WATER_CAULDRON.defaultBlockState().setValue(BlockStateProperties.LEVEL_CAULDRON, 3));
		set(2, 5, 5, stairs(Blocks.QUARTZ_STAIRS, Direction.NORTH, false));
		set(7, 6, 5, Blocks.GLASS_PANE);
		decay(1, 5, -5, 7, 8, 5, 0.3F, 0.02F);
	}

	private void roof() {
		for (int i = 0; i <= 7; i++) {
			int y = 9 + i;
			for (int x = -9; x <= 9; x++) {
				set(x, y, -7 + i, stairs(Blocks.DEEPSLATE_TILE_STAIRS, Direction.SOUTH, false));
				set(x, y, 7 - i, stairs(Blocks.DEEPSLATE_TILE_STAIRS, Direction.NORTH, false));
				if (i < 7) {
					for (int z = -6 + i; z <= 6 - i; z++) {
						if (x == -8 || x == 8) {
							set(x, y, z, SIDING[rand.nextInt(SIDING.length)]);
						}
					}
				}
			}
		}
		for (int x = -9; x <= 9; x++) {
			set(x, 16, 0, slab(Blocks.DEEPSLATE_TILE_SLAB, false));
		}
		// a few missing shingles
		for (int k = 0; k < 6; k++) {
			int i = rand.nextInt(6);
			set(-8 + rand.nextInt(17), 9 + i, -7 + i, Blocks.AIR);
		}
		set(-8, 12, 0, Blocks.GLASS_PANE);
		set(8, 12, 0, Blocks.AIR);
	}

	private void porch() {
		for (int x = -4; x <= 4; x++) {
			for (int z = -9; z <= -7; z++) {
				set(x, 0, z, slab(Blocks.SPRUCE_SLAB, false));
				set(x, 4, z, slab(Blocks.SPRUCE_SLAB, false));
			}
		}
		for (int y = 0; y <= 3; y++) {
			set(-4, y, -9, Blocks.SPRUCE_FENCE);
			set(4, y, -9, Blocks.SPRUCE_FENCE);
		}
		set(0, 0, -10, stairs(Blocks.SPRUCE_STAIRS, Direction.NORTH, false));
		set(-3, 1, -8, stairs(Blocks.DARK_OAK_STAIRS, Direction.EAST, false));
		candles(2, 1, -7, 1, true);
		set(2, 0, -7, Blocks.BARREL);
	}

	private void finish() {
		ShapeFixer.refresh(this, -18, -7, -16, 18, 17, 18);
	}
}
