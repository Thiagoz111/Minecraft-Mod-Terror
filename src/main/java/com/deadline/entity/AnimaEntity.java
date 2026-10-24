package com.deadline.entity;

import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** A wandering soul. Invisible to the naked eye; the camera flash or UV light reveals it. */
public class AnimaEntity extends HauntEntity {
	private static final EntityDataAccessor<Integer> REVEALED = SynchedEntityData.defineId(AnimaEntity.class, EntityDataSerializers.INT);
	private Vec3 home;
	private Vec3 drift = Vec3.ZERO;

	public AnimaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.setNoGravity(true);
		this.setInvisible(true);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 20.0)
				.add(Attributes.MOVEMENT_SPEED, 0.2)
				.add(Attributes.FLYING_SPEED, 0.2);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(REVEALED, 0);
	}

	@Override
	protected void registerGoals() {
	}

	public boolean isRevealed() {
		return this.entityData.get(REVEALED) > 0;
	}

	public void reveal(int ticks) {
		this.entityData.set(REVEALED, Math.max(ticks, this.entityData.get(REVEALED)));
	}

	@Override
	public void tick() {
		super.tick();
		if (HauntEntity.SHOWCASE) {
			return;
		}
		this.setNoGravity(true);
		if (this.level().isClientSide()) {
			if (this.random.nextInt(4) == 0) {
				this.level().addParticle(ModParticles.COLD_BREATH, this.getRandomX(1.2), this.getRandomY(), this.getRandomZ(1.2), 0, -0.01, 0);
			}
			return;
		}
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		int rev = this.entityData.get(REVEALED);
		if (rev > 0) {
			this.entityData.set(REVEALED, rev - 1);
		}
		this.setInvisible(rev <= 0);
		if (home == null) {
			home = this.position();
		}
		Player near = level.getNearestPlayer(this, 12);
		if (this.tickCount % 40 == 0) {
			Vec3 goal;
			if (near != null && this.random.nextInt(3) > 0) {
				goal = near.position().add(this.random.nextGaussian() * 3, 1 + this.random.nextDouble(), this.random.nextGaussian() * 3);
			} else {
				goal = home.add(this.random.nextGaussian() * 6, this.random.nextDouble() * 2, this.random.nextGaussian() * 6);
			}
			drift = goal.subtract(this.position()).normalize().scale(0.05);
		}
		this.setDeltaMovement(this.getDeltaMovement().scale(0.8).add(drift).add(0, Math.sin(this.tickCount * 0.1) * 0.005, 0));
		if (!drift.equals(Vec3.ZERO)) {
			this.setYRot((float) (Math.atan2(-drift.x, drift.z) * 180 / Math.PI));
			this.setYBodyRot(this.getYRot());
		}
		if (this.tickCount % 200 == 0 && this.random.nextBoolean()) {
			this.playSound(ModSounds.ANIMA_MOAN, 1.2F, 0.8F + this.random.nextFloat() * 0.4F);
		}
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (!isRevealed()) {
			return false;
		}
		return super.hurtServer(level, source, amount);
	}

	@Override
	protected void becomeWeakened(ServerLevel level) {
		super.becomeWeakened(level);
		reveal(400);
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.ANIMA_MOAN;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.ANIMA_MOAN;
	}
}
