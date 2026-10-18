package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
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
import net.minecraft.world.level.LightLayer;

/** Sor Agonia only moves in darkness. Light (flashlight, candles, flares) freezes and burns her. */
public class MonjaEntity extends HauntEntity {
	public static final int ACT_IDLE = 0, ACT_HUNT = 1, ACT_BURN = 2, ACT_SCREAM = 3;
	private int teleportCooldown = 240;
	private int whisperCooldown = 120;
	private int screamTimer;

	public MonjaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 110.0)
				.add(Attributes.MOVEMENT_SPEED, 0.3)
				.add(Attributes.ATTACK_DAMAGE, 8.0)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.9);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2, true));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.5));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 24.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	public static int lightAt(Level level, BlockPos pos) {
		return Math.max(level.getBrightness(LightLayer.BLOCK, pos), level.getBrightness(LightLayer.BLOCK, pos.above()));
	}

	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level) || this.isWeakened()) {
			return;
		}
		if (screamTimer > 0) {
			screamTimer--;
		}
		int light = lightAt(level, this.blockPosition());
		if (light >= 8) {
			// Caught in the light: frozen, hissing, burning.
			this.stun(6);
			this.setAction(ACT_BURN);
			if (this.tickCount % 6 == 0) {
				level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 1.8, this.getZ(), 4, 0.25, 0.3, 0.25, 0.02);
			}
			if (this.tickCount % 30 == 0) {
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_HISS, SoundSource.HOSTILE, 1.6F, 0.9F + this.random.nextFloat() * 0.2F);
				if (!this.isAnchored()) {
					this.hurtServer(level, this.damageSources().magic(), 2.0F);
				}
			}
			return;
		}
		LivingEntity target = this.getTarget();
		this.setAction(screamTimer > 0 ? ACT_SCREAM : (target != null ? ACT_HUNT : ACT_IDLE));
		if (--whisperCooldown <= 0) {
			whisperCooldown = 160 + this.random.nextInt(200);
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_WHISPER, SoundSource.HOSTILE, 1.8F, 1.0F);
		}
		if (target == null) {
			return;
		}
		if (--teleportCooldown <= 0 && lightAt(level, target.blockPosition()) < 6 && !this.isWatchedBy(target, 0.3)) {
			teleportCooldown = 220 + this.random.nextInt(240);
			if (this.teleportBehind(target, 2.5)) {
				screamTimer = 20;
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_SCREAM, SoundSource.HOSTILE, 2.5F, 1.0F);
				if (target instanceof ServerPlayer p) {
					Fx.shake(p, 0.7F, 15);
				}
			}
		}
	}

	@Override
	public float holyWeakness() {
		return 1.6F;
	}

	@Override
	public float fearAura() {
		return 0.75F;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.MONJA_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.MONJA_DEATH;
	}
}
