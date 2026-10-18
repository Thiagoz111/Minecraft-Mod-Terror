package com.deadline.caseload.sites;

import com.deadline.registry.ModBlocks;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraft.world.phys.Vec3;

/**
 * Procedural builder for a case location. Coordinates are relative to the site origin; y = 0 is the first
 * air layer above the flat ground (the grass surface is y = -1).
 */
public abstract class SiteBuilder {
	public record Extra(EntityType<?> type, Vec3 pos) {
	}

	public record Layout(Vec3 spawn, float yaw, Vec3 boss, Vec3 anchor, List<Extra> extras) {
	}

	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;

	protected ServerLevel level;
	protected BlockPos o;
	protected RandomSource rand;
	protected final List<Extra> extras = new ArrayList<>();

	public final Layout build(ServerLevel level, BlockPos origin, RandomSource random) {
		this.level = level;
		this.o = origin;
		this.rand = random;
		this.extras.clear();
		return generate();
	}

	protected abstract Layout generate();

	// ------------------------------------------------------------------ coordinates
	protected BlockPos at(int x, int y, int z) {
		return o.offset(x, y, z);
	}

	protected Vec3 v(double x, double y, double z) {
		return new Vec3(o.getX() + x, o.getY() + y, o.getZ() + z);
	}

	protected void extra(EntityType<?> type, double x, double y, double z) {
		extras.add(new Extra(type, v(x, y, z)));
	}

	protected Layout layout(Vec3 spawn, float yaw, Vec3 boss, Vec3 anchor) {
		return new Layout(spawn, yaw, boss, anchor, new ArrayList<>(extras));
	}

	// ------------------------------------------------------------------ primitives
	protected void set(int x, int y, int z, BlockState s) {
		level.setBlock(at(x, y, z), s, FLAGS);
	}

	protected void set(int x, int y, int z, Block b) {
		set(x, y, z, b.defaultBlockState());
	}

	protected BlockState get(int x, int y, int z) {
		return level.getBlockState(at(x, y, z));
	}

	protected boolean isAir(int x, int y, int z) {
		return get(x, y, z).isAir();
	}

