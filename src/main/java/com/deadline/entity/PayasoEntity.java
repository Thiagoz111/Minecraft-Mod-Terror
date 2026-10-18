package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntitySpawnReason;
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
import net.minecraft.world.phys.Vec3;

/**
 * Sonrisas. Hides (invisible) while its music box plays and red balloons drift toward the hunter.
 * When the music stops, it appears right in front of you.
 */
public class PayasoEntity extends HauntEntity {
	public static final int ACT_HIDDEN = 0, ACT_STALK = 1, ACT_FRENZY = 2, ACT_LAUGH = 3;
	private int phaseTimer = 500;
	private boolean hidden = true;
	private int musicCooldown = 0;
	private int balloonCooldown = 120;
	private int laughTimer;

	public PayasoEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 110.0)
				.add(Attributes.MOVEMENT_SPEED, 0.27)
				.add(Attributes.ATTACK_DAMAGE, 8.0)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.7);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.4, true));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.6));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 24.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
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
		if (this.isWeakened()) {
			setHidden(false);
			this.setAction(ACT_STALK);
			return;
		}
		if (laughTimer > 0 && --laughTimer == 0) {
			this.setAction(hidden ? ACT_HIDDEN : ACT_FRENZY);
		}
		LivingEntity target = this.getTarget();
		if (hidden) {
			if (--musicCooldown <= 0) {
				musicCooldown = 230;
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.PAYASO_MUSICBOX, SoundSource.HOSTILE, 2.2F, 1.0F);
			}
			if (target != null && --balloonCooldown <= 0) {
				balloonCooldown = 180 + this.random.nextInt(160);
				spawnBalloon(level, target);
			}
		}
		if (--phaseTimer <= 0) {
			if (hidden && target != null) {
				ambush(level, target);
			} else {
				setHidden(true);
				phaseTimer = 400 + this.random.nextInt(300);
				this.setAction(ACT_HIDDEN);
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.PAYASO_LAUGH, SoundSource.HOSTILE, 2.0F, 0.8F);
			}
		}
	}

	private void setHidden(boolean h) {
		this.hidden = h;
		this.setInvisible(h);
	}

	/** The music stops. Then it is right in front of you. */
	private void ambush(ServerLevel level, LivingEntity target) {
		setHidden(false);
		phaseTimer = 260 + this.random.nextInt(140);
		Vec3 look = target.getLookAngle();
		Vec3 front = target.position().add(look.x * 2.6, 0, look.z * 2.6);
		if (!this.teleportNear(front, 0.0, 1.0)) {
			this.teleportBehind(target, 3.0);
		}
		this.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, target.getEyePosition());
		this.setAction(ACT_LAUGH);
		laughTimer = 25;
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.PAYASO_LAUGH, SoundSource.HOSTILE, 3.0F, 1.0F);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.PAYASO_HONK, SoundSource.HOSTILE, 2.0F, 1.0F);
		if (target instanceof ServerPlayer p && this.isWatchedBy(p, 0.35)) {
			Fx.jumpscare(p, "payaso");
			SanityManager.add(p, -15.0F);
		}
	}

	private void spawnBalloon(ServerLevel level, LivingEntity target) {
		BalloonEntity balloon = ModEntities.BALLOON.create(level, EntitySpawnReason.EVENT);
		if (balloon == null) {
			return;
		}
		Vec3 look = target.getLookAngle();
		double a = this.random.nextDouble() * Math.PI * 2;
		double x = target.getX() + look.x * 7 + Math.cos(a) * 3;
		double z = target.getZ() + look.z * 7 + Math.sin(a) * 3;
		balloon.snapTo(x, target.getY() + 0.5, z, 0, 0);
		level.addFreshEntity(balloon);
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (hidden) {
			setHidden(false);
			phaseTimer = 200;
			this.setAction(ACT_FRENZY);
		}
		return super.hurtServer(level, source, amount);
	}

	@Override
	public boolean doHurtTarget(ServerLevel level, net.minecraft.world.entity.Entity target) {
		this.playSound(ModSounds.PAYASO_HONK, 1.5F, 0.8F);
		return super.doHurtTarget(level, target);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.PAYASO_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.PAYASO_DEATH;
	}
}
