package com.deadline.horror.casa.setpiece;

import com.deadline.car.CarEntity;
import com.deadline.director.casa.CasaScript;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.dog.Choripan;
import com.deadline.horror.casa.dog.ChoripanEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Act 1, the drive (design 2): halfway there, in the headlights, Choripán standing on two legs in the middle of the road,
 * his back to the car. The headlights flicker -- and he is not there any more. If the hunter drives past without seeing
 * him (looking elsewhere, lights off, too fast), he is quietly taken away and put on the road again a little further on
 * (up to three times). The radio, all static until then, hums a child's lullaby while he stands there.
 * <p>Fired by CasaScript once the car is 60-150 blocks from the house; it ends when he has been seen (or 45 blocks
 * from the house, or after three misses). No run event: the drive goes on.
 */
public class SpPerroCamino extends HorrorEvent {
	private static final int TRIES = 3;
	/** He is put on the road this far ahead (beyond the headlights' reach: he comes into the light, never pops in). */
	private static final double AHEAD_MIN = 26.0, AHEAD_MAX = 34.0;
	private static final int WAIT = 0, FLICKER = 1;

	public SpPerroCamino() {
		super("sp_perro_camino", Kind.SETPIECE);
		this.acts(1, 1).intensity(3).cooldown(30).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		return !Apparitions.hidden(c.p) && c.p.level() == c.run.level && !HouseQuery.inHouse(c.run, c.p);
	}

	@Override
	public void start(Ctx c) {
		c.put("tries", 0);
		c.put("next", 0);
		c.put("phase", WAIT);
	}

	@Override
	public boolean tick(Ctx c) {
		ServerPlayer p = c.p;
		if (p.level() != c.run.level) {
			return true;
		}
		double toHouse = p.position().distanceTo(CasaScript.arrival(c.run));
		ChoripanEntity dog = c.get("dog");
		int phase = c.<Integer>get("phase");
		if (phase == FLICKER) {
			return flicker(c, dog);
		}
		if (Apparitions.gone(dog)) {
			if (toHouse < 45.0 || c.<Integer>get("tries") >= TRIES) {
				return true;
			}
			if (c.t >= c.<Integer>get("next") && !place(c)) {
				c.put("next", c.t + 20);
			}
			return false;
		}
		Entity mover = p.getVehicle() != null ? p.getVehicle() : p;
		double dist = mover.position().distanceTo(dog.position());
		// seen = looked at while he stands in light (the headlights' pool), or simply close
		BlockPos at = dog.blockPosition().above();
		boolean lit = c.level().getBrightness(LightLayer.BLOCK, at) >= 6 || !c.level().isDarkOutside() || dist < 11.0;
		Apparitions.Gaze g = Apparitions.gaze(c);
		g.update(lit && dist < 30.0 && Apparitions.watches(c, dog, 24F));
		if (g.seen >= 8 || dist < 8.5) {
			c.put("phase", FLICKER);
			c.put("flick", c.t);
			CarEntity car = p.getVehicle() instanceof CarEntity ce ? ce : null;
			c.put("lights", car != null && car.lightsOn());
			return false;
		}
		// driven past without seeing him (he is behind the car), or left far behind: taken away, tried again further on
		Vec3 fwd = Stage.forward(mover.getYRot());
		Vec3 to = dog.position().subtract(mover.position());
		if (to.x * fwd.x + to.z * fwd.z < -3.0 || dist > 48.0) {
			Choripan.remove(c.run);
			c.put("dog", null);
			c.put("tries", c.<Integer>get("tries") + 1);
			c.put("next", c.t + 20 * 15);
			Apparitions.gaze(c).seen = 0;
		}
		return c.t > 20 * 240;
	}

	/** The headlights die twice; when they come back he is gone. The radio goes back to plain static. */
	private boolean flicker(Ctx c, ChoripanEntity dog) {
		int k = c.t - c.<Integer>get("flick");
		CarEntity car = c.p.getVehicle() instanceof CarEntity ce ? ce : null;
		boolean wasOn = Boolean.TRUE.equals(c.get("lights"));
		if (k == 0) {
			c.run.sound(ModSounds.CAR_RADIO_STATIC, c.p.getEyePosition(), 1.3F, 0.7F);
			Fx.shake(c.p, 0.3F, 10);
			if (car != null) {
				car.radio(null);
			}
		}
		if (car != null && wasOn) {
			if (k == 0 || k == 6 || k == 14) {
				car.setLights(false);
			} else if (k == 3 || k == 12 || k == 18) {
				car.setLights(true);
			}
		} else if (k == 4) {
			Fx.fade(c.p, 12);  // on foot (or lights already off): a blink of black
		}
		if (k == 9) {
			// in the dark of the second cut: gone
			if (!Apparitions.gone(dog)) {
				Choripan.remove(c.run);
			}
			c.put("dog", null);
		}
		return k >= 20;
	}

	/** Puts him on the road ahead: on the ground, in the line the car is driving along, his back to it. */
	private boolean place(Ctx c) {
		ServerPlayer p = c.p;
		Entity mover = p.getVehicle() != null ? p.getVehicle() : p;
		Vec3 vel = mover.getDeltaMovement().multiply(1, 0, 1);
		Vec3 dir = vel.lengthSqr() > 0.0025 ? vel.normalize() : Stage.forward(mover.getYRot());
		double ahead = Mth.clamp(AHEAD_MIN + vel.length() * 8.0, AHEAD_MIN, AHEAD_MAX);
		Vec3 spot = mover.position().add(dir.scale(ahead));
		BlockPos col = BlockPos.containing(spot);
		if (!c.level().isLoaded(col)) {
			return false;
		}
		int y = c.level().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col.getX(), col.getZ());
		BlockPos feet = new BlockPos(col.getX(), y, col.getZ());
		if (Math.abs(y - mover.getY()) > 6.0 || !HouseQuery.standable(c.run, feet) || !c.level().getFluidState(feet.below()).isEmpty()) {
			return false;
		}
		Vec3 pos = new Vec3(spot.x, Apparitions.floorY(c.run, feet), spot.z);
		if (Apparitions.sees(c, pos.add(0, 0.8, 0), 70F) && c.level().getBrightness(LightLayer.BLOCK, feet.above()) >= 6) {
			return false;  // never appear inside the light, under his eyes
		}
		ChoripanEntity dog = Choripan.standAt(c.run, pos, Stage.yawTo(mover.position(), pos));
		if (dog == null) {
			return false;
		}
		c.put("dog", dog);
		if (p.getVehicle() instanceof CarEntity car) {
			car.radio(ModSounds.SP_RADIO_CUNA);  // between the static, a child humming a lullaby
		}
		return true;
	}

	@Override
	public void stop(Ctx c) {
		ChoripanEntity dog = c.get("dog");
		if (!Apparitions.gone(dog) && Choripan.get(c.run) == dog) {
			Choripan.remove(c.run);
		}
		if (c.p.getVehicle() instanceof CarEntity car) {
			if (Boolean.TRUE.equals(c.get("lights")) && !car.lightsOn()) {
				car.setLights(true);
			}
			if (car.isRadioOn() && !car.radioSound().isEmpty()) {
				car.radio(null);
			}
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 250;
	}
}