	protected void fill(int x0, int y0, int z0, int x1, int y1, int z1, BlockState s) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) {
			for (int y = Math.min(y0, y1); y <= Math.max(y0, y1); y++) {
				for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) {
					set(x, y, z, s);
				}
			}
		}
	}

	protected void fill(int x0, int y0, int z0, int x1, int y1, int z1, Block b) {
		fill(x0, y0, z0, x1, y1, z1, b.defaultBlockState());
	}

	/** Fill with a random mix: palette entries are picked uniformly. */
	protected void fillMix(int x0, int y0, int z0, int x1, int y1, int z1, Block... palette) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) {
			for (int y = Math.min(y0, y1); y <= Math.max(y0, y1); y++) {
				for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) {
					set(x, y, z, palette[rand.nextInt(palette.length)]);
				}
			}
		}
	}

	protected void clear(int x0, int y0, int z0, int x1, int y1, int z1) {
		fill(x0, y0, z0, x1, y1, z1, Blocks.AIR);
	}

	/** Walls of a box (no floor/ceiling), mixing a decayed palette. */
	protected void walls(int x0, int y0, int z0, int x1, int y1, int z1, Block... palette) {
		for (int y = y0; y <= y1; y++) {
			for (int x = x0; x <= x1; x++) {
				set(x, y, z0, palette[rand.nextInt(palette.length)]);
				set(x, y, z1, palette[rand.nextInt(palette.length)]);
			}
			for (int z = z0; z <= z1; z++) {
				set(x0, y, z, palette[rand.nextInt(palette.length)]);
				set(x1, y, z, palette[rand.nextInt(palette.length)]);
			}
		}
	}

	/** Rough, decayed ground: re-surfaces a square area with a mixed palette and scatters plants. */
	protected void ground(int r, Block[] surface, Block[] plants, float plantChance) {
		for (int x = -r; x <= r; x++) {
			for (int z = -r; z <= r; z++) {
				set(x, -1, z, surface[rand.nextInt(surface.length)]);
				clear(x, 0, z, x, 0, z);
				if (plants.length > 0 && rand.nextFloat() < plantChance) {
					set(x, 0, z, plants[rand.nextInt(plants.length)]);
				}
			}
		}
	}

	/** Clears the air volume above the site (in case of leftovers). */
	protected void clearAbove(int r, int h) {
		clear(-r, 0, -r, r, h, r);
	}

	// ------------------------------------------------------------------ block-state helpers
	protected static BlockState stairs(Block b, Direction facing, boolean top) {
		return b.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, facing).setValue(BlockStateProperties.HALF, top ? Half.TOP : Half.BOTTOM);
	}

	protected static BlockState slab(Block b, boolean top) {
		return b.defaultBlockState().setValue(BlockStateProperties.SLAB_TYPE, top ? SlabType.TOP : SlabType.BOTTOM);
	}

	protected static BlockState facing(Block b, Direction d) {
		return b.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, d);
	}

	/** For blocks using the six-way FACING property (barrels, dispensers...). */
	protected static BlockState dir(Block b, Direction d) {
		return b.defaultBlockState().setValue(BlockStateProperties.FACING, d);
	}

	protected static BlockState log(Block b, Direction.Axis axis) {
		return b.defaultBlockState().setValue(BlockStateProperties.AXIS, axis);
	}

	protected void door(int x, int y, int z, Block door, Direction facing, boolean open) {
		BlockState base = door.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, facing).setValue(BlockStateProperties.OPEN, open);
		set(x, y, z, base.setValue(BlockStateProperties.DOUBLE_BLOCK_HALF, DoubleBlockHalf.LOWER));
		set(x, y + 1, z, base.setValue(BlockStateProperties.DOUBLE_BLOCK_HALF, DoubleBlockHalf.UPPER));
	}

	/** Bed with its foot at (x,z) and head one block toward {@code facing}. */
	protected void bed(int x, int y, int z, Block bed, Direction facing) {
		BlockState b = bed.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, facing);
		set(x, y, z, b.setValue(BlockStateProperties.BED_PART, BedPart.FOOT));
		set(x + facing.getStepX(), y, z + facing.getStepZ(), b.setValue(BlockStateProperties.BED_PART, BedPart.HEAD));
	}

	protected void candles(int x, int y, int z, int count, boolean lit) {
		set(x, y, z, ModBlocks.RITUAL_CANDLE.defaultBlockState().setValue(BlockStateProperties.CANDLES, Math.max(1, Math.min(4, count))).setValue(BlockStateProperties.LIT, lit));
	}

	protected void blood(int x, int y, int z) {
		if (isAir(x, y, z) && !isAir(x, y - 1, z)) {
			set(x, y, z, ModBlocks.BLOOD_STAIN);
		}
	}

	protected void web(int x, int y, int z) {
		if (isAir(x, y, z)) {
			set(x, y, z, Blocks.COBWEB);
		}
	}

	protected void lantern(int x, int y, int z, Block lantern, boolean hanging) {
		set(x, y, z, lantern.defaultBlockState().setValue(BlockStateProperties.HANGING, hanging));
	}

	/** Scatter cobwebs in the upper corners and random blood stains inside a room. */
	protected void decay(int x0, int y0, int z0, int x1, int y1, int z1, float webs, float bloods) {
		for (int x = x0; x <= x1; x++) {
			for (int z = z0; z <= z1; z++) {
				boolean edge = x == x0 || x == x1 || z == z0 || z == z1;
				if (edge && rand.nextFloat() < webs) {
					web(x, y1, z);
				}
				if (rand.nextFloat() < bloods) {
					blood(x, y0, z);
				}
			}
		}
	}

	// ------------------------------------------------------------------ nature
	/** A leafless dead tree with twisted branches. */
	protected void deadTree(int x, int z, Block log, int height) {
		for (int y = 0; y < height; y++) {
			set(x, y, z, log);
		}
		int branches = 2 + rand.nextInt(3);
		for (int b = 0; b < branches; b++) {
			int by = height / 2 + rand.nextInt(Math.max(1, height / 2));
			Direction d = Direction.Plane.HORIZONTAL.getRandomDirection(rand);
			int len = 2 + rand.nextInt(3);
			for (int i = 1; i <= len; i++) {
				set(x + d.getStepX() * i, by + (i > 1 ? 1 : 0) + i / 3, z + d.getStepZ() * i, log(log, d.getAxis()));
			}
		}
	}

	/** Tall conifer for the black forest. */
	protected void spruce(int x, int z, int height, boolean dead) {
		for (int y = 0; y < height; y++) {
			set(x, y, z, dead ? Blocks.STRIPPED_SPRUCE_LOG : Blocks.SPRUCE_LOG);
		}
		if (dead) {
			return;
		}
		for (int y = 3; y < height + 1; y++) {
			int r = Math.max(0, (height - y) / 3);
			if ((y & 1) == 0 && r > 0) {
				r = Math.max(1, r - 1);
			}
			for (int dx = -r; dx <= r; dx++) {
				for (int dz = -r; dz <= r; dz++) {
					if (Math.abs(dx) + Math.abs(dz) <= r + 1 && (dx != 0 || dz != 0 || y >= height) && isAir(x + dx, y, z + dz)) {
						set(x + dx, y, z + dz, Blocks.SPRUCE_LEAVES.defaultBlockState().setValue(BlockStateProperties.PERSISTENT, true));
					}
				}
			}
		}
		set(x, height, z, Blocks.SPRUCE_LEAVES.defaultBlockState().setValue(BlockStateProperties.PERSISTENT, true));
	}

	/** Gnarled swamp/willow tree with hanging roots. */
	protected void willow(int x, int z, int height) {
		for (int y = 0; y < height; y++) {
			set(x, y, z, Blocks.MANGROVE_LOG);
		}
		for (Direction d : Direction.Plane.HORIZONTAL) {
			set(x + d.getStepX(), 0, z + d.getStepZ(), Blocks.MANGROVE_ROOTS);
		}
		int r = 3;
		for (int dx = -r; dx <= r; dx++) {
			for (int dz = -r; dz <= r; dz++) {
				if (dx * dx + dz * dz <= r * r + 1) {
					set(x + dx, height, z + dz, Blocks.MANGROVE_LEAVES.defaultBlockState().setValue(BlockStateProperties.PERSISTENT, true));
					if ((dx * dx + dz * dz >= 4) && rand.nextFloat() < 0.6F) {
						int len = 1 + rand.nextInt(4);
						for (int i = 1; i <= len; i++) {
							if (isAir(x + dx, height - i, z + dz)) {
								set(x + dx, height - i, z + dz, i == len ? Blocks.HANGING_ROOTS : Blocks.MANGROVE_LEAVES.defaultBlockState().setValue(BlockStateProperties.PERSISTENT, true));
							}
						}
					}
				}
			}
		}
		set(x, height + 1, z, Blocks.MANGROVE_LEAVES.defaultBlockState().setValue(BlockStateProperties.PERSISTENT, true));
	}

	/** Wooden memorial / grave cross. */
	protected void cross(int x, int y, int z, Block post, boolean inverted) {
		set(x, y, z, post);
		set(x, y + 1, z, post);
		set(x, y + 2, z, post);
		int arm = inverted ? y + 1 : y + 2;
		set(x - 1, arm, z, post);
		set(x + 1, arm, z, post);
	}
}
