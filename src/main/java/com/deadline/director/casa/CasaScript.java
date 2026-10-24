package com.deadline.director.casa;

import com.deadline.car.CarEntity;
import com.deadline.caseload.CaseManager;
import com.deadline.director.CaseScript;
import com.deadline.director.Run;
import com.deadline.director.Script;
import com.deadline.director.Steps;
import com.deadline.horror.Haunt;
import com.deadline.horror.HorrorEvents;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.hunt.Hunt;
import com.deadline.net.Fx;
import com.deadline.phone.PhoneMessages;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

/**
 * Case 2, "Casa Morales v2 — Ella escucha todo" (docs/design/casa_terror.md 2). No objectives, no title cards, nobody
 * speaks: the story moves on by itself (time, place, scares lived) and only the phone tells it. One chapter per act
 * (chapter n = act n, chapter 7 = the ending), so a death or a restart replays the act from its checkpoint.
 *
 * <p>The script owns the act number of the {@link Haunt} (the random horror director), the phone messages of 8 and
 * the transitions. Set pieces are scripted {@link com.deadline.horror.HorrorEvent}s fired by id ("sp_*"); while one is
 * not written yet the act falls back to a plain version so the night can always be played to the end. Set pieces post
 * run events the script listens to: "cena:fin", "cuarto61:fin", "final:fin".
 */
public class CasaScript extends CaseScript {
	public static final double ARRIVAL_RADIUS = 24.0;
	public static final int FINAL = 7;

	/** Act 4 set pieces: each happens once, in a random order (design 2, Act 4). */
	private static final List<String> NIGHT_SET_PIECES = List.of("sp_lucia_techo", "sp_jorge_sonambulo", "sp_ropero_toti",
			"torre_sillas", "sp_nona_reza");

	/** Script state that must survive chapter changes (run vars and counters are reset per chapter). */
	private static final class State {
		long chapterStart = Long.MIN_VALUE;
		int msg;
		int knocks;
		long knockAt;
		long nearDoorSince = -1;
		long insideAt = -1;
		long dinnerAt = -1;
		long transitionAt = -1;
		long nextSetPiece;
		int bigAtStart;
		int capturesAtStart;
		long huntSince = -1;
		boolean huntStarted;
		long escapeAt = -1;
		long finalAt = -1;
		final List<String> setPieces = new ArrayList<>();
	}

	private static final Map<Run, State> STATES = new WeakHashMap<>();

	@Override
	public String siteKey() {
		return "casa";
	}

	@Override
	public void define(Script s) {
		s.chapter(1, "llegada").noCard();        // act 1: the drive (only hunters already at the house go back to it)
		s.chapter(2, "puerta_entrada").noCard(); // act 2: knocking, the Nona at the door, the silent dinner
		s.chapter(3, "comedor").noCard();        // act 3: the first hour
		s.chapter(4, "huespedes").noCard();      // act 4: the night
		s.chapter(5, "huespedes_cama").noCard(); // act 5: the hunt
		s.chapter(6, "pasillo_pb").noCard();     // act 6: the basement
		s.chapter(FINAL, "final_auto").noCard(); // the ending: dawn, the car
		// knocking does not open it (the Nona does); once inside it never opens by hand again until the ending
		s.lock("entrada", 1, FINAL);
		s.lock("porton", 3, FINAL);
	}

	private static State state(Run run) {
		return STATES.computeIfAbsent(run, r -> new State());
	}

	@Override
	public void tick(Run run) {
		ServerPlayer p = run.star();
		if (p == null) {
			return;
		}
		State s = state(run);
		Haunt h = Haunt.of(run);
		int ch = run.chapter();
		// /deadline horror act <n>: a retake of that act from its checkpoint
		for (int n = 1; n <= 6; n++) {
			if (run.event("act:" + n) && n != ch) {
				run.jump(n, p);
				return;
			}
		}
		long start = run.now() - run.chapterTicks();
		if (s.chapterStart != start) {
			s.chapterStart = start;
			enter(run, s, h, p, ch);
		}
		switch (ch) {
			case 1 -> drive(run, s, h, p);
			case 2 -> arrival(run, s, h, p);
			case 3 -> firstHour(run, s, h, p);
			case 4 -> night(run, s, h, p);
			case 5 -> hunt(run, s, h, p);
			case 6 -> descent(run, s, h, p);
			case FINAL -> ending(run, s, h, p);
			default -> {
			}
		}
		h.tick();
	}

