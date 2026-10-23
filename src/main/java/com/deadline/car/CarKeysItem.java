package com.deadline.car;

import com.deadline.DeadLine;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The car keys. Right click: the car flashes its headlights and honks (the remote of a car that never had one); if the
 * car is far (more than {@link #FAR} blocks), unloaded, in another dimension or lost, it is brought behind you (a new
 * one if it cannot be found).
 */
public class CarKeysItem extends Item {
	public static final double FAR = 160.0;

	public CarKeysItem(Item.Properties props) {
		super(props);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		if (player instanceof ServerPlayer sp) {
			CarEntity car = find(sp);
			if (car != null && car.level() == sp.level() && car.distanceTo(sp) <= FAR) {
				car.flash();
				car.honk();
			} else {
				Vec3 back = sp.position().subtract(sp.getLookAngle().multiply(1, 0, 1).normalize().scale(5.0));
				CarEntity brought = bring(sp, car, back, sp.getYRot());
				if (brought != null) {
					brought.flash();
					sp.displayClientMessage(Component.translatable("deadline.car.brought"), true);
				}
			}
			sp.getCooldowns().addCooldown(player.getItemInHand(hand), 30);
		}
		return InteractionResult.SUCCESS;
	}

	/** The owner's current car if it is loaded anywhere (null otherwise). */
	public static CarEntity find(ServerPlayer p) {
		MinecraftServer server = p.level().getServer();
		UUID id = CarData.get(server).car(p.getUUID());
		if (id == null) {
			return null;
		}
		for (ServerLevel level : server.getAllLevels()) {
			Entity e = level.getEntity(id);
			if (e instanceof CarEntity c && !c.isRemoved()) {
				return c;
			}
		}
		return null;
	}

	/**
	 * Brings the owner's car near `at` facing `yaw` (teleporting it when it is loaded in the same level, otherwise a new
	 * car replaces it). Null if there is no room anywhere around.
	 */
	public static CarEntity bring(ServerPlayer p, CarEntity car, Vec3 at, float yaw) {
		ServerLevel level = p.level();
		Vec3 spot = findSpot(level, at, p.position(), yaw);
		if (spot == null) {
			return null;
		}
		if (car != null && car.level() == level) {
			car.ejectPassengers();
			car.teleportTo(level, spot.x, spot.y, spot.z, java.util.Set.of(), yaw, 0F, false);
			car.setDeltaMovement(Vec3.ZERO);
			return car;
		}
		if (car != null) {
			car.ejectPassengers();
			car.discard();
		}
		return spawn(p, spot, yaw);
	}

	/** A new car for the player at a spot (becomes their car; the old one is discarded wherever it loads). */
	public static CarEntity spawn(ServerPlayer p, Vec3 spot, float yaw) {
		ServerLevel level = p.level();
		CarEntity car = Cars.CAR.create(level, EntitySpawnReason.EVENT);
		if (car == null) {
			return null;
		}
		car.snapTo(spot.x, spot.y, spot.z, yaw, 0F);
		car.setYHeadRot(yaw);
		car.setYBodyRot(yaw);
		car.setOwner(p.getUUID());
		if (!level.addFreshEntity(car)) {
			return null;
		}
		CarData.get(level.getServer()).setCar(p.getUUID(), car.getUUID());
		DeadLine.LOGGER.info("Car for {} at {}", p.getName().getString(), spot);
		return car;
	}

	/**
	 * Case accepted (overworld case): the keys (if the hunter has none) and, unless they already have a car within 64
	 * blocks, the car 4 blocks away, nose pointing at the house.
	 */
	public static void giveForCase(ServerPlayer p, Vec3 site) {
		if (!p.getInventory().contains(s -> s.is(Cars.CAR_KEYS))) {
			ItemStack keys = new ItemStack(Cars.CAR_KEYS);
			if (!p.getInventory().add(keys)) {
				p.drop(keys, false);
			}
		}
		ServerLevel level = p.level();
		if (!level.getEntitiesOfClass(CarEntity.class, p.getBoundingBox().inflate(64)).isEmpty()) {
			return;
		}
		float yaw = site == null ? p.getYRot() : (float) Math.toDegrees(Math.atan2(-(site.x - p.getX()), site.z - p.getZ()));
		Vec3 look = p.getLookAngle().multiply(1, 0, 1);
		if (look.lengthSqr() < 1.0E-4) {
			look = new Vec3(0, 0, 1);
		}
		Vec3 at = p.position().add(look.normalize().scale(4.0));
		Vec3 spot = findSpot(level, at, p.position(), yaw);
		if (spot != null) {
			CarEntity old = find(p);
			if (old != null) {
				old.ejectPassengers();
				old.discard();
			}
			spawn(p, spot, yaw);
		}
	}

	/**
	 * Free ground for a car facing `yaw` near `at`: the spot itself, then around it (4-8 blocks from `from`), a few
	 * blocks up or down; last resort, the surface at `at`.
	 */
	static Vec3 findSpot(ServerLevel level, Vec3 at, Vec3 from, float yaw) {
		if (fits(level, at, yaw)) {
			return new Vec3(at.x, Math.floor(at.y), at.z);
		}
		for (int dy : new int[] {1, -1, 2, -2, 3}) {
			Vec3 v = new Vec3(at.x, Math.floor(at.y) + dy, at.z);
			if (fits(level, v, yaw)) {
				return v;
			}
		}
		for (double r : new double[] {4.5, 6.5, 8.5}) {
			for (int k = 0; k < 12; k++) {
				double a = k * Math.PI / 6;
				for (int dy : new int[] {0, 1, -1, 2, -2}) {
					Vec3 v = new Vec3(from.x + Math.cos(a) * r, Math.floor(from.y) + dy, from.z + Math.sin(a) * r);
					if (fits(level, v, yaw)) {
						return v;
					}
				}
			}
		}
		int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mth.floor(at.x), Mth.floor(at.z));
		return new Vec3(at.x, y, at.z);
	}

	/** Room for the whole (rotated) car body on solid, dry ground. */
	private static boolean fits(ServerLevel level, Vec3 v, float yaw) {
		float r = yaw * Mth.DEG_TO_RAD;
		double fx = Math.abs(Mth.sin(r)), fz = Math.abs(Mth.cos(r));
		double hx = fx * CarEntity.HALF_LENGTH + fz * CarEntity.HALF_WIDTH;
		double hz = fz * CarEntity.HALF_LENGTH + fx * CarEntity.HALF_WIDTH;
		AABB box = new AABB(v.x - hx, v.y + 0.05, v.z - hz, v.x + hx, v.y + 2.0, v.z + hz);
		if (!level.noCollision(box)) {
			return false;
		}
		BlockPos below = BlockPos.containing(v.x, v.y - 0.5, v.z);
		return !level.getBlockState(below).getCollisionShape(level, below).isEmpty() && level.getFluidState(below.above()).isEmpty();
	}

	/** A car that loads while its owner already has another one (it was replaced by the keys) goes away. */
	static boolean stale(CarEntity car) {
		if (!(car.level() instanceof ServerLevel level) || car.owner() == null) {
			return false;
		}
		UUID current = CarData.get(level.getServer()).car(car.owner());
		return current != null && !current.equals(car.getUUID());
	}
}
