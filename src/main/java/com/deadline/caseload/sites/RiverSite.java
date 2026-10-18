package com.deadline.caseload.sites;

import com.deadline.registry.ModEntities;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Rio de los Lamentos: a black river crossing a swampy bank, a collapsed adobe house, a broken bridge,
 * memorial crosses and a pier where a child's shoe still floats.
 */
public class RiverSite extends SiteBuilder {
	private static final Block[] ADOBE = {Blocks.PACKED_MUD, Blocks.MUD_BRICKS, Blocks.MUD_BRICKS, Blocks.TERRACOTTA, Blocks.BROWN_TERRACOTTA};

	@Override
	protected Layout generate() {
		clearAbove(44, 18);
		ground(44, new Block[]{Blocks.GRASS_BLOCK, Blocks.MUD, Blocks.COARSE_DIRT, Blocks.GRASS_BLOCK, Blocks.PODZOL, Blocks.MOSS_BLOCK},
				new Block[]{Blocks.SHORT_GRASS, Blocks.SHORT_GRASS, Blocks.FERN, Blocks.DEAD_BUSH}, 0.25F);
		river();
		bridge();
		pier();
		house();
		memorials();
		for (int i = 0; i < 14; i++) {
			int x = -40 + rand.nextInt(80);
			int z = (rand.nextBoolean() ? 1 : -1) * (10 + rand.nextInt(28));
			if (Math.abs(x - 10) < 9 && z > 8 && z < 22) {
				continue;
			}
			if (Math.abs(x) < 4 && z < -8 && z > -24) {
				continue;
			}
			if (rand.nextFloat() < 0.6F) {
				willow(x, z, 5 + rand.nextInt(3));
			} else {
				deadTree(x, z, Blocks.MANGROVE_LOG, 5 + rand.nextInt(4));
			}
		}
		ShapeFixer.refresh(this, -44, -5, -44, 44, 12, 44);

		extra(ModEntities.ANIMA, 6.5, 1.5, -2.5);
		extra(ModEntities.ANIMA, -18.5, 1.5, 6.5);
		return layout(v(0.5, 0, -30.5), 0.0F, v(10.5, 0, 16.5), v(-6.5, 0.6, 0.5));
	}

	private void river() {
		for (int x = -44; x <= 44; x++) {
			int wobble = (int) Math.round(Math.sin(x * 0.12) * 2.0);
			for (int z = -6; z <= 6; z++) {
				int zz = z + wobble;
				int depth = Math.abs(z) <= 3 ? 3 : (Math.abs(z) <= 5 ? 2 : 1);
				for (int d = 1; d <= depth; d++) {
					set(x, -d, zz, Blocks.WATER);
				}
				set(x, -depth - 1, zz, rand.nextBoolean() ? Blocks.MUD : Blocks.CLAY);
				clear(x, 0, zz, x, 1, zz);
				if (Math.abs(z) == 6 && rand.nextFloat() < 0.5F) {
					set(x, 0, zz, Blocks.SUGAR_CANE);
					if (rand.nextBoolean()) {
						set(x, 1, zz, Blocks.SUGAR_CANE);
					}
					set(x, -1, zz, Blocks.MUD);
				} else if (Math.abs(z) <= 4 && rand.nextFloat() < 0.06F) {
					set(x, 0, zz, Blocks.LILY_PAD);
				}
			}
			// muddy banks
			for (int z : new int[]{-8, -7, 7, 8}) {
				if (rand.nextFloat() < 0.7F) {
					set(x, -1, z + wobble, rand.nextBoolean() ? Blocks.MUD : Blocks.MUDDY_MANGROVE_ROOTS);
				}
			}
		}
	}

	private void bridge() {
		int bx = 18;
		for (int z = -10; z <= 10; z++) {
			boolean broken = z >= -1 && z <= 2;
			for (int x = bx - 1; x <= bx + 1; x++) {
				if (!broken || (x == bx - 1 && z == -1)) {
					set(x, 0, z, slab(Blocks.DARK_OAK_SLAB, false));
				}
			}
			if (!broken && (z & 1) == 0) {
				set(bx - 2, 1, z, Blocks.DARK_OAK_FENCE);
				set(bx + 2, 1, z, Blocks.DARK_OAK_FENCE);
			}
			if (Math.abs(z) == 6) {
				for (int y = -3; y <= -1; y++) {
					set(bx - 1, y, z, Blocks.DARK_OAK_LOG);
					set(bx + 1, y, z, Blocks.DARK_OAK_LOG);
				}
			}
		}
	}