	// ------------------------------------------------------------------ entering an act (also on checkpoint replays)
	private void enter(Run run, State s, Haunt h, ServerPlayer p, int ch) {
		h.stopAll();
		h.act(Math.min(ch, 6));
		h.pause(ch <= 2 || ch == FINAL);
		s.msg = 0;
		s.transitionAt = -1;
		if (ch != 5 && Hunt.active(run)) {
			Hunt.stop(run);
		}
		switch (ch) {
			case 1 -> run.lights("luces_cuarto_nono", true);  // ONE light upstairs: the dead grandfather's room
			case 2 -> {
				run.lights("luces_cuarto_nono", true);
				s.knocks = 0;
				s.nearDoorSince = -1;
				s.insideAt = -1;
				s.dinnerAt = -1;
			}
			case 3 -> {
				run.door("entrada", false, false);
				// the family is up: the house lit like any other night (only the dead grandfather's room stays as it was)
				for (String g : groups(run, "luces_")) {
					run.lights(g, true);
				}
				if (run.actor("nona") == null && !com.deadline.horror.casa.SetPieces.firstHour(run)) {
					family(run, true);
				}
			}
			case 4 -> {
				blackout(run, false);
				s.bigAtStart = h.bigScares();
				s.setPieces.clear();
				s.setPieces.addAll(NIGHT_SET_PIECES);
				java.util.Collections.shuffle(s.setPieces, new java.util.Random(run.level.getRandom().nextLong()));
				s.nextSetPiece = run.now() + 20 * 70;
			}
			case 5 -> {
				blackout(run, false);
				s.huntSince = -1;
				s.capturesAtStart = Hunt.captures(run);
				// "La Nona se rompe": in the kitchen, back turned; the hunt starts when she drops to all fours
				if (s.huntStarted) {
					Hunt.start(run);
					s.huntSince = run.now();
				} else if (h.fire("sp_nona_se_rompe") == null) {
					String at = run.def.points.containsKey("cocina") ? "cocina" : "pasillo_pb";
					Hunt.transform(run, run.at(at), run.yaw(at));
				}
			}
			case 6 -> {
				blackout(run, false);
				s.escapeAt = -1;
				openThePath(run, p);
			}
			case FINAL -> {
				s.finalAt = run.now();
				blackout(run, false);
				run.door("entrada", true, false);
				run.level.setDayTime(Math.floorDiv(run.level.getDayTime(), 24000L) * 24000L + 23200L);  // a grey dawn
				run.sound(ModSounds.MORNING_BIRDS, run.at("final_auto"), 0.5F, 0.9F);
				h.stopAll();
				// C (sp_final_auto needs the car): his car waits on the street, at final_auto, unless it is already near
				if (run.def.points.containsKey("final_auto")) {
					CarEntity car = com.deadline.car.CarKeysItem.find(p);
					Vec3 street = run.at("final_auto");
					if (car == null || car.level() != run.level || car.position().distanceTo(street) > 40.0) {
						com.deadline.car.CarKeysItem.bring(p, car, street, run.yaw("final_auto"));
					}
				}
			}
			default -> {
			}
		}
	}

	// ------------------------------------------------------------------ act 1: the drive
	private void drive(Run run, State s, Haunt h, ServerPlayer p) {
		long t = run.chapterTicks();
		if (s.msg == 0 && t > 20 * 60) {
			s.msg = 1;
			PhoneMessages.typing(p, PhoneMessages.MARTA, 40);
			PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.ya_viene", 40);
			PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.luces_auto", 20 * 30);
		}
		Vec3 target = arrival(run);
		double d = p.position().distanceTo(target);
		// halfway there, in the headlights: Choripán standing on two legs in the middle of the road, his back turned
		if (!run.has("sp:perro_camino") && p.getVehicle() instanceof CarEntity && d > 60 && d < 150 && t > 20 * 20) {
			run.flag("sp:perro_camino");
			h.fire("sp_perro_camino", p, false);
		}
		if (d < ARRIVAL_RADIUS && p.level() == run.level) {
			run.flag("llegada");
			run.post("llegada");
			run.startChapter(2, false);
		}
	}

