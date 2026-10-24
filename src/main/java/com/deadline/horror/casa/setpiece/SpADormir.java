package com.deadline.horror.casa.setpiece;

import com.deadline.casa.FamilyEntity;
import com.deadline.director.Run;
import com.deadline.entity.PoseidaEntity;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.world.phys.Vec3;

/**
 * End of Act 3 (design 2): the family goes to bed. Nobody says good night: they stop what they were doing and go to
 * their rooms in silence -- Jorge and Toti up the main stair, the Nona shuffling to her room downstairs -- and every
 * door closes behind them. Marta goes to find him first, looks at him, and leads the way up; at the door of the guest
 * room she stops and points at it, and waits until he has seen it (or for half a minute) before she goes to her own
 * room. When they are all in their rooms the set piece posts {@code a_dormir:fin} (the act script then trips the
 * breaker: the night begins).
 */
public class SpADormir extends HorrorEvent {
	/** Rooms: actor -> {door marker, room point, room area}. */
	private static final Map<String, String[]> ROOMS = Map.of(
			Stage.NONA, new String[] {"nona_cuarto", "nona_cuarto", "nona_cuarto"},
			Stage.MARTA, new String[] {"matrimonial", "matrimonial", "matrimonial"},
			Stage.JORGE, new String[] {"matrimonial", "matrimonial", "matrimonial"},
			Stage.TOTI, new String[] {"toti", "toti_cuarto", "toti"});
	private static final int FIND = 0, LEAD = 1, POINT = 2, BED = 3;
	private static final int POINT_WAIT = 20 * 30, GIVE_UP = 20 * 140;

	public SpADormir() {
		super("sp_a_dormir", Kind.SETPIECE);
		this.acts(3, 3).intensity(2).cooldown(60).scripted().once();
	}

	@Override
	public boolean canRun(Ctx c) {
		return Stage.hasArea(c.run, "casa");
	}

	@Override
	public void start(Ctx c) {
		Run r = c.run;
		Map<String, Stage.Route> routes = new HashMap<>();
		for (String who : new String[] {Stage.NONA, Stage.JORGE, Stage.TOTI}) {
			FamilyEntity f = Stage.member(r, who);
			if (f == null) {
				continue;
			}
			Stage.cancelChore(r, f);
			getUp(f);
			String[] room = ROOMS.get(who);
			routes.put(who, Stage.routeTo(r, f, room[0], room[1], who.equals(Stage.NONA) ? 0.45 : 0.75));
		}
		c.put("routes", routes);
		FamilyEntity marta = Stage.member(r, Stage.MARTA);
		if (marta != null) {
			Stage.cancelChore(r, marta);
			getUp(marta);
		}
		c.put("marta", FIND);
		c.put("phaseAt", 0);
		// Lucía is already in her room (she cannot walk): the next time nobody looks, she has gone to bed
		PoseidaEntity lucia = Stage.lucia(r);
		if (lucia != null) {
			Stage.whenUnseen(r, lucia, Stage.LUCIA, null, 0F, null);
		}
	}

	private static void getUp(FamilyEntity f) {
		if (f.action() == FamilyEntity.POSE_SIT) {
			f.setAction(FamilyEntity.POSE_IDLE);
		}
		f.setExpression(0);
		f.watch(null);
		f.lookAt(null);
		f.watchPlayers(false);  // nobody looks at him: they just go
		f.propSounds = true;
	}

	@Override
	public boolean tick(Ctx c) {
		Run r = c.run;
		Map<String, Stage.Route> routes = c.get("routes");
		for (Map.Entry<String, Stage.Route> en : routes.entrySet()) {
			FamilyEntity f = Stage.member(r, en.getKey());
			if (f != null && en.getValue().tick(f)) {
				toBed(c, en.getKey(), f);
			}
		}
		tickMarta(c);
		boolean anyone = false;
		for (String who : Stage.MEMBERS) {
			anyone |= Stage.member(r, who) != null;
		}
		anyone |= Stage.lucia(r) != null;
		if (!anyone || c.t > GIVE_UP) {
			r.post("a_dormir:fin");
			c.put("done", true);
			return true;
		}
		return false;
	}

