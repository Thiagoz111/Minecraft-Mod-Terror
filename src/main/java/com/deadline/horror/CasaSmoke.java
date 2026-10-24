package com.deadline.horror;

import com.deadline.DeadLine;
import com.deadline.director.Run;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import net.fabricmc.fabric.api.entity.FakePlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.Vec3;

/**
 * CI smoke test of the Casa (called by {@link com.deadline.SmokeTest} on the placed site): the marker contract of
 * docs/design/casa_terror.md 11, then every registered horror event fired once with a fake player standing at a few
 * places of the house, ticked for a few seconds and stopped. Any exception inside an event counts as a failure.
 */
public final class CasaSmoke {
	private static final String[] POINTS = {"spawn", "llegada", "porton", "camino", "puerta_entrada", "nona_umbral", "farol",
			"patio", "patio_fondo", "cucha", "cucha_techo", "parrilla", "pileta", "soga", "galpon", "limonero",
			"ventana_1p_afuera", "final_auto", "perro_mira_1", "perro_mira_2", "perro_mira_3", "perro_mira_4",
			"hall", "espejo_hall", "living", "tv", "sillon_jorge", "mecedora", "comedor", "silla_1", "silla_2", "silla_3",
			"silla_4", "silla_5", "silla_6", "silla_7", "silla_8", "aparador", "cocina", "heladera", "mesada", "cuchillos",
			"canilla_cocina", "despensa", "lavadero", "tablero", "bano_pb", "nona_cuarto", "nona_cama", "nona_altar",
			"nona_mecedora", "costurero", "maquina_coser", "escritorio", "escritorio_silla", "pasillo_pb", "pasillo_pb_fondo",
			"esc_principal_pie", "esc_principal_arriba", "esc_servicio_pie", "esc_servicio_arriba", "telefono_fijo",
			"pasillo_1p", "pasillo_1p_fondo", "lucia_cuarto", "lucia_cama", "lucia_techo", "pasillo_techo", "estante_munecas",
			"caja_musica", "toti_cuarto", "toti_cama", "toti_rincon", "matrimonial", "matrimonial_cama", "tocador",
			"huespedes", "huespedes_cama", "bano_1p", "banera", "espejo_bano", "balcon", "cuarto_nono", "altillo_trampa",
			"altillo", "altillo_baul", "sotano_escalera", "sotano", "caldera", "sotano_pared", "cuarto61", "cuarto61_cama",
			"cuarto61_techo", "familia61_1", "familia61_2", "familia61_3", "familia61_4"};
	private static final String[] HIDES = {"ropero_nona", "ropero_lucia", "ropero_toti", "ropero_matrimonial",
			"ropero_huespedes", "ropero_hall", "cama_lucia", "cama_toti", "cama_matrimonial", "cama_huespedes", "cama_nona",
			"despensa", "banera", "baul_altillo", "galpon"};
	private static final String[] AREAS = {"sitio", "casa", "exterior", "hall", "living", "comedor", "cocina", "despensa",
			"lavadero", "bano_pb", "nona_cuarto", "costurero", "escritorio", "pasillo_pb", "esc_principal", "esc_servicio",
			"pasillo_1p", "lucia", "toti", "matrimonial", "huespedes", "bano_1p", "balcon", "cuarto_nono", "altillo", "sotano",
			"cuarto61", "patio"};
	private static final String[] GROUPS = {"luces_pasillo_1p", "comedor_sillas", "aparador_platos", "cuchillos",
			"cuadros_pasillo", "persianas_pb", "persianas_1p", "estante_munecas", "tv", "sotano_pared", "velas_sotano",
			"altar_velas", "ventanas_1p", "cajones"};
	private static final String[] DOORS = {"entrada", "porton", "puerta_patio", "cocina", "despensa", "lavadero", "bano_pb",
			"nona_cuarto", "costurero", "escritorio", "lucia", "toti", "matrimonial", "huespedes", "bano_1p", "balcon",
			"cuarto_nono", "sotano", "galpon"};
	private static final String[] WRITES = {"lemaza", "espejo_azamel", "cuaderno"};
	/** Where the fake player stands while each event looks for its place (first spot where canRun passes wins). */
	private static final String[] SPOTS = {"pasillo_pb", "hall", "comedor", "cocina", "living", "pasillo_1p", "lucia_cuarto",
			"toti_cuarto", "huespedes", "bano_1p", "nona_cuarto", "sotano", "cuarto61", "patio", "llegada"};
	private static final int TICKS = 100;

	private CasaSmoke() {
	}

	public static int run(Run run) {
		return contract(run.def) + events(run);
	}

	private static int contract(SiteDef def) {
		List<String> points = new ArrayList<>(List.of(POINTS));
		for (String h : HIDES) {
			points.add("hide_" + h);
			points.add("hide_" + h + "_out");
		}
		List<String> writes = new ArrayList<>(List.of(WRITES));
		for (int i = 1; i <= 12; i++) {
			writes.add("escritura_" + i);
		}
		return missing("point", def.points.keySet(), points) + missing("area", def.areas.keySet(), List.of(AREAS))
				+ missing("group", def.groups.keySet(), List.of(GROUPS)) + missing("door", def.doors.keySet(), List.of(DOORS))
				+ missing("write", def.writes.keySet(), writes);
	}

	private static int missing(String kind, Collection<String> have, Collection<String> want) {
		List<String> out = new ArrayList<>();
		for (String w : want) {
			if (!have.contains(w)) {
				out.add(w);
			}
		}
		if (!out.isEmpty()) {
			DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL casa: missing {} markers {}", kind, out);
		}
		return out.isEmpty() ? 0 : 1;
	}

	private static int events(Run run) {
		ServerLevel level = run.level;
		FakePlayer fake = FakePlayer.get(level);
		Haunt h = Haunt.of(run);
		int before = Haunt.errors;
		int ran = 0;
		List<String> idle = new ArrayList<>();
		List<HorrorEvent> all = HorrorEvents.of("casa");
		for (HorrorEvent e : all) {
			h.act(Math.max(1, Math.min(6, e.minAct())));
			Ctx c = null;
			for (String spot : SPOTS) {
				if (!run.def.points.containsKey(spot)) {
					continue;
				}
				Vec3 v = run.at(spot);
				fake.snapTo(v.x, v.y, v.z, run.yaw(spot), 0F);
				c = h.fire(e.id, fake, true);
				if (c != null) {
					break;
				}
			}
			if (c == null) {
				idle.add(e.id);
				continue;
			}
			ran++;
			for (int i = 0; i < TICKS && h.isRunning(e.id); i++) {
				level.tick(() -> true);
				h.tick();
			}
			h.stopAll();
		}
		Haunt.forget(run);
		int errors = Haunt.errors - before;
		DeadLine.LOGGER.info("DEADLINE-SMOKE casa horror: {} events, {} ran, {} errors; did not find their place: {}",
				all.size(), ran, errors, idle);
		if (errors > 0) {
			DeadLine.LOGGER.error("DEADLINE-SMOKE FAIL casa: {} horror event errors (see 'Horror event' lines)", errors);
		}
		return errors > 0 ? 1 : 0;
	}
}
