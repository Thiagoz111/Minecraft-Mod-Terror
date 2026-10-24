package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntity;
import com.deadline.director.Run;
import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.dog.Choripan;
import com.deadline.horror.casa.dog.ChoripanEntity;
import com.deadline.registry.ModSounds;
import com.deadline.voice.NoiseMeter;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * Act 2, the silent dinner (design 2): the family eats at the long table without a word -- forks on china, nothing else.
 * The Nona at the head (silla_1) stares at him the whole meal, her head following him round the room further than it
 * should. Marta (silla_2) looks up at him, then down at the phone in her lap (her text arrives: "No hable. Siéntese.");
 * every now and then she looks up again. Jorge and Toti keep their eyes on their plates; Lucía sits with her head bowed.
 * Choripán growls low under the table, at the Nona. If he makes noise (talks, runs), everything stops: the forks, the
 * chewing; every head turns to him; the dog whines; then, slowly, they go back to their plates.
 * <p>Posts {@code cena:fin} when he leaves the dining room after at least a minute of dinner (or after four minutes),
 * and the family goes on with the night in silence (Act 3): Marta to the sink, Jorge to his armchair facing the TV, the
 * Nona to the rocking chair in her room, Toti to the kitchen table, Lucía up to her room; the dog bolts out.
 */
public class SpCena extends HorrorEvent {
	private static final int MIN_DINNER = 20 * 60, LONG_DINNER = 20 * 90, MAX_DINNER = 20 * 240;

	public SpCena() {
		super("sp_cena", Kind.SETPIECE);
		this.acts(2, 2).intensity(2).cooldown(60).scripted().once();
	}

	/** The point on the table in front of a dinner seat (where the eyes go). */
	public static Vec3 plate(Run r, String who) {
		String chair = Stage.SEATS.get(who);
		if (chair == null || !Stage.has(r, chair)) {
			return null;
		}
		return r.at(chair).add(Stage.forward(r.yaw(chair)).scale(1.0)).add(0, 0.85, 0);
	}

	/** Marta's lap (the phone). */
	private static Vec3 lap(Run r) {
		return Stage.has(r, "silla_2") ? r.at("silla_2").add(Stage.forward(r.yaw("silla_2")).scale(0.45)).add(0, 0.5, 0) : null;
	}

	@Override
	public boolean canRun(Ctx c) {
		return Stage.hasArea(c.run, "comedor") && Stage.has(c.run, "silla_1");
	}

	@Override
	public void start(Ctx c) {
		Run r = c.run;
		for (String who : new String[] {Stage.MARTA, Stage.JORGE, Stage.TOTI}) {
			FamilyEntity f = Stage.member(r, who);
			if (f == null || f.action() != FamilyEntity.POSE_SIT) {
				f = Stage.seat(r, who);
			}
			if (f != null) {
				Stage.cancelChore(r, f);
				f.watchPlayers(false);
				f.lookAt(plate(r, who));
			}
		}
		if (Stage.lucia(r) == null) {
			Stage.seatLucia(r);
		}
		FamilyEntity n = Stage.member(r, Stage.NONA);
		if (n == null) {
			sitNona(c);
		} else if (Stage.has(r, "silla_1") && n.position().distanceTo(r.at("silla_1")) > 0.8 && !n.isWalking()) {
			n.walkTo(r.at("silla_1"), 0.45);
		}
		ChoripanEntity dog = Choripan.get(r);
		if (dog == null || Stage.has(r, "silla_1") && dog.position().distanceTo(r.at("silla_1")) > 4.0) {
			Stage.dogUnderTable(r);
		}
		if (r.def.groups.containsKey("luces_comedor")) {
			r.lights("luces_comedor", true);
		}
		c.put("entered", -1);
		c.put("glance", 8);
		c.put("glanceEnd", -1);
		c.put("hush", -1);
		c.put("cutlery", 20);
	}

	private void sitNona(Ctx c) {
		FamilyEntity n = Stage.seat(c.run, Stage.NONA);
		if (n != null) {
			n.setExpression(FamilyEntity.EXPR_STARE);
			n.watch(c.p);
			c.put("nonaSat", true);
		}
	}

