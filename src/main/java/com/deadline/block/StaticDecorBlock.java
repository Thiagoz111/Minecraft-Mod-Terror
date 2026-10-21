package com.deadline.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Non-rotating prop from the DEAD LINE building kit. */
public class StaticDecorBlock extends Block {
	private final VoxelShape shape;

	public StaticDecorBlock(Properties props, double[][] boxes) {
		super(props);
		this.shape = DecorBlock.build(boxes, Direction.NORTH);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return shape.isEmpty() ? Shapes.box(0.25, 0, 0.25, 0.75, 0.25, 0.75) : shape;
	}

	@Override
	protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return this.hasCollision ? shape : Shapes.empty();
	}
}
