package com.deadline.horror.casa;

import com.deadline.horror.HorrorEvents;
import com.deadline.horror.casa.dog.SpPerroLargo;
import com.deadline.horror.casa.events.BajoCama;
import com.deadline.horror.casa.events.CopiaSonrie;
import com.deadline.horror.casa.events.DetrasHombro;
import com.deadline.horror.casa.events.FiguraEspejo;
import com.deadline.horror.casa.events.LuciaTechoCorre;
import com.deadline.horror.casa.events.NonaFondo;
import com.deadline.horror.casa.events.NonaVentana;
import com.deadline.horror.casa.events.OfeliaAparece;
import com.deadline.horror.casa.events.PerroMira;
import com.deadline.horror.casa.events.Sabana;
import com.deadline.horror.casa.events.SombraCruza;
import com.deadline.horror.casa.events.TotiRincon;
import com.deadline.horror.casa.events.Visitante;

/**
 * The "Apariciones" of the Casa catalogue (docs/design/casa_terror.md 5, entries 33-45): what the house SHOWS him.
 * Every one is placed out of his view and found, or placed where he is looking; every one goes when he looks away or
 * comes close (unless its entry says otherwise), none can be killed or pushed, and each removes what it spawned in
 * stop(). Call {@link #register()} once from the mod initializer (it also registers the small apparition entities).
 */
public final class ApparitionEvents {
	private static boolean done;

	private ApparitionEvents() {
	}

	public static void register() {
		if (done) {
			return;
		}
		done = true;
		ApparitionEntities.init();
		HorrorEvents.register("casa", new SombraCruza());       // 33
		HorrorEvents.register("casa", new NonaFondo());         // 34
		HorrorEvents.register("casa", new NonaVentana());       // 35
		HorrorEvents.register("casa", new PerroMira());         // 36
		HorrorEvents.register("casa", new FiguraEspejo());      // 37
		HorrorEvents.register("casa", new DetrasHombro());      // 38 (SCARE)
		HorrorEvents.register("casa", new BajoCama());          // 39
		HorrorEvents.register("casa", new TotiRincon());        // 40
		HorrorEvents.register("casa", new CopiaSonrie());       // 41
		HorrorEvents.register("casa", new LuciaTechoCorre());   // 42
		HorrorEvents.register("casa", new OfeliaAparece());     // 43
		HorrorEvents.register("casa", new Sabana());            // 44
		HorrorEvents.register("casa", new Visitante());         // 45
		HorrorEvents.register("casa", new SpPerroLargo());      // design 7: the long dog (scripted, CasaScript fires it)
	}
}