	@Override
	public boolean tick(Ctx c) {
		Run r = c.run;
		int t = c.t;
		// the Nona reaches the head of the table and sits, staring at him
		FamilyEntity n = Stage.member(r, Stage.NONA);
		if (n != null && c.get("nonaSat") == null && Stage.has(r, "silla_1")
				&& (n.hasArrived() || n.position().distanceTo(r.at("silla_1")) < 0.7 || t > 20 * 40)) {
			sitNona(c);
		}
		FamilyEntity marta = Stage.member(r, Stage.MARTA);
		boolean hushed = c.<Integer>get("hush") >= 0 && t - c.<Integer>get("hush") < 110;
		// Marta: looks up at him, then down at the phone in her lap; now and then she looks up again
		if (marta != null && !hushed) {
			int glance = c.get("glance");
			int end = c.get("glanceEnd");
			if (end < 0 && t >= glance) {
				marta.watch(c.p);
				c.put("glanceEnd", t + (t < 20 ? 62 : 30 + c.rnd.nextInt(25)));
			} else if (end >= 0 && t >= end) {
				marta.watch(null);
				marta.lookAt(lap(r));
				c.put("glanceEnd", -1);
				c.put("glance", t + 20 * (14 + c.rnd.nextInt(12)));
			}
		}
		// forks on china, cups set down: the only sounds at the table
		int cutlery = c.get("cutlery");
		if (!hushed && t >= cutlery) {
			String who = Stage.MEMBERS.get(c.rnd.nextInt(Stage.MEMBERS.size()));
			Vec3 plate = plate(r, who);
			if (plate != null) {
				r.sound(ModSounds.SP_CUBIERTOS, plate, 0.35F, 0.9F + c.rnd.nextFloat() * 0.2F);
			}
			c.put("cutlery", t + 30 + c.rnd.nextInt(60));
		}
		// "ella escucha todo": a noise and the whole table stops and looks at him
		boolean near = Stage.hasArea(r, "comedor") && r.area("comedor").inflate(6.0).contains(c.p.position());
		if (!hushed && near && t > 40 && NoiseMeter.get(c.p) > 30F) {
			c.put("hush", t);
			for (String who : List.of(Stage.MARTA, Stage.JORGE, Stage.TOTI)) {
				FamilyEntity f = Stage.member(r, who);
				if (f != null) {
					f.watch(c.p);
				}
			}
			ChoripanEntity dog = Choripan.get(r);
			if (dog != null) {
				r.sound(ModSounds.CHORIPAN_WHINE, dog.position(), 0.7F, 0.9F);
			}
			if (n != null) {
				r.sound(ModSounds.HUNT_JAW, n.getEyePosition(), 0.5F, 1.2F);
			}
		}
		if (c.<Integer>get("hush") >= 0 && t - c.<Integer>get("hush") == 110) {
			for (String who : List.of(Stage.MARTA, Stage.JORGE, Stage.TOTI)) {
				FamilyEntity f = Stage.member(r, who);
				if (f != null) {
					f.watch(null);
					f.lookAt(who.equals(Stage.MARTA) ? lap(r) : plate(r, who));
				}
			}
		}
		// the end of the dinner: he leaves the dining room after a while (or it simply goes on too long)
		boolean inside = Stage.in(r, c.p, "comedor");
		if (inside && c.<Integer>get("entered") < 0) {
			c.put("entered", t);
		}
		boolean left = !inside && t >= MIN_DINNER && (c.<Integer>get("entered") >= 0 || t >= LONG_DINNER);
		if (left || t >= MAX_DINNER) {
			r.post("cena:fin");
			disperse(c);
			c.put("done", true);
			return true;
		}
		return false;
	}

