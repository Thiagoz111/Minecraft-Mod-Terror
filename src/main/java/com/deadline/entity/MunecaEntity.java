package com.deadline.entity;

import com.deadline.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/** A porcelain doll that only moves when nobody is looking at it. */
public class MunecaEntity extends HauntEntity {
	/**
	 * C, scripted only (Ofelia in the 1961 room): sitting, legs out, perfectly still; {@link #ACT_SIT_TURN} = the same,
	 * and the head comes all the way round (180 degrees) while the body does not move.
	 */
	public static final int ACT_SIT = 2, ACT_SIT_TURN = 3;
	private boolean frozen;
	private boolean frozenSetNoAi;

	public MunecaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 24.0)
				.add(Attributes.MOVEMENT_SPEED, 0.42)
				.add(Attributes.ATTACK_DAMAGE, 3.0)
				.add(Attributes.FOLLOW_RANGE, 32.0);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true));
		this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	public boolean isFrozen() {
		return this.action() == 1;
	}

	@Override
	public void tick() {
		super.tick();
		if (HauntEntity.SHOWCASE) {
			return;
		}
		if (this.scripted && (this.action() == ACT_SIT || this.action() == ACT_SIT_TURN)) {
			return;  // a seated set-piece doll: the script owns the pose (no freezing when watched)
		}
		if (!(this.level() instanceof ServerLevel level) || this.isStunned()) {
			return;
		}
		boolean seen = false;
		for (ServerPlayer p : level.players()) {
			if (!p.isSpectator() && p.distanceToSqr(this) < 40 * 40 && this.isWatchedBy(p, 0.25)) {
				seen = true;
				break;
			}
		}
		if (seen && !frozen) {
			frozen = true;
			this.setAction(1);
			this.getNavigation().stop();
			if (!this.isNoAi()) {
				this.setNoAi(true);
				frozenSetNoAi = true;
			}
		} else if (!seen && frozen) {
			frozen = false;
			this.setAction(0);
			if (frozenSetNoAi) {
				this.setNoAi(false);
				frozenSetNoAi = false;
			}
			if (this.random.nextInt(3) == 0) {
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MUNECA_CREAK, SoundSource.HOSTILE, 1.0F, 1.0F + this.random.nextFloat() * 0.3F);
			}
		}
	}

	@Override
	public boolean doHurtTarget(ServerLevel level, Entity target) {
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MUNECA_GIGGLE, SoundSource.HOSTILE, 1.4F, 1.0F);
		return super.doHurtTarget(level, target);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return this.frozen ? null : ModSounds.MUNECA_GIGGLE;
	}

	@Override
	public int getAmbientSoundInterval() {
		return 360;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.MUNECA_CREAK;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.MUNECA_GIGGLE;
	}
}
