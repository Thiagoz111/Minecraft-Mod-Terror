package com.deadline.caseload.sites;

import com.deadline.registry.ModEntities;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Bosque Negro: a dense black forest, an abandoned campsite, a ranger cabin covered in antlers and a
 * stone ritual circle where the bone totem sleeps.
 */
public class ForestSite extends SiteBuilder {
	@Override
	protected Layout generate() {
		clearAbove(50, 26);
		ground(50, new Block[]{Blocks.PODZOL, Blocks.COARSE_DIRT, Blocks.GRASS_BLOCK, Blocks.PODZOL, Blocks.MOSS_BLOCK, Blocks.ROOTED_DIRT},
				new Block[]{Blocks.FERN, Blocks.FERN, Blocks.DEAD_BUSH, Blocks.SHORT_GRASS, Blocks.BROWN_MUSHROOM, Blocks.SWEET_BERRY_BUSH}, 0.22F);
		path();
		trees();
		camp();
		cabin();
		ritualCircle();
		clear(-26, 0, 25, -23, 4, 28);
		ShapeFixer.refresh(this, -50, -2, -50, 50, 10, 50);

		extra(ModEntities.ANIMA, -4.5, 1.5, 6.5);
		extra(ModEntities.ANIMA, 22.5, 1.5, -18.5);
		return layout(v(0.5, 0, -44.5), 0.0F, v(-24.5, 0, 26.5), v(0.5, 1.2, 33.5));
	}

	private boolean reserved(int x, int z) {
		if (x * x + z * z < 13 * 13) {
			return true;                          // campsite clearing
		}
		if (Math.abs(x) <= 2 && z < 0) {
			return true;                          // trail from the road
		}
		if (x >= 18 && x <= 32 && z >= -6 && z <= 8) {
			return true;                          // cabin
		}
		if (x * x + (z - 33) * (z - 33) < 8 * 8) {
			return true;                          // ritual circle
		}
		return Math.abs(x) <= 1 && z > 10 && z < 30;
	}

	private void path() {
		for (int z = -50; z <= 0; z++) {
			for (int x = -1; x <= 1; x++) {
				set(x, -1, z, rand.nextFloat() < 0.7F ? Blocks.DIRT_PATH : Blocks.COARSE_DIRT);
				clear(x, 0, z, x, 0, z);
			}
		}
		for (int z = 12; z <= 28; z++) {
			if (rand.nextFloat() < 0.6F) {
				set(0, -1, z, Blocks.COARSE_DIRT);
			}
		}
		// claw marks and blood leading north
		for (int z = 14; z <= 26; z += 2 + rand.nextInt(2)) {
			blood(rand.nextInt(3) - 1, 0, z);
		}
	}

	private void trees() {
		for (int gx = -48; gx <= 48; gx += 4) {
			for (int gz = -48; gz <= 48; gz += 4) {
				int x = gx + rand.nextInt(3) - 1;
				int z = gz + rand.nextInt(3) - 1;
				if (reserved(x, z) || rand.nextFloat() < 0.18F) {
					continue;
				}
				float r = rand.nextFloat();
				if (r < 0.62F) {
					spruce(x, z, 9 + rand.nextInt(8), false);
				} else if (r < 0.82F) {
					spruce(x, z, 7 + rand.nextInt(6), true);
				} else {
					deadTree(x, z, Blocks.DARK_OAK_LOG, 6 + rand.nextInt(4));
				}
			}
		}
		// fallen logs
		for (int i = 0; i < 10; i++) {
			int x = -44 + rand.nextInt(88);
			int z = -44 + rand.nextInt(88);
			if (reserved(x, z)) {
				continue;
			}
			boolean alongX = rand.nextBoolean();
			for (int k = 0; k < 4 + rand.nextInt(3); k++) {
				int xx = alongX ? x + k : x;
				int zz = alongX ? z : z + k;
				if (isAir(xx, 0, zz)) {
					set(xx, 0, zz, log(Blocks.SPRUCE_LOG, alongX ? Direction.Axis.X : Direction.Axis.Z));
				}
			}
		}
	}

	private void camp() {
		tent(-6, -3, Blocks.ORANGE_WOOL, Direction.EAST);
		tent(5, -5, Blocks.GREEN_WOOL, Direction.WEST);
		tent(-1, 6, Blocks.BLUE_WOOL, Direction.NORTH);
		set(0, 0, 0, Blocks.CAMPFIRE.defaultBlockState().setValue(BlockStateProperties.LIT, false));
		for (Direction d : Direction.Plane.HORIZONTAL) {
			set(d.getStepX() * 2, 0, d.getStepZ() * 2, log(Blocks.SPRUCE_LOG, d.getAxis() == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X));
		}
		set(3, 0, 2, facing(Blocks.CHEST, Direction.WEST));
		set(-3, 0, 3, Blocks.BARREL);
		lantern(-3, 1, 3, Blocks.LANTERN, false);
		// torn gear and blood
		for (int i = 0; i < 7; i++) {
			blood(-7 + rand.nextInt(15), 0, -7 + rand.nextInt(15));
		}
		set(7, 0, 4, Blocks.RED_CARPET);
		set(-8, 0, 1, Blocks.WHITE_CARPET);
	}