	/** Act 3 begins: everyone gets up without a word and goes on with the night. */
	private void disperse(Ctx c) {
		Run r = c.run;
		FamilyEntity n = Stage.member(r, Stage.NONA);
		if (n != null) {
			standUp(n);
			n.propSounds = true;
			sitAt(r, n, "nona_mecedora", "nona_cuarto", null);
		}
		FamilyEntity marta = Stage.member(r, Stage.MARTA);
		if (marta != null && Stage.has(r, "mesada")) {
			standUp(marta);
			Vec3 sink = r.at("mesada");
			float yaw = r.yaw("mesada");
			Stage.walkThen(r, marta, new Stage.Route(0.7, sink), f -> {
				f.face(yaw);
				f.watchPlayers(false);
				f.lookAt(sink.add(Stage.forward(yaw).scale(0.9)).add(0, 0.8, 0));  // washing the plates, eyes down
			});
		}
		FamilyEntity jorge = Stage.member(r, Stage.JORGE);
		if (jorge != null) {
			standUp(jorge);
			sitAt(r, jorge, "sillon_jorge", null, Stage.at(r, "tv") != null ? r.at("tv").add(0, 0.8, 0) : null);
		}
		FamilyEntity toti = Stage.member(r, Stage.TOTI);
		if (toti != null) {
			standUp(toti);
			BlockPos chair = Stage.has(r, "cocina") ? Stage.kitNear(r, r.at("cocina"), "silla_cocina", 5) : null;
			if (chair != null) {
				float yaw = Stage.chairYaw(r, chair, 0F);
				Vec3 seat = new Vec3(chair.getX() + 0.5, chair.getY(), chair.getZ() + 0.5);
				Vec3 side = Stage.stand(r, seat.add(Stage.forward(yaw).scale(-1.0)));
				Stage.walkThen(r, toti, new Stage.Route(0.8, side != null ? side : seat), f -> {
					f.teleportTo(seat.x, seat.y, seat.z);
					f.face(yaw);
					f.setAction(FamilyEntity.POSE_SIT);
					f.watchPlayers(false);
					f.lookAt(seat.add(Stage.forward(yaw).scale(0.9)).add(0, 0.85, 0));  // drawing
				});
			} else if (Stage.has(r, "cocina")) {
				Stage.walkThen(r, toti, new Stage.Route(0.8, r.at("cocina")), null);
			}
		}
		PoseidaEntity lucia = Stage.lucia(r);
		if (lucia != null) {
			// she cannot walk: she is up in her room the next time anybody looks (at her little desk if there is one)
			BlockPos desk = Stage.has(r, "lucia_cuarto") ? Stage.kitNear(r, r.at("lucia_cuarto"), "silla_nena", 6) : null;
			Vec3 to = desk != null ? new Vec3(desk.getX() + 0.5, desk.getY(), desk.getZ() + 0.5) : Stage.at(r, "lucia_cuarto");
			float yaw = desk != null ? Stage.chairYaw(r, desk, 0F) : Stage.has(r, "lucia_cuarto") ? r.yaw("lucia_cuarto") : 0F;
			boolean sit = desk != null;
			if (to != null) {
				Stage.whenUnseen(r, lucia, Stage.LUCIA, to, yaw, e -> {
					if (e instanceof PoseidaEntity l) {
						l.setAction(sit ? PoseidaEntity.ACT_SIT : PoseidaEntity.ACT_IDLE);
					}
				});
			}
		}
		ChoripanEntity dog = Choripan.get(r);
		if (dog != null) {
			// the dog bolts out of the room and is not seen again (not as a dog)
			Vec3 out = Stage.at(r, "cocina");
			if (out == null) {
				out = Stage.at(r, "pasillo_pb_fondo");
			}
			if (out != null) {
				dog.dash(out);
			}
			r.sound(ModSounds.CHORIPAN_WHINE, dog.position(), 0.8F, 1.1F);
			Stage.whenUnseen(r, dog, Choripan.ACTOR, null, 0F, null);
		}
		if (n != null) {
			n.setExpression(0);
		}
	}

	private static void standUp(FamilyEntity f) {
		f.setAction(FamilyEntity.POSE_IDLE);
		f.setExpression(0);
		f.watch(null);
		f.lookAt(null);
		f.watchPlayers(true);
	}

	/**
	 * Walks to the seat at a marker (through a door when given), sits on it facing the marker yaw; eyes on `eyes` (null:
	 * on whoever comes near).
	 */
	private static void sitAt(Run r, FamilyEntity f, String seatPoint, String door, Vec3 eyes) {
		Vec3 seat = Stage.at(r, seatPoint);
		if (seat == null) {
			return;
		}
		float yaw = r.yaw(seatPoint);
		Vec3 front = Stage.stand(r, seat.add(Stage.forward(yaw).scale(1.0)));
		Stage.Route route;
		if (door != null && r.def.doors.containsKey(door)) {
			Vec3 corridor = Stage.at(r, "pasillo_pb");
			route = new Stage.Route(0.5, Stage.doorStep(r, door, corridor != null ? corridor : f.position(), 1.2),
					Stage.doorStep(r, door, seat, 1.0), front != null ? front : seat);
		} else {
			route = new Stage.Route(0.6, front != null ? front : seat);
		}
		Stage.walkThen(r, f, route, e -> {
			e.teleportTo(seat.x, seat.y, seat.z);
			e.face(yaw);
			e.setAction(FamilyEntity.POSE_SIT);
			e.propSounds = false;
			if (eyes != null) {
				e.watchPlayers(false);
				e.lookAt(eyes);
			}
		});
	}

	@Override
	public void stop(Ctx c) {
		if (c.get("done") != null) {
			return;  // the family goes on with the night (their chores), the house lit by the next act
		}
		// aborted (a replay of the act, the case ending): the table empty again, the lamp off
		Stage.dismissFamily(c.run);
		if (c.run.def.groups.containsKey("luces_comedor")) {
			c.run.lights("luces_comedor", false);
		}
	}

	@Override
	public int maxTicks() {
		return MAX_DINNER + 40;
	}
}
