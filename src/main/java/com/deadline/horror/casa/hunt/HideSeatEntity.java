package com.deadline.horror.casa.hunt;

import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * The invisible seat a hunter "sits" on inside a hiding place ({@link HideSpots}): it holds him still with his eyes
 * at the slats (or the gap under the bed), lets him turn his head 70 degrees each way from the way out, and puts him
 * back in front of the hiding place when he sneaks out. Never saved; gone as soon as it is empty.
 */
public class HideSeatEntity extends Entity {
	/** Degrees the hidden hunter may look away from the way out (yaw) and up / down (pitch). */
	public static final float LOOK_YAW = 70F, LOOK_PITCH = 55F;

	private Vec3 out;

	public HideSeatEntity(EntityType<? extends HideSeatEntity> type, Level level) {
		super(type, level);
		this.setNoGravity(true);
		this.noPhysics = true;
	}

	void setup(Vec3 exit) {
		this.out = exit;
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
	}

	@Override
	public void tick() {
		super.tick();
		this.setDeltaMovement(Vec3.ZERO);
		if (!this.level().isClientSide() && this.tickCount > 3 && this.getPassengers().isEmpty()) {
			HideSpots.seatEmptied(this);
			this.discard();
		}
	}

	/** The rider sits exactly at the seat (its position is computed from the eye height by HideSpots). */
	@Override
	protected Vec3 getPassengerAttachmentPoint(Entity passenger, EntityDimensions dimensions, float partialTick) {
		return Vec3.ZERO;
	}

	@Override
	public Vec3 getDismountLocationForPassenger(LivingEntity passenger) {
		return this.out != null ? this.out : super.getDismountLocationForPassenger(passenger);
	}

	/** Runs on the client as the mouse turns the head (Entity.turn): keeps the look within the slats. */
	@Override
	public void onPassengerTurned(Entity passenger) {
		float yaw = this.getYRot();
		float rel = Mth.wrapDegrees(passenger.getYRot() - yaw);
		float clamped = Mth.clamp(rel, -LOOK_YAW, LOOK_YAW);
		passenger.yRotO += clamped - rel;
		passenger.setYRot(passenger.getYRot() + clamped - rel);
		passenger.setYHeadRot(passenger.getYRot());
		float pitch = Mth.clamp(passenger.getXRot(), -LOOK_PITCH, LOOK_PITCH);
		passenger.xRotO += pitch - passenger.getXRot();
		passenger.setXRot(pitch);
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPickable() {
		return false;
	}

	@Override
	public boolean shouldBeSaved() {
		return false;
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
	}
}
