package com.deadline.caseload.sites;

import com.deadline.registry.ModEntities;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

/**
 * Parque Mundo Feliz: an abandoned amusement park -- entrance arch, ticket booth, carousel, a giant
 * ferris wheel and the circus tent where the music box keeps playing.
 */
public class ParkSite extends SiteBuilder {
	private static final Block[] PAVING = {Blocks.GRAY_CONCRETE, Blocks.ANDESITE, Blocks.GRAVEL, Blocks.GRAY_CONCRETE, Blocks.COARSE_DIRT, Blocks.CRACKED_STONE_BRICKS, Blocks.GRAY_CONCRETE_POWDER};

	@Override
	protected Layout generate() {
		clearAbove(46, 34);
		ground(46, PAVING, new Block[]{Blocks.SHORT_GRASS, Blocks.DEAD_BUSH, Blocks.SHORT_GRASS}, 0.07F);
		entrance();
		carousel(-18, -6);
		ferrisWheel(16, 6);
		circusTent(0, 22);
		stands();
		lamps();
		ShapeFixer.refresh(this, -46, -1, -46, 46, 30, 46);

		for (int i = 0; i < 6; i++) {
			extra(ModEntities.BALLOON, -20 + rand.nextInt(40) + 0.5, 0.5, -20 + rand.nextInt(40) + 0.5);
		}
		extra(ModEntities.ANIMA, -18.5, 2, -6.5);
		extra(ModEntities.ANIMA, 16.5, 3, 6.5);
		return layout(v(0.5, 0, -40.5), 0.0F, v(0.5, 0, 26.5), v(0.5, 1.6, 22.5));
	}

	private void entrance() {
		int z = -32;
		for (int x : new int[]{-6, 6}) {
			for (int y = 0; y <= 7; y++) {
				set(x, y, z, (y & 1) == 0 ? Blocks.RED_CONCRETE : Blocks.WHITE_CONCRETE);
			}
			set(x, 8, z, Blocks.GOLD_BLOCK);
		}
		for (int x = -6; x <= 6; x++) {
			set(x, 7, z, Blocks.YELLOW_CONCRETE);
			set(x, 8, z, (x & 1) == 0 ? Blocks.RED_TERRACOTTA : Blocks.WHITE_TERRACOTTA);
			if (Math.abs(x) <= 4) {
				set(x, 9, z, (x & 1) == 0 ? Blocks.RED_TERRACOTTA : Blocks.WHITE_TERRACOTTA);
			}
			if (Math.abs(x) <= 2) {
				set(x, 10, z, Blocks.RED_TERRACOTTA);
			}
		}
		// broken bulbs along the arch
		for (int x = -5; x <= 5; x += 2) {
			set(x, 6, z, rand.nextBoolean() ? Blocks.REDSTONE_LAMP : Blocks.GLOWSTONE);
		}
		// fence of the park
		for (int x = -46; x <= 46; x++) {
			if (Math.abs(x) > 6 && rand.nextFloat() < 0.85F) {
				set(x, 0, z, Blocks.IRON_BARS);
				set(x, 1, z, Blocks.IRON_BARS);
			}
		}
		// ticket booth
		fill(8, 0, -30, 11, 3, -27, Blocks.RED_CONCRETE);
		clear(9, 0, -29, 10, 2, -28);
		set(9, 1, -30, Blocks.GLASS_PANE);
		set(10, 1, -30, Blocks.AIR);
		fill(7, 4, -31, 12, 4, -26, Blocks.WHITE_CONCRETE);
	}

