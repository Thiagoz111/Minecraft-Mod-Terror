package com.deadline.car;

import com.deadline.item.FlashlightLights;
import com.deadline.registry.ModSounds;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The hunter's car (docs/design/casa_terror.md 6.9): a grey, dented 1970s Argentine four-door sedan with a rosary
 * hanging from the rear-view mirror. Four seats: 0 = driver (front LEFT, Argentina), 1 = front passenger, 2 = rear
 * left, 3 = rear right; NPCs can be seated with {@link #seat(Entity, int)}.
 *
 * <p>Driving uses the vanilla ridden-mob path (like horses and pigs): the controlling player's client simulates the
 * car in {@link #travel(Vec3)} and sends the vehicle moves, so it is smooth. W/S: throttle / brake / reverse with
 * inertia; A/D: steering, the turn rate grows with speed; ~0.9 blocks/tick on roads, slower on grass and sand; climbs
 * 1-block steps; stops against walls and people (nobody is hurt). Indestructible, never pushed by mobs, no drops.
 * Right click to get in, sneak to get out (on your own side: the driver gets out on the left).
 *
 * <p>Engine on while a player drives (start sound, idle/rev loops on the client), headlights (automatic at night,
 * key to toggle; two light beams through {@link FlashlightLights}), horn, and a radio that plays static unless a story
 * event puts a loop on it ({@link #radio(SoundEvent)}).
 */
public class CarEntity extends Mob {
	public static final int SEATS = 4;
	public static final int DRIVER = 0, FRONT_PASSENGER = 1, REAR_LEFT = 2, REAR_RIGHT = 3;
	/**
	 * Rider feet positions in blocks relative to the car: [to the car's LEFT, up, forward]. The seated player's eye
	 * (feet + 1.62) ends up 1.1 above the car floor (the floor is 0.375 above the ground; tools/models/ent_auto.py).
	 */
	private static final double[][] SEAT = {{0.53, -0.145, 0.125}, {-0.53, -0.145, 0.125}, {0.53, -0.145, -1.0}, {-0.53, -0.145, -1.0}};
	public static final double HALF_LENGTH = 2.65;
	public static final double HALF_WIDTH = 1.12;
	public static final float WHEEL_RADIUS = 0.4375F;
	public static final float MAX_SPEED = 0.9F;
	private static final float ACCEL = 0.022F, BRAKE = 0.05F, REVERSE_ACCEL = 0.012F, REVERSE_MAX = 0.25F;
	/** How far the driver can look around (degrees either side of straight ahead). */
	public static final float LOOK_LIMIT = 120F;

	private static final EntityDataAccessor<Integer> SEAT_0 = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> SEAT_1 = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> SEAT_2 = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> SEAT_3 = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Boolean> ENGINE = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Boolean> LIGHTS = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Integer> FLASH = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Boolean> RADIO = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<String> RADIO_SOUND = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.STRING);
	private static final EntityDataAccessor<Float> STEER = SynchedEntityData.defineId(CarEntity.class, EntityDataSerializers.FLOAT);

	// ---- driving state, simulated by the client of the controlling player
	/** Signed speed along the heading, blocks/tick. */
	private float speed;
	/** Smoothed steering, -1 (right) .. 1 (left). */
	private float steer;
	private int simulatedAt = -100;
	private float deltaRotation;
	private int bumpCooldown;

	// ---- client visuals (every client)
	public float wheelRot;
	public float wheelRotO;
	private float clientSpeed;
	private boolean unpaved;

	// ---- server
	private final Map<Integer, Integer> pendingSeat = new HashMap<>();
	private final Map<UUID, Integer> savedSeats = new HashMap<>();
	private UUID owner;
	/** Headlights left as the driver set them (otherwise they follow the night). */
	private boolean lightsManual;
	private int hornCooldown;

	public CarEntity(EntityType<? extends CarEntity> type, Level level) {
		super(type, level);
		this.setPersistenceRequired();
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Mob.createMobAttributes()
				.add(Attributes.MAX_HEALTH, 100.0)
				.add(Attributes.MOVEMENT_SPEED, 0.0)
				.add(Attributes.STEP_HEIGHT, 1.05)
				.add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
				.add(Attributes.EXPLOSION_KNOCKBACK_RESISTANCE, 1.0);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		super.defineSynchedData(builder);
		builder.define(SEAT_0, -1);
		builder.define(SEAT_1, -1);
		builder.define(SEAT_2, -1);
		builder.define(SEAT_3, -1);
		builder.define(ENGINE, false);
		builder.define(LIGHTS, false);
		builder.define(FLASH, 0);
		builder.define(RADIO, false);
		builder.define(RADIO_SOUND, "");
		builder.define(STEER, 0F);
	}

	// ------------------------------------------------------------------ seats
	private static EntityDataAccessor<Integer> seatKey(int seat) {
		return switch (seat) {
			case 1 -> SEAT_1;
			case 2 -> SEAT_2;
			case 3 -> SEAT_3;
			default -> SEAT_0;
		};
	}

	private int seatId(int seat) {
		return this.entityData.get(seatKey(seat));
	}

	private void setSeatId(int seat, int id) {
		if (seat >= 0 && seat < SEATS) {
			this.entityData.set(seatKey(seat), id);
		}
	}

	/** Seat of a passenger (-1: not seated in this car). */
	public int seatOf(Entity e) {
		for (int i = 0; i < SEATS; i++) {
			if (seatId(i) == e.getId()) {
				return i;
			}
		}
		return -1;
	}

	/** Who sits in a seat (null when empty). */
	public Entity occupant(int seat) {
		if (seat < 0 || seat >= SEATS) {
			return null;
		}
		int id = seatId(seat);
		if (id < 0) {
			return null;
		}
		for (Entity e : this.getPassengers()) {
			if (e.getId() == id) {
				return e;
			}
		}
		return null;
	}

	public Entity driver() {
		return occupant(DRIVER);
	}

	private int firstFree(boolean player) {
		int[] order = player ? new int[] {DRIVER, FRONT_PASSENGER, REAR_LEFT, REAR_RIGHT} : new int[] {FRONT_PASSENGER, REAR_LEFT, REAR_RIGHT, DRIVER};
		for (int s : order) {
			if (occupant(s) == null) {
				return s;
			}
		}
		return -1;
	}

	/**
	 * Puts an entity (the hunter, a family NPC...) in a seat: 0 driver, 1 front passenger, 2 rear left, 3 rear right.
	 * Moves it from another seat of this car, or off whatever it rides. Server side; false when the seat is taken.
	 */
	public boolean seat(Entity e, int seat) {
		if (this.level().isClientSide() || e == this || seat < 0 || seat >= SEATS) {
			return false;
		}
		Entity cur = occupant(seat);
		if (cur == e) {
			return true;
		}
		if (cur != null) {
			return false;
		}
		if (this.hasPassenger(e)) {
			int from = seatOf(e);
			setSeatId(from, -1);
			setSeatId(seat, e.getId());
			if (from == DRIVER) {
				engine(false);
			}
			if (seat == DRIVER && e instanceof Player) {
				engine(true);
			}
			return true;
		}
		if (e.isPassenger()) {
			e.stopRiding();
		}
		pendingSeat.put(e.getId(), seat);
		boolean ok = e.startRiding(this);
		pendingSeat.remove(e.getId());
		return ok && this.hasPassenger(e);
	}

	/** World position of a seat (where the seated entity's feet go). */
	public Vec3 seatPos(int seat) {
		double[] s = SEAT[Mth.clamp(seat, 0, SEATS - 1)];
		float yaw = this.getYRot() * Mth.DEG_TO_RAD;
		double fx = -Mth.sin(yaw), fz = Mth.cos(yaw);
		double lx = Mth.cos(yaw), lz = Mth.sin(yaw);
		return new Vec3(this.getX() + lx * s[0] + fx * s[2], this.getY() + s[1], this.getZ() + lz * s[0] + fz * s[2]);
	}

	@Override
	protected boolean canAddPassenger(Entity passenger) {
		return this.getPassengers().size() < SEATS;
	}

	@Override
	protected void addPassenger(Entity passenger) {
		super.addPassenger(passenger);
		if (this.level().isClientSide()) {
			return;
		}
		Integer pending = pendingSeat.remove(passenger.getId());
		Integer saved = savedSeats.remove(passenger.getUUID());
		int seat = pending != null ? pending : saved != null ? saved : -1;
		if (seat < 0 || occupant(seat) != null && occupant(seat) != passenger) {
			seat = firstFree(passenger instanceof Player);
		}
		setSeatId(seat, passenger.getId());
		boolean loading = this.tickCount < 2;  // passengers re-attached while the world loads: no door, no engine start
		if (!loading) {
			this.playSound(ModSounds.CAR_DOOR_OPEN, 0.9F, 0.95F + this.random.nextFloat() * 0.1F);
		}
		if (seat == DRIVER && passenger instanceof Player) {
			if (loading) {
				this.entityData.set(ENGINE, true);
			} else {
				engine(true);
			}
		}
	}

	@Override
	protected void removePassenger(Entity passenger) {
		super.removePassenger(passenger);
		if (this.level().isClientSide()) {
			return;
		}
		int seat = seatOf(passenger);
		if (seat >= 0) {
			setSeatId(seat, -1);
		}
		if (!this.isRemoved() && this.tickCount > 2) {
			this.playSound(ModSounds.CAR_DOOR_CLOSE, 1.0F, 0.95F + this.random.nextFloat() * 0.1F);
		}
		if (seat == DRIVER && !this.isRemoved()) {
			engine(false);
		}
	}

	@Override
	public LivingEntity getControllingPassenger() {
		return driver() instanceof Player p ? p : null;
	}

	@Override
	protected void positionRider(Entity passenger, Entity.MoveFunction move) {
		if (!this.hasPassenger(passenger)) {
			return;
		}
		int seat = seatOf(passenger);
		if (seat < 0) {
			seat = Math.max(0, this.getPassengers().indexOf(passenger)) % SEATS;  // seat data not synced yet
		}
		Vec3 p = seatPos(seat);
		move.accept(passenger, p.x, p.y, p.z);
		// riders turn with the car
		passenger.setYRot(passenger.getYRot() + this.deltaRotation);
		passenger.setYHeadRot(passenger.getYHeadRot() + this.deltaRotation);
		if (passenger instanceof Player) {
			clampLook(passenger);
		}
	}

	@Override
	public void onPassengerTurned(Entity passenger) {
		if (passenger instanceof Player) {
			clampLook(passenger);
		}
	}

	/** Seated players can look around ±{@link #LOOK_LIMIT} degrees from straight ahead. */
	private void clampLook(Entity passenger) {
		passenger.setYBodyRot(this.getYRot());
		float rel = Mth.wrapDegrees(passenger.getYRot() - this.getYRot());
		float clamped = Mth.clamp(rel, -LOOK_LIMIT, LOOK_LIMIT);
		passenger.yRotO += clamped - rel;
		passenger.setYRot(passenger.getYRot() + clamped - rel);
		passenger.setYHeadRot(passenger.getYRot());
	}

	@Override
	public Vec3 getDismountLocationForPassenger(LivingEntity passenger) {
		int seat = seatOf(passenger);
		boolean left = seat != FRONT_PASSENGER && seat != REAR_RIGHT;  // everyone gets out on their own side
		Vec3 base = seatPos(seat < 0 ? DRIVER : seat);
		float yaw = this.getYRot() * Mth.DEG_TO_RAD;
		Vec3 side = new Vec3(Mth.cos(yaw), 0, Mth.sin(yaw));
		Vec3 fwd = new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
		Vec3[] dirs = {left ? side : side.reverse(), left ? side.reverse() : side, fwd, fwd.reverse()};
		double[] dist = {HALF_WIDTH + 0.55, HALF_WIDTH + 0.55, HALF_LENGTH + 0.6, HALF_LENGTH + 0.6};
		for (int i = 0; i < dirs.length; i++) {
			Vec3 c = new Vec3(base.x, this.getY(), base.z).add(dirs[i].scale(dist[i]));
			for (int dy : new int[] {0, 1, -1, 2}) {
				Vec3 t = new Vec3(c.x, Math.floor(c.y) + dy, c.z);
				AABB box = passenger.getDimensions(Pose.STANDING).makeBoundingBox(t);
				BlockPos below = BlockPos.containing(t.x, t.y - 0.5, t.z);
				if (this.level().noCollision(passenger, box)
						&& !this.level().getBlockState(below).getCollisionShape(this.level(), below).isEmpty()) {
					return t;
				}
			}
		}
		return new Vec3(this.getX(), this.getBoundingBox().maxY, this.getZ());
	}

	// ------------------------------------------------------------------ driving
	@Override
	protected Vec3 getRiddenInput(Player player, Vec3 travelVector) {
		return new Vec3(player.xxa, 0.0, player.zza);
	}

	@Override
	public void travel(Vec3 input) {
		this.resetFallDistance();
		boolean driven = this.getControllingPassenger() instanceof Player;
		float throttle = driven ? (float) input.z : 0F;
		float steerIn = driven ? (float) Mth.clamp(input.x, -1.0, 1.0) : 0F;
		boolean onGround = this.onGround();
		float surface = surfaceFactor();
		float vmax = MAX_SPEED * surface * (this.isInWater() ? 0.3F : 1F);
		if (onGround) {
			if (throttle > 0.05F) {
				if (speed < -0.01F) {
					speed = Math.min(0F, speed + BRAKE);
				} else {
					speed += ACCEL * throttle * Math.max(0F, 1F - Math.max(0F, speed) / vmax);
				}
			} else if (throttle < -0.05F) {
				if (speed > 0.01F) {
					speed = Math.max(0F, speed - BRAKE);
				} else {
					speed = Math.max(-REVERSE_MAX * surface, speed - REVERSE_ACCEL);
				}
			} else {
				speed *= 0.97F;  // engine braking and rolling resistance
				if (Math.abs(speed) < 0.004F) {
					speed = 0F;
				}
			}
			if (speed > vmax) {
				speed = Math.max(vmax, speed - 0.03F);  // from the road onto the grass
			}
		}
		steer += (steerIn - steer) * 0.3F;
		if (Math.abs(steer) < 0.01F) {
			steer = 0F;
		}
		if (onGround && Math.abs(speed) > 0.003F) {
			// the faster it goes the wider it turns (radius 4..11 blocks); reversing turns the nose the other way
			float radius = 4.0F + 8.0F * Math.abs(speed);
			this.setYRot(this.getYRot() - (float) Math.toDegrees(speed / radius) * steer);
		}
		float yaw = this.getYRot() * Mth.DEG_TO_RAD;
		double vx = -Mth.sin(yaw) * speed;
		double vz = Mth.cos(yaw) * speed;
		double vy = this.getDeltaMovement().y;
		vy = onGround && vy <= 0 ? -0.08 : (vy - 0.08) * 0.98;
		if (speed != 0F && blockedAhead(speed > 0F)) {
			bump(Math.abs(speed));
			speed = 0F;
			vx = 0;
			vz = 0;
		}
		this.setDeltaMovement(vx, vy, vz);
		Vec3 before = this.position();
		this.move(MoverType.SELF, this.getDeltaMovement());
		if (this.horizontalCollision && (vx != 0 || vz != 0)) {
			double want = Math.sqrt(vx * vx + vz * vz);
			double got = this.position().subtract(before).horizontalDistance();
			if (got < want * 0.5) {
				bump(Math.abs(speed));
				speed *= 0.2F;  // a wall the step-up could not climb
			}
		}
		this.setYBodyRot(this.getYRot());
		this.setYHeadRot(this.getYRot());
		if (this.level().isClientSide() && driven) {
			simulatedAt = this.tickCount;
		}
	}

	/** Full speed on roads, paths and stone; slower on grass, dirt, snow; slowest on sand. */
	private float surfaceFactor() {
		BlockState s = this.level().getBlockState(BlockPos.containing(this.getX(), this.getY() - 0.2, this.getZ()));
		if (s.is(BlockTags.SAND) || s.is(Blocks.SOUL_SAND) || s.is(Blocks.SOUL_SOIL) || s.is(Blocks.MUD)) {
			return 0.55F;
		}
		if (s.is(Blocks.SNOW_BLOCK) || s.is(Blocks.SNOW) || s.is(Blocks.POWDER_SNOW)) {
			return 0.6F;
		}
		if (s.is(Blocks.DIRT_PATH) || s.is(Blocks.GRAVEL)) {
			return 0.9F;
		}
		if (s.is(BlockTags.DIRT) || s.is(Blocks.FARMLAND)) {
			return 0.75F;
		}
		return 1.0F;
	}

	/** Unpaved ground under the wheels (the tyres crunch gravel/dirt/grass/sand). */
	private boolean onUnpavedGround() {
		BlockState s = this.level().getBlockState(BlockPos.containing(this.getX(), this.getY() - 0.2, this.getZ()));
		return s.is(BlockTags.DIRT) || s.is(BlockTags.SAND) || s.is(Blocks.GRAVEL) || s.is(Blocks.DIRT_PATH) || s.is(Blocks.FARMLAND)
				|| s.is(Blocks.SNOW_BLOCK) || s.is(Blocks.SNOW);
	}

	/**
	 * A wall at the bumper (2+ blocks rising straight up there, which the 1-block step cannot climb) or somebody standing
	 * in front. The bounding box is square and shorter than the car, so this keeps the bonnet out of walls.
	 */
	private boolean blockedAhead(boolean forward) {
		float yaw = this.getYRot() * Mth.DEG_TO_RAD;
		double dir = forward ? 1 : -1;
		double fx = -Mth.sin(yaw) * dir, fz = Mth.cos(yaw) * dir;
		double lx = Mth.cos(yaw), lz = Mth.sin(yaw);
		double reach = HALF_LENGTH + 0.15 + Math.abs(speed);
		for (double side : new double[] {-0.85, 0.0, 0.85}) {
			double x = this.getX() + fx * reach + lx * side;
			double z = this.getZ() + fz * reach + lz * side;
			double bx = this.getX() + fx * (reach - 1.3) + lx * side;
			double bz = this.getZ() + fz * (reach - 1.3) + lz * side;
			if (solid(x, this.getY() + 1.15, z) && solid(x, this.getY() + 1.75, z) && !solid(bx, this.getY() + 1.15, bz)) {
				return true;
			}
		}
		Vec3 nose = this.position().add(fx * (HALF_LENGTH + 0.3 + Math.abs(speed)), 0.9, fz * (HALF_LENGTH + 0.3 + Math.abs(speed)));
		AABB front = new AABB(nose, nose).inflate(1.0, 0.9, 1.0);
		return !this.level().getEntities(this, front, e -> e instanceof LivingEntity && !(e instanceof CarEntity) && e.isAlive()
				&& !e.isSpectator() && !this.hasPassenger(e)).isEmpty();
	}

	private boolean solid(double x, double y, double z) {
		BlockPos p = BlockPos.containing(x, y, z);
		return !this.level().getBlockState(p).getCollisionShape(this.level(), p).isEmpty();
	}

	private void bump(float atSpeed) {
		if (atSpeed > 0.2F && bumpCooldown <= 0) {
			bumpCooldown = 10;
			this.level().playLocalSound(this.getX(), this.getY(), this.getZ(), ModSounds.CAR_BUMP, SoundSource.NEUTRAL,
					Math.min(1.2F, atSpeed * 1.4F), 0.9F + this.random.nextFloat() * 0.2F, false);
		}
	}

	// ------------------------------------------------------------------ ticking
	@Override
	public void tick() {
		float yawBefore = this.getYRot();
		super.tick();
		this.deltaRotation = Mth.wrapDegrees(this.getYRot() - yawBefore);
		this.resetFallDistance();
		if (bumpCooldown > 0) {
			bumpCooldown--;
		}
		if (this.level().isClientSide()) {
			// wheels, engine pitch and tyre noise follow the real motion (also for cars other players drive)
			float yaw = this.getYRot() * Mth.DEG_TO_RAD;
			double dx = this.getX() - this.xo;
			double dz = this.getZ() - this.zo;
			clientSpeed = (float) (dx * -Mth.sin(yaw) + dz * Mth.cos(yaw));
			wheelRotO = wheelRot;
			wheelRot += clientSpeed / WHEEL_RADIUS;
			unpaved = this.onGround() && onUnpavedGround();
			return;
		}
		if (hornCooldown > 0) {
			hornCooldown--;
		}
		int flash = this.entityData.get(FLASH);
		if (flash > 0) {
			this.entityData.set(FLASH, flash - 1);
		}
		if (isEngineOn() && !lightsManual && this.tickCount % 20 == 0) {
			this.entityData.set(LIGHTS, this.level().isDarkOutside());
		}
		ServerLevel level = (ServerLevel) this.level();
		if (lightsShown() && this.tickCount % 2 == 0) {
			beams(level);
		} else if (!lightsShown()) {
			FlashlightLights.clear(level.getServer(), beamKey(0));
			FlashlightLights.clear(level.getServer(), beamKey(1));
		}
	}

	/** Two headlight beams: light blocks where they hit, a little apart and dipped towards the road. */
	private void beams(ServerLevel level) {
		float yaw = this.getYRot() * Mth.DEG_TO_RAD;
		double fx = -Mth.sin(yaw), fz = Mth.cos(yaw);
		double lx = Mth.cos(yaw), lz = Mth.sin(yaw);
		for (int i = 0; i < 2; i++) {
			double side = i == 0 ? 0.75 : -0.75;
			Vec3 from = new Vec3(this.getX() + fx * (HALF_LENGTH - 0.2) + lx * side, this.getY() + 0.75, this.getZ() + fz * (HALF_LENGTH - 0.2) + lz * side);
			double spread = (i == 0 ? 1 : -1) * 0.08;
			Vec3 dir = new Vec3(fx + lx * spread, -0.075, fz + lz * spread).normalize();
			FlashlightLights.beam(beamKey(i), level, from, dir, 22.0, 15, this);
		}
	}

	private UUID beamKey(int i) {
		UUID u = this.getUUID();
		return new UUID(u.getMostSignificantBits() ^ 0x5CA4L, u.getLeastSignificantBits() + i + 1);
	}

	@Override
	public void remove(Entity.RemovalReason reason) {
		if (this.level() instanceof ServerLevel level) {
			FlashlightLights.clear(level.getServer(), beamKey(0));
			FlashlightLights.clear(level.getServer(), beamKey(1));
		}
		super.remove(reason);
	}

	// ------------------------------------------------------------------ engine, lights, horn, radio
	public boolean isEngineOn() {
		return this.entityData.get(ENGINE);
	}

	/** Engine on (start sound; radio static and, at night, headlights come on with it) or off. */
	public void engine(boolean on) {
		if (on == isEngineOn() || this.level().isClientSide()) {
			return;
		}
		this.entityData.set(ENGINE, on);
		if (on) {
			this.playSound(ModSounds.CAR_ENGINE_START, 1.2F, 0.95F + this.random.nextFloat() * 0.1F);
			lightsManual = false;
			this.entityData.set(LIGHTS, this.level().isDarkOutside());
			this.entityData.set(RADIO, true);
		} else {
			this.entityData.set(LIGHTS, false);
			this.entityData.set(RADIO, false);
		}
	}

	public boolean lightsOn() {
		return this.entityData.get(LIGHTS);
	}

	/** Headlights as they are seen right now (on, or blinking from the keys). */
	public boolean lightsShown() {
		int f = this.entityData.get(FLASH);
		return lightsOn() || f > 0 && (f / 4) % 2 == 0;
	}

	public void setLights(boolean on) {
		lightsManual = true;
		this.entityData.set(LIGHTS, on);
		this.playSound(ModSounds.CAR_LIGHTS, 0.6F, on ? 1.1F : 0.9F);
	}

	/** Blinks the headlights a few times (the keys' remote, or a story event). */
	public void flash() {
		this.entityData.set(FLASH, 24);
	}

	public void honk() {
		if (hornCooldown <= 0 && !this.level().isClientSide()) {
			hornCooldown = 12;
			this.playSound(ModSounds.CAR_HORN, 3.0F, 1.0F);
		}
	}

	public boolean isRadioOn() {
		return this.entityData.get(RADIO);
	}

	/** Id of the loop the radio plays ("" = static). */
	public String radioSound() {
		return this.entityData.get(RADIO_SOUND);
	}

	/** Turns the radio on with a story loop (null: back to static). Works with the engine off too. */
	public void radio(SoundEvent loop) {
		this.entityData.set(RADIO_SOUND, loop == null ? "" : loop.location().toString());
		this.entityData.set(RADIO, true);
	}

	public void radioOff() {
		this.entityData.set(RADIO, false);
		this.entityData.set(RADIO_SOUND, "");
	}

	/** The loop the radio plays, resolved on the client (null: static). */
	public SoundEvent radioLoop() {
		String id = radioSound();
		if (id.isEmpty()) {
			return null;
		}
		Identifier rid = Identifier.tryParse(id);
		return rid == null ? null : BuiltInRegistries.SOUND_EVENT.getValue(rid);
	}

	/** A control from the riding player (horn, lights, radio, steering angle for the others to see). */
	public void input(ServerPlayer p, int action, float value) {
		int seat = seatOf(p);
		if (seat < 0) {
			return;
		}
		switch (action) {
			case CarInputPayload.HORN -> {
				if (seat == DRIVER) {
					honk();
				}
			}
			case CarInputPayload.LIGHTS -> {
				if (seat == DRIVER) {
					setLights(!lightsOn());
				}
			}
			case CarInputPayload.RADIO -> {
				if (seat <= FRONT_PASSENGER) {
					this.entityData.set(RADIO, !isRadioOn());
					this.playSound(ModSounds.CAR_LIGHTS, 0.4F, 1.4F);
				}
			}
			case CarInputPayload.STEER -> {
				if (seat == DRIVER) {
					this.entityData.set(STEER, Mth.clamp(value, -1F, 1F));
				}
			}
			default -> {
			}
		}
	}

	// ------------------------------------------------------------------ client visuals
	/** Steering angle to draw (-1 right .. 1 left): the local simulation for the driver, the synced value for others. */
	public float steerAngle() {
		return this.level().isClientSide() && this.tickCount - simulatedAt <= 2 ? steer : this.entityData.get(STEER);
	}

	/** True on the client of the player driving this car. */
	public boolean simulatedHere() {
		return this.level().isClientSide() && this.tickCount - simulatedAt <= 2;
	}

	/** Signed speed (blocks/tick) seen on this client. */
	public float clientSpeed() {
		return clientSpeed;
	}

	public boolean onUnpaved() {
		return unpaved;
	}

	// ------------------------------------------------------------------ owner
	public UUID owner() {
		return owner;
	}

	public void setOwner(UUID owner) {
		this.owner = owner;
	}

	// ------------------------------------------------------------------ rules of an indestructible prop
	@Override
	protected InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (player.isSecondaryUseActive() || this.hasPassenger(player) || this.getPassengers().size() >= SEATS) {
			return InteractionResult.PASS;
		}
		if (!this.level().isClientSide()) {
			int seat = occupant(DRIVER) == null ? DRIVER : nearestFreeSeat(player.position());
			return seat >= 0 && this.seat(player, seat) ? InteractionResult.SUCCESS : InteractionResult.PASS;
		}
		return InteractionResult.SUCCESS;
	}

	private int nearestFreeSeat(Vec3 from) {
		int best = -1;
		double bd = Double.MAX_VALUE;
		for (int s = 0; s < SEATS; s++) {
			if (occupant(s) == null) {
				double d = seatPos(s).distanceToSqr(from);
				if (d < bd) {
					bd = d;
					best = s;
				}
			}
		}
		return best;
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		// only /kill and the void get rid of it
		return source.is(DamageTypeTags.BYPASSES_INVULNERABILITY) && super.hurtServer(level, source, amount);
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean isPushedByFluid() {
		return false;
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return false;
	}

	@Override
	protected Entity.MovementEmission getMovementEmission() {
		return Entity.MovementEmission.NONE;
	}

	@Override
	public AABB getBoundingBoxForCulling() {
		return this.getBoundingBox().inflate(HALF_LENGTH - 1.0, 0.3, HALF_LENGTH - 1.0);
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		super.addAdditionalSaveData(out);
		out.putBoolean("Engine", isEngineOn());
		out.putBoolean("Lights", lightsOn());
		out.putBoolean("LightsManual", lightsManual);
		out.putBoolean("Radio", isRadioOn());
		out.putString("RadioSound", radioSound());
		out.putString("Owner", owner == null ? "" : owner.toString());
		for (int i = 0; i < SEATS; i++) {
			Entity e = occupant(i);
			out.putString("Seat" + i, e == null ? "" : e.getUUID().toString());
		}
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		super.readAdditionalSaveData(in);
		this.entityData.set(ENGINE, in.getBooleanOr("Engine", false));
		this.entityData.set(LIGHTS, in.getBooleanOr("Lights", false));
		this.lightsManual = in.getBooleanOr("LightsManual", false);
		this.entityData.set(RADIO, in.getBooleanOr("Radio", false));
		this.entityData.set(RADIO_SOUND, in.getStringOr("RadioSound", ""));
		this.owner = parse(in.getStringOr("Owner", ""));
		for (int i = 0; i < SEATS; i++) {
			UUID u = parse(in.getStringOr("Seat" + i, ""));
			if (u != null) {
				savedSeats.put(u, i);
			}
		}
	}

	private static UUID parse(String s) {
		try {
			return s == null || s.isEmpty() ? null : UUID.fromString(s);
		} catch (IllegalArgumentException ex) {
			return null;
		}
	}
}
