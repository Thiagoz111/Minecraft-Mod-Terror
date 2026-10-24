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
 * behind him, and an old woman breathes: the Nona sits in the back seat. When he looks up into the rear-view mirror
 * (or after a while his eyes are drawn there: the rosary hanging from it rattles), she is no longer in the back: she is
 * leaning in between the front seats, her face at his shoulder, and his head snaps round to her. She grins; she lunges:
 * the final jumpscare, cut to black. If he turns round to the back seat instead, she lunges from there. Posts
 * {@code final:fin} (the act script shows DEAD LINE and sends him home). On foot (he never got in the car) the same
 * happens with her right behind him.
 */
public class SpFinalAuto extends HorrorEvent {
	private static final int ARRIVE = 70, DRAW = 20 * 7, RATTLE = 40, STARE = 22, CUT = 18, END = 50;
	/** The rear-view mirror in the car's frame (blocks: forward, up), from the car model (tools/models/ent_auto.py). */
	private static final double MIRROR_FWD = 0.6, MIRROR_UP = 1.72;
	/** Where she leans in: between the front seats, beside his head (forward, toward the middle of the car). */
	private static final double LEAN_FWD = 0.0, LEAN_IN = 0.45;
	/** How much lower her head is in POSE_SIT than standing (NonaModel: sew_calm's body row, 5 texels). */
	private static final double SIT_DROP = 5.0 / 16.0;

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
		c.put("clock", 0);
	}

	@Override
	public boolean tick(Ctx c) {
		CarEntity car = c.get("car");
		if (car != null && (car.isRemoved() || c.p.getVehicle() != car)) {
			car = null;  // he got out (or the car is gone): she is simply behind him
			c.put("car", null);
		}
		int revealAt = c.get("revealAt");
		// her clock only runs while he is not hidden (the shed in the yard is a hiding place too): never on a hidden hunter
		boolean held = revealAt < 0 && Apparitions.hidden(c.p);
		int t = c.<Integer>get("clock") + (held ? 0 : 1);
		c.put("clock", t);
		if (held) {
			return false;
		}
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
				boolean seated = car != null && n.isPassenger() && n.getVehicle() == car;
				if (seated && (lookingInMirror(c, car) || t > ARRIVE + DRAW + RATTLE)) {
					// in the mirror, the back seat -- and she is not in it any more: she is at his shoulder
					FamilyEntity lean = leanIn(c, car, n);
					if (lean != null) {
						c.put("e", lean);
					}
					c.put("revealAt", t);
				} else if (Apparitions.watches(c, n, 40F) || turnedBack(c, car)) {
					c.put("revealAt", t);  // he turned round: there she is
				} else if (seated && t == ARRIVE + DRAW) {
					// his eyes are drawn up to the mirror: the rosary hanging from it rattles by itself
					c.run.sound(ModSounds.POLTER_OBJETO, mirror(car), 0.5F, 1.6F);
					c.p.lookAt(EntityAnchorArgument.Anchor.EYES, mirror(car));
				} else if (!seated && t > ARRIVE + DRAW) {
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
		if (k == STARE + CUT + 44 && n != null && !n.isPassenger()) {
			Apparitions.vanish(n, false);  // in the black (one still in a seat waits for stop(): no car door heard)
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
		if (car != null) {
			at = car.seatPos(CarEntity.REAR_RIGHT);
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
		boolean seated = false;
		if (car != null) {
			n.setAction(FamilyEntity.POSE_SIT);
			n.setNoGravity(true);  // the seat holds her (the car places its riders every tick)
			// the back seat behind him (any free one; the front passenger seat if the back is full)
			for (int seat : new int[] {CarEntity.REAR_RIGHT, CarEntity.REAR_LEFT, CarEntity.FRONT_PASSENGER}) {
				if (car.occupant(seat) == null && car.seat(n, seat)) {
					seated = true;
					c.run.sound(ModSounds.SP_ASIENTO, car.seatPos(seat), 0.9F, 0.9F);
					break;
				}
			}
		}
		if (!seated) {
			if (car != null) {
				// a full car: she stands right behind it, at the boot, staring at him through the rear window
				Vec3 boot = car.position().subtract(Stage.forward(car.getYRot()).scale(CarEntity.HALF_LENGTH + 0.6));
				Vec3 floor = Stage.stand(c.run, boot);
				Vec3 to = floor != null ? floor : boot;
				n.teleportTo(to.x, to.y, to.z);
				n.face(Apparitions.yawTo(to, c.p.position()));
				n.setNoGravity(false);
			}
			n.setAction(FamilyEntity.POSE_STAND_WALKER);
		}
		c.run.sound(ModSounds.ANDADOR_SQUEAK, at, 0.7F, 0.75F);
		c.put("e", n);
	}

	/** World position of the rear-view mirror of the car. */
	private static Vec3 mirror(CarEntity car) {
		return car.position().add(Stage.forward(car.getYRot()).scale(MIRROR_FWD)).add(0, MIRROR_UP, 0);
	}

	/** He looks up into the rear-view mirror (it is right there on his screen, near the middle). */
	private static boolean lookingInMirror(Ctx c, CarEntity car) {
		return c.run.looking(c.p, mirror(car), 14F, 4.0);
	}

	/**
	 * Out of the back seat (while his eyes are on the mirror) and in between the front seats, her face by his. The one in
	 * the seat just stops being there (made invisible, not taken out: getting off a car seat sounds like its door); the
	 * one at his shoulder is a second actor of this run. Returns it (null: she could not be put there).
	 */
	private static FamilyEntity leanIn(Ctx c, CarEntity car, FamilyEntity seated) {
		int seat = car.seatOf(c.p);
		double side = seat == CarEntity.FRONT_PASSENGER || seat == CarEntity.REAR_RIGHT ? -1.0 : 1.0;  // + = the car's left
		float yaw = car.getYRot();
		// the car's left (+) / right (-) axis is (cos yaw, sin yaw): see CarEntity.seatPos
		Vec3 left = new Vec3(Mth.cos(yaw * Mth.DEG_TO_RAD), 0, Mth.sin(yaw * Mth.DEG_TO_RAD));
		Vec3 face = c.p.getEyePosition().add(left.scale(-side * LEAN_IN)).add(Stage.forward(yaw).scale(LEAN_FWD));
		c.run.sound(ModSounds.SP_ASIENTO, seated.position(), 1.0F, 0.75F);
		FamilyEntity n = Apparitions.spawn(c, FamilyEntities.NONA, face, Apparitions.yawTo(face, c.p.position()));
		if (n == null) {
			return null;
		}
		seated.setInvisible(true);
		n.setVariant(FamilyEntity.LOOK_POSSESSED);
		n.propSounds = false;
		n.setNoGravity(true);
		// the seated body (no walker in a car: every standing pose of hers shows it); it sits SIT_DROP lower than standing
		n.setAction(FamilyEntity.POSE_SIT);
		n.watch(c.p);
		Vec3 feet = face.subtract(0, n.getEyeHeight() - SIT_DROP, 0);
		n.teleportTo(feet.x, feet.y, feet.z);
		n.face(Apparitions.yawTo(feet, c.p.position()));
		Apparitions.sound(c, ModSounds.APARICION_NONA_RESPIRA, face, 1.2F, 0.8F);
		c.p.lookAt(EntityAnchorArgument.Anchor.EYES, face);
		return n;
	}

	/** His head turned well round toward the back (in the car he can look 120 degrees either way). */
	private static boolean turnedBack(Ctx c, CarEntity car) {
		if (car == null) {
			return false;
		}
		return Math.abs(Mth.wrapDegrees(c.p.getYHeadRot() - car.getYRot())) > 95F;
	}

	@Override
	public void stop(Ctx c) {
		Apparitions.despawnAll(c);  // (a seated actor leaves its seat as it is removed)
	}

	@Override
	public int maxTicks() {
		return 20 * 60 * 20;  // the timeline itself ends in ~17 s of unhidden time; this only bounds a hunter who stays hidden
	}
}