	private void tent(int cx, int cz, Block wool, Direction opening) {
		boolean alongZ = opening.getAxis() == Direction.Axis.Z;
		for (int a = -2; a <= 2; a++) {
			for (int h = 0; h <= 2; h++) {
				int w = 2 - h;
				for (int s : new int[]{-w, w}) {
					int x = alongZ ? cx + s : cx + a;
					int z = alongZ ? cz + a : cz + s;
					set(x, h, z, wool);
				}
			}
		}
		// open the front
		int fx = cx + opening.getStepX() * 2;
		int fz = cz + opening.getStepZ() * 2;
		clear(fx, 0, fz, fx, 1, fz);
		set(cx, 0, cz, Blocks.BROWN_CARPET);
	}

	private void cabin() {
		int x0 = 20, x1 = 30, z0 = -4, z1 = 6;
		fill(x0, -1, z0, x1, -1, z1, Blocks.SPRUCE_PLANKS);
		for (int y = 0; y <= 4; y++) {
			for (int x = x0; x <= x1; x++) {
				set(x, y, z0, log(Blocks.SPRUCE_LOG, Direction.Axis.X));
				set(x, y, z1, log(Blocks.SPRUCE_LOG, Direction.Axis.X));
			}
			for (int z = z0; z <= z1; z++) {
				set(x0, y, z, log(Blocks.SPRUCE_LOG, Direction.Axis.Z));
				set(x1, y, z, log(Blocks.SPRUCE_LOG, Direction.Axis.Z));
			}
		}
		clear(x0 + 1, 0, z0 + 1, x1 - 1, 4, z1 - 1);
		for (int i = 0; i <= 6; i++) {
			for (int x = x0 - 1; x <= x1 + 1; x++) {
				set(x, 5 + i, z0 - 1 + i, stairs(Blocks.DARK_OAK_STAIRS, Direction.SOUTH, false));
				set(x, 5 + i, z1 + 1 - i, stairs(Blocks.DARK_OAK_STAIRS, Direction.NORTH, false));
			}
			for (int z = z0 + i; z <= z1 - i; z++) {
				set(x0, 5 + i, z, Blocks.SPRUCE_PLANKS);
				set(x1, 5 + i, z, Blocks.SPRUCE_PLANKS);
			}
		}
		door(x0, 0, 1, Blocks.SPRUCE_DOOR, Direction.WEST, true);
		set(x1, 2, 1, Blocks.GLASS_PANE);
		set(25, 2, z0, Blocks.AIR);
		bed(28, 0, 4, Blocks.BROWN_BED, Direction.EAST);
		set(23, 0, 4, Blocks.SPRUCE_FENCE);
		set(23, 1, 4, Blocks.SPRUCE_PRESSURE_PLATE);
		set(24, 0, -3, Blocks.BARREL);
		set(28, 0, -3, facing(Blocks.FURNACE, Direction.NORTH));
		// antler trophies (skulls) on the walls and the porch
		for (int x = 22; x <= 28; x += 3) {
			set(x, 3, z0 + 1, facing(Blocks.SKELETON_WALL_SKULL, Direction.SOUTH));
		}
		for (int z = -2; z <= 4; z += 3) {
			set(x0 - 2, 0, z, Blocks.BONE_BLOCK);
			set(x0 - 2, 1, z, Blocks.SPRUCE_FENCE);
			set(x0 - 2, 2, z, Blocks.SKELETON_SKULL.defaultBlockState().setValue(BlockStateProperties.ROTATION_16, 12));
		}
		decay(x0 + 1, 0, z0 + 1, x1 - 1, 4, z1 - 1, 0.35F, 0.06F);
	}

	private void ritualCircle() {
		int cz = 33;
		for (int a = 0; a < 360; a += 10) {
			int x = (int) Math.round(Math.cos(Math.toRadians(a)) * 6);
			int z = cz + (int) Math.round(Math.sin(Math.toRadians(a)) * 6);
			set(x, -1, z, Blocks.COBBLESTONE);
			if (a % 30 == 0) {
				set(x, 0, z, rand.nextBoolean() ? Blocks.MOSSY_COBBLESTONE_WALL : Blocks.COBBLESTONE_WALL);
				if (rand.nextBoolean()) {
					set(x, 1, z, Blocks.SKELETON_SKULL.defaultBlockState().setValue(BlockStateProperties.ROTATION_16, rand.nextInt(16)));
				}
			}
		}
		for (int a = 0; a < 360; a += 45) {
			int x = (int) Math.round(Math.cos(Math.toRadians(a)) * 3);
			int z = cz + (int) Math.round(Math.sin(Math.toRadians(a)) * 3);
			candles(x, 0, z, 1 + rand.nextInt(3), true);
		}
		set(0, -1, cz, Blocks.BONE_BLOCK);
		set(0, 0, cz, Blocks.BONE_BLOCK);
		// antler poles around the circle
		for (int[] p : new int[][]{{-8, cz - 4}, {8, cz + 3}, {-5, cz + 8}, {6, cz - 7}}) {
			for (int y = 0; y < 4; y++) {
				set(p[0], y, p[1], Blocks.STRIPPED_SPRUCE_LOG);
			}
			set(p[0], 4, p[1], Blocks.BONE_BLOCK);
			set(p[0] - 1, 4, p[1], Blocks.SPRUCE_FENCE);
			set(p[0] + 1, 4, p[1], Blocks.SPRUCE_FENCE);
		}
	}
}
