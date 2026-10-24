package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * Act 2, the arrival (design 2): he has knocked twice. Slow steps inside, the walker's wheel squeaking closer. The bolt,
 * twice. The door opens by itself, slowly: the Nona in the doorway, backlit by the one hall lamp, her face in shadow,
 * her walker. She stares at him four seconds without blinking. She smiles -- the dentures far too white. She shuffles
 * aside without taking her eyes off him, and her head keeps following him further round than a neck should.
 * <p>Meanwhile the rest of the family is already sitting at the dinner table (out of sight, deep in the house), with
 * the dog growling under it: {@link SpCena} finds them there. When he is in, the Nona turns and shuffles off to the
 * head of the table. The act script closes and bolts the door behind him.
 */
public class SpLlegada extends HorrorEvent {
	/** Timeline (ticks): the steps, the bolt twice, the door; she stares 4 s without blinking, smiles, steps aside. */
	private static final int SQUEAK_1 = 0, BOLT_1 = 100, BOLT_2 = 117, NONA = 112, OPEN = 136, SMILE = OPEN + 80, ASIDE = SMILE + 24;
	/** Ticks after the door opens that he gets to come in before the set piece lets go (she keeps standing there). */
	private static final int WAIT_IN = 20 * 90;

	public SpLlegada() {
		super("sp_llegada", Kind.SETPIECE);
		this.acts(2, 2).intensity(3).cooldown(60).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		return Stage.has(c.run, "nona_umbral") && c.run.def.doors.containsKey("entrada");
	}

	@Override
	public void start(Ctx c) {
		// the family at the table already: Marta, Jorge, Lucía, Toti and the dog (the Nona comes to the door)
		for (String who : new String[] {Stage.MARTA, Stage.JORGE, Stage.TOTI}) {
			FamilyEntity f = Stage.seat(c.run, who);
			if (f != null) {
				f.watchPlayers(false);
				f.lookAt(SpCena.plate(c.run, who));
			}
		}
		Stage.seatLucia(c.run);
		Stage.dogUnderTable(c.run);
		c.put("in", -1);
	}

	@Override
	public boolean tick(Ctx c) {
		int t = c.t;
		if (t == 0 && !canRun(c)) {
			// a site without the doorway markers: the door simply opens (fired without its conditions by the script)
			c.run.door("entrada", true, false);
			c.put("done", true);
			return true;
		}
		Vec3 umbral = c.run.at("nona_umbral");
		Vec3 hall = Stage.has(c.run, "hall") ? c.run.at("hall") : umbral.add(Stage.forward(c.run.yaw("nona_umbral")).scale(-3.0));
		Vec3 door = HouseQuery.doorPos(c.run, "entrada");
		// slow steps coming to the door: the walker's wheel, closer each time
		if (t >= SQUEAK_1 && t <= 84 && (t - SQUEAK_1) % 28 == 0) {
			float k = (t - SQUEAK_1) / 84F;
			Vec3 at = hall.lerp(umbral, k);
			c.run.sound(ModSounds.ANDADOR_SQUEAK, at, 0.35F + 0.35F * k, 0.82F);
			c.run.sound(ModSounds.HORROR_FOOTSTEPS, at, 0.25F + 0.25F * k, 0.7F);
		}
		if (t == BOLT_1 || t == BOLT_2) {
			c.run.sound(ModSounds.SP_CERROJO, door, 1.0F, t == BOLT_1 ? 0.95F : 0.85F);
		}
		if (t == NONA) {
			// behind the closed door: nobody sees her arrive. The hall lamp lights her from behind.
			FamilyEntity n = Stage.member(c.run, Stage.NONA, umbral, c.run.yaw("nona_umbral"));
			if (n != null) {
				n.setAction(FamilyEntity.POSE_STAND_WALKER);
				n.propSounds = false;
				n.setExpression(FamilyEntity.EXPR_STARE);
				n.watch(c.p);
				// under the dinner table the dog's head comes round to where she is, and he growls
				com.deadline.horror.casa.dog.ChoripanEntity dog = com.deadline.horror.casa.dog.Choripan.get(c.run);
				if (dog != null) {
					dog.watch(n);
				}
			}
			if (c.run.def.groups.containsKey("luces_hall")) {
				c.run.lights("luces_hall", true);
			}
		}
		if (t == OPEN) {
			c.run.door("entrada", true, false);
			c.run.sound(ModSounds.SP_PUERTA_CRUJE, door, 1.1F, 0.9F);
		}
		FamilyEntity n = Stage.member(c.run, Stage.NONA);
		if (n == null) {
			if (t > OPEN) {
				c.put("done", true);  // no Nona (a site without her): the door simply opened
				return true;
			}
			return false;
		}
		// he walks right up to her before she has moved: she smiles and steps aside at once (never walked through)
		Integer early = c.get("early");
		if (early == null && t > OPEN + 20 && t < ASIDE && n.distanceTo(c.p) < 2.4) {
			early = t;
			c.put("early", early);
		}
		int smileAt = early != null ? Math.min(SMILE, early) : SMILE;
		int asideAt = early != null ? early + 12 : ASIDE;
		if (t == smileAt) {
			n.setExpression(FamilyEntity.EXPR_STARE | FamilyEntity.EXPR_SMILE);
			c.run.sound(ModSounds.HUNT_JAW, n.getEyePosition(), 0.45F, 1.25F);
		}
		if (t == asideAt) {
			Vec3 aside = aside(c, umbral);
			if (aside != null) {
				n.walkTo(aside, 0.3);
			}
			c.put("aside", aside);
		}
		if (t > asideAt && c.get("aside") != null && n.hasArrived() && c.get("turned") == null) {
			// she stands aside facing into the hall; the head stays on him, round past her own shoulder
			c.put("turned", true);
			n.face(c.run.yaw("nona_umbral") + 180F + (c.rnd.nextBoolean() ? 25F : -25F));
		}
		int in = c.<Integer>get("in");
		if (in < 0 && t > OPEN && Stage.pastThreshold(c.run, c.p)) {
			c.put("in", t);
			in = t;
		}
		if (in >= 0 && t - in == 50) {
			// he is in: she lets him go and shuffles off to the head of the table
			n.setExpression(0);
			n.watch(null);
			n.propSounds = true;
			if (Stage.has(c.run, "silla_1")) {
				n.walkTo(c.run.at("silla_1"), 0.45);
			}
			c.put("done", true);
			return true;
		}
		if (t > OPEN + WAIT_IN) {
			c.put("done", true);
			return true;
		}
		return false;
	}

	/** A free spot beside the doorway, a little back into the hall (the side with more room). */
	private static Vec3 aside(Ctx c, Vec3 umbral) {
		float yaw = c.run.yaw("nona_umbral");
		Vec3 back = Stage.forward(yaw).scale(-0.7);
		Vec3 side = Stage.right(yaw);
		for (double s : new double[] {1.3, -1.3, 1.0, -1.0}) {
			Vec3 v = Stage.stand(c.run, umbral.add(back).add(side.scale(s)));
			if (v != null) {
				return v;
			}
		}
		return null;
	}

	@Override
	public void stop(Ctx c) {
		if (c.get("done") != null) {
			return;  // she stays: at the door if he never came in, on her way to the table if he did
		}
		// aborted (a replay of the act, the case ending): the house as it was before he knocked
		Stage.dismissFamily(c.run);
		c.run.door("entrada", false, false);
		if (c.run.def.groups.containsKey("luces_hall")) {
			c.run.lights("luces_hall", false);
		}
	}

	@Override
	public int maxTicks() {
		return OPEN + WAIT_IN + 60;
	}
}
