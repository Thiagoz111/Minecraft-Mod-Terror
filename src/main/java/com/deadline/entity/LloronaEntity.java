package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * La Llorona. Her weeping is heard <i>inverted</i>: loud and close when she is far, faint and distant
 * when she is right behind you. Looking at her makes her scream; turning away lets her blink closer.
 */
public class LloronaEntity extends HauntEntity {
	public static final int ACT_IDLE = 0, ACT_CHASE = 1, ACT_SCREAM = 2;
	private int screamCooldown = 160;
	private int blinkCooldown = 260;
	private int cryCooldown = 80;
	private int screamTimer;

	public LloronaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 90.0)
				.add(Attributes.MOVEMENT_SPEED, 0.25)
				.add(Attributes.ATTACK_DAMAGE, 7.0)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.8);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15, true));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.6));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 24.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level) || this.isWeakened()) {
			return;
		}
		LivingEntity target = this.getTarget();
		if (screamTimer > 0 && --screamTimer == 0) {
			this.setAction(target != null ? ACT_CHASE : ACT_IDLE);
		}
		if (--cryCooldown <= 0) {
			cryCooldown = 140 + this.random.nextInt(120);
			for (ServerPlayer p : level.players()) {
				if (p.distanceToSqr(this) < 72 * 72) {
					Fx.invertedSound(p, this, ModSounds.LLORONA_CRY, 1.0F);
				}
			}
			if (this.random.nextInt(3) == 0) {
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.LLORONA_WAIL, SoundSource.HOSTILE, 2.5F, 1.0F);
			}
		}
		if (target == null || this.isStunned()) {
			if (screamTimer == 0) {
				this.setAction(ACT_IDLE);
			}
			return;
		}
		if (screamTimer == 0) {
			this.setAction(ACT_CHASE);
		}
		double dist = this.distanceTo(target);
		if (--screamCooldown <= 0 && dist < 14 && this.isWatchedBy(target, 0.08)) {
			scream(level, target);
		}
		if (--blinkCooldown <= 0 && dist > 6 && !this.isWatchedBy(target, 0.4)) {
			blinkCooldown = 220 + this.random.nextInt(200);
			if (this.teleportBehind(target, 4 + this.random.nextInt(4))) {
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.LLORONA_WAIL, SoundSource.HOSTILE, 1.6F, 0.9F);
			}
		}
	}

	private void scream(ServerLevel level, LivingEntity target) {
		screamCooldown = 300 + this.random.nextInt(200);
		screamTimer = 30;
		this.setAction(ACT_SCREAM);
		this.stun(25);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.LLORONA_SCREAM, SoundSource.HOSTILE, 3.0F, 1.0F);
		target.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 120, 0));
		target.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 1));
		if (target instanceof ServerPlayer p) {
			SanityManager.add(p, -12.0F);
			Fx.shake(p, 1.0F, 30);
		}
	}

	@Override
	public float fearAura() {
		return 0.7F;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.LLORONA_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.LLORONA_DEATH;
	}
}
