package com.deadline.entity;

import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LeapAtTargetGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** El Wendigo: hunts the Bosque Negro, mimics the voices of the lost, and fears fire. */
public class WendigoEntity extends HauntEntity {
	public static final int ACT_IDLE = 0, ACT_HUNT = 1, ACT_SCREAM = 2, ACT_FLEE = 3;
	private int mimicCooldown = 200;
	private int screamTimer;
	private boolean announced;

	public WendigoEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 140.0)
				.add(Attributes.MOVEMENT_SPEED, 0.31)
				.add(Attributes.ATTACK_DAMAGE, 11.0)
				.add(Attributes.FOLLOW_RANGE, 64.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
				.add(Attributes.STEP_HEIGHT, 1.5);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(1, new FleeFireGoal(this));
		this.goalSelector.addGoal(2, new LeapAtTargetGoal(this, 0.5F));
		this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.35, true));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 32.0F));
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
		if (screamTimer > 0 && --screamTimer == 0) {
			this.setAction(ACT_HUNT);
		}
		LivingEntity target = this.getTarget();
		if (target == null) {
			announced = false;
			if (screamTimer == 0 && this.action() != ACT_FLEE) {
				this.setAction(ACT_IDLE);
			}
			return;
		}
		double dist = this.distanceTo(target);
		if (!announced && dist < 24) {
			announced = true;
			screamTimer = 30;
			this.setAction(ACT_SCREAM);
			this.stun(20);
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.WENDIGO_SCREAM, SoundSource.HOSTILE, 3.5F, 1.0F);
			for (ServerPlayer p : level.players()) {
				if (p.distanceToSqr(this) < 30 * 30) {
					Fx.shake(p, 1.2F, 25);
				}
			}
		} else if (screamTimer == 0 && this.action() != ACT_FLEE) {
			this.setAction(ACT_HUNT);
		}
		if (--mimicCooldown <= 0) {
			mimicCooldown = 260 + this.random.nextInt(300);
			if (dist > 12) {
				// A voice calling for help, from the trees, from where the hunter can't see.
				level.playSound(null, this.getX(), this.getEyeY(), this.getZ(), ModSounds.WENDIGO_MIMIC, SoundSource.HOSTILE, 3.0F, 1.0F);
			} else {
				level.playSound(null, this.getX(), this.getEyeY(), this.getZ(), ModSounds.WENDIGO_GROWL, SoundSource.HOSTILE, 2.0F, 0.9F);
			}
		}
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (source.is(DamageTypeTags.IS_FIRE)) {
			amount *= 3.0F;
			this.setAction(ACT_FLEE);
		}
		return super.hurtServer(level, source, amount);
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		this.playSound(ModSounds.WENDIGO_STEP, 0.6F, 0.8F + this.random.nextFloat() * 0.3F);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return ModSounds.WENDIGO_GROWL;
	}

	@Override
	public int getAmbientSoundInterval() {
		return 240;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.WENDIGO_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.WENDIGO_DEATH;
	}

	/** Runs from burning flares and fire. */
	static class FleeFireGoal extends net.minecraft.world.entity.ai.goal.Goal {
		private final WendigoEntity mob;
		private Vec3 fleeTo;

		FleeFireGoal(WendigoEntity mob) {
			this.mob = mob;
			this.setFlags(java.util.EnumSet.of(Flag.MOVE));
		}

		@Override
		public boolean canUse() {
			FlareEntity flare = nearestFlare();
			if (flare == null) {
				return false;
			}
			Vec3 away = mob.position().subtract(flare.position()).normalize().scale(14);
			fleeTo = mob.position().add(away);
			return true;
		}

		private FlareEntity nearestFlare() {
			for (FlareEntity f : mob.level().getEntitiesOfClass(FlareEntity.class, mob.getBoundingBox().inflate(10))) {
				if (f.isBurning()) {
					return f;
				}
			}
			return null;
		}

		@Override
		public void start() {
			mob.setAction(ACT_FLEE);
			mob.getNavigation().moveTo(fleeTo.x, fleeTo.y, fleeTo.z, 1.5);
			mob.playSound(ModSounds.WENDIGO_HURT, 2.0F, 1.3F);
		}

		@Override
		public boolean canContinueToUse() {
			return !mob.getNavigation().isDone() && nearestFlare() != null;
		}

		@Override
		public void stop() {
			mob.setAction(ACT_HUNT);
		}
	}
}
