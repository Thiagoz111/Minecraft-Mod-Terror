package com.deadline.entity;

import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/** Road flare: lands and burns bright red for 30 seconds. Lights the dark, scares the Wendigo. */
public class FlareEntity extends ThrowableItemProjectile {
	private static final EntityDataAccessor<Boolean> BURNING = SynchedEntityData.defineId(FlareEntity.class, EntityDataSerializers.BOOLEAN);
	private static final int BURN_TIME = 600;
	private int burnTicks;
	private BlockPos light;

	public FlareEntity(EntityType<? extends FlareEntity> type, Level level) {
		super(type, level);
	}

	public FlareEntity(Level level, LivingEntity owner, ItemStack stack) {
		super(ModEntities.FLARE, owner, level, stack);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(BURNING, false);
	}

	public boolean isBurning() {
		return this.entityData.get(BURNING);
	}

	@Override
	protected Item getDefaultItem() {
		return ModItems.FLARE;
	}

	@Override
	protected void onHitBlock(BlockHitResult hit) {
		super.onHitBlock(hit);
		if (!this.isBurning()) {
			this.entityData.set(BURNING, true);
			this.setNoGravity(true);
			Vec3 loc = hit.getLocation();
			net.minecraft.core.Direction d = hit.getDirection();
			this.setPos(loc.x + d.getStepX() * 0.1, loc.y + d.getStepY() * 0.1, loc.z + d.getStepZ() * 0.1);
			this.setDeltaMovement(Vec3.ZERO);
			this.level().playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.FLARE_IGNITE, SoundSource.PLAYERS, 1.5F, 1.0F);
		}
	}

	@Override
	protected void onHitEntity(EntityHitResult hit) {
		super.onHitEntity(hit);
		hit.getEntity().igniteForSeconds(5.0F);
	}

	@Override
	public void tick() {
		if (this.isBurning()) {
			this.setDeltaMovement(Vec3.ZERO);
			this.baseTick();
			burnTicks++;
			if (this.level().isClientSide()) {
				for (int i = 0; i < 2; i++) {
					this.level().addParticle(new DustParticleOptions(0xFF2A1A, 1.2F), this.getX(), this.getY() + 0.1, this.getZ(),
							(this.random.nextDouble() - 0.5) * 0.1, 0.08, (this.random.nextDouble() - 0.5) * 0.1);
				}
				if (this.random.nextInt(3) == 0) {
					this.level().addParticle(ParticleTypes.SMOKE, this.getX(), this.getY() + 0.2, this.getZ(), 0, 0.05, 0);
				}
				if (this.random.nextInt(4) == 0) {
					this.level().addParticle(ParticleTypes.FLAME, this.getX(), this.getY() + 0.1, this.getZ(), 0, 0.02, 0);
				}
				return;
			}
			ServerLevel level = (ServerLevel) this.level();
			BlockPos pos = this.blockPosition();
			if (!pos.equals(light)) {
				clearLight();
				if (level.getBlockState(pos).isAir()) {
					level.setBlock(pos, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, 15), 3);
					light = pos;
				}
			}
			if (burnTicks % 40 == 0) {
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.FLARE_BURN, SoundSource.PLAYERS, 0.8F, 1.0F);
			}
			if (burnTicks >= BURN_TIME) {
				this.discard();
			}
			return;
		}
		super.tick();
	}

	private void clearLight() {
		if (light != null && this.level().getBlockState(light).is(Blocks.LIGHT)) {
			this.level().setBlock(light, Blocks.AIR.defaultBlockState(), 3);
		}
		light = null;
	}

	@Override
	public void remove(RemovalReason reason) {
		if (!this.level().isClientSide()) {
			clearLight();
		}
		super.remove(reason);
	}
}
