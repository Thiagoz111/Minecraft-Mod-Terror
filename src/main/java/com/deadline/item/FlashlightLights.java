package com.deadline.item;

import com.deadline.entity.AnimaEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Moves invisible light blocks to wherever each lit flashlight is pointing. */
public final class FlashlightLights {
	private record Placed(ResourceKey<Level> dim, BlockPos pos) {
	}

	private static final Map<UUID, Placed> LIGHTS = new HashMap<>();
	private static final double RANGE = 26.0;

	private FlashlightLights() {
	}

	public static void tick(MinecraftServer server) {
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			ItemStack held = p.getMainHandItem().is(ModItems.FLASHLIGHT) ? p.getMainHandItem()
					: (p.getOffhandItem().is(ModItems.FLASHLIGHT) ? p.getOffhandItem() : ItemStack.EMPTY);
			if (held.isEmpty() || !FlashlightItem.isOn(held) || p.isSpectator()) {
				clear(p);
				continue;
			}
			update(p, FlashlightItem.isUv(held));
		}
	}

	private static void update(ServerPlayer p, boolean uv) {
		ServerLevel level = p.level();
		// Flicker near entities.
		boolean nearHaunt = !level.getEntitiesOfClass(HauntEntity.class, p.getBoundingBox().inflate(12), e -> !(e instanceof AnimaEntity)).isEmpty();
		if (nearHaunt && p.getRandom().nextInt(5) == 0) {
			clear(p);
			if (p.getRandom().nextInt(6) == 0) {
				level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.FLASHLIGHT_FLICKER, SoundSource.PLAYERS, 0.5F, 1.0F);
			}
			return;
		}
		Vec3 eye = p.getEyePosition();
		Vec3 end = eye.add(p.getLookAngle().scale(RANGE));
		BlockHitResult hit = level.clip(new ClipContext(eye, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, p));
		BlockPos target;
		if (hit.getType() == HitResult.Type.MISS) {
			target = BlockPos.containing(end);
		} else {
			target = hit.getBlockPos().relative(hit.getDirection());
		}
		Placed old = LIGHTS.get(p.getUUID());
		if (old == null || !old.pos().equals(target) || old.dim() != level.dimension()) {
			clear(p);
			BlockState st = level.getBlockState(target);
			if (st.isAir() || st.is(Blocks.LIGHT)) {
				level.setBlock(target, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, uv ? 9 : 14), 3);
				LIGHTS.put(p.getUUID(), new Placed(level.dimension(), target));
			}
		}
		if (uv && p.tickCount % 5 == 0) {
			Vec3 look = p.getLookAngle();
			for (AnimaEntity a : level.getEntitiesOfClass(AnimaEntity.class, p.getBoundingBox().inflate(RANGE))) {
				Vec3 to = a.position().add(0, 1, 0).subtract(eye);
				if (to.normalize().dot(look) > 0.93 && p.hasLineOfSight(a)) {
					a.reveal(30);
				}
			}
			if (p.getRandom().nextInt(3) == 0) {
				Vec3 h = hit.getLocation();
				level.sendParticles(p, ModParticles.HANDPRINT, true, false, h.x, h.y, h.z, 1, 0.6, 0.6, 0.6, 0);
			}
		}
	}

	public static void clear(ServerPlayer p) {
		clear(p.level().getServer(), p.getUUID());
	}

	/** Removes the light block a key (a player's flashlight, a car headlight beam) placed, if it is still there. */
	public static void clear(MinecraftServer server, UUID key) {
		Placed old = LIGHTS.remove(key);
		if (old == null) {
			return;
		}
		ServerLevel level = server.getLevel(old.dim());
		if (level != null && level.isLoaded(old.pos()) && level.getBlockState(old.pos()).is(Blocks.LIGHT)) {
			level.setBlock(old.pos(), Blocks.AIR.defaultBlockState(), 3);
		}
	}

	/**
	 * Any other beam of light (the car's headlights): moves the light block of `key` to where a ray from `from` along
	 * `dir` hits within `range` (in the air just before the hit). Call every tick or two; {@link #clear(MinecraftServer,
	 * UUID)} when it goes dark.
	 */
	public static void beam(UUID key, ServerLevel level, Vec3 from, Vec3 dir, double range, int lightLevel, net.minecraft.world.entity.Entity source) {
		Vec3 end = from.add(dir.normalize().scale(range));
		BlockHitResult hit = level.clip(new ClipContext(from, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, source));
		BlockPos target = hit.getType() == HitResult.Type.MISS ? BlockPos.containing(end) : hit.getBlockPos().relative(hit.getDirection());
		Placed old = LIGHTS.get(key);
		if (old != null && old.pos().equals(target) && old.dim() == level.dimension()) {
			return;
		}
		clear(level.getServer(), key);
		for (BlockPos p : new BlockPos[] {target, target.above()}) {  // tall grass or a flower where the beam lands: one up
			if (!level.isLoaded(p)) {
				return;
			}
			BlockState st = level.getBlockState(p);
			if (st.isAir() || st.is(Blocks.LIGHT)) {
				level.setBlock(p, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, Math.max(1, Math.min(15, lightLevel))), 3);
				LIGHTS.put(key, new Placed(level.dimension(), p));
				return;
			}
		}
	}
}
