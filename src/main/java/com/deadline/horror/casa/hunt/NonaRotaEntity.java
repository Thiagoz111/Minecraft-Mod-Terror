package com.deadline.horror.casa.hunt;

import com.deadline.director.Director;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.entity.HauntEntity;
import com.deadline.entity.HolyWaterEntity;
import com.deadline.entity.SaltGuard;
import com.deadline.registry.ModBlocks;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.voice.NoiseMeter;
import com.deadline.voice.Voice;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.Node;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Nona, broken (design 7 "Nona Pocha", variant 'rota'): the hunter of Act 5. Half-blind with cataracts, she hunts
 * by EAR (docs/design/casa_terror.md 6.1): the noise meter of every hunter (scaled by distance, muffled by walls and
 * closed doors), the microphone (talking draws her straight there, shouting is an immediate chase), doors, thrown
 * things ({@link Hunt#noise}) and the flashlight clicking. She only SEES what is lit by its own flashlight within 6
 * blocks in front of her, or what she bumps into.
 * <p>States: PATROL (between room markers, slow; upright and stumbling or crawling like a spider), LISTEN (freezes, the
 * head cocked, sniffing: the worst 2-4 s), INVESTIGATE (to the last heard spot, opening doors, then checks the
 * hiding places within 8 blocks of it), CHASE (fast spider crawl, ~0.36), SEARCH (at hide_&lt;id&gt;_out: opens the
 * wardrobe / looks under the bed, her face at the slats; whoever is not holding his breath in silence is dragged out),
 * RECOIL (crucifix: 3 s, hissing), FLEE (holy water: 8 s), and the salt line she will not cross for 20 s.
 * She never deals damage: a capture is {@link Hunt#capture} (fail forward).
 */
public class NonaRotaEntity extends HauntEntity {
	// ------------------------------------------------------------------ synced actions (the model's poses)
	public static final int ACT_STAND = 0, ACT_TRANSFORM = 1, ACT_CRAWL = 2, ACT_UPRIGHT = 3, ACT_LISTEN = 4, ACT_SEARCH = 5,
			ACT_RECOIL = 6, ACT_FLEE = 7, ACT_CEILING = 8, ACT_GRAB = 9, ACT_SEARCH_LOW = 10;
	/** Length of "La Nona se rompe" (ticks); the client timeline (NonaRotaModel) uses the same numbers. */
	public static final int TRANSFORM_TICKS = 150;
	/** Look variants: 0 the broken face (nona_rota.png), 1 the possessed grandmother before she breaks. */
	public static final int LOOK_ROTA = 0, LOOK_BEFORE = 1;

	private static final EntityDataAccessor<Integer> ACTION_AT = SynchedEntityData.defineId(NonaRotaEntity.class, EntityDataSerializers.INT);

	// ------------------------------------------------------------------ tuning
	/** Perceived loudness (meter units after distance and walls) that she notices / that makes her chase at once. */
	private static final float HEAR = 9F, CHASE_LOUD = 30F;
	/** Speeds (movement speed attribute; the navigation runs at 1.0). */
	private static final double SPEED_PATROL_CRAWL = 0.19, SPEED_PATROL_UPRIGHT = 0.14, SPEED_INVESTIGATE = 0.26,
			SPEED_CHASE = 0.36, SPEED_LUNGE = 0.5, SPEED_FLEE = 0.42;
	private static final double SIGHT = 6.0, TOUCH = 2.2, CAPTURE_REACH = 1.45;
	private static final int LISTEN_MIN = 40, LISTEN_MAX = 80, SEARCH_TICKS = 84, SEARCH_GRACE = 22, RECOIL_TICKS = 60,
			FLEE_TICKS = 160, SALT_HOLD = 400, LOST_CONTACT = 70;

	private enum Mode {
		IDLE, TRANSFORM, PATROL, LISTEN, INVESTIGATE, CHASE, SEARCH, RECOIL, FLEE
	}

	private Run run;
	private int unbound;
	private Mode mode = Mode.IDLE;
	private int modeTicks;
	private int modeLength;
	private Vec3 goal;
	private boolean upright;
	private boolean loudLead;
	private Vec3 heardAt;
	private ServerPlayer target;
	private Vec3 lastKnown;
	private long lastContact;
	private int lungeTicks;
	private int lungeCooldown;
	private final List<HideSpots.Spot> searchQueue = new ArrayList<>();
	private HideSpots.Spot searching;
	private boolean searchOpened;
	private BlockPos doorPos;
	private int doorWait;
	private int saltTicks;
	private Vec3 lastPos = Vec3.ZERO;
	private int stillTicks;
	private int tapCooldown = 10;
	private int groanCooldown = 120;
	private int sniffCooldown;
	private int hissCooldown;
	private int clackCooldown = 200;
	/** Ticks she holds the grab pose after catching someone (so it reaches the clients before she moves on). */
	private int grabTicks;

	public NonaRotaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
		this.xpReward = 0;
		this.getNavigation().setCanOpenDoors(true);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 200.0)
				.add(Attributes.MOVEMENT_SPEED, SPEED_PATROL_CRAWL)
				.add(Attributes.FOLLOW_RANGE, 64.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
				.add(Attributes.STEP_HEIGHT, 1.05);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(ACTION_AT, 0);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
	}

	// ------------------------------------------------------------------ synced pose
	/** Game time at which the current action started (the client's timelines count from it). */
	public int actionAt() {
		return this.entityData.get(ACTION_AT);
	}

	private void act(int action) {
		if (this.action() != action) {
			this.setAction(action);
			this.entityData.set(ACTION_AT, (int) this.level().getGameTime());
		}
	}

	// ------------------------------------------------------------------ binding / script hooks
	void bind(Run r) {
		this.run = r;
		this.setSiteIndex(r.site);
		this.directorActor = true;
		this.scripted = false;
		this.setPersistenceRequired();
	}

	public boolean isTransforming() {
		return mode == Mode.TRANSFORM;
	}

	/** True while she chases this very player (his chase music plays). */
	public boolean isChasing(ServerPlayer p) {
		return mode == Mode.CHASE && target == p;
	}

	/** True while she is hunting (not transforming, not held in a scripted pose). */
	public boolean isHunting() {
		return mode != Mode.TRANSFORM && mode != Mode.IDLE;
	}

	/** Starts "La Nona se rompe" where she stands (the look starts as the possessed grandmother). */
	void startTransform() {
		setMode(Mode.TRANSFORM, TRANSFORM_TICKS);
		this.setVariant(LOOK_BEFORE);
		this.setAction(ACT_STAND);  // re-trigger the timeline even if she was standing
		act(ACT_TRANSFORM);
		this.getNavigation().stop();
	}

	/** The hunt begins (after the transformation, after a respawn): straight at a close hunter or out on patrol. */
	void beginHunt(boolean afterTransform) {
		this.setVariant(LOOK_ROTA);
		ServerPlayer p = nearestHunter(afterTransform ? 14.0 : 0.0);
		if (p != null && afterTransform && hasLineTo(p)) {
			chase(p);
			return;
		}
		listen(null, afterTransform ? 30 : 20);
	}

	/** After a capture she is somewhere else, far, and deaf for a while (Hunt.GRACE_AFTER_CAPTURE). */
	void afterCapture(ServerPlayer p) {
		target = null;
		searching = null;
		searchQueue.clear();
		if (run != null) {
			String far = null;
			double best = -1;
			for (String k : Hunt.rooms(run)) {
				double d = run.at(k).distanceTo(p.position());
				if (d > best && d < 60) {
					best = d;
					far = k;
				}
			}
			if (far != null) {
				Vec3 v = run.at(far);
				this.teleportTo(v.x, v.y, v.z);
				this.getNavigation().stop();
			}
		}
		patrol();
	}

	/** Holds a scripted pose (set pieces: ACT_CEILING, ACT_STAND...) without hunting until {@link #resumeHunt()}. */
	public void holdPose(int action) {
		setMode(Mode.IDLE, 0);
		this.getNavigation().stop();
		act(action);
	}

	public void resumeHunt() {
		beginHunt(false);
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		super.tick();
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		if (run == null) {
			// spawned by hand (a command, a spawn egg): adopt the case of the nearest hunter, or go away
			if (++unbound % 20 == 0) {
				ServerPlayer p = nearestAny(level, 64);
				Run r = p != null ? Director.of(p) : null;
				if (r != null) {
					bind(r);
					r.actor(Hunt.ACTOR, this);
				} else if (unbound > 100) {
					this.discard();
				}
			}
			return;
		}
		if (Director.get(run.type, run.site) != run) {
			this.discard();
			return;
		}
		if (grabTicks > 0) {
			grabTicks--;
			this.getNavigation().stop();
			act(ACT_GRAB);
			return;
		}
		modeTicks++;
		lungeCooldown = Math.max(0, lungeCooldown - 1);
		hissCooldown = Math.max(0, hissCooldown - 1);
		sniffCooldown = Math.max(0, sniffCooldown - 1);
		switch (mode) {
			case TRANSFORM -> tickTransform(level);
			case PATROL -> tickPatrol(level);
			case LISTEN -> tickListen(level);
			case INVESTIGATE -> tickInvestigate(level);
			case CHASE -> tickChase(level);
			case SEARCH -> tickSearch(level);
			case RECOIL -> tickRecoil(level);
			case FLEE -> tickFlee(level);
			case IDLE -> {
			}
		}
		if (mode == Mode.PATROL || mode == Mode.INVESTIGATE || mode == Mode.LISTEN || mode == Mode.CHASE) {
			if ((this.tickCount + this.getId()) % 4 == 0) {
				hear(level);
				look(level);
			}
		}
		if (mode != Mode.TRANSFORM && mode != Mode.IDLE) {
			doors(level);
			salt(level);
			ambience(level);
		}
	}

	private void setMode(Mode m, int length) {
		mode = m;
		modeTicks = 0;
		modeLength = length;
	}

	// ------------------------------------------------------------------ the transformation (La Nona se rompe)
	private void tickTransform(ServerLevel level) {
		int t = modeTicks;
		this.getNavigation().stop();
		this.setDeltaMovement(this.getDeltaMovement().multiply(0.0, 1.0, 0.0));
		// the body keeps its yaw (her back to the room); the timeline lives in NonaRotaModel
		this.yHeadRot = this.yBodyRot = this.getYRot();
		if (t == 4) {
			sound(level, ModSounds.HUNT_GROAN, 1.2F, 0.7F);
		}
		if (t == 14 || t == 22 || t == 27 || t == 96 || t == 101 || t == 108 || t == 113 || t == 119) {
			sound(level, ModSounds.HUNT_BONE_CRACK, 1.6F, 0.85F + this.random.nextFloat() * 0.3F);
		}
		if (t == 30) {
			this.setVariant(LOOK_ROTA);  // the face goes as the neck starts to turn
			sound(level, ModSounds.HUNT_NECK_TWIST, 2.0F, 1.0F);
		}
		if (t == 64) {
			sound(level, ModSounds.HUNT_JAW, 1.8F, 0.7F);
		}
		if (t == 122) {
			sound(level, ModSounds.HUNT_SCREAM, 2.6F, 1.0F);
			for (ServerPlayer p : level.players()) {
				if (p.distanceToSqr(this) < 24 * 24) {
					com.deadline.net.Fx.shake(p, 0.9F, 16);
				}
			}
		}
		if (t % 6 == 0 && t > 30 && t < 120) {
			level.sendParticles(ParticleTypes.DAMAGE_INDICATOR, this.getX(), this.getY() + 1.6, this.getZ(), 1, 0.15, 0.2, 0.15, 0.0);
		}
		if (t >= TRANSFORM_TICKS) {
			Hunt.transformed(run);
			beginHunt(true);
		}
	}

	// ------------------------------------------------------------------ patrol
	private void patrol() {
		setMode(Mode.PATROL, 0);
		target = null;
		goal = null;
		upright = this.random.nextFloat() < 0.32F;
	}

	private void tickPatrol(ServerLevel level) {
		if (!searchQueue.isEmpty()) {
			search(searchQueue.remove(0));
			return;
		}
		if (goal == null || arrived(goal, 1.4) || (modeTicks > 40 && this.getNavigation().isDone())) {
			if (goal != null && modeTicks > 0) {
				// a pause in the room: stand there and listen
				goal = null;
				listen(null, LISTEN_MIN + this.random.nextInt(40));
				return;
			}
			goal = pickRoom();
			upright = this.random.nextFloat() < 0.32F;
			modeTicks = 1;
		}
		act(upright ? ACT_UPRIGHT : ACT_CRAWL);
		move(goal, upright ? SPEED_PATROL_UPRIGHT : SPEED_PATROL_CRAWL, 20);
	}

	/** A room marker 6-30 blocks away; often one close to a hunter (she drifts towards you even when she has not heard). */
	private Vec3 pickRoom() {
		List<String> rooms = Hunt.rooms(run);
		ServerPlayer near = nearestHunter(0.0);
		Vec3 from = this.position();
		boolean drift = near != null && this.random.nextFloat() < 0.45F;
		List<Vec3> ok = new ArrayList<>();
		for (String k : rooms) {
			Vec3 v = run.at(k);
			double d = v.distanceTo(from);
			if (d < 5 || d > 32) {
				continue;
			}
			if (drift && v.distanceTo(near.position()) > 14) {
				continue;
			}
			ok.add(v);
		}
		if (ok.isEmpty()) {
			return run.at(rooms.get(this.random.nextInt(rooms.size())));
		}
		return ok.get(this.random.nextInt(ok.size()));
	}

	// ------------------------------------------------------------------ listen
	/** Freezes with the head cocked and sniffs; then goes to `at` (or back to patrol). */
	private void listen(Vec3 at, int ticks) {
		setMode(Mode.LISTEN, ticks);
		heardAt = at;
		this.getNavigation().stop();
		act(ACT_LISTEN);
		sniffCooldown = 6;
	}

	private void tickListen(ServerLevel level) {
		this.getNavigation().stop();
		act(ACT_LISTEN);
		if (sniffCooldown == 0) {
			sniffCooldown = 18 + this.random.nextInt(14);
			sound(level, ModSounds.HUNT_SNIFF, 0.9F, 0.9F + this.random.nextFloat() * 0.2F);
		}
		if (heardAt != null) {
			this.getLookControl().setLookAt(heardAt.x, heardAt.y + 1.0, heardAt.z, 10F, 10F);
		}
		if (modeTicks >= modeLength) {
			if (heardAt != null) {
				investigate(heardAt, false);
			} else {
				patrol();
			}
		}
	}

	// ------------------------------------------------------------------ investigate
	private void investigate(Vec3 at, boolean voice) {
		boolean refresh = mode == Mode.INVESTIGATE;
		if (!refresh) {
			setMode(Mode.INVESTIGATE, 20 * 30);
		}
		goal = at;
		loudLead = voice;
		target = null;
		if (refresh) {
			this.getNavigation().stop();  // re-path to the new spot
		}
	}

	private void tickInvestigate(ServerLevel level) {
		act(ACT_CRAWL);
		move(goal, loudLead ? SPEED_INVESTIGATE + 0.05 : SPEED_INVESTIGATE, 12);
		boolean there = arrived(goal, 1.8);
		boolean stuck = modeTicks > 30 && this.getNavigation().isDone() && !there;
		if (there || stuck || modeTicks >= modeLength) {
			queueSearches(goal, loudLead ? 3 : 2);
			sound(level, ModSounds.HUNT_SNIFF, 1.0F, 0.85F);
			if (searchQueue.isEmpty()) {
				listen(null, 30 + this.random.nextInt(30));
			} else {
				search(searchQueue.remove(0));
			}
		}
	}

	/**
	 * Hiding places within 8 blocks of where she heard the noise, nearest first. A place someone hides in is added even
	 * when it is not among the nearest (she smells fear): the hunter's breath is what saves him, not luck.
	 */
	private void queueSearches(Vec3 around, int max) {
		searchQueue.clear();
		if (around == null) {
			return;
		}
		List<HideSpots.Spot> spots = new ArrayList<>();
		for (HideSpots.Spot s : HideSpots.spots(run)) {
			if (s.out().distanceTo(around) <= 8.0) {
				spots.add(s);
			}
		}
		spots.sort((a, b) -> Double.compare(a.out().distanceTo(around), b.out().distanceTo(around)));
		for (int i = 0; i < spots.size() && searchQueue.size() < max; i++) {
			searchQueue.add(spots.get(i));
		}
		for (HideSpots.Spot s : spots) {
			if (!searchQueue.contains(s) && HideSpots.occupant(run, s) != null && this.random.nextFloat() < 0.6F) {
				searchQueue.add(0, s);
			}
		}
	}

	// ------------------------------------------------------------------ chase
	private void chase(ServerPlayer p) {
		if (mode != Mode.CHASE) {
			setMode(Mode.CHASE, 0);
			sound(this.level() instanceof ServerLevel l ? l : null, ModSounds.HUNT_SCREAM, 2.0F, 1.1F + this.random.nextFloat() * 0.15F);
		}
		target = p;
		lastKnown = p.position();
		lastContact = this.level().getGameTime();
		NoiseMeter.heard(p);
	}

	private void tickChase(ServerLevel level) {
		ServerPlayer p = target;
		if (p == null || p.isRemoved() || !targetable(p)) {
			investigate(lastKnown != null ? lastKnown : this.position(), false);
			return;
		}
		long now = level.getGameTime();
		double d = p.distanceTo(this);
		if (HideSpots.hidden(p)) {
			HideSpots.Spot s = HideSpots.spotOf(p);
			// she heard the door close behind him (or saw him crawl under): straight to that place
			if (s != null && now - lastContact < 30 && d < 12) {
				target = null;
				search(s);
			} else {
				target = null;
				investigate(lastKnown, false);
			}
			return;
		}
		boolean contact = d < 10 && hasLineTo(p) || d < TOUCH || NoiseMeter.get(p) > 14F && d < 16;
		if (contact) {
			lastKnown = p.position();
			lastContact = now;
		}
		if (now - lastContact > LOST_CONTACT) {
			target = null;
			investigate(lastKnown, false);
			return;
		}
		act(ACT_CRAWL);
		// elastic: faster when far, a lunge when she is right behind you
		double speed = SPEED_CHASE + 0.06 * Mth.clamp((d - 4.0) / 10.0, 0.0, 1.0);
		if (lungeTicks > 0) {
			lungeTicks--;
			speed = SPEED_LUNGE;
		} else if (d < 4.2 && lungeCooldown == 0 && hasLineTo(p)) {
			lungeTicks = 9;
			lungeCooldown = 70;
			sound(level, ModSounds.HUNT_HISS, 1.6F, 1.25F);
		}
		this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(speed);
		if (modeTicks % 5 == 1 || this.getNavigation().isDone()) {
			if (contact) {
				this.getNavigation().moveTo(p, 1.0);
			} else {
				this.getNavigation().moveTo(lastKnown.x, lastKnown.y, lastKnown.z, 1.0);
			}
		}
		this.getLookControl().setLookAt(p, 30F, 30F);
		double dy = Math.abs(p.getY() - this.getY());
		if (d < CAPTURE_REACH + 0.4 && dy < 1.6) {
			Hunt.capture(run, p);
			target = null;
			listen(null, 40);
			grab();
		}
	}

	// ------------------------------------------------------------------ searching a hiding place
	private void search(HideSpots.Spot s) {
		setMode(Mode.SEARCH, 0);
		searching = s;
		searchOpened = false;
		goal = s.out();
		target = null;
	}

	private void tickSearch(ServerLevel level) {
		HideSpots.Spot s = searching;
		if (s == null) {
			patrol();
			return;
		}
		if (!searchOpened) {
			act(ACT_CRAWL);
			move(s.out(), SPEED_INVESTIGATE, 10);
			boolean there = arrived(s.out(), 1.1);
			if (there || (modeTicks > 60 && this.getNavigation().isDone()) || modeTicks > 20 * 20) {
				if (!there && this.position().distanceTo(s.out()) > 3.0) {
					searching = null;  // cannot get there
					patrol();
					return;
				}
				searchOpened = true;
				modeTicks = 0;
				this.getNavigation().stop();
				HideSpots.open(run, s, true);
				HideSpots.searched(run, s, true);
				act(s.low() ? ACT_SEARCH_LOW : ACT_SEARCH);
				sound(level, ModSounds.HUNT_SNIFF, 1.1F, 0.8F);
			}
			return;
		}
		// her face right at the slats / the gap under the bed: she leans in and breathes it in
		Vec3 lean = s.out().add(s.hide().subtract(s.out()).normalize().scale(s.low() ? 0.55 : 0.75));
		this.getMoveControl().setWantedPosition(lean.x, lean.y, lean.z, 0.6);
		float yaw = Props.yawTowards(this.position(), s.hide());
		this.setYRot(yaw);
		this.yBodyRot = yaw;
		this.yHeadRot = yaw;
		if (modeTicks == 26 || modeTicks == 52 || modeTicks == 70) {
			sound(level, ModSounds.HUNT_SNIFF, 1.2F, 0.75F + this.random.nextFloat() * 0.1F);
		}
		if (modeTicks == 40) {
			sound(level, ModSounds.HUNT_JAW, 0.9F, 0.9F);
		}
		ServerPlayer hidden = HideSpots.occupant(run, s);
		if (hidden != null && modeTicks > SEARCH_GRACE) {
			boolean breathing = !Breath.holding(hidden);
			boolean noisy = NoiseMeter.get(hidden) > 12F || (Voice.enabled(hidden) && Voice.speaking(hidden, level.getGameTime()));
			if (breathing || noisy) {
				HideSpots.searched(run, s, false);
				Hunt.capture(run, hidden);
				searching = null;
				listen(null, 40);
				grab();
				return;
			}
		}
		// someone sneaking out right under her nose
		for (ServerPlayer p : run.hunters()) {
			if (targetable(p) && !HideSpots.hidden(p) && p.distanceTo(this) < TOUCH + 0.4) {
				HideSpots.searched(run, s, false);
				searching = null;
				chase(p);
				return;
			}
		}
		if (modeTicks >= SEARCH_TICKS) {
			HideSpots.searched(run, s, false);
			HideSpots.open(run, s, false);
			searching = null;
			if (!searchQueue.isEmpty()) {
				search(searchQueue.remove(0));
			} else {
				listen(null, 30);
			}
		}
	}

	/** Holds the grab / lunge pose for a second (she has him). */
	private void grab() {
		grabTicks = 22;
		act(ACT_GRAB);
		this.getNavigation().stop();
	}

	// ------------------------------------------------------------------ hearing and the little she sees
	private void hear(ServerLevel level) {
		if (Hunt.deaf(run) || mode == Mode.CHASE && target != null && modeTicks < 10) {
			return;
		}
		long now = level.getGameTime();
		Vec3 ear = this.getEyePosition();
		float best = 0F;
		ServerPlayer who = null;
		Vec3 where = null;
		boolean voice = false;
		boolean shout = false;
		for (ServerPlayer p : run.hunters()) {
			if (!targetable(p)) {
				continue;
			}
			double d = p.distanceTo(this);
			if (d > 48) {
				continue;
			}
			float raw = NoiseMeter.get(p);
			boolean speaking = Voice.enabled(p) && Voice.speaking(p, now) && !Breath.holding(p);
			boolean yell = speaking && Voice.relative(p) > 12F;
			if (speaking) {
				raw = Math.max(raw, yell ? 100F : 62F);
			}
			float pre = raw / (1F + (float) d / 8F);
			if (pre < HEAR) {
				continue;
			}
			float per = pre * occlusion(level, ear, p.getEyePosition());
			if (per > best) {
				best = per;
				who = p;
				where = p.position();
				voice = speaking;
				shout = yell;
			}
		}
		for (Hunt.Noise n : Hunt.noises(run)) {
			double d = n.pos().distanceTo(ear);
			float pre = n.loudness() / (1F + (float) d / 8F);
			if (pre < HEAR || pre <= best) {
				continue;
			}
			float per = pre * occlusion(level, ear, n.pos());
			if (per > best) {
				best = per;
				who = null;
				where = n.pos();
				voice = false;
				shout = false;
			}
		}
		if (best < HEAR || where == null) {
			return;
		}
		if (who != null) {
			NoiseMeter.heard(who);
		}
		boolean hidden = who != null && HideSpots.hidden(who);
		if (who != null && !hidden && (best >= CHASE_LOUD || shout || who.distanceTo(this) < 4.0)) {
			chase(who);
			return;
		}
		if (mode == Mode.CHASE) {
			return;
		}
		if (hidden) {
			// a noise from inside a hiding place: she goes to check THAT one first
			HideSpots.Spot s = HideSpots.spotOf(who);
			if (s != null) {
				searchQueue.remove(s);
				searchQueue.add(0, s);
			}
		}
		if (voice || mode == Mode.INVESTIGATE) {
			investigate(where, voice);
		} else if (mode != Mode.LISTEN || heardAt == null) {
			listen(where, Math.max(20, LISTEN_MIN + this.random.nextInt(LISTEN_MAX - LISTEN_MIN) - (int) best));
		} else {
			heardAt = where;  // listening already: she turns to the new sound
		}
	}

	/** She sees only what a flashlight shows her within 6 blocks in front, or what she bumps into. */
	private void look(ServerLevel level) {
		if (mode == Mode.CHASE) {
			return;
		}
		Vec3 eye = this.getEyePosition();
		float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
		Vec3 fwd = new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
		for (ServerPlayer p : run.hunters()) {
			if (!targetable(p) || HideSpots.hidden(p)) {
				continue;
			}
			double d = p.distanceTo(this);
			if (d < TOUCH) {
				chase(p);
				return;
			}
			if (d > SIGHT || !Props.lit(p)) {
				continue;
			}
			Vec3 to = p.getEyePosition().subtract(eye);
			Vec3 flat = new Vec3(to.x, 0, to.z);
			if (flat.lengthSqr() < 1.0E-4 || flat.normalize().dot(fwd) < 0.5 || !hasLineTo(p)) {
				continue;
			}
			chase(p);
			return;
		}
	}

	/** 1 in the open; each wall in between muffles to 40 %, each closed door to 55 %. */
	private float occlusion(ServerLevel level, Vec3 from, Vec3 to) {
		float k = 1F;
		Vec3 a = from;
		Vec3 dir = to.subtract(from);
		double len = dir.length();
		if (len < 1.0E-3) {
			return 1F;
		}
		Vec3 n = dir.scale(1.0 / len);
		for (int i = 0; i < 3; i++) {
			BlockHitResult hit = level.clip(new ClipContext(a, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
			if (hit.getType() == HitResult.Type.MISS) {
				return k;
			}
			BlockState st = level.getBlockState(hit.getBlockPos());
			k *= st.getBlock() instanceof DoorBlock ? 0.55F : 0.4F;
			a = hit.getLocation().add(n.scale(1.05));
			if (a.distanceToSqr(from) >= len * len) {
				return k;
			}
		}
		return k * 0.5F;
	}

	private boolean hasLineTo(Entity e) {
		Vec3 from = this.getEyePosition();
		Vec3 to = e.getEyePosition();
		return this.level().clip(new ClipContext(from, to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, this)).getType() == HitResult.Type.MISS;
	}

	private boolean targetable(ServerPlayer p) {
		return p.isAlive() && !p.isSpectator() && !p.isCreative() && p.level() == this.level() && !Hunt.capturing(run, p);
	}

	// ------------------------------------------------------------------ repelled
	/** The crucifix (CrucifixItem stuns every haunt in its cone): she recoils for 3 s, hissing, smoking. */
	@Override
	public void stun(int ticks) {
		if (mode == Mode.TRANSFORM || mode == Mode.IDLE || mode == Mode.FLEE) {
			return;
		}
		if (mode != Mode.RECOIL) {
			sound(this.level() instanceof ServerLevel l ? l : null, ModSounds.HUNT_HISS, 2.0F, 0.8F);
			searchQueue.clear();
			if (searching != null) {
				HideSpots.searched(run, searching, false);
				searching = null;
			}
		}
		setMode(Mode.RECOIL, RECOIL_TICKS);
		target = null;
		this.getNavigation().stop();
		act(ACT_RECOIL);
	}

	private void tickRecoil(ServerLevel level) {
		act(ACT_RECOIL);
		ServerPlayer p = nearestHunter(12.0);
		if (p != null && modeTicks % 4 == 0) {
			Vec3 away = this.position().subtract(p.position());
			away = new Vec3(away.x, 0, away.z);
			if (away.lengthSqr() > 1.0E-4) {
				away = away.normalize().scale(0.12);
				this.setDeltaMovement(away.x, this.getDeltaMovement().y, away.z);
			}
			this.getLookControl().setLookAt(p, 30F, 30F);
		}
		if (modeTicks % 5 == 0) {
			level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 0.9, this.getZ(), 4, 0.3, 0.4, 0.3, 0.02);
		}
		if (modeTicks >= modeLength) {
			listen(p != null ? p.position() : null, 30);
		}
	}

	/** Holy water: she flees, burning, to the far end of the house for 8 s. */
	private void flee(Entity from) {
		setMode(Mode.FLEE, FLEE_TICKS);
		target = null;
		searchQueue.clear();
		if (searching != null) {
			HideSpots.searched(run, searching, false);
			searching = null;
		}
		Vec3 src = from != null ? from.position() : this.position();
		String far = null;
		double best = -1;
		for (String k : Hunt.rooms(run)) {
			double d = run.at(k).distanceTo(src);
			if (d > best && run.at(k).distanceTo(this.position()) < 40) {
				best = d;
				far = k;
			}
		}
		goal = far != null ? run.at(far) : this.position();
		this.getNavigation().stop();
		sound(this.level() instanceof ServerLevel l ? l : null, ModSounds.HUNT_SCREAM, 2.4F, 1.3F);
	}

	private void tickFlee(ServerLevel level) {
		act(ACT_FLEE);
		this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(SPEED_FLEE);
		if (modeTicks % 8 == 1 || this.getNavigation().isDone()) {
			this.getNavigation().moveTo(goal.x, goal.y, goal.z, 1.0);
		}
		if (modeTicks % 3 == 0) {
			level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 0.6, this.getZ(), 3, 0.3, 0.3, 0.3, 0.02);
		}
		if (modeTicks >= modeLength) {
			patrol();
		}
	}

	/** A salt line holds her for 20 s; then she claws through it, scattering the salt. */
	private void salt(ServerLevel level) {
		boolean moving = mode == Mode.PATROL || mode == Mode.INVESTIGATE || mode == Mode.CHASE || mode == Mode.SEARCH && !searchOpened
				|| mode == Mode.FLEE;
		Vec3 pos = this.position();
		double moved = pos.distanceToSqr(lastPos);
		lastPos = pos;
		stillTicks = moving && moved < 0.0004 ? stillTicks + 1 : 0;
		if (!moving || !SaltGuard.near(level, this.blockPosition(), 1)) {
			saltTicks = Math.max(0, saltTicks - 2);
			return;
		}
		if (stillTicks < 8) {
			return;
		}
		if (saltTicks == 0 || saltTicks % 120 == 0) {
			sound(level, ModSounds.HUNT_HISS, 1.6F, 0.9F);
			level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 0.4, this.getZ(), 8, 0.4, 0.2, 0.4, 0.02);
		}
		saltTicks++;
		if (saltTicks >= SALT_HOLD) {
			saltTicks = 0;
			BlockPos c = this.blockPosition();
			for (BlockPos p : BlockPos.betweenClosed(c.offset(-2, -1, -2), c.offset(2, 1, 2))) {
				if (level.getBlockState(p).is(ModBlocks.SALT_LINE)) {
					level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
					level.sendParticles(ModParticles.SALT_SPARKLE, p.getX() + 0.5, p.getY() + 0.1, p.getZ() + 0.5, 6, 0.3, 0.05, 0.3, 0.05);
				}
			}
			sound(level, ModSounds.HUNT_SCREAM, 1.8F, 0.8F);
		}
	}

	// ------------------------------------------------------------------ doors
	/** Closed wooden doors on her path: the handle rattles, then it opens (at once, slammed, while chasing). */
	private void doors(ServerLevel level) {
		if (doorWait > 0) {
			BlockState st = level.getBlockState(doorPos);
			if (!(st.getBlock() instanceof DoorBlock door) || door.isOpen(st)) {
				doorWait = 0;
				return;
			}
			if (--doorWait == 0) {
				door.setOpen(this, level, st, doorPos, true);
				if (mode == Mode.CHASE) {
					level.playSound(null, doorPos, ModSounds.DOOR_SLAM, SoundSource.BLOCKS, 1.4F, 1.1F);
				}
			}
			return;
		}
		Path path = this.getNavigation().getPath();
		if (path == null || path.isDone()) {
			return;
		}
		int end = Math.min(path.getNextNodeIndex() + 2, path.getNodeCount());
		for (int i = Math.max(0, path.getNextNodeIndex() - 1); i < end; i++) {
			Node node = path.getNode(i);
			for (int dy = 0; dy <= 1; dy++) {
				BlockPos pos = new BlockPos(node.x, node.y + dy, node.z);
				BlockState st = level.getBlockState(pos);
				if (st.getBlock() instanceof DoorBlock door && DoorBlock.isWoodenDoor(st) && !door.isOpen(st)
						&& this.distanceToSqr(Vec3.atBottomCenterOf(pos)) < 2.7 * 2.7) {
					doorPos = pos;
					doorWait = mode == Mode.CHASE || mode == Mode.FLEE ? 2 : 12 + this.random.nextInt(10);
					if (doorWait > 2) {
						level.playSound(null, pos, ModSounds.HUNT_RATTLE, SoundSource.BLOCKS, 1.0F, 0.9F + this.random.nextFloat() * 0.2F);
					}
					return;
				}
			}
		}
	}

	// ------------------------------------------------------------------ sounds of her body
	private void ambience(ServerLevel level) {
		double moved = this.getDeltaMovement().horizontalDistance();
		if (--tapCooldown <= 0 && moved > 0.02) {
			boolean crawl = this.action() == ACT_CRAWL || this.action() == ACT_FLEE;
			tapCooldown = crawl ? Math.max(3, (int) (0.9 / Math.max(0.05, moved))) : 9 + this.random.nextInt(6);
			sound(level, crawl ? ModSounds.HUNT_CRAWL_TAP : ModSounds.HUNT_BONE_CRACK, crawl ? 0.7F : 0.35F,
					0.85F + this.random.nextFloat() * 0.3F);
		}
		if (--groanCooldown <= 0) {
			groanCooldown = 90 + this.random.nextInt(110);
			if (mode != Mode.SEARCH && mode != Mode.LISTEN) {
				sound(level, ModSounds.HUNT_GROAN, mode == Mode.CHASE ? 1.4F : 0.9F, 0.85F + this.random.nextFloat() * 0.25F);
			}
		}
		if (--clackCooldown <= 0) {
			clackCooldown = 160 + this.random.nextInt(240);
			sound(level, ModSounds.HUNT_JAW, 0.8F, 0.9F + this.random.nextFloat() * 0.2F);
		}
	}

	private void sound(ServerLevel level, SoundEvent s, float volume, float pitch) {
		if (level != null && s != null) {
			level.playSound(null, this.getX(), this.getY() + 0.8, this.getZ(), s, SoundSource.HOSTILE, volume, pitch);
		}
	}

	// ------------------------------------------------------------------ movement helpers
	private void move(Vec3 to, double speed, int repath) {
		if (to == null) {
			return;
		}
		this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(speed);
		if (modeTicks % repath == 1 || this.getNavigation().isDone()) {
			this.getNavigation().moveTo(to.x, to.y, to.z, 1.0);
		}
	}

	private boolean arrived(Vec3 at, double r) {
		if (at == null) {
			return true;
		}
		double dx = at.x - this.getX();
		double dz = at.z - this.getZ();
		return dx * dx + dz * dz < r * r && Math.abs(at.y - this.getY()) < 2.0;
	}

	private ServerPlayer nearestHunter(double max) {
		ServerPlayer best = null;
		double bd = max > 0 ? max * max : Double.MAX_VALUE;
		if (run == null) {
			return null;
		}
		for (ServerPlayer p : run.hunters()) {
			if (!targetable(p)) {
				continue;
			}
			double d = p.distanceToSqr(this);
			if (d < bd) {
				bd = d;
				best = p;
			}
		}
		return best;
	}

	private ServerPlayer nearestAny(ServerLevel level, double max) {
		ServerPlayer best = null;
		double bd = max * max;
		for (ServerPlayer p : level.players()) {
			double d = p.distanceToSqr(this);
			if (d < bd) {
				bd = d;
				best = p;
			}
		}
		return best;
	}

	// ------------------------------------------------------------------ not a monster you can fight
	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
			return super.hurtServer(level, source, amount);
		}
		if (run != null && mode != Mode.TRANSFORM && mode != Mode.IDLE) {
			if (source.getDirectEntity() instanceof HolyWaterEntity) {
				flee(source.getEntity());
			} else if (source.getDirectEntity() instanceof ServerPlayer p && targetable(p) && mode != Mode.RECOIL && mode != Mode.FLEE) {
				chase(p);  // you hit her: she has you
			}
		}
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		// her own taps and cracks (ambience) replace the vanilla footsteps
	}

	@Override
	public float holyWeakness() {
		return 2.0F;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.HUNT_HISS;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.HUNT_SCREAM;
	}

	@Override
	public boolean shouldBeSaved() {
		return false;  // the hunt respawns her (Hunt.tick); a saved copy would be an orphan after a restart
	}
}