	// ------------------------------------------------------------------ act 2: the door, the Nona, the dinner
	private void arrival(Run run, State s, Haunt h, ServerPlayer p) {
		long now = run.now();
		boolean inside = HouseQuery.inHouse(run, p);
		if (s.insideAt < 0) {
			// three knocks (right click on the door). Silence. Knock again: slow steps, the bolt, the door opens by itself
			Vec3 door = run.at("puerta_entrada");
			boolean near = p.position().distanceTo(door) < 3.0;
			if (run.event("use:entrada") && now - s.knockAt > 30) {
				s.knockAt = now;
				s.knocks++;
				for (int i = 0; i < 3; i++) {
					final int k = i;
					run.start("knock", p, List.of(Steps.delay(6 * k), Steps.run(e -> run.sound(ModSounds.HORROR_KNOCK, door, 1.0F, 0.75F + 0.05F * k))));
				}
			}
			s.nearDoorSince = near ? (s.nearDoorSince < 0 ? now : s.nearDoorSince) : -1;
			boolean waited = s.nearDoorSince >= 0 && now - s.nearDoorSince > 20 * 25;
			if (!run.has("puerta:abierta") && (s.knocks >= 2 && now - s.knockAt > 20 * 3 || waited)) {
				run.flag("puerta:abierta");
				if (h.fire("sp_llegada", p, false) == null) {
					Vec3 in = run.at("nona_umbral");
					run.start("door", p, List.of(
							Steps.run(e -> run.sound(ModSounds.ANDADOR_SQUEAK, in, 0.6F, 0.8F)),
							Steps.delay(50),
							Steps.run(e -> run.sound(ModSounds.ANDADOR_SQUEAK, in, 0.8F, 0.75F)),
							Steps.delay(40),
							Steps.run(e -> run.sound(SoundEvents.CHEST_LOCKED, door, 1.0F, 0.6F)),
							Steps.delay(14),
							Steps.run(e -> run.sound(SoundEvents.CHEST_LOCKED, door, 1.0F, 0.5F)),
							Steps.delay(30),
							Steps.door("entrada", true, false)));
				}
			}
			if (inside && run.has("puerta:abierta")) {
				s.insideAt = now;
			}
			return;
		}
		// inside: the door closes behind you and the bolt turns. It will not open again until the end
		if (!run.has("puerta:cerrada") && now - s.insideAt > 40) {
			Vec3 door = HouseQuery.doorPos(run, "entrada");
			if (door == null || p.position().distanceTo(door) > 2.2) {
				run.flag("puerta:cerrada");
				run.door("entrada", false, true);
				run.start("bolt", p, List.of(Steps.delay(16), Steps.run(e -> run.sound(SoundEvents.CHEST_LOCKED, run.at("puerta_entrada"), 1.0F, 0.5F))));
				PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.no_sola", 20 * 4);
			}
		}
		// the family eats in silence; Marta looks up, down at her phone, and texts you
		if (s.dinnerAt < 0 && run.has("puerta:cerrada") && (run.inside(p, "comedor") || now - s.insideAt > 20 * 40)) {
			s.dinnerAt = now;
			PhoneMessages.typing(p, PhoneMessages.MARTA, 30);
			PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.no_hable", 30);
			if (h.fire("sp_cena", p, false) == null) {
				family(run, true);
			}
		}
		boolean dinnerScripted = HorrorEvents.get(run.type.key(), "sp_cena") != null;
		if (s.dinnerAt >= 0 && (run.event("cena:fin") || now - s.dinnerAt > 20 * (dinnerScripted ? 240 : 90))) {
			run.startChapter(3, false);
		}
	}

	// ------------------------------------------------------------------ act 3: the first hour
	private static final Object[][] ACT3 = {
			{45, "deadline.sms.marta.no_duerme"}, {135, "deadline.sms.marta.ropero"}, {210, "deadline.sms.marta.perro"},
			{285, "deadline.sms.marta.no_coma"}};

