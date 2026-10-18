package com.deadline.registry;

import com.deadline.DeadLine;
import com.deadline.block.BloodStainBlock;
import com.deadline.block.RitualCandleBlock;
import com.deadline.block.SaltLineBlock;
import java.util.function.Function;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;

public final class ModBlocks {
	public static final SaltLineBlock SALT_LINE = register("salt_line", SaltLineBlock::new,
			BlockBehaviour.Properties.of().mapColor(MapColor.SNOW).noCollision().instabreak().sound(SoundType.SAND).pushReaction(PushReaction.DESTROY), false);
	public static final RitualCandleBlock RITUAL_CANDLE = register("ritual_candle", RitualCandleBlock::new,
			BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK).noOcclusion().strength(0.1F).sound(SoundType.CANDLE)
					.lightLevel(state -> state.getValue(RitualCandleBlock.LIT) ? 3 * state.getValue(RitualCandleBlock.CANDLES) : 0)
					.pushReaction(PushReaction.DESTROY), true);
	public static final BloodStainBlock BLOOD_STAIN = register("blood_stain", BloodStainBlock::new,
			BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).noCollision().instabreak().sound(SoundType.SLIME_BLOCK).pushReaction(PushReaction.DESTROY), true);

	private ModBlocks() {
	}

	private static <T extends Block> T register(String name, Function<BlockBehaviour.Properties, T> factory, BlockBehaviour.Properties props, boolean withItem) {
		ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, DeadLine.id(name));
		T block = factory.apply(props.setId(key));
		Registry.register(BuiltInRegistries.BLOCK, key, block);
		if (withItem) {
			ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, DeadLine.id(name));
			Registry.register(BuiltInRegistries.ITEM, itemKey, new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
		}
		return block;
	}

	public static void init() {
	}
}
