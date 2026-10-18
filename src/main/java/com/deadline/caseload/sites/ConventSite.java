package com.deadline.caseload.sites;

import com.deadline.registry.ModEntities;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Convento de Santa Ines: a gothic church with a bell tower, a nave of black pews and red windows, an
 * altar with an inverted cross, a crypt underneath and a graveyard outside.
 */
public class ConventSite extends SiteBuilder {
	private static final Block[] WALL = {Blocks.DEEPSLATE_BRICKS, Blocks.DEEPSLATE_BRICKS, Blocks.CRACKED_DEEPSLATE_BRICKS, Blocks.STONE_BRICKS, Blocks.MOSSY_STONE_BRICKS, Blocks.POLISHED_DEEPSLATE};
	private static final int X0 = -7, X1 = 7, Z0 = -10, Z1 = 22, H = 12;

	@Override
	protected Layout generate() {
		clearAbove(42, 34);
		ground(42, new Block[]{Blocks.GRASS_BLOCK, Blocks.GRAVEL, Blocks.COARSE_DIRT, Blocks.GRASS_BLOCK, Blocks.PODZOL},
				new Block[]{Blocks.SHORT_GRASS, Blocks.DEAD_BUSH, Blocks.WITHER_ROSE, Blocks.SHORT_GRASS}, 0.12F);
		nave();
		roof();
		tower();
		crypt();
		graveyard();
		ShapeFixer.refresh(this, -42, -8, -42, 42, 30, 42);

		extra(ModEntities.ANIMA, 22.5, 1.5, 4.5);
		extra(ModEntities.ANIMA, 26.5, 1.5, 14.5);
		extra(ModEntities.ANIMA, 0.5, -4, 18.5);
		return layout(v(0.5, 0, -32.5), 0.0F, v(0.5, 0, 8.5), v(0.5, -4.4, 18.5));
	}

	private void nave() {
		fill(X0, -1, Z0, X1, -1, Z1, Blocks.POLISHED_DEEPSLATE);
		for (int z = Z0; z <= Z1; z++) {
			for (int x = X0 + 1; x <= X1 - 1; x++) {
				set(x, -1, z, ((x + z) & 1) == 0 ? Blocks.POLISHED_BLACKSTONE : Blocks.CHISELED_POLISHED_BLACKSTONE);
			}
			set(0, -1, z, Blocks.POLISHED_DEEPSLATE);
		}
		walls(X0, 0, Z0, X1, H, Z1, WALL);
		clear(X0 + 1, 0, Z0 + 1, X1 - 1, H, Z1 - 1);
		// buttress pillars + tall pointed windows of red glass
		for (int z = Z0 + 3; z <= Z1 - 3; z += 5) {
			for (int x : new int[]{X0, X1}) {
				int out = x < 0 ? -1 : 1;
				for (int y = 0; y <= 7; y++) {
					set(x + out, y, z - 1, Blocks.DEEPSLATE_BRICK_WALL);
				}
				for (int y = 2; y <= 8; y++) {
					set(x, y, z, Blocks.RED_STAINED_GLASS_PANE);
				}
				set(x, 9, z, Blocks.BLACK_STAINED_GLASS_PANE);
			}
		}
		// portal + rose window
		clear(-1, 0, Z0, 1, 3, Z0);
		door(-1, 0, Z0, Blocks.DARK_OAK_DOOR, Direction.NORTH, true);
		door(1, 0, Z0, Blocks.DARK_OAK_DOOR, Direction.NORTH, false);
		set(0, 2, Z0, Blocks.DARK_OAK_PLANKS);
		set(0, 3, Z0, Blocks.DARK_OAK_PLANKS);
		for (int a = 0; a < 360; a += 15) {
			int x = (int) Math.round(Math.cos(Math.toRadians(a)) * 2.5);
			int y = 8 + (int) Math.round(Math.sin(Math.toRadians(a)) * 2.5);
			set(x, y, Z0, Blocks.RED_STAINED_GLASS_PANE);
		}
		set(0, 8, Z0, Blocks.BLACK_STAINED_GLASS_PANE);
		// columns
		for (int z = Z0 + 3; z <= Z1 - 6; z += 5) {
			for (int x : new int[]{-4, 4}) {
				for (int y = 0; y <= H - 1; y++) {
					set(x, y, z, y == 0 || y == H - 1 ? Blocks.CHISELED_DEEPSLATE : Blocks.DEEPSLATE_BRICK_WALL);
				}
			}
		}
		// pews facing the altar, red carpet aisle
		for (int z = Z0 + 3; z <= 12; z += 2) {
			for (int x = X0 + 1; x <= X1 - 1; x++) {
				if (Math.abs(x) <= 1 || Math.abs(x) == 4) {
					continue;
				}
				set(x, 0, z, stairs(Blocks.DARK_OAK_STAIRS, Direction.SOUTH, false));
			}
		}
		for (int z = Z0 + 1; z <= 15; z++) {
			set(0, 0, z, Blocks.RED_CARPET);
		}
		// altar
		fill(X0 + 1, 0, 16, X1 - 1, 0, Z1 - 1, Blocks.POLISHED_DEEPSLATE);
		fill(-2, 1, 18, 2, 1, 19, Blocks.CHISELED_DEEPSLATE);
		set(-2, 1, 17, stairs(Blocks.POLISHED_DEEPSLATE_STAIRS, Direction.SOUTH, false));
		// inverted cross on the back wall
		for (int y = 2; y <= 10; y++) {
			set(0, y, Z1 - 1, Blocks.DARK_OAK_PLANKS);
		}
		set(-1, 4, Z1 - 1, Blocks.DARK_OAK_PLANKS);
		set(1, 4, Z1 - 1, Blocks.DARK_OAK_PLANKS);
		set(-2, 4, Z1 - 1, Blocks.DARK_OAK_PLANKS);
		set(2, 4, Z1 - 1, Blocks.DARK_OAK_PLANKS);
		for (int x = -2; x <= 2; x += 2) {
			candles(x, 2, 18, 4, true);
		}
		candles(-5, 1, 17, 3, true);
		candles(5, 1, 17, 3, true);
		// chandeliers (unlit)
		for (int z = Z0 + 5; z <= 10; z += 8) {
			for (int y = H - 3; y <= H - 1; y++) {
				set(0, y, z, Blocks.IRON_CHAIN);
			}
			lantern(0, H - 4, z, Blocks.SOUL_LANTERN, true);
		}
		// confessional
		fill(X1 - 3, 0, Z0 + 2, X1 - 1, 2, Z0 + 3, Blocks.DARK_OAK_PLANKS);
		clear(X1 - 2, 0, Z0 + 2, X1 - 2, 1, Z0 + 2);
		decay(X0 + 1, 0, Z0 + 1, X1 - 1, H - 1, Z1 - 1, 0.18F, 0.012F);
	}