	private void firstHour(Run run, State s, Haunt h, ServerPlayer p) {
		messages(run, s, p, ACT3, PhoneMessages.MARTA);
		long t = h.actTicks();
		boolean upstairs = upstairs(run, p);
		if (s.transitionAt < 0 && (t > 20 * 360 || upstairs && t > 20 * 120)) {
			// the family goes to bed; Marta points at the guest room; the whole house goes dark (the breaker trips)
			s.transitionAt = run.now();
			if (h.fire("sp_a_dormir", p, false) == null) {
				run.post("a_dormir:fin");
			}
		}
		// C: the scripted bedtime walks everyone up the stairs and waits for him at his door: give it time
		boolean bedtimeScripted = HorrorEvents.get(run.type.key(), "sp_a_dormir") != null;
		if (s.transitionAt >= 0 && (run.event("a_dormir:fin") || run.now() - s.transitionAt > 20 * (bedtimeScripted ? 150 : 60))) {
			family(run, false);
			blackout(run, true);
			run.startChapter(4, false);
		}
	}

	// ------------------------------------------------------------------ act 4: the night
	private static final Object[][] ACT4 = {
			{30, "deadline.sms.marta.jorge_cama"}, {105, "deadline.sms.marta.lucia_cama"}, {180, "deadline.sms.marta.pasillo"},
			{200, "deadline.sms.marta.no_es_usted"}, {300, "deadline.sms.marta.escondase"}};

	private void night(Run run, State s, Haunt h, ServerPlayer p) {
		messages(run, s, p, ACT4, PhoneMessages.MARTA);
		long t = h.actTicks();
		if (t > 20 * 375 && !run.has("msg:puntos")) {
			run.flag("msg:puntos");
			PhoneMessages.typing(p, PhoneMessages.DESCONOCIDO, 20 * 8);
			PhoneMessages.textLater(p, PhoneMessages.DESCONOCIDO, "deadline.sms.desconocido.puntos", 20 * 9);
		}
		// the big set pieces of the night, once each, never on top of another scare
		if (!s.setPieces.isEmpty() && run.now() >= s.nextSetPiece && !h.busy() && h.phase() != Haunt.Phase.RELAX) {
			String id = s.setPieces.get(0);
			if (HorrorEvents.get(run.type.key(), id) == null || h.happened(id)) {
				s.setPieces.remove(0);
			} else if (h.fire(id, p, true) != null) {
				s.setPieces.remove(0);
				s.nextSetPiece = run.now() + 20 * (75 + run.level.getRandom().nextInt(40));
			} else {
				// not the right place yet: the next one gets its turn, this one waits at the back of the line (C)
				s.setPieces.add(s.setPieces.remove(0));
				s.nextSetPiece = run.now() + 20 * 10;
			}
		}
		if (t > 20 * 480 || h.bigScares() - s.bigAtStart >= 5 && t > 20 * 200) {
			run.startChapter(5, false);
		}
	}

	// ------------------------------------------------------------------ act 5: the hunt
	private static final Object[][] ACT5 = {
			{20, "deadline.sms.marta.sotano"}, {32, "deadline.sms.marta.arriba"}, {90, "deadline.sms.marta.no_respire"},
			{180, "deadline.sms.marta.escucha"}};

	private void hunt(Run run, State s, Haunt h, ServerPlayer p) {
		if (s.huntSince < 0) {
			if (run.event("hunt:transformed") || Hunt.active(run)) {
				s.huntSince = run.now();
				s.huntStarted = true;
			} else if (h.actTicks() > 20 * 40 && !h.isRunning("sp_nona_se_rompe")) {
				// the transformation never happened (no kitchen in sight): she is simply out there now (C: unless the set
				// piece is still luring him to the kitchen; it breaks her itself, seen or not)
				Hunt.start(run);
			}
			return;
		}
		messages(run, s, p, ACT5, PhoneMessages.MARTA);
		boolean survived = run.now() - s.huntSince > 20 * 360;
		if (survived || Hunt.captures(run) - s.capturesAtStart >= 2) {
			run.startChapter(6, false);
		}
	}

