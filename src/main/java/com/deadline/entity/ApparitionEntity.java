package com.deadline.entity;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/**
 * A ghost that is only ever staged by the director: the choir girls, the Mother Superior, Clara. No AI, no collision,
 * cannot be hurt, never drains sanity by itself. Poses are synced with {@link #setAction(int)}, looks with
 * {@link #setVariant(int)}.
 */
public class ApparitionEntity extends HauntEntity {
	public static final int POSE_STAND = 0, POSE_SING = 1, POSE_SIT = 2, POSE_FACE_WALL = 3, POSE_POINT = 4, POSE_COVER_EARS = 5,
			POSE_HEAD_180 = 6, POSE_RUN = 7, POSE_PEEK = 8, POSE_TURN = 9, POSE_WRITE = 10, POSE_STARE = 11, POSE_RISE = 12, POSE_BOW = 13,
			POSE_FREED = 14;

	public ApparitionEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.scripted = true;
		this.setNoAi(true);
		this.noPhysics = true;
		this.setInvulnerable(true);
		this.setNoGravity(true);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 100.0).add(Attributes.MOVEMENT_SPEED, 0.0);
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean isPickable() {
		return false;
	}

	@Override
	public float fearAura() {
		return 0F;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return null;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return null;
	}
}