	private void roof() {
		for (int i = 0; i <= 8; i++) {
			int y = H + 1 + i;
			for (int z = Z0 - 1; z <= Z1 + 1; z++) {
				set(X0 - 1 + i, y, z, stairs(Blocks.DEEPSLATE_TILE_STAIRS, Direction.EAST, false));
				set(X1 + 1 - i, y, z, stairs(Blocks.DEEPSLATE_TILE_STAIRS, Direction.WEST, false));
			}
			for (int x = X0 + i; x <= X1 - i; x++) {
				set(x, y, Z0, WALL[rand.nextInt(WALL.length)]);
				set(x, y, Z1, WALL[rand.nextInt(WALL.length)]);
			}
		}
		for (int y = H + 10; y <= H + 13; y++) {
			set(0, y, Z0, Blocks.DEEPSLATE_BRICK_WALL);
		}
		set(-1, H + 12, Z0, Blocks.DEEPSLATE_BRICK_WALL);
		set(1, H + 12, Z0, Blocks.DEEPSLATE_BRICK_WALL);
	}

	private void tower() {
		int x0 = -13, x1 = -9, z0 = -12, z1 = -8, top = 22;
		walls(x0, 0, z0, x1, top, z1, WALL);
		clear(x0 + 1, 0, z0 + 1, x1 - 1, top, z1 - 1);
		for (int y = 6; y <= top - 3; y += 4) {
			set(x0, y, (z0 + z1) / 2, Blocks.IRON_BARS);
			set(x1, y, (z0 + z1) / 2, Blocks.IRON_BARS);
		}
		for (int x = x0; x <= x1; x++) {
			for (int z = z0; z <= z1; z++) {
				if (x == x0 || x == x1 || z == z0 || z == z1) {
					if ((x + z) % 2 == 0) {
						set(x, top + 1, z, Blocks.DEEPSLATE_BRICK_WALL);
					}
				}
			}
		}
		set((x0 + x1) / 2, top - 2, (z0 + z1) / 2, Blocks.BELL);
		clear((x0 + x1) / 2, top - 4, z1, (x0 + x1) / 2, top - 3, z1);
		door(x1, 0, (z0 + z1) / 2, Blocks.DARK_OAK_DOOR, Direction.EAST, false);
	}

