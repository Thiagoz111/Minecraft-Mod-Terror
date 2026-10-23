package com.deadline.casa;

import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * The Morales family (Marta, Jorge, the Nona, Toti): actors staged by the Casa Morales script. Like
 * {@link com.deadline.entity.ApparitionEntity} they have no AI of their own, cannot be hurt or pushed and are
 * {@code scripted}; unlike the ghosts they are flesh and blood: gravity and block collision (a shoved Jorge falls into
 * the pelopincho and floats there on his back).
 * <ul>
 *   <li>Pose = {@link #setAction(int)} with the {@code POSE_*} ids below (one set for the four; each model maps the ids
 *   it has and shows its default for the rest). Look = {@link #setVariant(int)}: {@link #LOOK_NORMAL} or
 *   {@link #LOOK_POSSESSED} (Jorge 'poseido', the Nona 'poseida'; Marta and Toti have a single look).</li>
 *   <li>{@link #walkTo(Vec3, double)} walks on the ground navigation: the AI is switched on for the walk only and off
 *   again on arrival ({@link #hasArrived()}); a walk that cannot progress for 3 s snaps to the target.</li>
 *   <li>{@link #setFloating(boolean)}: no gravity, a gentle bob in place (the Nona in her rocker in the 1961 room);
 *   {@link #floatTo(Vec3, int)} glides there.</li>
 *   <li>While standing, the head follows the nearest hunter (or {@link #watch(Entity)}); the body keeps the yaw the
 *   script gave it ({@link #face(Vec3)}, or the yaw set by {@code Props.spawn / place}): vanilla's body control is
 *   overridden on both sides, so a rocker, a grill or a wardrobe door posed against the body stays put.</li>
 *   <li>{@link #say(Run, String)} plays a voice line at the mouth and moves the jaw for its length
 *   ({@link #talk(int)}).</li>
 *   <li>{@link #shove(Vec3)}: a scripted physical shove (vanilla {@code push} / knockback are left alone).</li>
 * </ul>
 * <p><b>P6 integration notes</b> (not fixable inside P1's files):
 * <ul>
 *   <li>The family is a {@link HauntEntity}, so everything that does {@code instanceof HauntEntity} treats them as
 *   ghosts: EMF 5 next to Marta (EmfItem), the flashlight flickering within 12 blocks (FlashlightLights), the camera
 *   flash stunning them and giving evidence (CameraItem; then they shake via HauntRenderer.isShaking), the crucifix
 *   shoving and stunning them (CrucifixItem), the spirit box answering (SpiritBoxItem), and salt lines blocking them
 *   (SaltLineBlock: a {@link #walkTo} through a salt circle stalls and snaps after 3 s). Exclude
 *   {@code e instanceof FamilyEntity f && !f.isPossessed()} in those six, or add an overridable
 *   {@code HauntEntity.isSpectral()} and override it here with {@code isPossessed()}.</li>
 *   <li>Peaceful: as a {@link Monster} they may be discarded on Peaceful. Probe 1.21.11 (api-probe) for
 *   {@code Monster/Mob.shouldDespawnInPeaceful} vs {@code EntityType.Builder.notInPeaceful} before overriding
 *   anything.</li>
 * </ul>
 */
public class FamilyEntity extends HauntEntity {
	// ------------------------------------------------------------------ poses (names = the model poses of ent_<key>.py)
	/** Everyone's default: Marta 'idle_nervous', Jorge 'idle', the Nona 'stand_walker', Toti playing standing (rest). */
	public static final int POSE_IDLE = 0;
	/** Marta 'point' ("¡Por la ventana!"), Jorge 'point' ("es la humedad"). Face the target first ({@link #face}). */
	public static final int POSE_POINT = 1;
	/** Marta 'scared' ("Ay, Dios mío"): fast blend, trembles. */
	public static final int POSE_SCARED = 2;
	/** Marta 'show_phone' (casa.ya_llego): the phone held up beside her face, screen to the player. */
	public static final int POSE_SHOW_PHONE = 3;
	/** Marta 'show_phone' with the 'scared' jaw and brows on top ("...Lucía no tiene celular"). */
	public static final int POSE_SHOW_PHONE_SCARED = 4;
	/** Marta 'throw' with the chorizo in her fist; any other pose afterwards = the release (snap, chorizo hidden). */
	public static final int POSE_THROW = 5;
	/** Marta 'throw' with the bread roll instead of the chorizo. */
	public static final int POSE_THROW_BREAD = 6;
	/** Marta 'shout' ("¡TIRALE ALGO!", "¡Te dije que no comas tanto chorizo!"). */
	public static final int POSE_SHOUT = 7;
	/** Jorge 'grill_flip' (possessed at the grill, bare hands): the 16-tick flip loop. */
	public static final int POSE_GRILL_FLIP = 8;
	/** Jorge 'knife_conduct': arms up in a V, the tongs as the baton, a downbeat every 10 ticks (launch on it). */
	public static final int POSE_KNIFE_CONDUCT = 9;
	/** Jorge 'limp_fall': falls back like a sack (8 ticks); afloat in water (he floats instead of sinking). */
	public static final int POSE_LIMP_FALL = 10;
	/** Jorge 'carry_bag': the charcoal sack on his belly, tongs hidden. */
	public static final int POSE_CARRY_BAG = 11;
	/** The Nona 'stand_walker' (same as {@link #POSE_IDLE} for her). */
	public static final int POSE_STAND_WALKER = 12;
	/** The Nona 'offer_mate' ("¿Querés un mate, nene?"): the gourd held out. */
	public static final int POSE_OFFER_MATE = 13;
	/** The Nona 'knit_sit': in the rocker, knitting, rocking slowly. */
	public static final int POSE_KNIT_SIT = 14;
	/** The Nona 'stand_no_walker': furious, fists on her hips (casa.chancleta). */
	public static final int POSE_STAND_NO_WALKER = 15;
	/** The Nona 'throw_chancleta': the slipper cocked; any other pose afterwards = the release (snap, slipper hidden). */
	public static final int POSE_THROW_CHANCLETA = 16;
	/** The Nona 'float_rock': floating in the rocker in the 1961 room (use with {@link #setFloating(boolean)}). */
	public static final int POSE_FLOAT_ROCK = 17;
	/** The Nona 'yarn_cast': arms flung out, the red yarn shooting from her hands (floating, seated). */
	public static final int POSE_YARN_CAST = 18;
	/** The Nona 'scream_dentures': the jaw dislocated, the dentures floating (shown with {@link #LOOK_POSSESSED}). */
	public static final int POSE_SCREAM_DENTURES = 19;
	/** The Nona 'sew_calm': seated, hands over Ofelia; from a floating pose she comes down slowly (~60 ticks). */
	public static final int POSE_SEW_CALM = 20;
	/** Toti 'crouch_closet': crouched in the wardrobe, absorbed in the ranked match. */
	public static final int POSE_CROUCH_CLOSET = 21;
	/** Toti 'slam': shoves the wardrobe door shut without looking ("¡Callate, Chori!"); back to crouch after. */
	public static final int POSE_SLAM = 22;
	/** Toti 'stand' (breakfast, "¿Qué me perdí?"): upright, shrugging, mic swung up. */
	public static final int POSE_STAND = 23;
	/**
	 * Marta's hand-over beat ("¡Tomá!"): the chorizo held out in her right fist toward whoever she faces (face them
	 * first); any other pose afterwards = handed over (chorizo hidden: give the item then). The bread is not shown.
	 */
	public static final int POSE_HAND_OVER = 24;

	// ------------------------------------------------------------------ looks
	public static final int LOOK_NORMAL = 0, LOOK_POSSESSED = 1;

	// ------------------------------------------------------------------ tuning
	/** Horizontal distance that counts as "arrived". */
	private static final double ARRIVE = 0.3;
	/** Ticks without moving before a walk gives up and snaps to its target. */
	private static final int STUCK_TICKS = 60;
	/** Degrees per tick the body turns to the yaw the script gave it while standing. */
	private static final float BODY_TURN = 25F;
	/** Head tracking: range of the nearest hunter, max yaw / pitch off the body, degrees per tick. */
	private static final double WATCH_RANGE = 10.0;
	private static final float HEAD_YAW_MAX = 75F, HEAD_PITCH_MAX = 40F, HEAD_TURN = 9F, HEAD_TILT = 5F;
	/** A target further round than this (behind her) is ignored: the head returns to the front. */
	private static final float HEAD_GIVE_UP = 115F;
	/** Floating bob: amplitude (blocks) and speed (rad / tick). */
	private static final double BOB = 0.05, BOB_SPEED = 0.06;
	/** Distance (blocks) the Nona's walker rolls between two squeaks of its wheel. */
	private static final double SQUEAK_EVERY = 1.1;
	/** Ticks between two creaks of the rocker (one rock of the model: 2 pi / 0.08). */
	private static final int CREAK_EVERY = 79;

	private static final EntityDataAccessor<Boolean> FLOATING = SynchedEntityData.defineId(FamilyEntity.class, EntityDataSerializers.BOOLEAN);
	/** Game time until which the jaw talks (the client compares it with its own clock). */
	private static final EntityDataAccessor<Integer> TALK_UNTIL = SynchedEntityData.defineId(FamilyEntity.class, EntityDataSerializers.INT);

	/** Plays the walker squeak and the rocker creak on its own (set false if the script plays them). */
	public boolean propSounds = true;

	private Vec3 walkTarget;
	private double walkSpeed;
	private boolean walkDirect;
	private int walkStuck;
	private boolean arrived;

	private Vec3 floatAnchor;
	private Vec3 floatFrom;
	private Vec3 floatGoal;
	private Vec3 floatSet;
	private int floatT;
	private int floatDur;
	private int floatStart;

	private Entity watchTarget;
	private boolean watchPlayers = true;
	private double squeak;
	/** The body yaw this class last wrote (NaN before the first tick); see {@link #tick()}. */
	private float bodyYaw = Float.NaN;

	public FamilyEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.scripted = true;
		this.setNoAi(true);
		this.setInvulnerable(true);
		this.xpReward = 0;
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 100.0)
				.add(Attributes.MOVEMENT_SPEED, 0.25)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(FLOATING, false);
		builder.define(TALK_UNTIL, 0);
	}

	// ------------------------------------------------------------------ pose helpers (shared with the models)
	/** The Nona's seated poses: the rocker is shown and the walker hidden. */
	public static boolean seated(int pose) {
		return pose == POSE_KNIT_SIT || pose == POSE_FLOAT_ROCK || pose == POSE_YARN_CAST || pose == POSE_SCREAM_DENTURES
				|| pose == POSE_SEW_CALM;
	}

	/** The Nona has her walker in this pose (every standing pose but the furious one and the throw). */
	public static boolean walkerShown(int pose) {
		return !seated(pose) && pose != POSE_STAND_NO_WALKER && pose != POSE_THROW_CHANCLETA;
	}

	/** The Nona's poses that float the rocker off the floor (the 1961 room). */
	public static boolean floatPose(int pose) {
		return pose == POSE_FLOAT_ROCK || pose == POSE_YARN_CAST || pose == POSE_SCREAM_DENTURES;
	}

	public boolean isPossessed() {
		return this.variant() == LOOK_POSSESSED;
	}

	// ------------------------------------------------------------------ talking
	/** Moves the jaw for the next `ticks` ticks (a voice line playing somewhere). 0 stops it. */
	public void talk(int ticks) {
		this.entityData.set(TALK_UNTIL, ticks <= 0 ? 0 : (int) this.level().getGameTime() + ticks);
	}

	public boolean isTalking() {
		return this.entityData.get(TALK_UNTIL) - (int) this.level().getGameTime() > 0;
	}

	/** Plays a voice line (Run.say) from this actor's mouth with its subtitle, and talks for its length. */
	public int say(Run r, String lineId) {
		int ticks = r.say(lineId, this.getEyePosition());
		this.talk(ticks);
		return ticks;
	}

	// ------------------------------------------------------------------ facing / looking
	/** Turns the whole actor toward a point (the body follows in a few ticks; the head at once). */
	public void face(Vec3 target) {
		this.face((float) (Mth.atan2(target.z - this.getZ(), target.x - this.getX()) * Mth.RAD_TO_DEG) - 90F);
	}

	public void face(float yaw) {
		this.setYRot(yaw);
		this.setYHeadRot(yaw);
	}

	/** The head follows this entity (null: back to the nearest hunter, if {@link #watchPlayers(boolean)} is on). */
	public void watch(Entity target) {
		this.watchTarget = target;
	}

	/** Whether the head follows the nearest hunter when no {@link #watch(Entity)} target is set (default on). */
	public void watchPlayers(boolean on) {
		this.watchPlayers = on;
	}

	// ------------------------------------------------------------------ walking
	/**
	 * Walks to a point on the ground navigation at `speed` (a multiplier of the 0.25 movement speed: 0.5 a shuffle,
	 * 0.8 a calm walk, 1.0 brisk, 1.4 a hurry). The AI is on only while walking. Returns false when no path was found
	 * (it then walks straight at it and snaps there if it gets stuck). Cancels floating.
	 */
	public boolean walkTo(Vec3 target, double speed) {
		if (this.level().isClientSide() || target == null) {
			return false;
		}
		if (this.isFloating()) {
			this.setFloating(false);
		}
		this.walkTarget = target;
		this.walkSpeed = speed;
		this.walkStuck = 0;
		this.walkDirect = false;
		this.arrived = false;
		this.setNoAi(false);
		boolean path = this.getNavigation().moveTo(target.x, target.y, target.z, speed);
		if (!path) {
			this.walkDirect = true;
		}
		return path;
	}

	public boolean isWalking() {
		return this.walkTarget != null;
	}

	/** True once the last {@link #walkTo} reached its target (or snapped to it); false while walking. */
	public boolean hasArrived() {
		return this.arrived;
	}

	/** Stops a walk where it is (AI off again). */
	public void stopWalking() {
		if (this.walkTarget != null) {
			this.finishWalk(false);
			this.arrived = false;
		}
	}

	private void tickWalk() {
		Vec3 target = this.walkTarget;
		if (this.isStunned()) {
			return;  // HauntEntity froze the AI for the stun; it resumes below once the stun is over
		}
		if (this.isNoAi()) {
			this.setNoAi(false);
			if (!this.walkDirect && !this.getNavigation().moveTo(target.x, target.y, target.z, this.walkSpeed)) {
				this.walkDirect = true;
			}
		}
		double dx = target.x - this.getX();
		double dz = target.z - this.getZ();
		double d = Math.sqrt(dx * dx + dz * dz);
		if (d < ARRIVE && Math.abs(target.y - this.getY()) < 1.25) {
			this.finishWalk(false);
			return;
		}
		if (!this.walkDirect && this.getNavigation().isDone()) {
			this.walkDirect = true;  // the path ends on the target's block: the last stretch goes straight to the point
		}
		if (this.walkDirect) {
			this.getMoveControl().setWantedPosition(target.x, target.y, target.z, this.walkSpeed);
		}
		double mx = this.getX() - this.xo;
		double mz = this.getZ() - this.zo;
		if (mx * mx + mz * mz > 1.0E-4) {
			this.walkStuck = 0;
		} else if (++this.walkStuck > STUCK_TICKS) {
			this.finishWalk(true);
		}
	}

	private void finishWalk(boolean snap) {
		Vec3 target = this.walkTarget;
		this.walkTarget = null;
		this.getNavigation().stop();
		this.setSpeed(0F);
		this.setZza(0F);
		if (snap && target != null) {
			this.teleportTo(target.x, target.y, target.z);
		}
		Vec3 v = this.getDeltaMovement();
		this.setDeltaMovement(0.0, Math.min(0.0, v.y), 0.0);
		if (this.scripted) {
			this.setNoAi(true);
		}
		this.arrived = true;
	}

	/**
	 * A scripted physical shove (Jorge falling back into the pool): stops any walk and REPLACES the velocity, which is
	 * then integrated with gravity and collision. Named apart from vanilla {@code push(Vec3)}, which explosions and
	 * wind charges call to ADD knockback.
	 */
	public void shove(Vec3 velocity) {
		this.stopWalking();
		this.setDeltaMovement(velocity);
	}

	// ------------------------------------------------------------------ floating
	/** No gravity and a gentle bob where it is now (the Nona in the rocker). Off: falls back to the floor. */
	public void setFloating(boolean on) {
		this.entityData.set(FLOATING, on);
		this.setNoGravity(on);
		this.setDeltaMovement(Vec3.ZERO);
		this.floatGoal = null;
		this.floatSet = null;
		if (on) {
			this.stopWalking();
			this.floatAnchor = this.position();
			this.floatStart = this.tickCount;
		}
	}

	public boolean isFloating() {
		return this.entityData.get(FLOATING);
	}

	/** Glides (eased) to a point over `ticks` while floating (starts floating if needed): rise, drift, come down. */
	public void floatTo(Vec3 target, int ticks) {
		if (!this.isFloating()) {
			this.setFloating(true);
		}
		this.floatFrom = this.floatAnchor != null ? this.floatAnchor : this.position();
		this.floatGoal = target;
		this.floatT = 0;
		this.floatDur = Math.max(1, ticks);
	}

	private void tickFloat() {
		if (this.floatSet != null && this.position().distanceToSqr(this.floatSet) > 1.0E-4) {
			this.floatAnchor = this.position();  // moved by the script (Props.place): float there
			this.floatGoal = null;
		}
		if (this.floatAnchor == null) {
			this.floatAnchor = this.position();
		}
		if (this.floatGoal != null) {
			this.floatT++;
			float u = Math.min(1F, this.floatT / (float) this.floatDur);
			this.floatAnchor = this.floatFrom.lerp(this.floatGoal, u * u * (3F - 2F * u));
			if (u >= 1F) {
				this.floatGoal = null;
			}
		}
		double bob = BOB * Math.sin((this.tickCount - this.floatStart) * BOB_SPEED);
		this.setDeltaMovement(Vec3.ZERO);
		this.setPos(this.floatAnchor.x, this.floatAnchor.y + bob, this.floatAnchor.z);
		this.floatSet = this.position();
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		Vec3 before = this.position();
		if (this.yBodyRot != this.bodyYaw) {
			// first tick, or set from outside since the last one (Props.spawn / place, a load): start from it
			this.bodyYaw = this.yBodyRot;
		}
		super.tick();
		if (this.isNoAi()) {
			// standing: LivingEntity.tick() always runs tickHeadTurn -> BodyRotationControl.clientTick (both sides, AI off
			// or not), which swings the body round onto the head once it holds still. Overwrite it with our own yaw,
			// eased to the one the script gave (face()); yBodyRotO is copied from it at the start of the next tick.
			this.bodyYaw = Mth.approachDegrees(this.bodyYaw, this.getYRot(), BODY_TURN);
			this.yBodyRot = this.bodyYaw;
		} else {
			this.bodyYaw = this.yBodyRot;  // walking: the move control turns the body
		}
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		if (this.walkTarget != null) {
			this.tickWalk();
		}
		if (this.isFloating()) {
			this.tickFloat();
		} else if (this.isNoAi()) {
			this.tickPhysics(before);
		}
		this.tickHead(level);
		this.tickProps(level);
	}

	/** Gravity, friction and block collision while the AI is off (a NoAI mob gets none of them from vanilla). */
	private void tickPhysics(Vec3 before) {
		if (this.position().distanceToSqr(before) > 1.0E-6) {
			return;  // already moved this tick (by vanilla or a teleport)
		}
		Vec3 v = this.getDeltaMovement();
		double vx = v.x;
		double vy = v.y;
		double vz = v.z;
		if (this.isInWater()) {
			if (this.action() == POSE_LIMP_FALL) {
				// he floats on his back: the feet settle ~0.3 under the surface
				boolean deep = this.level().getFluidState(BlockPos.containing(this.getX(), this.getY() + 0.3, this.getZ())).is(FluidTags.WATER);
				vy = (vy + (deep ? 0.025 : -0.02)) * 0.7;
			} else {
				vy = (vy - 0.02) * 0.8;
			}
			vx *= 0.8;
			vz *= 0.8;
		} else {
			if (!this.isNoGravity()) {
				vy = (vy - 0.08) * 0.98;
			}
			double f = this.onGround() ? 0.546 : 0.91;
			vx *= f;
			vz *= f;
		}
		if (Math.abs(vx) < 0.003) {
			vx = 0.0;
		}
		if (Math.abs(vz) < 0.003) {
			vz = 0.0;
		}
		this.setDeltaMovement(vx, vy, vz);
		this.move(MoverType.SELF, this.getDeltaMovement());
	}

	/** Standing: the head turns to the watched entity / nearest hunter in front; walking: the look control. */
	private void tickHead(ServerLevel level) {
		Entity target = this.watchTarget;
		if (target != null && (target.isRemoved() || target.level() != level || target.distanceToSqr(this) > 32.0 * 32.0)) {
			target = null;
		}
		if (!this.isNoAi()) {
			if (target != null) {
				this.getLookControl().setLookAt(target, 30F, 30F);
			}
			return;
		}
		if (target == null && this.watchPlayers) {
			target = nearestHunter(level);
		}
		float body = this.yBodyRot;
		float yaw = body;
		float pitch = 0F;
		if (target != null) {
			Vec3 to = target.getEyePosition().subtract(this.getEyePosition());
			double h = Math.sqrt(to.x * to.x + to.z * to.z);
			float rel = Mth.wrapDegrees((float) (Mth.atan2(to.z, to.x) * Mth.RAD_TO_DEG) - 90F - body);
			if (Math.abs(rel) < HEAD_GIVE_UP) {
				yaw = body + Mth.clamp(rel, -HEAD_YAW_MAX, HEAD_YAW_MAX);
				pitch = Mth.clamp((float) -(Mth.atan2(to.y, h) * Mth.RAD_TO_DEG), -HEAD_PITCH_MAX, HEAD_PITCH_MAX);
			}
		}
		this.setYHeadRot(Mth.approachDegrees(this.getYHeadRot(), yaw, HEAD_TURN));
		this.setXRot(Mth.approach(this.getXRot(), pitch, HEAD_TILT));
	}

	private ServerPlayer nearestHunter(ServerLevel level) {
		ServerPlayer best = null;
		double bestD = WATCH_RANGE * WATCH_RANGE;
		for (ServerPlayer p : level.players()) {
			if (p.isSpectator()) {
				continue;
			}
			double d = p.distanceToSqr(this);
			if (d < bestD) {
				bestD = d;
				best = p;
			}
		}
		return best;
	}

	/** The Nona's walker squeaks as it rolls; her rocker creaks once per rock. */
	private void tickProps(ServerLevel level) {
		if (!this.propSounds || this.getType() != FamilyEntities.NONA) {
			return;
		}
		int a = this.action();
		double mx = this.getX() - this.xo;
		double mz = this.getZ() - this.zo;
		double moved = Math.sqrt(mx * mx + mz * mz);
		if (moved > 0.01 && moved < 1.0 && walkerShown(a) && !this.isFloating()) {
			this.squeak += moved;
			if (this.squeak > SQUEAK_EVERY) {
				this.squeak = 0.0;
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.ANDADOR_SQUEAK, SoundSource.NEUTRAL, 0.8F,
						0.9F + this.random.nextFloat() * 0.25F);
			}
		}
		if ((a == POSE_FLOAT_ROCK || a == POSE_KNIT_SIT) && this.tickCount % CREAK_EVERY == 0) {
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.ROCKING_CREAK_SLOW, SoundSource.NEUTRAL, 0.6F,
					0.95F + this.random.nextFloat() * 0.1F);
		}
	}

	/** Possessed Jorge steams at the collar (white puffs either side of his neck, drifting up). */
	@Override
	protected void clientEffects() {
		super.clientEffects();
		if (this.getType() == FamilyEntities.JORGE && this.isPossessed() && this.action() != POSE_LIMP_FALL && this.tickCount % 4 == 0) {
			float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
			float side = this.random.nextBoolean() ? 0.12F : -0.12F;
			this.level().addParticle(ParticleTypes.POOF, this.getX() + Mth.cos(yaw) * side, this.getY() + 1.4,
					this.getZ() + Mth.sin(yaw) * side, 0.0, 0.03, 0.0);
		}
	}

	// ------------------------------------------------------------------ not a monster
	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	/** The family is not scary; a possessed one chills you a little. */
	@Override
	public float fearAura() {
		return this.isPossessed() ? 0.4F : 0F;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return null;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return null;
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		super.addAdditionalSaveData(out);
		out.putInt("Look", this.variant());
		out.putInt("FamilyPose", this.action());
		out.putBoolean("Floating", this.isFloating());
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		super.readAdditionalSaveData(in);
		this.setVariant(in.getIntOr("Look", LOOK_NORMAL));
		this.setAction(in.getIntOr("FamilyPose", POSE_IDLE));
		if (in.getBooleanOr("Floating", false)) {
			this.setFloating(true);
		}
	}
}
