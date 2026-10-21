package com.deadline.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Directional furniture/prop from the DEAD LINE building kit: model faces north, shape rotates with the facing. */
public class DecorBlock extends HorizontalDirectionalBlock {
	private final VoxelShape[] shapes = new VoxelShape[4];

	public DecorBlock(Properties props, double[][] northBoxes) {
		super(props);
		for (Direction d : Direction.Plane.HORIZONTAL) {
			shapes[d.get2DDataValue()] = build(northBoxes, d);
		}
		this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	static VoxelShape build(double[][] boxes, Direction facing) {
		if (boxes == null || boxes.length == 0) {
			return Shapes.empty();
		}
		int turns = switch (facing) {
			case EAST -> 1;
			case SOUTH -> 2;
			case WEST -> 3;
			default -> 0;
		};
		VoxelShape shape = Shapes.empty();
		for (double[] b : boxes) {
			double x1 = b[0], y1 = b[1], z1 = b[2], x2 = b[3], y2 = b[4], z2 = b[5];
			for (int i = 0; i < turns; i++) {
				double nx1 = 16 - z2, nz1 = x1, nx2 = 16 - z1, nz2 = x2;
				x1 = nx1;
				z1 = nz1;
				x2 = nx2;
				z2 = nz2;
			}
			shape = Shapes.or(shape, Block.box(x1, y1, z1, x2, y2, z2));
		}
		return shape.optimize();
	}

	@Override
	protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
		return simpleCodec(p -> new DecorBlock(p, new double[0][]));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
		builder.add(FACING);
	}

	@Override
	public BlockState getStateForPlacement(BlockPlaceContext ctx) {
		return this.defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		VoxelShape s = shapes[state.getValue(FACING).get2DDataValue()];
		return s.isEmpty() ? Shapes.box(0.25, 0, 0.25, 0.75, 0.25, 0.75) : s;
	}

	@Override
	protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		// props without collision still get their boxes as the outline, so they can be aimed at and clicked
		return this.hasCollision ? shapes[state.getValue(FACING).get2DDataValue()] : Shapes.empty();
	}
}