	private void carousel(int cx, int cz) {
		int r = 6;
		for (int x = -r; x <= r; x++) {
			for (int z = -r; z <= r; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d <= r + 0.3) {
					set(cx + x, 0, cz + z, slab(Blocks.POLISHED_ANDESITE_SLAB, false));
					if (d > r - 0.9) {
						set(cx + x, 0, cz + z, ((int) Math.round(Math.toDegrees(Math.atan2(z, x))) / 30 & 1) == 0 ? Blocks.RED_CONCRETE : Blocks.WHITE_CONCRETE);
					}
				}
				// conical roof
				double rr = r + 1 - d;
				if (d <= r + 1 && rr >= 0) {
					int y = 6 + (int) Math.round(rr * 0.6);
					boolean stripe = (((int) Math.round(Math.toDegrees(Math.atan2(z, x)) + 180) / 20) & 1) == 0;
					set(cx + x, y, cz + z, stripe ? Blocks.RED_WOOL : Blocks.WHITE_WOOL);
				}
			}
		}
		for (int y = 0; y <= 6; y++) {
			set(cx, y, cz, Blocks.GOLD_BLOCK);
		}
		// horses on poles
		for (int a = 0; a < 360; a += 45) {
			int x = cx + (int) Math.round(Math.cos(Math.toRadians(a)) * 4);
			int z = cz + (int) Math.round(Math.sin(Math.toRadians(a)) * 4);
			for (int y = 1; y <= 5; y++) {
				set(x, y, z, Blocks.IRON_BARS);
			}
			int hy = 1 + (a / 45 % 2);
			set(x, hy, z, a % 90 == 0 ? Blocks.WHITE_WOOL : Blocks.BROWN_WOOL);
			Direction d = Direction.fromYRot(a + 90);
			set(x + d.getStepX(), hy + 1, z + d.getStepZ(), stairs(Blocks.QUARTZ_STAIRS, d, false));
		}
	}

	private void ferrisWheel(int cx, int cz) {
		int r = 12, cy = 14;
		// A-frame supports
		for (int y = 0; y <= cy; y++) {
			int off = (cy - y) / 2;
			set(cx - off, y, cz - 2, Blocks.IRON_BLOCK);
			set(cx + off, y, cz - 2, Blocks.IRON_BLOCK);
			set(cx - off, y, cz + 2, Blocks.IRON_BLOCK);
			set(cx + off, y, cz + 2, Blocks.IRON_BLOCK);
		}
		for (int z = cz - 2; z <= cz + 2; z++) {
			set(cx, cy, z, Blocks.IRON_BLOCK);
		}
		// rim and spokes (vertical ring in the X/Y plane)
		for (int a = 0; a < 360; a += 3) {
			int x = cx + (int) Math.round(Math.cos(Math.toRadians(a)) * r);
			int y = cy + (int) Math.round(Math.sin(Math.toRadians(a)) * r);
			if (y >= 0) {
				set(x, y, cz, Blocks.RED_STAINED_GLASS_PANE);
				set(x, y, cz - 1, Blocks.IRON_BARS);
			}
		}
		for (int a = 0; a < 360; a += 45) {
			for (int k = 1; k < r; k++) {
				int x = cx + (int) Math.round(Math.cos(Math.toRadians(a)) * k);
				int y = cy + (int) Math.round(Math.sin(Math.toRadians(a)) * k);
				set(x, y, cz, Blocks.IRON_BARS);
			}
			int x = cx + (int) Math.round(Math.cos(Math.toRadians(a)) * r);
			int y = cy + (int) Math.round(Math.sin(Math.toRadians(a)) * r);
			// hanging gondola
			Block color = new Block[]{Blocks.YELLOW_CONCRETE, Blocks.CYAN_CONCRETE, Blocks.RED_CONCRETE, Blocks.LIME_CONCRETE}[(a / 45) % 4];
			if (y - 3 >= 0) {
				set(x, y - 1, cz + 1, Blocks.IRON_CHAIN);
				fill(x - 1, y - 3, cz + 1, x + 1, y - 2, cz + 2, color);
				clear(x, y - 2, cz + 1, x, y - 2, cz + 2);
			}
		}
	}

	private void circusTent(int cx, int cz) {
		int r = 10;
		for (int x = -r - 1; x <= r + 1; x++) {
			for (int z = -r - 1; z <= r + 1; z++) {
				double d = Math.sqrt(x * x + z * z);
				int sector = (((int) Math.round(Math.toDegrees(Math.atan2(z, x)) + 180)) / 15) & 1;
				Block stripe = sector == 0 ? Blocks.RED_WOOL : Blocks.WHITE_WOOL;
				if (d <= r) {
					set(cx + x, -1, cz + z, d < 4 ? Blocks.SAND : Blocks.SPRUCE_PLANKS);
				}
				if (d > r - 0.6 && d <= r + 0.4) {
					for (int y = 0; y <= 5; y++) {
						set(cx + x, y, cz + z, stripe);
					}
				}
				if (d <= r + 0.4) {
					int y = 6 + (int) Math.round((r - d) * 0.9);
					set(cx + x, y, cz + z, stripe);
				}
			}
		}
		// entrance flaps facing the park
		clear(cx - 1, 0, cz - r, cx + 1, 3, cz - r + 1);
		set(cx - 2, 0, cz - r, Blocks.RED_WOOL);
		set(cx + 2, 0, cz - r, Blocks.RED_WOOL);
		for (int y = 0; y <= 15; y++) {
			set(cx, y, cz + 6, Blocks.STRIPPED_DARK_OAK_LOG);
		}
		set(cx, 16, cz + 6, Blocks.RED_WOOL);
		// ring and bleachers
		for (int a = 0; a < 360; a += 8) {
			int x = (int) Math.round(Math.cos(Math.toRadians(a)) * 4);
			int z = (int) Math.round(Math.sin(Math.toRadians(a)) * 4);
			set(cx + x, 0, cz + z, (a / 8 & 1) == 0 ? Blocks.RED_CONCRETE : Blocks.YELLOW_CONCRETE);
		}
		for (int a = 20; a <= 160; a += 7) {
			for (int row = 0; row < 3; row++) {
				int x = (int) Math.round(Math.cos(Math.toRadians(a)) * (6 + row));
				int z = (int) Math.round(Math.sin(Math.toRadians(a)) * (6 + row));
				Direction face = Math.abs(x) > Math.abs(z) ? (x > 0 ? Direction.EAST : Direction.WEST) : (z > 0 ? Direction.SOUTH : Direction.NORTH);
				set(cx + x, row, cz + z, stairs(Blocks.SPRUCE_STAIRS, face, false));
			}
		}
		set(cx, 0, cz, Blocks.RED_CONCRETE);
		set(cx, 1, cz, Blocks.GOLD_BLOCK);
		for (int a = 0; a < 360; a += 60) {
			candles(cx + (int) Math.round(Math.cos(Math.toRadians(a)) * 2), 0, cz + (int) Math.round(Math.sin(Math.toRadians(a)) * 2), 3, true);
		}
		decay(cx - r + 1, 0, cz - r + 1, cx + r - 1, 6, cz + r - 1, 0.04F, 0.015F);
	}

	private void stands() {
		int[][] spots = {{-26, 10}, {24, -16}, {-10, -22}, {28, 24}};
		Block[] colors = {Blocks.PINK_CONCRETE, Blocks.LIGHT_BLUE_CONCRETE, Blocks.YELLOW_CONCRETE, Blocks.LIME_CONCRETE};
		for (int i = 0; i < spots.length; i++) {
			int x = spots[i][0], z = spots[i][1];
			fill(x, 0, z, x + 3, 1, z + 2, colors[i]);
			clear(x + 1, 1, z, x + 2, 1, z);
			for (int xx = x - 1; xx <= x + 4; xx++) {
				for (int zz = z - 1; zz <= z + 3; zz++) {
					set(xx, 3, zz, ((xx + zz) & 1) == 0 ? Blocks.RED_WOOL : Blocks.WHITE_WOOL);
				}
			}
			for (int y = 0; y <= 2; y++) {
				set(x - 1, y, z - 1, Blocks.SPRUCE_FENCE);
				set(x + 4, y, z - 1, Blocks.SPRUCE_FENCE);
			}
		}
	}

	private void lamps() {
		for (int z = -28; z <= 8; z += 9) {
			for (int x : new int[]{-3, 3}) {
				for (int y = 0; y <= 3; y++) {
					set(x, y, z, Blocks.DARK_OAK_FENCE);
				}
				if (rand.nextFloat() < 0.5F) {
					lantern(x, 4, z, Blocks.SOUL_LANTERN, false);
				} else {
					set(x, 4, z, Blocks.DARK_OAK_FENCE);
				}
			}
		}
	}
}
