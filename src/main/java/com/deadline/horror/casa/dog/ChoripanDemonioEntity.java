package com.deadline.horror.casa.dog;

import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * "El perro largo" (docs/design/casa_terror.md 7, Acts 5-6): Choripán's body that never finishes coming out of the
 * doghouse -- a chain of fur segments with human arms (tools/models/ent_choripan_demonio.py). The server entity is the
 * HEAD only (0.8 x 0.8); the client draws the chain behind it along the path the head travelled, and the segments that
 * have not come out yet stay telescoped inside the doghouse (ChoripanDemonioRenderer, "trail mode").
 * <ul>
 *   <li>{@link #STATE_EMERGE}: the head crawls out of the door for {@link #EMERGE_TICKS} (6 s), a wet crack for every
 *   segment that pops out; then it holds, staring, until the script sends it after somebody.</li>
 *   <li>{@link #STATE_CRAWL}: a fast skittering run: along a list of points ({@link #crawl(List)}) or straight at a
 *   hunter ({@link #chase(ServerPlayer)}, ground navigation through open doors). Reaching the hunter = the jumpscare
 *   'perro_largo' (fail forward: a scare, no death) and it pulls back.</li>
 *   <li>{@link #STATE_RETRACT}: it goes back along its own path into the doghouse, fast, and is gone.</li>
 * </ul>
 * The door (plane centre + the yaw it comes out along) is synced so the client can keep the hidden segments inside.
 */
public class ChoripanDemonioEntity extends HauntEntity {
	public static final int STATE_IDLE = 0, STATE_EMERGE = 1, STATE_CRAWL = 2, STATE_RETRACT = 3, STATE_HOLD = 4;
	public static final int EMERGE_TICKS = 120;
	/** How far the head comes out of the door while emerging (blocks). */
	public static final double EMERGE_DIST = 2.4;
	/** Blocks per tick: the skitter along points, the retract. */
	public static final double CRAWL_SPEED = 0.30, RETRACT_SPEED = 0.42;

	private static final EntityDataAccessor<Float> DOOR_X = SynchedEntityData.defineId(ChoripanDemonioEntity.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> DOOR_Y = SynchedEntityData.defineId(ChoripanDemonioEntity.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> DOOR_Z = SynchedEntityData.defineId(ChoripanDemonioEntity.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> DOOR_YAW = SynchedEntityData.defineId(ChoripanDemonioEntity.class, EntityDataSerializers.FLOAT);
	/** Game time the current state began (the client times the emerge with it). */
	private static final EntityDataAccessor<Integer> STATE_AT = SynchedEntityData.defineId(ChoripanDemonioEntity.class, EntityDataSerializers.INT);

	/** Where the head has been (oldest first), one point every 0.25 block: the way back into the doghouse. */
	private final List<Vec3> path = new ArrayList<>();
	private final List<Vec3> waypoints = new ArrayList<>();
	private ServerPlayer target;
	private int repath;
	private double popped;
	private int skitterCd;
	/** Set once it caught somebody: the script reads it (and the run gets 'perro_largo:caught'). */
	public boolean caught;
	/** Called when it is back in the doghouse (or caught somebody); the static API posts the run events. */
	public Runnable onRetracted;
	public java.util.function.Consumer<ServerPlayer> onCaught;

	public ChoripanDemonioEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.scripted = true;
		this.noPhysics = true;
		this.setNoGravity(true);
		this.setNoAi(true);
		this.setInvulnerable(true);
		this.xpReward = 0;
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 200.0)
				.add(Attributes.MOVEMENT_SPEED, 0.36)
				.add(Attributes.FOLLOW_RANGE, 64.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(DOOR_X, 0F);
		builder.define(DOOR_Y, 0F);
		builder.define(DOOR_Z, 0F);
		builder.define(DOOR_YAW, 0F);
		builder.define(STATE_AT, 0);
	}

	@Override
	protected void registerGoals() {
	}

	// ------------------------------------------------------------------ synced door
	/** The doghouse door: centre of its plane on the floor, and the yaw a body coming out of it faces. */
	public void setDoor(Vec3 plane, float outYaw) {
		this.entityData.set(DOOR_X, (float) plane.x);
		this.entityData.set(DOOR_Y, (float) plane.y);
		this.entityData.set(DOOR_Z, (float) plane.z);
		this.entityData.set(DOOR_YAW, outYaw);
	}

	public Vec3 door() {
		return new Vec3(this.entityData.get(DOOR_X), this.entityData.get(DOOR_Y), this.entityData.get(DOOR_Z));
	}

	public float doorYaw() {
		return this.entityData.get(DOOR_YAW);
	}

	public static Vec3 forward(float yaw) {
		float r = yaw * Mth.DEG_TO_RAD;
		return new Vec3(-Mth.sin(r), 0, Mth.cos(r));
	}

	public int state() {
		return this.action();
	}

	public int stateTicks() {
		return (int) this.level().getGameTime() - this.entityData.get(STATE_AT);
	}

	private void state(int s) {
		this.setAction(s);
		this.entityData.set(STATE_AT, (int) this.level().getGameTime());
		this.popped = 0.0;
	}

	// ------------------------------------------------------------------ commands
	/** Starts the emerge at the door: the head on the door plane, facing out. */
	public void emerge() {
		Vec3 d = this.door();
		this.snapTo(d.x, d.y, d.z, this.doorYaw(), 0F);
		this.setYHeadRot(this.doorYaw());
		this.setYBodyRot(this.doorYaw());
		this.path.clear();
		this.path.add(d);
		this.state(STATE_EMERGE);
		this.sound(ModSounds.CHORIPAN_UNSPOOL, 1.4F, 0.8F);
		this.sound(ModSounds.PERRO_LARGO_RESPIRA, 1.2F, 0.9F);
	}

	/** Skitters through these points in order, then holds there staring. */
	public void crawl(List<Vec3> points) {
		this.waypoints.clear();
		this.waypoints.addAll(points);
		this.target = null;
		this.navOff();
		this.state(STATE_CRAWL);
	}

	/** Runs at the hunter along the ground (through open doors). Reaching him = the jumpscare. */
	public void chase(ServerPlayer p) {
		this.waypoints.clear();
		this.target = p;
		this.repath = 0;
		this.state(STATE_CRAWL);
	}

	/** Back into the doghouse along its own path, fast; removed once inside. */
	public void retract() {
		this.waypoints.clear();
		this.target = null;
		this.navOff();
		this.state(STATE_RETRACT);
		this.sound(ModSounds.PERRO_LARGO_RETRAE, 1.6F, 1.0F);
	}

	/** Stops where it is, staring at the nearest hunter. */
	public void hold() {
		this.waypoints.clear();
		this.target = null;
		this.navOff();
		this.state(STATE_HOLD);
	}

	private void navOff() {
		this.getNavigation().stop();
		this.setNoAi(true);
		this.noPhysics = true;
		this.setNoGravity(true);
		this.setDeltaMovement(Vec3.ZERO);
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		switch (this.state()) {
			case STATE_EMERGE -> this.tickEmerge();
			case STATE_CRAWL -> this.tickCrawl(level);
			case STATE_RETRACT -> this.tickRetract();
			default -> this.tickHold(level);
		}
		this.record();
	}

	private void tickEmerge() {
		int t = this.stateTicks();
		float u = Mth.clamp(t / (float) EMERGE_TICKS, 0F, 1F);
		// out in surges: it pushes, stops, pushes again (an ease with three hitches), weaving a little
		float surge = u + 0.04F * Mth.sin(u * Mth.PI * 6F);
		double d = EMERGE_DIST * Mth.clamp(surge * (2F - surge), 0F, 1F);
		Vec3 f = forward(this.doorYaw());
		Vec3 side = new Vec3(-f.z, 0, f.x);
		double weave = Math.sin(t * 0.18) * 0.12 * u;
		Vec3 at = this.door().add(f.scale(d)).add(side.scale(weave));
		this.setPos(at.x, at.y, at.z);
		this.setYRot(this.doorYaw() + (float) (Math.cos(t * 0.18) * 8.0 * u));
		this.setYBodyRot(this.getYRot());
		if (d - this.popped > 0.4) {
			this.popped = d;
			this.sound(ModSounds.CHORIPAN_CRACK, 1.3F, 0.8F + this.random.nextFloat() * 0.3F);
		}
		this.lookAtNearest();
		if (t >= EMERGE_TICKS) {
			this.state(STATE_HOLD);
		}
	}

	private void tickHold(ServerLevel level) {
		this.lookAtNearest();
	}

	private void tickCrawl(ServerLevel level) {
		if (this.target != null) {
			ServerPlayer p = this.target;
			if (p.isRemoved() || !p.isAlive() || p.level() != level || p.distanceToSqr(this) > 48 * 48) {
				this.retract();
				return;
			}
			if (this.distanceToSqr(p) < 1.3 * 1.3 + 0.6) {
				this.catchHim(p);
				return;
			}
			// ground navigation: AI on for the run, gravity and collision on
			if (this.isNoAi()) {
				this.setNoAi(false);
				this.noPhysics = false;
				this.setNoGravity(false);
			}
			if (--this.repath <= 0) {
				this.repath = 8;
				this.getNavigation().moveTo(p, 1.0);
			}
			this.getLookControl().setLookAt(p, 40F, 40F);
		} else if (!this.waypoints.isEmpty()) {
			Vec3 next = this.waypoints.get(0);
			Vec3 pos = this.position();
			Vec3 to = next.subtract(pos);
			double len = to.length();
			if (len <= CRAWL_SPEED) {
				this.setPos(next.x, next.y, next.z);
				this.waypoints.remove(0);
			} else {
				Vec3 step = pos.add(to.scale(CRAWL_SPEED / len));
				this.setPos(step.x, step.y, step.z);
			}
			if (len > 1.0E-3) {
				float yaw = (float) (Mth.atan2(to.z, to.x) * Mth.RAD_TO_DEG) - 90F;
				this.setYRot(Mth.approachDegrees(this.getYRot(), yaw, 30F));
				this.setYBodyRot(this.getYRot());
				this.setYHeadRot(this.getYRot());
			}
			if (this.waypoints.isEmpty()) {
				this.state(STATE_HOLD);
			}
		} else {
			this.state(STATE_HOLD);
			return;
		}
		if (--this.skitterCd <= 0) {
			this.skitterCd = 26;
			this.sound(ModSounds.PERRO_LARGO_REPTAR, 1.5F, 0.9F + this.random.nextFloat() * 0.2F);
		}
	}

	private void catchHim(ServerPlayer p) {
		this.caught = true;
		Fx.jumpscare(p, "perro_largo");
		Fx.shake(p, 1.4F, 26);
		Fx.redFlash(p, 0.8F);
		this.sound(ModSounds.CHORIPAN_DEMON_ROAR, 2.0F, 0.8F);
		if (this.onCaught != null) {
			this.onCaught.accept(p);
		}
		this.retract();
	}

	private void tickRetract() {
		Vec3 pos = this.position();
		double left = RETRACT_SPEED;
		Vec3 heading = null;
		while (left > 0 && !this.path.isEmpty()) {
			Vec3 last = this.path.get(this.path.size() - 1);
			Vec3 to = last.subtract(pos);
			double len = to.length();
			if (len <= left) {
				pos = last;
				left -= len;
				this.path.remove(this.path.size() - 1);
			} else {
				heading = to;
				pos = pos.add(to.scale(left / len));
				left = 0;
			}
		}
		if (this.path.isEmpty()) {
			// at the door: in it goes, then it is gone
			Vec3 in = this.door().subtract(forward(this.doorYaw()).scale(0.6));
			Vec3 to = in.subtract(pos);
			double len = to.length();
			if (len < 0.2) {
				this.setPos(in.x, in.y, in.z);
				if (this.onRetracted != null) {
					this.onRetracted.run();
				}
				this.discard();
				return;
			}
			heading = to;
			pos = pos.add(to.scale(Math.min(1.0, RETRACT_SPEED / len)));
		}
		this.setPos(pos.x, pos.y, pos.z);
		if (heading != null && heading.lengthSqr() > 1.0E-6) {
			// it goes back head first? no: it is PULLED back, the face still toward you
			float yaw = (float) (Mth.atan2(-heading.z, -heading.x) * Mth.RAD_TO_DEG) - 90F;
			this.setYRot(Mth.approachDegrees(this.getYRot(), yaw, 25F));
			this.setYBodyRot(this.getYRot());
			this.setYHeadRot(this.getYRot());
		}
		if (this.tickCount % 5 == 0) {
			this.sound(ModSounds.CHORIPAN_CRACK, 1.0F, 1.1F + this.random.nextFloat() * 0.3F);
		}
	}

	/** Keeps the way back: a point every 0.25 block the head moves (not while retracting). */
	private void record() {
		if (this.state() == STATE_RETRACT) {
			return;
		}
		Vec3 here = this.position();
		if (this.path.isEmpty() || this.path.get(this.path.size() - 1).distanceToSqr(here) > 0.0625) {
			this.path.add(here);
			if (this.path.size() > 4096) {
				this.path.remove(0);
			}
		}
	}

	private void lookAtNearest() {
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		ServerPlayer best = null;
		double bd = 24 * 24;
		for (ServerPlayer p : level.players()) {
			double d = p.distanceToSqr(this);
			if (!p.isSpectator() && d < bd) {
				bd = d;
				best = p;
			}
		}
		if (best != null) {
			Vec3 to = best.getEyePosition().subtract(this.getEyePosition());
			float yaw = (float) (Mth.atan2(to.z, to.x) * Mth.RAD_TO_DEG) - 90F;
			float rel = Mth.clamp(Mth.wrapDegrees(yaw - this.yBodyRot), -40F, 40F);
			this.setYHeadRot(Mth.approachDegrees(this.getYHeadRot(), this.yBodyRot + rel, 12F));
			double h = Math.sqrt(to.x * to.x + to.z * to.z);
			this.setXRot(Mth.approach(this.getXRot(), Mth.clamp((float) -(Mth.atan2(to.y, h) * Mth.RAD_TO_DEG), -30F, 35F), 6F));
		}
	}

	private void sound(SoundEvent s, float volume, float pitch) {
		this.level().playSound(null, this.getX(), this.getY(), this.getZ(), s, SoundSource.HOSTILE, volume, pitch);
	}

	// ------------------------------------------------------------------ not killable, not pushable, drawn long
	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return false;
	}

	/** A box round the door and the head together: the chain between them must not pop out of view at corners. */
	public AABB cullingBox() {
		Vec3 d = this.door();
		AABB b = this.getBoundingBox();
		return new AABB(Math.min(b.minX, d.x), Math.min(b.minY, d.y), Math.min(b.minZ, d.z), Math.max(b.maxX, d.x), Math.max(b.maxY, d.y),
				Math.max(b.maxZ, d.z)).inflate(4.0, 1.5, 4.0);
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
	public boolean shouldBeSaved() {
		return false;
	}
}