	private void crypt() {
		fill(-6, -8, 12, 6, -1, 21, Blocks.DEEPSLATE_BRICKS);
		clear(-5, -6, 13, 5, -2, 20);
		fill(-5, -7, 13, 5, -7, 20, Blocks.POLISHED_DEEPSLATE);
		// stairs down behind the altar (east side)
		for (int i = 0; i < 6; i++) {
			set(5, -1 - i, 21 - i, stairs(Blocks.DEEPSLATE_BRICK_STAIRS, Direction.SOUTH, false));
			clear(5, -i, 21 - i, 5, -i + 1, 21 - i);
		}
		// coffins along the walls
		for (int z = 14; z <= 19; z += 3) {
			fill(-5, -6, z, -4, -6, z + 1, Blocks.DARK_OAK_PLANKS);
			set(-5, -5, z, slab(Blocks.DARK_OAK_SLAB, false));
			set(-4, -5, z + 1, slab(Blocks.DARK_OAK_SLAB, false));
			set(3, -6, z, Blocks.SKELETON_SKULL.defaultBlockState().setValue(BlockStateProperties.ROTATION_16, rand.nextInt(16)));
		}
		// reliquary in the centre for the anchor
		set(0, -6, 18, Blocks.CHISELED_DEEPSLATE);
		for (int a = 0; a < 360; a += 90) {
			candles((int) Math.round(Math.cos(Math.toRadians(a)) * 2), -6, 18 + (int) Math.round(Math.sin(Math.toRadians(a)) * 2), 2, true);
		}
		for (int y = -4; y <= -2; y++) {
			set(-3, y, 14, Blocks.IRON_CHAIN);
			set(2, y, 20, Blocks.IRON_CHAIN);
		}
		decay(-5, -6, 13, 5, -2, 20, 0.5F, 0.04F);
	}

	private void graveyard() {
		for (int x = 14; x <= 36; x += 4) {
			for (int z = -6; z <= 24; z += 5) {
				int gx = x + rand.nextInt(2), gz = z + rand.nextInt(2);
				if (rand.nextFloat() < 0.15F) {
					continue;
				}
				switch (rand.nextInt(3)) {
					case 0 -> cross(gx, 0, gz, Blocks.STONE_BRICK_WALL, false);
					case 1 -> {
						set(gx, 0, gz, Blocks.MOSSY_STONE_BRICK_WALL);
						set(gx, 1, gz, slab(Blocks.STONE_BRICK_SLAB, false));
					}
					default -> {
						set(gx, 0, gz, Blocks.CHISELED_STONE_BRICKS);
						set(gx, 1, gz, Blocks.STONE_BRICK_WALL);
					}
				}
				set(gx, -1, gz - 1, Blocks.COARSE_DIRT);
				set(gx, -1, gz - 2, Blocks.COARSE_DIRT);
				if (rand.nextFloat() < 0.3F) {
					candles(gx + 1, 0, gz, 1, rand.nextBoolean());
				}
			}
		}
		for (int x = 12; x <= 38; x++) {
			for (int z : new int[]{-9, 27}) {
				if (rand.nextFloat() < 0.85F) {
					set(x, 0, z, Blocks.IRON_BARS);
					set(x, 1, z, Blocks.IRON_BARS);
				}
			}
		}
		for (int z = -9; z <= 27; z++) {
			if (rand.nextFloat() < 0.85F) {
				set(38, 0, z, Blocks.IRON_BARS);
				set(38, 1, z, Blocks.IRON_BARS);
			}
		}
		deadTree(30, 2, Blocks.DARK_OAK_LOG, 9);
		deadTree(19, 20, Blocks.DARK_OAK_LOG, 7);
		deadTree(-24, -20, Blocks.DARK_OAK_LOG, 8);
		// gate path
		for (int z = -40; z <= Z0 - 1; z++) {
			for (int x = -1; x <= 1; x++) {
				set(x, -1, z, rand.nextFloat() < 0.75F ? Blocks.GRAVEL : Blocks.COBBLESTONE);
				clear(x, 0, z, x, 0, z);
			}
		}
	}
}
