package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.commands.arguments.EntityAnchorArgument;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * El Hombre Sombra. Appears at the edge of a frightened mind. Look at it and it fades;
 * look away and it is closer every time.
 */
public class SombraEntity extends HauntEntity {
	private int life = 1400;
	private int watched;
	private int stepCooldown = 40;

	public SombraEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 40.0)
				.add(Attributes.MOVEMENT_SPEED, 0.0)
				.add(Attributes.FOLLOW_RANGE, 64.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
	}

	@Override
	protected void registerGoals() {
	}

	@Override
	public void tick() {
		super.tick();
		if (HauntEntity.SHOWCASE) {
			return;
		}
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		ServerPlayer target = null;
		double best = 48 * 48;
		for (ServerPlayer p : level.players()) {
			double d = p.distanceToSqr(this);
			if (d < best && !p.isSpectator()) {
				best = d;
				target = p;
			}
		}
		if (target == null || --life <= 0) {
			vanish(level);
			return;
		}
		this.lookAt(EntityAnchorArgument.Anchor.EYES, target.getEyePosition());
		this.setYBodyRot(this.getYRot());
		this.setYHeadRot(this.getYRot());
		if (this.isWatchedBy(target, 0.06)) {
			if (++watched > 8) {
				vanish(level);
			}
			return;
		}
		watched = 0;
		double dist = Math.sqrt(best);
		if (dist < 2.2) {
			Fx.jumpscare(target, "sombra");
			SanityManager.add(target, -25.0F);
			target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0));
			target.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 120, 0));
			vanish(level);
			return;
		}
		if (--stepCooldown <= 0) {
			stepCooldown = 25 + this.random.nextInt(25);
			Vec3 toward = target.position().subtract(this.position()).normalize().scale(Math.min(3.0, dist - 1.5));
			this.teleportNear(this.position().add(toward), 0.0, 0.6);
		}
	}

	public void vanish(ServerLevel level) {
		level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 1.4, this.getZ(), 30, 0.3, 0.9, 0.3, 0.03);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.SOMBRA_VANISH, SoundSource.HOSTILE, 1.2F, 1.0F);
		this.discard();
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		vanish(level);
		return false;
	}

	@Override
	public float fearAura() {
		return 1.0F;
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
		return ModSounds.SOMBRA_VANISH;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.SOMBRA_VANISH;
	}
}
