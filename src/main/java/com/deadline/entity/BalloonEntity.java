package com.deadline.entity;

import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/** A red balloon drifting where Sonrisas has been. Pops when you get close. */
public class BalloonEntity extends Entity {
	private double baseY = Double.NaN;
	private int life = 1200;

	public BalloonEntity(EntityType<? extends BalloonEntity> type, Level level) {
		super(type, level);
		this.setNoGravity(true);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
	}

	@Override
	public void tick() {
		super.tick();
		if (Double.isNaN(baseY)) {
			baseY = this.getY();
		}
		double rise = Math.min(1.8, this.tickCount * 0.02);
		this.setPos(this.getX() + Math.sin(this.tickCount * 0.05) * 0.005, baseY + rise + Math.sin(this.tickCount * 0.08) * 0.08, this.getZ());
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		if (--life <= 0) {
			this.discard();
			return;
		}
		Player p = level.getNearestPlayer(this, 2.4);
		if (p != null && !p.isSpectator()) {
			pop(level);
		}
	}

	public void pop(ServerLevel level) {
		level.sendParticles(new DustParticleOptions(0xD0101C, 1.5F), this.getX(), this.getY() + 0.5, this.getZ(), 25, 0.3, 0.3, 0.3, 0.1);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.BALLOON_POP, SoundSource.HOSTILE, 1.5F, 1.0F);
		if (this.random.nextInt(3) == 0) {
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.PAYASO_LAUGH, SoundSource.HOSTILE, 1.0F, 1.2F);
		}
		for (ServerPlayer sp : level.players()) {
			if (sp.distanceToSqr(this) < 25) {
				SanityManager.add(sp, -3.0F);
			}
		}
		this.discard();
	}

	@Override
	public boolean isPickable() {
		return true;
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		pop(level);
		return true;
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		this.life = in.getIntOr("Life", 600);
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		out.putInt("Life", this.life);
	}
}
