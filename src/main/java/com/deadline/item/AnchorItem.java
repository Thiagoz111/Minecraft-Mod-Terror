package com.deadline.item;

import com.deadline.entity.AnchorEntity;
import com.deadline.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;

/** A cursed object. In creative it can be placed as a floating anchor to set up custom scenes. */
public class AnchorItem extends Item {
	public AnchorItem(Properties props) {
		super(props);
	}

	@Override
	public InteractionResult useOn(UseOnContext ctx) {
		Player p = ctx.getPlayer();
		if (p == null || !p.isCreative()) {
			return InteractionResult.PASS;
		}
		if (ctx.getLevel() instanceof ServerLevel level) {
			AnchorEntity anchor = ModEntities.ANCHOR.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
			if (anchor != null) {
				BlockPos pos = ctx.getClickedPos().relative(ctx.getClickedFace());
				anchor.setItem(new ItemStack(this));
				anchor.snapTo(pos.getX() + 0.5, pos.getY() + 0.3, pos.getZ() + 0.5, 0, 0);
				level.addFreshEntity(anchor);
			}
		}
		return InteractionResult.SUCCESS;
	}
}
