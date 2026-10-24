package com.deadline.horror.casa;

import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.horror.HorrorEvents;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.events.polter.ApagonCuarto;
import com.deadline.horror.casa.events.polter.Cajones;
import com.deadline.horror.casa.events.polter.CanillaSangre;
import com.deadline.horror.casa.events.polter.Cascada;
import com.deadline.horror.casa.events.polter.Cuadros;
import com.deadline.horror.casa.events.polter.Cuchillos;
import com.deadline.horror.casa.events.polter.Heladera;
import com.deadline.horror.casa.events.polter.LamparaFondo;
import com.deadline.horror.casa.events.polter.Mecedora;
import com.deadline.horror.casa.events.polter.MunecasMiran;
import com.deadline.horror.casa.events.polter.Parpadeo;
import com.deadline.horror.casa.events.polter.Persianas;
import com.deadline.horror.casa.events.polter.Picaporte;
import com.deadline.horror.casa.events.polter.PlatosVuelan;
import com.deadline.horror.casa.events.polter.Portazo;
import com.deadline.horror.casa.events.polter.PuertaLenta;
import com.deadline.horror.casa.events.polter.SillaCorre;
import com.deadline.horror.casa.events.polter.TeleSola;
import com.deadline.horror.casa.events.polter.TorreSillas;
import com.deadline.horror.casa.events.polter.VuelaObjeto;
import com.deadline.horror.casa.events.sound.CajaMusica;
import com.deadline.horror.casa.events.sound.Dentadura;
import com.deadline.horror.casa.events.sound.LlantoSotano;
import com.deadline.horror.casa.events.sound.Palmadas;
import com.deadline.horror.casa.events.sound.PasosArriba;
import com.deadline.horror.casa.events.sound.PerroRasca;
import com.deadline.horror.casa.events.sound.Respiracion;
import com.deadline.horror.casa.events.sound.RezoReves;
import com.deadline.horror.casa.events.sound.Risita;
import com.deadline.horror.casa.events.sound.TelefonoFijo;
import com.deadline.horror.casa.events.sound.TresGolpes;
import com.deadline.horror.casa.events.sound.TuVoz;
import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.server.level.ServerPlayer;

/**
 * The poltergeist of the Casa catalogue (docs/design/casa_terror.md 5, entries 1-32): the house alive (sounds 1-12)
 * and doors, lights and objects that move by themselves (13-32), plus the interactables of 6.3 ({@link Interactables})
 * and the flying objects of 6.4 ({@link FlyingProp}). Call {@link #register()} once from the mod initializer, before
 * the director registers its use callback. The case script calls {@link #cleanup(Run)} when the case is left: the
 * pictures that were turned to the wall stay turned until then, and whatever the hunter changed is put back.
 */
public final class PoltergeistEvents {
	private static final Map<Run, Map<String, Long>> LAST_IN = new WeakHashMap<>();
	private static boolean done;

	private PoltergeistEvents() {
	}

	public static void register() {
		if (done) {
			return;
		}
		done = true;
		Interactables.init();
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (server.getTickCount() % 10 != 0) {
				return;
			}
			for (ServerPlayer p : server.getPlayerList().getPlayers()) {
				Run r = Director.of(p);
				if (r != null && "casa".equals(r.type.key()) && r.level == p.level()) {
					String room = HouseQuery.room(r, p);
					if (room != null) {
						LAST_IN.computeIfAbsent(r, k -> new HashMap<>()).put(room, r.now());
					}
				}
			}
		});
		// sounds: the house is alive
		HorrorEvents.register("casa", new PasosArriba());      // 1
		HorrorEvents.register("casa", new TresGolpes());       // 2
		HorrorEvents.register("casa", new Palmadas());         // 3
		HorrorEvents.register("casa", new Risita());           // 4
		HorrorEvents.register("casa", new CajaMusica());       // 5
		HorrorEvents.register("casa", new Dentadura());        // 6
		HorrorEvents.register("casa", new TuVoz());            // 7
		HorrorEvents.register("casa", new Respiracion());      // 8
		HorrorEvents.register("casa", new RezoReves());        // 9
		HorrorEvents.register("casa", new PerroRasca());       // 10
		HorrorEvents.register("casa", new TelefonoFijo());     // 11
		HorrorEvents.register("casa", new LlantoSotano());     // 12
		// doors, lights and objects
		HorrorEvents.register("casa", new PuertaLenta());      // 13
		HorrorEvents.register("casa", new Portazo());          // 14
		HorrorEvents.register("casa", new Cascada());          // 15
		HorrorEvents.register("casa", new Picaporte());        // 16
		HorrorEvents.register("casa", new Parpadeo());         // 17
		HorrorEvents.register("casa", new ApagonCuarto());     // 18
		HorrorEvents.register("casa", new LamparaFondo());     // 19
		HorrorEvents.register("casa", new TeleSola());         // 20
		HorrorEvents.register("casa", new SillaCorre());       // 21
		HorrorEvents.register("casa", new TorreSillas());      // 22 (also an Act 4 set piece of the script)
		HorrorEvents.register("casa", new PlatosVuelan());     // 23
		HorrorEvents.register("casa", new Cuchillos());        // 24
		HorrorEvents.register("casa", new Cuadros());          // 25
		HorrorEvents.register("casa", new Cajones());          // 26
		HorrorEvents.register("casa", new Mecedora());         // 27
		HorrorEvents.register("casa", new MunecasMiran());     // 28
		HorrorEvents.register("casa", new CanillaSangre());    // 29
		HorrorEvents.register("casa", new Persianas());        // 30
		HorrorEvents.register("casa", new Heladera());         // 31
		HorrorEvents.register("casa", new VuelaObjeto());      // 32
	}

	/** Ticks since the star was last in a room (Long.MAX_VALUE if never), sampled every 10 ticks. */
	public static long sinceIn(Run r, String room) {
		Map<String, Long> m = LAST_IN.get(r);
		Long t = m == null ? null : m.get(room);
		return t == null ? Long.MAX_VALUE : r.now() - t;
	}

	/**
	 * Undoes what the poltergeist left on purpose when the case is left: the pictures turned to the wall come back,
	 * the blinds, the TV and the rest the hunter touched go back as they were, any flying prop still out is put back.
	 * Call from CasaScript.onLeave (blood is BloodEvents' own cleanup).
	 */
	public static void cleanup(Run r) {
		if (r == null) {
			return;
		}
		Cuadros.clear(r);
		Interactables.clear(r);
		FlyingProp.clear(r);
		LAST_IN.remove(r);
	}
}