	private void pier() {
		// from the south bank out over the water; the shoe floats at its end
		for (int z = -12; z <= 0; z++) {
			for (int x = -7; x <= -5; x++) {
				if (z > -3 && x == -5 && rand.nextBoolean()) {
					continue;
				}
				set(x, 0, z, slab(Blocks.SPRUCE_SLAB, false));
			}
			if (z % 3 == 0) {
				for (int y = -3; y <= 0; y++) {
					set(-8, y, z, Blocks.STRIPPED_SPRUCE_LOG);
					set(-4, y, z, Blocks.STRIPPED_SPRUCE_LOG);
				}
				set(-8, 1, z, Blocks.SPRUCE_FENCE);
			}
		}
		lantern(-8, 2, -6, Blocks.SOUL_LANTERN, false);
		candles(-4, 1, 0, 2, true);
		set(-4, 1, -3, Blocks.WITHER_ROSE);
	}

	private void house() {
		int x0 = 4, x1 = 16, z0 = 12, z1 = 22;
		fill(x0, -1, z0, x1, -1, z1, Blocks.PACKED_MUD);
		walls(x0, 0, z0, x1, 4, z1, ADOBE);
		clear(x0 + 1, 0, z0 + 1, x1 - 1, 5, z1 - 1);
		// collapsed corner
		for (int x = x1 - 4; x <= x1; x++) {
			for (int y = 1 + (x1 - x) / 2; y <= 4; y++) {
				set(x, y, z0, Blocks.AIR);
			}
		}
		for (int k = 0; k < 10; k++) {
			set(x1 - rand.nextInt(5), 0, z0 - 1 - rand.nextInt(3), ADOBE[rand.nextInt(ADOBE.length)]);
		}
		// door and windows
		clear(10, 0, z0, 10, 1, z0);
		for (int x : new int[]{6, 14}) {
			set(x, 1, z1, Blocks.IRON_BARS);
			set(x, 2, z1, Blocks.IRON_BARS);
		}
		set(x0, 2, 17, Blocks.AIR);
		// partial roof of rotten beams
		for (int x = x0; x <= x1 - 5; x++) {
			for (int z = z0; z <= z1; z++) {
				if (rand.nextFloat() < 0.75F) {
					set(x, 5, z, (z & 1) == 0 ? log(Blocks.STRIPPED_DARK_OAK_LOG, Direction.Axis.X) : slab(Blocks.DARK_OAK_SLAB, false));
				}
			}
		}
		// crib, rocking chair, shrine
		set(6, 0, 20, Blocks.SPRUCE_FENCE);
		set(7, 0, 20, Blocks.WHITE_CARPET);
		set(8, 0, 20, Blocks.SPRUCE_FENCE);
		set(6, 0, 21, Blocks.SPRUCE_FENCE);
		set(8, 0, 21, Blocks.SPRUCE_FENCE);
		set(7, 0, 21, Blocks.WHITE_CARPET);
		set(13, 0, 18, stairs(Blocks.DARK_OAK_STAIRS, Direction.EAST, false));
		set(15, 0, 21, Blocks.DARK_OAK_PLANKS);
		set(15, 1, 21, Blocks.DARK_OAK_PLANKS);
		set(15, 2, 21, Blocks.DARK_OAK_PLANKS);
		set(15, 2, 20, Blocks.DARK_OAK_FENCE);
		candles(14, 0, 21, 4, true);
		candles(15, 3, 21, 2, true);
		set(13, 0, 21, Blocks.WITHER_ROSE);
		decay(x0 + 1, 0, z0 + 1, x1 - 1, 4, z1 - 1, 0.3F, 0.03F);
		for (int i = 0; i < 6; i++) {
			set(5 + rand.nextInt(10), 0, 13 + rand.nextInt(8), Blocks.MOSS_CARPET);
		}
	}

	private void memorials() {
		int[][] spots = {{-14, -12}, {-11, -14}, {-17, -16}, {12, -14}, {-20, 13}, {-24, 16}};
		for (int[] s : spots) {
			cross(s[0], 0, s[1], Blocks.STRIPPED_SPRUCE_WOOD, false);
			candles(s[0], 0, s[1] - 1, 1 + rand.nextInt(3), rand.nextBoolean());
			if (rand.nextBoolean()) {
				set(s[0] + 1, 0, s[1] - 1, Blocks.WITHER_ROSE);
			}
		}
		set(-14, 0, -11, Blocks.WHITE_CARPET);
	}
}
