package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
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
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Lucia, la Poseida. Climbs walls and ceilings, crawls belly-up when hunting, lifts hunters into the air.
 * Cannot be jarred: once weakened she must be exorcised with the Libro de Rituales.
 */
public class PoseidaEntity extends HauntEntity {
	public static final int ACT_IDLE = 0, ACT_CRAWL = 1, ACT_EXORCISM = 2, ACT_HEADSPIN = 3;
	public static final int EXORCISM_TICKS = 260;
	private static final EntityDataAccessor<Boolean> CLIMBING = SynchedEntityData.defineId(PoseidaEntity.class, EntityDataSerializers.BOOLEAN);
	private int voiceCooldown = 100;
	private int levitateCooldown = 200;
	private int exorcism;
	private int lastExorcismTick;
	private final ServerBossEvent exorcismBar = new ServerBossEvent(Component.translatable("deadline.boss.exorcism"), BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10);

	public PoseidaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.exorcismBar.setVisible(false);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 100.0)
				.add(Attributes.MOVEMENT_SPEED, 0.32)
				.add(Attributes.ATTACK_DAMAGE, 6.0)
				.add(Attributes.FOLLOW_RANGE, 40.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.6);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(CLIMBING, false);
	}

	@Override
	protected PathNavigation createNavigation(Level level) {
		return new WallClimberNavigation(this, level);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25, true));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 16.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	public boolean isClimbing() {
		return this.entityData.get(CLIMBING);
	}

	@Override
	public boolean onClimbable() {
		return this.isClimbing() && !this.isWeakened();
	}

	@Override
	public boolean requiresExorcism() {
		return true;
	}

	public float exorcismProgress() {
		return exorcism / (float) EXORCISM_TICKS;
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
		this.entityData.set(CLIMBING, this.horizontalCollision);
		if (this.isWeakened()) {
			tickBound(level);
			return;
		}
		LivingEntity target = this.getTarget();
		if (target == null || this.isStunned()) {
			this.setAction(ACT_IDLE);
			if (--voiceCooldown <= 0) {
				voiceCooldown = 200 + this.random.nextInt(200);
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_GIGGLE, SoundSource.HOSTILE, 1.5F, 1.0F);
			}
			return;
		}
		double dist = this.distanceTo(target);
		if (this.action() != ACT_HEADSPIN) {
			this.setAction(dist > 3.5 ? ACT_CRAWL : ACT_IDLE);
		}
		if (this.tickCount % 40 == 0 && this.action() == ACT_CRAWL && this.random.nextInt(3) == 0) {
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_CRACK, SoundSource.HOSTILE, 1.4F, 0.8F + this.random.nextFloat() * 0.4F);
		}
		if (--voiceCooldown <= 0) {
			voiceCooldown = 140 + this.random.nextInt(160);
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_DEMON, SoundSource.HOSTILE, 2.2F, 1.0F);
			if (!this.isWatchedBy(target, 0.3) && this.random.nextBoolean()) {
				this.setAction(ACT_HEADSPIN);
				this.stun(30);
			}
		}
		if (this.action() == ACT_HEADSPIN && !this.isStunned()) {
			this.setAction(ACT_CRAWL);
		}
		if (--levitateCooldown <= 0 && dist < 10 && this.hasLineOfSight(target)) {
			levitateCooldown = 360 + this.random.nextInt(240);
			target.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 45, 1));
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_SCREAM, SoundSource.HOSTILE, 2.5F, 1.0F);
			if (target instanceof ServerPlayer p) {
				Fx.shake(p, 0.8F, 40);
				SanityManager.add(p, -8.0F);
			}
		}
	}

	/** Weakened: she floats, bound, and the exorcism can begin. */
	private void tickBound(ServerLevel level) {
		this.setAction(ACT_EXORCISM);
		this.setNoGravity(true);
		this.getNavigation().stop();
		double hover = Math.sin(this.tickCount * 0.08) * 0.02;
		if (this.level().getBlockState(this.blockPosition().below(2)).isAir()) {
			this.setDeltaMovement(0, hover - 0.01, 0);
		} else {
			this.setDeltaMovement(0, 0.03 + hover, 0);
		}
		boolean chanting = this.tickCount - lastExorcismTick < 10;
		if (!chanting && exorcism > 0 && this.tickCount % 2 == 0) {
			exorcism--;
		}
		exorcismBar.setProgress(Math.min(1.0F, exorcismProgress()));
		exorcismBar.setVisible(exorcism > 0);
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(this) < 40 * 40) {
				exorcismBar.addPlayer(p);
			} else {
				exorcismBar.removePlayer(p);
			}
		}
		if (chanting && this.tickCount % 50 == 0) {
			poltergeist(level);
		}
	}

	/** Called every tick a hunter chants the rite nearby. */
	public void chant(ServerPlayer player) {
		if (!this.isWeakened() || !(this.level() instanceof ServerLevel level)) {
			return;
		}
		lastExorcismTick = this.tickCount;
		exorcism++;
		if (exorcism % 40 == 0) {
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_DEMON, SoundSource.HOSTILE, 2.5F, 0.7F);
			Fx.shake(player, 0.5F + exorcismProgress(), 20);
		}
		if (exorcism >= EXORCISM_TICKS) {
			finishExorcism(level, player);
		}
	}

	private void poltergeist(ServerLevel level) {
		int roll = this.random.nextInt(4);
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(this) > 20 * 20) {
				continue;
			}
			switch (roll) {
				case 0 -> {
					Vec3 push = p.position().subtract(this.position()).normalize().scale(1.2);
					p.push(push.x, 0.4, push.z);
					p.hurtMarked = true;
				}
				case 1 -> Fx.flash(p, 0.7F);
				case 2 -> {
					Fx.shake(p, 1.5F, 30);
					SanityManager.add(p, -5.0F);
				}
				default -> Fx.staticNoise(p, 0.8F, 30);
			}
		}
		if (roll == 3) {
			MunecaEntity doll = ModEntities.MUNECA.create(level, EntitySpawnReason.EVENT);
			if (doll != null) {
				doll.snapTo(this.getX() + this.random.nextInt(5) - 2, this.getY() - 1, this.getZ() + this.random.nextInt(5) - 2, this.random.nextFloat() * 360, 0);
				doll.setSiteIndex(this.siteIndex);
				level.addFreshEntity(doll);
			}
		}
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.POSEIDA_SCREAM, SoundSource.HOSTILE, 2.0F, 0.7F + this.random.nextFloat() * 0.3F);
	}

	private void finishExorcism(ServerLevel level, ServerPlayer player) {
		LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level, EntitySpawnReason.EVENT);
		if (bolt != null) {
			bolt.snapTo(this.getX(), this.getY(), this.getZ());
			bolt.setVisualOnly(true);
			level.addFreshEntity(bolt);
		}
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.RITUAL_COMPLETE, SoundSource.PLAYERS, 3.0F, 1.0F);
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(this) < 40 * 40) {
				Fx.flash(p, 1.0F);
			}
		}
		exorcismBar.removeAllPlayers();
		this.banish(level, player);
	}

	@Override
	public void remove(RemovalReason reason) {
		exorcismBar.removeAllPlayers();
		super.remove(reason);
	}

	@Override
	public float fearAura() {
		return 0.8F;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return ModSounds.POSEIDA_GIGGLE;
	}

	@Override
	public int getAmbientSoundInterval() {
		return 300;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.POSEIDA_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.POSEIDA_DEATH;
	}
}