	// ------------------------------------------------------------------ act 6: the basement
	private void openThePath(Run run, ServerPlayer p) {
		// every door slams shut but the ones down to the basement; the cracked wall is broken from the inside
		run.unflag("escape");
		List<String> doors = new ArrayList<>(run.def.doors.keySet());
		doors.removeIf(d -> d.equals("sotano") || d.equals("entrada") || d.equals("porton") || d.startsWith("ropero_")
				|| p.position().distanceTo(HouseQuery.doorPos(run, d)) < 2.5);
		for (int i = 0; i < doors.size(); i++) {
			String d = doors.get(i);
			run.start("slam", p, List.of(Steps.delay(4 * i), Steps.door(d, false, true)));
		}
		run.start("slam", p, List.of(Steps.delay(4 * doors.size() + 10), Steps.door("sotano", true, false)));
		if (run.def.groups.containsKey("sotano_pared")) {
			for (BlockPos rel : run.def.group("sotano_pared")) {
				run.setBlock(run.origin.offset(rel), Blocks.AIR.defaultBlockState());
			}
			run.sound(ModSounds.WALL_BREAK, run.at("sotano_pared"), 1.4F, 0.7F);
		}
		PhoneMessages.textLater(p, PhoneMessages.DESCONOCIDO, "deadline.sms.desconocido.baja", 20 * 10);
		PhoneMessages.textLater(p, PhoneMessages.DESCONOCIDO, "deadline.sms.desconocido.baja", 20 * 22);
		PhoneMessages.textLater(p, PhoneMessages.DESCONOCIDO, "deadline.sms.desconocido.baja", 20 * 34);
	}

	private void descent(Run run, State s, Haunt h, ServerPlayer p) {
		// candles light up by themselves as you pass, showing the way down
		if (run.def.groups.containsKey("velas_sotano") && run.now() % 5 == 0) {
			List<BlockPos> velas = run.def.group("velas_sotano");
			for (int i = 0; i < velas.size(); i++) {
				if (Vec3.atCenterOf(run.origin.offset(velas.get(i))).distanceTo(p.position()) < 7.0) {
					run.light("velas_sotano", i, true);
				}
			}
		}
		// C: the scripted 1961 room starts as he reaches the basement (the family is put in the room before he can see in)
		boolean roomScripted = HorrorEvents.get(run.type.key(), "sp_cuarto61") != null;
		boolean inRoom = run.def.areas.containsKey("cuarto61") && run.inside(p, "cuarto61");
		boolean below = roomScripted && run.def.areas.containsKey("sotano") && run.inside(p, "sotano");
		if (!run.has("cuarto61") && (inRoom || below)) {
			run.flag("cuarto61");
			if (h.fire("sp_cuarto61", p, false) == null) {
				// fallback: the lights die, a flash, the stinger, and the way out is open
				Fx.flash(p, 0.8F);
				Fx.shake(p, 1.2F, 30);
				run.sound(ModSounds.AMBIENT_STINGER, p.position(), 1.4F, 0.7F);
				run.post("cuarto61:fin");
			}
		}
		if (!run.has("escape") && run.event("cuarto61:fin")) {
			run.flag("escape");
			run.door("entrada", true, false);
		}
		if (run.has("escape") && !HouseQuery.inHouse(run, p) && run.def.areas.containsKey("exterior") && run.inside(p, "exterior")) {
			run.startChapter(FINAL, false);
		}
	}

	// ------------------------------------------------------------------ the ending
	private void ending(Run run, State s, Haunt h, ServerPlayer p) {
		long t = run.now() - s.finalAt;
		if (t > 20 * 3 && !run.has("msg:gracias")) {
			run.flag("msg:gracias");
			PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.gracias", 20);
			PhoneMessages.typing(p, PhoneMessages.MARTA, 20 * 5);
			PhoneMessages.textLater(p, PhoneMessages.MARTA, "deadline.sms.marta.ya_somos", 20 * 7);
			PhoneMessages.photoLater(p, PhoneMessages.MARTA, "final_familia", 20 * 10);
		}
		// you get in the car and start it: in the mirror, the Nona sitting in the back seat
		if (!run.has("final:auto") && t > 20 * 12 && (p.getVehicle() instanceof CarEntity || t > 20 * 120)) {
			run.flag("final:auto");
			if (h.fire("sp_final_auto", p, false) == null) {
				run.start("final", p, List.of(
						Steps.delay(60),
						Steps.run(e -> Fx.jumpscare(p, "nona_rota")),
						Steps.run(e -> run.sound(ModSounds.JUMPSCARE, p.position(), 1.6F, 0.8F)),
						Steps.delay(16),
						Steps.fade(80),
						Steps.delay(30),
						Steps.run(e -> run.post("final:fin"))));
			}
		}
		if (run.event("final:fin") && !run.has("final:fin")) {
			run.flag("final:fin");
			for (ServerPlayer hunter : run.hunters()) {
				Fx.bigText(hunter, "deadline.casa.fin", 120, 1F);
				CaseManager.returnHome(hunter, true);
			}
		}
	}

