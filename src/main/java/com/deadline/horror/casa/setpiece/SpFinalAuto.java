package com.deadline.horror.casa.setpiece;

import com.deadline.car.CarEntity;
import com.deadline.casa.FamilyEntities;
import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import net.minecraft.commands.arguments.EntityAnchorArgument;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * The ending (design 2, "Final"): grey dawn, the house dark behind him. He gets in the car; the engine starts; the
 * radio is static for a moment and then nothing at all. The back seat creaks. A wheel squeaks -- the walker's wheel --
 * behind him, and an old woman breathes. In the mirror, over his shoulder: the Nona sits in the back seat, staring at
 * him (if he does not turn round, his eyes are drawn there anyway). She lunges: the final jumpscare, cut to black.
 * Posts {@code final:fin} (the act script shows DEAD LINE and sends him home). On foot (he never got in the car) the
 * same happens with her right behind him.
 */
public class SpFinalAuto extends HorrorEvent {
	private static final int ARRIVE = 70, DRAW = 20 * 7, STARE = 22, CUT = 18, END = 50;

	public SpFinalAuto() {
		super("sp_final_auto", Kind.SETPIECE);
		this.acts(6, 6).intensity(5).cooldown(600).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		return !Apparitions.hidden(c.p) && !HouseQuery.inHouse(c.run, c.p);
	}

	@Override
	public void start(Ctx c) {
		CarEntity car = c.p.getVehicle() instanceof CarEntity ce ? ce : null;
		c.put("car", car);
		if (car != null) {
			if (car.seatOf(c.p) == CarEntity.DRIVER) {
				car.engine(true);
			}
			car.radio(null);  // static
		}
		c.put("revealAt", -1);
	}

	@Override
	public boolean tick(Ctx c) {
		CarEntity car = c.get("car");
		int t = c.t;
		int revealAt = c.get("revealAt");
		if (revealAt < 0) {
			if (t == 40 && car != null) {
				car.radioOff();  // silence
			}
			if (t == ARRIVE) {
				arrive(c, car);
			}
			FamilyEntity n = c.get("e");
			if (t > ARRIVE && n == null) {
				c.put("revealAt", t);  // she could not be put there: only her face, then
				return false;
			}
			if (t > ARRIVE && n != null) {
				if (t % 45 == 0) {
					Apparitions.sound(c, ModSounds.APARICION_NONA_RESPIRA, n.getEyePosition(), 0.9F, 0.85F);
				}
				// he turns round (or glances back) and sees her; or his eyes are drawn there
				boolean sees = Apparitions.watches(c, n, 40F);
				if (sees || turnedBack(c, car)) {
					c.put("revealAt", t);
				} else if (t > ARRIVE + DRAW) {
					c.p.lookAt(EntityAnchorArgument.Anchor.EYES, n.getEyePosition());
					c.put("revealAt", t);
				}
			}
			return false;
		}
		int k = t - revealAt;
		FamilyEntity n = c.get("e");
		if (k == 1 && n != null) {
			n.setExpression(FamilyEntity.EXPR_STARE | FamilyEntity.EXPR_SMILE);
			Apparitions.sound(c, ModSounds.HUNT_JAW, n.getEyePosition(), 0.8F, 1.1F);
		}
		if (k == STARE) {
			Fx.jumpscare(c.p, "nona_rota");
			c.haunt.jumpscared();
			Fx.shake(c.p, 2.4F, 24);
			c.run.sound(ModSounds.HUNT_SCREAM, c.p.getEyePosition(), 2.2F, 1.0F);
		}
		if (k == STARE + CUT) {
			Fx.fade(c.p, 120);  // cut to black: full black ~43-77 ticks in; the case ends inside it
		}
		if (k == STARE + CUT + 44 && n != null) {
			Apparitions.despawnAll(c);  // in the black
		}
		return endNow(c, k >= STARE + CUT + END ? 1 : 0);
	}

	/** Posts the end once (returns true so the event finishes with it). */
	private static boolean endNow(Ctx c, int go) {
		if (go <= 0 || c.get("posted") != null) {
			return c.get("posted") != null;
		}
		c.put("posted", true);
		c.run.post("final:fin");
		return true;
	}

	/** The back seat creaks; the walker squeaks behind him; she is there. */
	private void arrive(Ctx c, CarEntity car) {
		Vec3 at;
		float yaw;
		if (car != null && !car.isRemoved()) {
			Vec3 seat = car.seatPos(CarEntity.REAR_RIGHT);
			at = seat;
			yaw = car.getYRot();
		} else {
			Vec3 behind = HouseQuery.behind(c.run, c.p, 1.6);
			at = behind != null ? behind : c.p.position().subtract(Stage.look(c.p).scale(1.4));
			yaw = Apparitions.yawTo(at, c.p.position());
		}
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, at, yaw);
		if (n == null) {
			return;
		}
		n.setVariant(FamilyEntity.LOOK_POSSESSED);
		n.propSounds = false;
		n.watch(c.p);
		if (car != null && !car.isRemoved()) {
			n.setAction(FamilyEntity.POSE_SIT);
			car.seat(n, CarEntity.REAR_RIGHT);
			c.run.sound(ModSounds.SP_ASIENTO, at, 0.9F, 0.9F);
		} else {
			n.setAction(FamilyEntity.POSE_STAND_WALKER);
		}
		c.run.sound(ModSounds.ANDADOR_SQUEAK, at, 0.7F, 0.75F);
		c.put("e", n);
	}

	/** His head turned well round toward the back (in the car he can look 120 degrees either way). */
	private static boolean turnedBack(Ctx c, CarEntity car) {
		float ahead = car != null ? car.getYRot() : c.p.getYRot();
		if (car == null) {
			return false;
		}
		return Math.abs(Mth.wrapDegrees(c.p.getYHeadRot() - ahead)) > 95F;
	}

	@Override
	public void stop(Ctx c) {
		FamilyEntity n = c.get("e");
		if (n != null && n.isPassenger()) {
			n.stopRiding();
		}
		Apparitions.despawnAll(c);
	}

	@Override
	public int maxTicks() {
		return ARRIVE + DRAW + 20 * 12;
	}
}
