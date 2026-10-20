package com.deadline.director.colegio;

import static com.deadline.director.Steps.*;
import static com.deadline.director.Triggers.*;

import com.deadline.director.CaseScript;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.director.Script;
import com.deadline.director.Step;
import com.deadline.entity.MonjaEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;

/**
 * Case 1, "Colegio Santa Inés de la Vigilia" (docs/design/BIBLIA.md 2.1). Chapters follow the night of 21/6/1984:
 * 1 arrival, 2 study (roll call, blackboard, lesson), 3 dinner (light on/off gag, key, burst lamps), 4 principal's
 * office (PA, mate, the file, the bakelite phone), 5 compline (confession, the upper choir), 6 great silence,
 * 7 dead hour, 8 matins (the prayer), 9 lauds.
 */
public class ColegioScript extends CaseScript {
	static final String NUN = "monja";
	static final String[] SURNAMES = {"ferreyra", "quiroga", "bazan", "luna", "sosa", "heredia", "moyano"};
	static final String[] GIRL_SPOTS = {"aula_voz_1", "aula_voz_2", "aula_voz_3", "aula_voz_4"};

	@Override
	public String siteKey() {
		return "colegio";
	}

	@Override
	public void define(Script s) {
		chapters(s);
		arrival(s);
		study(s);
		dinner(s);
		office(s);
		compline(s);
		corridorRule(s);
	}

	// ================================================================== chapters
	private void chapters(Script s) {
		s.chapter(1, "spawn").noCard().objectives("entrar").hint("entrar")
				.setup(lights("hall_arana", true), lights("pasillo_pb", true), door("entrada", true, false));
		s.chapter(2, "aula_puerta").objectives("aula", "frente").hint("aula")
				.setup(lights("pasillo_pb", true), door("aula", true, false), run(e -> Props.write(e.run, "pizarron", Props.chalk(""), 1.6F)));
		s.chapter(3, "refectorio").objectives("llave").hint("llave")
				.setup(lights("refectorio_velas", false), lights("pasillo_pb", true), door("cocina", true, false));
		s.chapter(4, "hall").objectives("direccion").hint("direccion")
				.setup(lights("pasillo_pb", false), door("direccion", true, false));
		s.chapter(5, "capilla_puerta").objectives("confesar", "coro").hint("confesar")
				.setup(lights("capilla_lampara", true), door("capilla", true, false));
		s.chapter(6, "dormitorio_puerta").objectives("dormitorio", "espejo", "silencio").hint("dormitorio")
				.setup(lights("hall_arana", false), door("dormitorio", true, false));
		s.chapter(7, "sacristia").objectives("regla", "volver").hint("regla")
				.setup(lights("capilla_lampara", true));
		s.chapter(8, "coro_alto").objectives("velas", "rezar", "romper").hint("velas");
		s.chapter(9, "capilla_puerta").noCard().objectives("volver_casa");
	}

	// ================================================================== 1. arrival
	private void arrival(Script s) {
		s.beat("timbre").chapter(1).when(enter("hall")).then(
				complete("entrar"),
				door("entrada", false, true),
				sound(ModSounds.COLEGIO_TIMBRE, "hall_centro", 2.5F),
				shake(0.5F, 30),
				run(e -> dust(e.run, "hall_centro")),
				sound(ModSounds.COLEGIO_POLVO, "hall_centro", 1.0F),
				wait(70),
				chapter(2));
	}