	// ------------------------------------------------------------------ helpers
	@Override
	public void onCheckpoint(Run run, ServerPlayer p) {
		state(run).chapterStart = Long.MIN_VALUE;  // replay the act setup on the next tick
	}

	@Override
	public void onLeave(Run run, ServerPlayer p) {
		Hunt.stop(run);
		Haunt.forget(run);
		// what the poltergeist left changed (pictures turned, blinds, TV, drawers, flying props still out)
		com.deadline.horror.casa.PoltergeistEvents.cleanup(run);
		// the blood, the teeth and the papers laid out in the house (B1b)
		com.deadline.horror.casa.BloodDecals.clear(run);
		com.deadline.horror.casa.SetPieces.forget(run);
		STATES.remove(run);
	}

	/** Sends the act's messages (seconds of act time → lang key), in order, one at a time. */
	private static void messages(Run run, State s, ServerPlayer p, Object[][] list, String thread) {
		if (s.msg >= list.length) {
			return;
		}
		long t = Haunt.of(run).actTicks();
		if (t >= 20L * (Integer) list[s.msg][0]) {
			PhoneMessages.typing(p, thread, 30);
			PhoneMessages.textLater(p, thread, (String) list[s.msg][1], 30);
			s.msg++;
		}
	}

	/** The breaker trips: every light of the house goes out (the panel in the laundry can bring them back for a while). */
	private static void blackout(Run run, boolean withSound) {
		for (String g : groups(run, "luces_")) {
			run.lights(g, false);
		}
		if (withSound && run.def.points.containsKey("tablero")) {
			run.sound(ModSounds.CASA_BREAKER_TRIP, run.at("tablero"), 1.2F, 0.9F);
			run.sound(ModSounds.LUCES_FUERA, null, 0.8F, 0.8F);
		}
	}

	/** Plain fallback while the dinner/bedtime set pieces are missing: the family sits at the table, then goes away. */
	private static void family(Run run, boolean on) {
		String[][] seats = {{"nona", "silla_1"}, {"marta", "silla_2"}, {"jorge", "silla_3"}, {"toti", "silla_5"}};
		for (String[] seat : seats) {
			if (!on) {
				run.despawn(seat[0]);
				continue;
			}
			if (run.actor(seat[0]) != null || !run.def.points.containsKey(seat[1])) {
				continue;
			}
			var type = switch (seat[0]) {
				case "nona" -> com.deadline.casa.FamilyEntities.NONA;
				case "marta" -> com.deadline.casa.FamilyEntities.MARTA;
				case "jorge" -> com.deadline.casa.FamilyEntities.JORGE;
				default -> com.deadline.casa.FamilyEntities.TOTI;
			};
			com.deadline.director.Props.spawn(run, seat[0], type, seat[1], false);
		}
	}

	private static List<String> groups(Run run, String prefix) {
		List<String> out = new ArrayList<>();
		for (String g : run.def.groups.keySet()) {
			if (g.startsWith(prefix)) {
				out.add(g);
			}
		}
		return out;
	}

	/** The player is on the first floor (or higher): any room of the 1P, the attic. */
	private static boolean upstairs(Run run, ServerPlayer p) {
		String room = HouseQuery.room(run, p);
		return room != null && List.of("pasillo_1p", "lucia", "toti", "matrimonial", "huespedes", "bano_1p", "balcon",
				"cuarto_nono", "altillo").contains(room);
	}

	/** World position of the arrival marker ("llegada", or "spawn" for sites that do not have one). */
	public static Vec3 arrival(Run run) {
		return run.at(run.def.points.containsKey("llegada") ? "llegada" : "spawn");
	}
}