	/** In the room: the door closes behind them; once nobody sees them they are in bed (gone from the run). */
	private void toBed(Ctx c, String who, FamilyEntity f) {
		if (c.get("bed:" + who) != null) {
			return;
		}
		c.put("bed:" + who, true);
		String[] room = ROOMS.get(who);
		if (c.run.def.doors.containsKey(room[0]) && (!Stage.hasArea(c.run, room[2]) || !Stage.in(c.run, c.p, room[2]))) {
			c.run.door(room[0], false, false);
		}
		Stage.whenUnseen(c.run, f, who, null, 0F, null);
	}

	/** Marta finds him, looks at him, leads the way upstairs and points at his door. */
	private void tickMarta(Ctx c) {
		Run r = c.run;
		FamilyEntity m = Stage.member(r, Stage.MARTA);
		if (m == null) {
			return;
		}
		int phase = c.get("marta");
		int since = c.t - c.<Integer>get("phaseAt");
		Vec3 guestDoor = Stage.doorStep(r, "huespedes", Stage.at(r, "pasillo_1p") != null ? r.at("pasillo_1p") : m.position(), 2.0);
		switch (phase) {
			case FIND -> {
				boolean upstairs = guestDoor != null && Math.abs(c.p.getY() - guestDoor.y) < 2.5;
				double d = m.position().distanceTo(c.p.position());
				if (upstairs || guestDoor == null) {
					next(c, LEAD);
					return;
				}
				Integer met = c.get("met");
				if (met == null && d < 3.2) {
					met = c.t;
					c.put("met", met);
					m.stopWalking();
					m.face(c.p.position());
					m.watch(c.p);  // she looks at him; then she goes up, and he follows (or not)
				}
				if (met != null && c.t - met > 45 || since > 20 * 25) {
					next(c, LEAD);
				} else if (met == null && (!m.isWalking() || since % 40 == 0)) {
					Vec3 toward = c.p.position().add(m.position().subtract(c.p.position()).normalize().scale(2.0));
					Vec3 spot = Stage.stand(r, toward);
					m.walkTo(spot != null ? spot : c.p.position(), 0.8);
				}
			}
			case LEAD -> {
				if (since == 0 || c.get("lead") == null) {
					m.watch(null);
					c.put("lead", guestDoor == null ? new Stage.Route(0.75) : guestRoute(r, m, guestDoor));
				}
				Stage.Route lead = c.get("lead");
				if (lead.tick(m)) {
					Vec3 door = HouseQuery.doorPos(r, "huespedes");
					if (door != null) {
						m.face(door);
						m.setAction(FamilyEntity.POSE_POINT);
					}
					next(c, POINT);
				}
			}
			case POINT -> {
				// holds the point (her head turning to him when he comes) until he is close, or half a minute
				boolean close = m.position().distanceTo(c.p.position()) < 4.5;
				if (close) {
					m.watch(c.p);
				}
				if (close && c.get("pointSeen") == null) {
					c.put("pointSeen", c.t);
				}
				Integer seen = c.get("pointSeen");
				if (seen != null && c.t - seen > 50 || since > POINT_WAIT) {
					m.setAction(FamilyEntity.POSE_IDLE);
					m.watch(null);
					String[] room = ROOMS.get(Stage.MARTA);
					c.put("martaRoute", Stage.routeTo(r, m, room[0], room[1], 0.7));
					next(c, BED);
				}
			}
			default -> {
				Stage.Route route = c.get("martaRoute");
				if (route == null || route.tick(m)) {
					toBed(c, Stage.MARTA, m);
				}
			}
		}
	}

	private static Stage.Route guestRoute(Run r, FamilyEntity m, Vec3 guestDoor) {
		boolean up = guestDoor.y - m.getY() > 2.5;
		if (!up) {
			return new Stage.Route(0.75, guestDoor);
		}
		return new Stage.Route(0.75, Stage.at(r, "esc_principal_pie"), Stage.at(r, "esc_principal_arriba"), guestDoor);
	}

	private static void next(Ctx c, int phase) {
		c.put("marta", phase);
		c.put("phaseAt", c.t);
	}

	@Override
	public void stop(Ctx c) {
		// whoever is still up goes to bed now (the act script then turns the lights out): the night has no family
		Stage.dismissFamily(c.run);
	}

	@Override
	public int maxTicks() {
		return GIVE_UP + 40;
	}
}