	// ================================================================== 2. study: roll call, blackboard, lesson
	private void study(Script s) {
		List<Step> lista = new ArrayList<>(List.of(complete("aula"), wait(30), say("colegio.madre.lista", "aula_frente"), wait(12)));
		for (int i = 0; i < SURNAMES.length; i++) {
			lista.add(say("colegio.madre." + SURNAMES[i], "aula_frente"));
			lista.add(wait(8 + i % 3 * 4));
			lista.add(say("colegio.alumna.presente", GIRL_SPOTS[i % GIRL_SPOTS.length]));
		}
		lista.addAll(List.of(
				say("colegio.madre.albornoz", "aula_frente"),
				wait(50),
				say("colegio.madre.ausente", "aula_frente"),
				wait(20),
				say("colegio.madre.usted", "aula_frente"),
				// answer with your voice (Simple Voice Chat) within 4 s, or be marked absent
				run(e -> e.run.counters.remove("voice_seen")),
				loop(e -> {
					if (e.run.event("voice")) {
						e.run.counters.put("voice_seen", 1);
						return true;
					}
					return e.t >= 80;
				}),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null && e.run.count("voice_seen") == 0) {
						Props.reprimand(e.run, p, "lista", 1);
					}
				}),
				flag("lista_done")));
		s.beat("lista").chapter(2).when(enter("aula")).then(lista.toArray(Step[]::new));

		s.beat("pizarron").chapter(2).requires("lista_done").when(lookAt("aula_pizarron", 25, 14)).then(
				Props.chalkWrite("pizarron", e -> "NO MIRES ATRÁS"),
				// wait until they look away from the board (nothing there)...
				waitUntil(e -> e.target() != null && !e.run.looking(e.target(), e.run.at("aula_pizarron"), 50, 20)),
				wait(10),
				// ...and back: now it says TE DIJE, and she is standing at the back, behind them, in the dark
				waitUntil(e -> e.target() != null && e.run.looking(e.target(), e.run.at("aula_pizarron"), 30, 20), 20 * 30),
				run(e -> {
					Props.write(e.run, "pizarron", Props.chalk("TE DIJE"), 1.6F);
					e.run.sound(ModSounds.TIZA_ROMPE, e.run.at("aula_pizarron"), 1.0F, 1.0F);
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "aula_fondo", true);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_IDLE);
					}
				}),
				sound(ModSounds.MONJA_REGLA_TAP, "aula_fondo", 1.2F),
				wait(30),
				// burn her with the flashlight (or she sinks by herself after a while)
				waitUntil(e -> e.target() != null && Props.beamOn(e.target(), e.run.actor(NUN)), 20 * 25),
				run(e -> {
					Props.action(e.run, NUN, MonjaEntity.ACT_BURN);
					e.run.sound(ModSounds.MONJA_HISS, e.run.at("aula_fondo"), 1.8F, 1.0F);
				}),
				wait(16),
				run(e -> Props.burnAway(e.run, NUN)),
				wait(20),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.faceGroup(e.run, "aula_sillas", p.position());
					}
					e.run.sound(ModSounds.PUPITRES_GIRAN, e.run.at("aula_centro"), 2.0F, 1.0F);
				}),
				shake(0.4F, 20),
				wait(30),
				Props.chalkWrite("pizarron", e -> (e.target() != null ? e.target().getName().getString().toUpperCase() : "ALUMNO") + " PASÁ AL FRENTE"),
				flag("pizarron_done"));

		s.beat("leccion").chapter(2).requires("pizarron_done").when(enter("aula_tarima")).then(
				run(e -> Props.write(e.run, "pizarron", Props.chalk("¿CUÁNTAS ERAN EN EL CORO?\nA) 7   B) 8\nC) 12   D) NI IDEA"), 1.2F)),
				say("colegio.madre.pregunta1", "aula_frente"),
				answer(),
				run(e -> {
					String a = (String) e.run.vars.get("answer");
					ServerPlayer p = e.target();
					if ("b".equals(a)) {
						e.run.say("colegio.madre.correcto", e.run.at("aula_frente"));
						if (p != null) {
							Props.commend(e.run, p);
						}
					} else {
						e.run.say("colegio.madre.conta_bien", e.run.at("aula_frente"));
						if ("a".equals(a) && p != null) {
							reglazo(e.run, p);
						}
					}
				}),
				wait(50),
				run(e -> Props.write(e.run, "pizarron", Props.chalk("¿QUIÉN CASTIGA?\nA) LA MADRE   B) SOR MARÍA\nC) DIOS   D) TU VIEJA"), 1.2F)),
				say("colegio.madre.pregunta2", "aula_frente"),
				answer(),
				run(e -> {
					String a = (String) e.run.vars.get("answer");
					ServerPlayer p = e.target();
					if ("d".equals(a)) {
						e.run.say("colegio.madre.como_dijo", e.run.at("aula_frente"));
						if (p != null) {
							Props.reprimand(e.run, p, "irrespeto", 3);
						}
						e.run.say("colegio.alumna.risitas", e.run.at("aula_centro"));
					}
				}),
				wait(40),
				Props.chalkWrite("pizarron", e -> "ELLA"),
				door("aula", false, true),
				shake(0.6F, 20),
				complete("frente"),
				wait(40),
				door("aula", true, false),
				chapter(3));
	}

	/** Waits until the hunter crouches on one of the chalk squares a/b/c/d for 1 s; stores vars.answer. */
	private static Step answer() {
		return e -> {
			ServerPlayer p = e.target();
			if (p == null) {
				return true;
			}
			for (String k : new String[] {"a", "b", "c", "d"}) {
				String key = "ans:" + k;
				if (e.run.inside(p, "aula_" + k) && p.isShiftKeyDown()) {
					if (e.run.inc(key) >= 20) {
						e.run.counters.remove(key);
						e.run.vars.put("answer", k);
						return true;
					}
				} else {
					e.run.counters.remove(key);
				}
			}
			if (e.t > 20 * 40) {
				e.run.vars.put("answer", "c");
				return true;
			}
			return false;
		};
	}

	static void reglazo(Run r, ServerPlayer p) {
		r.level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.MONJA_REGLAZO, SoundSource.HOSTILE, 1.6F, 1.0F);
		p.hurtServer(r.level, r.level.damageSources().magic(), 3.0F);
		Fx.redFlash(p, 0.7F);
		Fx.shake(p, 0.8F, 10);
	}

	// ================================================================== 3. dinner: on/off, the key, burst lamps
	private void dinner(Script s) {
		s.beat("prendo_apago").chapter(3).when(enter("refectorio").and(lookAt("ventanilla", 30, 14))).then(
				run(e -> {
					for (int i = 0; i < e.run.def.group("refectorio_velas").size(); i++) {
						e.run.light("refectorio_velas", i, true);
					}
				}),
				sound(ModSounds.MONJA_CAMPANITA, "cocina_fondo", 1.0F),
				run(e -> {
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "cocina_fondo", true);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_BURN);
					}
					e.run.vars.put("toggles", 0);
				}),
				// every off->on of the flashlight brings her closer; at the third she is at the hatch
				loop(e -> {
					if (e.run.event("item:deadline:flashlight")) {
						int t = (Integer) e.run.vars.getOrDefault("toggles", 0) + 1;
						e.run.vars.put("toggles", t);
						if (t % 2 == 0) {
							String[] steps = {"cocina_p1", "cocina_p2", "ventanilla_monja"};
							int k = Math.min(2, t / 2 - 1);
							Props.place(e.run, NUN, steps[k], true);
							e.run.level.sendParticles(ModParticles.DEMON_SMOKE, e.run.at(steps[k]).x, e.run.at(steps[k]).y + 1.6, e.run.at(steps[k]).z, 8, 0.2, 0.3, 0.2, 0.01);
							return k == 2;
						}
					}
					return e.t > 20 * 60;
				}),
				run(e -> {
					Props.place(e.run, NUN, "ventanilla_monja", true);
					e.run.sound(ModSounds.MONJA_HISS, e.run.at("ventanilla"), 2.2F, 0.9F);
					for (ServerPlayer p : e.run.hunters()) {
						Fx.shake(p, 0.9F, 14);
						Fx.redFlash(p, 0.5F);
					}
				}),
				wait(14),
				run(e -> {
					hatch(e.run, false);
					e.run.despawn(NUN);
				}),
				wait(30),
				// she blows the candles out one by one
				loop(e -> {
					List<?> g = e.run.def.group("refectorio_velas");
					if (e.t % 14 == 0) {
						int i = e.t / 14;
						if (i >= g.size()) {
							return true;
						}
						e.run.light("refectorio_velas", i, false);
						Vec3 v = Vec3.atCenterOf(e.run.origin.offset(e.run.def.group("refectorio_velas").get(i)));
						e.run.sound(ModSounds.MONJA_SOPLIDO, v, 1.0F, 0.9F + e.run.level.random.nextFloat() * 0.2F);
						e.run.level.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE, v.x, v.y + 0.3, v.z, 6, 0.05, 0.1, 0.05, 0.01);
					}
					return false;
				}),
				flag("prendo_done"));

		s.beat("llave").chapter(3).when(event("use:tablero")).then(
				give(ModItems.LLAVE_CAPILLA, 1),
				sound(ModSounds.TIZA_ROMPE, "tablero", 0.6F),
				complete("llave"),
				flag("llave"));

		s.beat("pasillo").chapter(3).requires("llave").when(enter("pasillo_pb")).then(
				sound(ModSounds.MONJA_REGLA_TAP, "pasillo_fondo", 1.6F),
				wait(10),
				// the lamps burst from the far end towards you
				loop(e -> {
					List<?> g = e.run.def.group("pasillo_pb");
					if (e.t % 9 == 0) {
						int i = e.t / 9;
						if (i >= g.size()) {
							return true;
						}
						e.run.light("pasillo_pb", i, false);
						Vec3 v = Vec3.atCenterOf(e.run.origin.offset(e.run.def.group("pasillo_pb").get(i)));
						e.run.sound(ModSounds.FAROL_REVIENTA, v, 1.6F, 0.9F + e.run.level.random.nextFloat() * 0.2F);
						e.run.level.sendParticles(ModParticles.HOLY_SPARK, v.x, v.y, v.z, 10, 0.2, 0.2, 0.2, 0.05);
						if (i % 2 == 1) {
							e.run.sound(ModSounds.MONJA_REGLA_TAP, e.run.at("pasillo_fondo"), 1.4F, 1.0F);
						}
					}
					return false;
				}),
				flag("pasillo_done"));

		s.beat("cena_fin").chapter(3).requires("pasillo_done").when(enter("hall")).then(chapter(4));
	}

	/** Opens/closes the service hatch trapdoor between the dining hall and the kitchen. */
	static void hatch(Run r, boolean open) {
		net.minecraft.core.BlockPos pos = r.block("ventanilla");
		var st = r.level.getBlockState(pos);
		if (st.hasProperty(net.minecraft.world.level.block.state.properties.BlockStateProperties.OPEN)) {
			r.setBlock(pos, st.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.OPEN, open));
			r.sound(ModSounds.DOOR_SLAM, Vec3.atCenterOf(pos), 1.2F, 1.4F);
		}
	}

	// ================================================================== 4. the principal's office
	private void office(Script s) {
		s.beat("megafonia").chapter(4).when(chapterTime(30)).then(
				sound(ModSounds.COLEGIO_PA_CHIME, "megafono", 2.0F),
				wait(30),
				say("colegio.madre.megafonia", "megafono"));

		s.beat("mate").chapter(4).when(event("use:direccion_mate")).repeat(40).then(
				sound(ModSounds.MATE_SORBO, "direccion_mate", 1.0F),
				run(e -> {
					int n = e.run.inc("mate");
					for (ServerPlayer p : e.run.hunters()) {
						Fx.subtitle(p, "deadline.speaker.tu", "deadline.line.colegio.mate.lavado" + (n == 1 ? 1 : 2), 70);
						if (n == 2) {
							SanityManager.add(p, 5F);
						}
					}
				}));

		s.beat("legajo").chapter(4).when(event("use:direccion_legajo")).then(
				complete("direccion"),
				bigText("deadline.text.colegio.legajo", 140),
				wait(90),
				// the bakelite phone rings until it is answered
				loop(e -> {
					if (e.t % 50 == 0) {
						e.run.sound(ModSounds.TELEFONO_BAQUELITA_RING, e.run.at("direccion_telefono"), 1.8F, 1.0F);
					}
					return e.run.event("use:direccion_telefono") || e.t > 20 * 30;
				}),
				sound(ModSounds.TELEFONO_LINEA, null, 1.0F),
				wait(30),
				// TODO(voice): your own "presente" from the roll call, then reversed (Simple Voice Chat capture)
				say("colegio.clara.1984", null),
				wait(15),
				say("colegio.clara.ya_sabe", null),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.faceGroup(e.run, "direccion_silla", p.position());
					}
				}),
				sound(ModSounds.SILLA_GIRA, "direccion_silla", 1.4F),
				wait(40),
				chapter(5));
	}

	// ================================================================== 5. compline: confession and the upper choir
	private void compline(Script s) {
		s.beat("confesionario").chapter(5).when(crouch("confesionario_in", 40)).then(
				say("colegio.cura.ave", "confesionario"),
				// he listens for 4-8 s of your voice (6 s without a microphone)
				waitUntil(e -> e.run.count("voice_ticks") >= 80 || e.t >= 120),
				run(e -> e.run.say("colegio.cura.r" + (1 + e.run.level.random.nextInt(4)), e.run.at("confesionario"))),
				wait(70),
				say("colegio.cura.corre", "confesionario"),
				sound(ModSounds.CONFESIONARIO_REJILLA, "confesionario", 1.2F),
				run(e -> {
					Props.spawn(e.run, NUN, ModEntities.MONJA, "confesionario_cara", true);
					Props.action(e.run, NUN, MonjaEntity.ACT_SCREAM);
					e.run.sound(ModSounds.MONJA_SCREAM, e.run.at("confesionario"), 2.0F, 1.0F);
					for (ServerPlayer p : e.run.hunters()) {
						Fx.shake(p, 1.0F, 18);
						Fx.redFlash(p, 0.7F);
					}
				}),
				wait(26),
				despawn(NUN),
				complete("confesar"),
				flag("confesado"));

		s.beat("coro_alto").chapter(5).requires("confesado").when(enter("capilla")).then(
				run(e -> {
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "coro_monja", false);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_CONDUCT);
					}
				}),
				sound(ModSounds.CORO_AVE_REVES, "coro_alto", 2.2F),
				waitUntil(e -> e.target() != null && (Props.beamOn(e.target(), e.run.actor(NUN))
						|| e.run.looking(e.target(), e.run.at("coro_monja"), 12, 30) && e.t > 100), 20 * 40),
				run(e -> {
					for (ServerPlayer p : e.run.hunters()) {
						p.connection.send(new net.minecraft.network.protocol.game.ClientboundStopSoundPacket(
								ModSounds.CORO_AVE_REVES.location(), SoundSource.HOSTILE));
					}
					Props.place(e.run, NUN, "coro_monja", true);
					Props.action(e.run, NUN, MonjaEntity.ACT_IDLE);
				}),
				wait(40),
				lights("capilla_lampara", false),
				wait(6),
				lights("capilla_lampara", true),
				wait(4),
				lights("capilla_lampara", false),
				despawn(NUN),
				wait(10),
				lights("capilla_lampara", true),
				say("colegio.paloma.toma", "coro_alto"),
				complete("coro"),
				wait(40),
				chapter(6));
	}

	// ================================================================== the corridor rule (all chapters)
	private void corridorRule(Script s) {
		s.beat("no_se_corre").from(3).repeat(20 * 90).when((r, p) -> p.isSprinting() && r.inside(p, "edificio")).then(
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.reprimand(e.run, p, "correr", 1);
					}
				}),
				say("colegio.monja.no_se_corre", null));
	}

	// ================================================================== helpers
	static void dust(Run r, String point) {
		Vec3 v = r.at(point);
		r.level.sendParticles(net.minecraft.core.particles.ParticleTypes.WHITE_ASH, v.x, v.y + 4.5, v.z, 120, 3.0, 0.3, 3.0, 0.01);
	}
}
