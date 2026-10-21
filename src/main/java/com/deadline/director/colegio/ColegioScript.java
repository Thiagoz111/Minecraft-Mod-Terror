package com.deadline.director.colegio;

import static com.deadline.director.Steps.*;
import static com.deadline.director.Triggers.*;

import com.deadline.DeadLine;
import com.deadline.director.CaseScript;
import com.deadline.director.Props;
import com.deadline.director.Run;
import com.deadline.director.Script;
import com.deadline.director.Step;
import com.deadline.entity.ApparitionEntity;
import com.deadline.entity.MonjaEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Brightness;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
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
		// doors that stay locked until their chapter opens them (the Silence Room only opens for the script)
		s.lock("aula", 1, 2).lock("cocina", 1, 4).lock("aula4", 1, 99).lock("direccion", 1, 4).lock("capilla", 1, 5).lock("capilla2", 1, 5)
				.lock("coro", 1, 5).lock("dormitorio", 1, 6).lock("banos", 1, 6).lock("sacristia", 1, 7)
				.lock("cuarto_silencio", 1, 99).lock("entrada", 2, 99);
		chapters(s);
		arrival(s);
		study(s);
		dinner(s);
		office(s);
		compline(s);
		greatSilence(s);
		deadHour(s);
		matins(s);
		lauds(s);
		corridorRule(s);
	}

	// ================================================================== chapters
	private void chapters(Script s) {
		s.chapter(1, "spawn").noCard().objectives("entrar").hint("entrar")
				.setup(lights("hall_arana", true), lights("pasillo_pb", true), door("entrada", true, false));
		s.chapter(2, "aula_puerta").objectives("aula", "frente").hint("aula")
				.setup(lights("pasillo_pb", true), door("aula", true, false), run(e -> Props.write(e.run, "pizarron", Props.chalk(""), 1.6F)));
		s.chapter(3, "refectorio").objectives("llave").hint("llave")
				.setup(lights("refectorio_velas", false), lights("pasillo_pb", true), door("cocina", false, false),
						run(e -> {
							hatch(e.run, true);
							Props.swap(e.run, "tablero", "colegio_tablero_llaves");
						}));
		s.chapter(4, "hall").objectives("direccion").hint("direccion")
				.setup(lights("pasillo_pb", false), door("direccion", true, false));
		s.chapter(5, "capilla_puerta").objectives("confesar", "coro").hint("confesar")
				.setup(lights("capilla_lampara", true), door("capilla", true, false));
		s.chapter(6, "dormitorio_puerta").objectives("dormitorio", "espejo", "silencio").hint("dormitorio")
				.setup(lights("hall_arana", false), lights("pasillo_pb", false), lights("dormitorio_luna", true),
						door("dormitorio", true, false), door("banos", true, false), door("cuarto_silencio", false, false),
						run(e -> moveChair(e.run, 0)));
		s.chapter(7, "sacristia").objectives("regla", "volver").hint("regla")
				.setup(lights("capilla_lampara", true), lights("cripta_islas", false), door("sacristia", true, false),
						run(e -> {
							flashlights(e.run, false);
							swapHolyWater(e.run, false);
							// a replay starts with the 1984 wall standing again
							for (BlockPos rel : e.run.def.group("cripta_muro")) {
								BlockState st = e.run.authored(rel);
								if (st != null) {
									e.run.setBlock(e.run.origin.offset(rel), st);
								}
							}
						}));
		s.chapter(8, "coro_alto").objectives("velas", "rezar", "romper").hint("velas")
				.setup(lights("coro_velas", false), lights("capilla_lampara", false), run(e -> {
					flashlights(e.run, true);
					// the ruler is needed to end it: back in hand after a retake or a death that dropped it
					for (ServerPlayer p : e.run.hunters()) {
						if (!p.getInventory().contains(new ItemStack(ModItems.REGLA_QUEBRACHO))) {
							p.getInventory().add(new ItemStack(ModItems.REGLA_QUEBRACHO));
						}
					}
				}));
		s.chapter(9, "coro_alto").noCard().objectives("volver_casa");
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
				delay(70),
				chapter(2));
	}

	// ================================================================== 2. study: roll call, blackboard, lesson
	private void study(Script s) {
		List<Step> lista = new ArrayList<>(List.of(complete("aula"), delay(30), say("colegio.madre.lista", "aula_frente"), delay(12)));
		for (int i = 0; i < SURNAMES.length; i++) {
			lista.add(say("colegio.madre." + SURNAMES[i], "aula_frente"));
			lista.add(delay(8 + i % 3 * 4));
			lista.add(say("colegio.alumna.presente", GIRL_SPOTS[i % GIRL_SPOTS.length]));
		}
		lista.addAll(List.of(
				say("colegio.madre.albornoz", "aula_frente"),
				delay(50),
				say("colegio.madre.ausente", "aula_frente"),
				delay(20),
				// answer with your voice (Simple Voice Chat) within 4 s, or be marked absent; the answer is kept
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						com.deadline.voice.Voice.tagNext(p, "presente", 6000);
					}
				}),
				run(e -> e.run.counters.remove("voice_seen")),
				loop(e -> {
					// she asks, and listens from the first word: raising your hand (sneak) answers too
					if (e.t == 0) {
						e.n = e.run.say("colegio.madre.usted", e.run.at("aula_frente"));
					}
					ServerPlayer p = e.target();
					boolean hand = p != null && p.isShiftKeyDown();
					if (e.run.event("voice") || hand) {
						e.run.counters.put("voice_seen", 1);
						return true;
					}
					return e.t >= e.n + 80;
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
				delay(10),
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
				delay(30),
				// burn her with the flashlight (or she sinks by herself after a while)
				waitUntil(e -> e.target() != null && Props.beamOn(e.target(), e.run.actor(NUN)), 20 * 25),
				run(e -> {
					Props.action(e.run, NUN, MonjaEntity.ACT_BURN);
					e.run.sound(ModSounds.MONJA_HISS, e.run.at("aula_fondo"), 1.8F, 1.0F);
				}),
				delay(16),
				run(e -> Props.burnAway(e.run, NUN)),
				delay(20),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.faceGroup(e.run, "aula_sillas", p.position());
					}
					e.run.sound(ModSounds.PUPITRES_GIRAN, e.run.at("aula_centro"), 2.0F, 1.0F);
				}),
				shake(0.4F, 20),
				delay(30),
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
				delay(50),
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
				delay(40),
				Props.chalkWrite("pizarron", e -> "ELLA"),
				door("aula", false, true),
				shake(0.6F, 20),
				complete("frente"),
				delay(40),
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
				delay(14),
				run(e -> {
					hatch(e.run, false);
					e.run.despawn(NUN);
				}),
				door("cocina", true, false),  // now you have to go in there for the key
				delay(30),
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
				run(e -> Props.swap(e.run, "tablero", "colegio_tablero_llaves_falta")),
				sound(ModSounds.TIZA_ROMPE, "tablero", 0.6F),
				complete("llave"),
				flag("llave"));

		s.beat("pasillo").chapter(3).requires("llave").when(enter("pasillo_pb")).then(
				sound(ModSounds.MONJA_REGLA_TAP, "pasillo_fondo", 1.6F),
				delay(10),
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

	/** Opens/closes the service hatch between the dining hall and the kitchen (a trapdoor: OPEN = vertical = shut). */
	static void hatch(Run r, boolean open) {
		net.minecraft.core.BlockPos pos = r.block("ventanilla");
		boolean hit = false;
		for (net.minecraft.core.BlockPos q : new net.minecraft.core.BlockPos[] {pos, pos.south()}) {  // the hatch is two trapdoors wide
			var st = r.level.getBlockState(q);
			if (st.getBlock() instanceof net.minecraft.world.level.block.TrapDoorBlock) {
				r.setBlock(q, st.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.OPEN, !open));
				hit = true;
			}
		}
		if (hit) {
			r.sound(ModSounds.DOOR_SLAM, Vec3.atCenterOf(pos), 1.2F, 1.4F);
		}
	}

	// ================================================================== 4. the principal's office
	private void office(Script s) {
		s.beat("megafonia").chapter(4).when(chapterTime(30)).then(
				sound(ModSounds.COLEGIO_PA_CHIME, "megafono", 2.0F),
				delay(30),
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

		s.beat("direccion_entra").chapter(4).when(enter("direccion")).then(
				delay(30),
				sound(ModSounds.CONFESIONARIO_REJILLA, "direccion_legajo", 1.1F),
				run(e -> {
					for (ServerPlayer p : e.run.hunters()) {
						Fx.subtitle(p, "deadline.speaker.cartel", "deadline.colegio.caption.archivero", 90);
					}
				}));

		s.beat("legajo").chapter(4).when(event("use:direccion_legajo")).then(
				complete("direccion"),
				bigText("deadline.text.colegio.legajo", 140),
				delay(90),
				// the bakelite phone rings until it is answered
				loop(e -> {
					if (e.t % 50 == 0) {
						e.run.sound(ModSounds.TELEFONO_BAQUELITA_RING, e.run.at("direccion_telefono"), 1.8F, 1.0F);
					}
					return e.run.event("use:direccion_telefono") || e.t > 20 * 30;
				}),
				sound(ModSounds.TELEFONO_LINEA, null, 1.0F),
				delay(30),
				// your own answer to the roll call comes back down the line... then backwards (voice use #1)
				run(e -> {
					ServerPlayer p = e.target();
					e.run.vars.put("echo", p != null && com.deadline.voice.Voice.play(p, p, "presente",
							com.deadline.voice.VoiceBackend.Effect.PHONE, null) ? 1 : 0);
				}),
				run(e -> {
					if (!Integer.valueOf(1).equals(e.run.vars.get("echo"))) {
						e.run.say("colegio.mimic.presente", null);  // no recording: a voice like yours, in words
					}
				}),
				delay(40),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null && Integer.valueOf(1).equals(e.run.vars.get("echo"))) {
						com.deadline.voice.Voice.play(p, p, "presente", com.deadline.voice.VoiceBackend.Effect.PHONE_REVERSED, null);
					}
				}),
				delay(40),
				say("colegio.clara.1984", null),
				delay(15),
				say("colegio.clara.ya_sabe", null),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.faceGroup(e.run, "direccion_silla", p.position());
					}
				}),
				sound(ModSounds.SILLA_GIRA, "direccion_silla_pt", 1.4F),
				delay(40),
				chapter(5));
	}

	// ================================================================== 5. compline: confession and the upper choir
	private void compline(Script s) {
		s.beat("confesionario").chapter(5).when(crouch("confesionario_in", 40).or(event("use:confesionario"))).then(
				say("colegio.cura.ave", "confesionario"),
				// he listens for 4-8 s of your voice (6 s without a microphone)
				run(e -> e.run.counters.remove("voice_ticks")),
				waitUntil(e -> {
					ServerPlayer p = e.target();
					boolean mic = p != null && com.deadline.voice.Voice.enabled(p);
					return mic ? e.run.count("voice_ticks") >= 80 || e.t >= 160 : e.t >= 120;
				}),
				run(e -> e.run.say("colegio.cura.r" + (1 + e.run.level.random.nextInt(4)), e.run.at("confesionario"))),
				delay(70),
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
				delay(26),
				despawn(NUN),
				complete("confesar"),
				flag("confesado"));

		s.beat("coro_alto").chapter(5).requires("confesado").when(enter("capilla")).then(
				run(e -> {
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "coro_monja", false);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_CONDUCT);
					}
					girls(e.run, "atril_", ApparitionEntity.POSE_SING);
				}),
				// the backwards Ave Maria (a 20 s loop) keeps going until they are caught in the light
				loop(e -> {
					if (e.t % 400 == 0 && e.t < 20 * 40) {
						e.run.sound(ModSounds.CORO_AVE_REVES, e.run.at("coro_alto"), 2.2F, 1.0F);
					}
					return e.t >= 20 * 40 || e.target() != null && (Props.beamOn(e.target(), e.run.actor(NUN))
							|| e.run.looking(e.target(), e.run.at("coro_monja"), 12, 30) && e.t > 100);
				}),
				run(e -> {
					for (ServerPlayer p : e.run.hunters()) {
						p.connection.send(new net.minecraft.network.protocol.game.ClientboundStopSoundPacket(
								ModSounds.CORO_AVE_REVES.location(), SoundSource.HOSTILE));
					}
					Props.place(e.run, NUN, "coro_monja", true);
					Props.action(e.run, NUN, MonjaEntity.ACT_IDLE);
					// the only head turn of the case: eight heads at once
					for (int i = 0; i < 7; i++) {
						Props.action(e.run, "alumna_" + i, ApparitionEntity.POSE_HEAD_180);
					}
				}),
				delay(40),
				lights("capilla_lampara", false),
				delay(6),
				lights("capilla_lampara", true),
				delay(4),
				lights("capilla_lampara", false),
				despawn(NUN),
				run(e -> despawnGirls(e.run)),
				delay(10),
				lights("capilla_lampara", true),
				run(e -> {
					ApparitionEntity paloma = Props.spawn(e.run, "paloma", ModEntities.ALUMNA, "atril_3", true);
					if (paloma != null) {
						paloma.setVariant(0);
						paloma.setAction(ApparitionEntity.POSE_POINT);
					}
					swapHolyWater(e.run, true);
				}),
				say("colegio.paloma.toma", "coro_alto"),
				despawn("paloma"),
				complete("coro"),
				delay(40),
				chapter(6));
	}

	// ================================================================== 6. the great silence: dormitory, mirror, Silence Room
	private void greatSilence(Script s) {
		s.beat("gran_silencio").chapter(6).when(chapterTime(10)).then(
				sound(ModSounds.LUCES_FUERA, null, 1.4F),
				lights("hall_arana", false),
				lights("pasillo_1p", false),
				run(e -> flashlights(e.run, false)),
				delay(40),
				say("colegio.clara.dormitorio", null));

		s.beat("dormitorio").chapter(6).when(enter("dormitorio")).then(
				sound(ModSounds.DORMITORIO_RESPIRA, "dorm_silla_2", 1.2F),
				run(e -> {
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "dorm_silla_0", false);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_SIT);
					}
					e.run.vars.put("silla", 0);
				}),
				delay(30),
				sayAsync("colegio.alumna.shh", "cama8"),
				delay(50),
				caption("colegio.cartel.agua", 100),
				flag("nubes"));

		// every 20 s the moon is covered: the chair is closer when it comes back; if you moved, she gets up
		s.beat("nube").chapter(6).requires("nubes").unless("dormitorio_hecho").repeat(20 * 14).when(always()).then(
				sound(ModSounds.COLEGIO_VIENTO, "dorm_silla_2", 1.5F),
				delay(40),
				lights("dormitorio_luna", false),
				run(e -> {
					ServerPlayer p = e.target();
					e.run.vars.put("nube_pos", p == null ? null : p.position());
				}),
				delay(100),
				run(e -> {
					ServerPlayer p = e.target();
					Vec3 before = (Vec3) e.run.vars.get("nube_pos");
					boolean moved = p != null && before != null && (p.position().distanceTo(before) > 1.2
							|| com.deadline.voice.NoiseMeter.get(p) > 40F);
					int i = Math.min(4, (Integer) e.run.vars.getOrDefault("silla", 0) + 1);
					moveChair(e.run, i);
					if (!e.run.has("persigue")) {
						Props.place(e.run, NUN, "dorm_silla_" + i, true);
						e.run.sound(ModSounds.SILLA_ARRASTRA, e.run.at("dorm_silla_" + i), 1.4F, 0.9F);
					}
					if (moved) {
						wakeNun(e.run, 200);
					}
				}),
				lights("dormitorio_luna", true));

		// the tap-water gag: the "holy water" Paloma gave you does nothing
		s.beat("canilla").chapter(6).requires("nubes").unless("dormitorio_hecho")
				.when(event("item:deadline:agua_canilla").and((r, p) -> r.actor(NUN) != null && r.actor(NUN).distanceTo(p) < 12)).then(
				run(e -> {
					Entity nun = e.run.actor(NUN);
					if (nun != null) {
						nun.setDeltaMovement(Vec3.ZERO);
						if (nun instanceof MonjaEntity m) {
							m.scripted = true;
							m.setNoAi(true);
							m.setTarget(null);
							m.getNavigation().stop();
							m.setAction(MonjaEntity.ACT_WET);
						}
						e.run.level.sendParticles(net.minecraft.core.particles.ParticleTypes.SPLASH, nun.getX(), nun.getY() + 1.4, nun.getZ(), 40, 0.3, 0.5, 0.3, 0.1);
						e.run.sound(ModSounds.MONJA_MOJADA, nun.position(), 1.6F, 1.0F);
					}
				}),
				delay(30),
				caption("colegio.cartel.canilla", 60),
				sayAsync("colegio.alumna.risitas", "cama8"),
				delay(20),
				run(e -> {
					Entity nun = e.run.actor(NUN);
					if (nun != null) {
						e.run.sound(ModSounds.MONJA_SCREAM, nun.position(), 2.2F, 1.0F);
					}
					wakeNun(e.run, 220);
				}),
				delay(120),
				run(e -> swapHolyWater(e.run, false)),
				say("colegio.paloma.perdon", null));

		s.beat("cama8").chapter(6).when(event("use:cama8")).then(
				give(ModItems.DIARIO_TERESITA, 1),
				sound(ModSounds.SILLA_ARRASTRA, "cama8", 0.6F),
				sayAsync("colegio.alumna.shh_viene", "cama8"));

		s.beat("banos").chapter(6).when(enter("banos")).then(
				complete("dormitorio"),
				flag("dormitorio_hecho"),
				run(e -> {
					e.run.unflag("persigue");
					e.run.despawn(NUN);
					swapHolyWater(e.run, false);
				}));

		// the diary only reads the right way round in the mirror; then she is behind the reflection
		s.beat("espejo").chapter(6).requires("dormitorio_hecho").when(holding(ModItems.DIARIO_TERESITA).and(lookAt("espejo", 25, 7))).then(
				run(e -> {
					for (int i = 0; i < 2; i++) {
						ApparitionEntity g = Props.spawn(e.run, "espejo_nena_" + i, ModEntities.ALUMNA, "espejo_nena_" + i, false);
						if (g != null) {
							g.setVariant(i + 2);
							g.setAction(ApparitionEntity.POSE_STAND);
						}
					}
					Display.TextDisplay td = Props.write(e.run, "diario_espejo",
							Props.chalk("21/6. Las escucho cantar al revés.\nLo hicieron sin mí.\nEran siete.\nEL LIBRO DICE OCHO."), 1.0F);
					if (td != null) {
						td.setBrightnessOverride(new Brightness(12, 0));
					}
				}),
				bigText("deadline.text.colegio.diario", 140),
				delay(120),
				run(e -> {
					Props.spawn(e.run, NUN, ModEntities.MONJA, "espejo_detras", false);
					e.run.sound(ModSounds.MONJA_REGLA_TAP, e.run.at("espejo_detras"), 1.2F, 1.0F);
				}),
				waitUntil(e -> e.target() != null && !e.run.looking(e.target(), e.run.at("espejo"), 60, 10), 20 * 12),
				run(e -> Props.place(e.run, NUN, "espejo_cara", false)),
				waitUntil(e -> e.target() != null && e.run.looking(e.target(), e.run.at("espejo"), 35, 10), 20 * 12),
				sound(ModSounds.ESPEJO_RAJA, "espejo", 2.0F),
				jumpscare("monja"),
				shake(1.0F, 20),
				delay(12),
				fade(60),
				delay(30),
				teleport("cuarto_silencio"),
				run(e -> {
					e.run.despawn(NUN);
					e.run.despawn("espejo_nena_0");
					e.run.despawn("espejo_nena_1");
					e.run.door("cuarto_silencio", false, true);
				}),
				complete("espejo"),
				flag("encerrado"));

		// 15 seconds of silence (voice) or stillness (no microphone); Paloma tries to make you laugh
		s.beat("cuarto_silencio").chapter(6).requires("encerrado").when(enter("cuarto_silencio")).then(
				delay(30),
				say("colegio.madre.pensa", null),
				silence(),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.commend(e.run, p);
					}
				}),
				door("cuarto_silencio", true, false),
				complete("silencio"),
				delay(40),
				chapter(7));
	}

	// ================================================================== 7. the dead hour: the ruler, the wall, run
	private void deadHour(Script s) {
		s.beat("tumba").chapter(7).when(event("use:cripta_tumba")).then(
				sound(ModSounds.TUMBA_TAPA, "cripta_tumba", 1.6F),
				delay(50),
				give(ModItems.REGLA_QUEBRACHO, 1),
				complete("regla"),
				sound(ModSounds.COLEGIO_CAMPANA_TRIPLE, null, 1.6F),
				shake(0.5F, 20),
				delay(60),
				shake(0.6F, 20),
				delay(60),
				shake(0.8F, 30),
				lights("capilla_lampara", false),
				delay(40),
				run(e -> {
					for (BlockPos rel : e.run.def.group("cripta_muro")) {
						e.run.setBlock(e.run.origin.offset(rel), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
					}
					e.run.sound(ModSounds.MURO_CAE, e.run.at("silla7_3"), 2.2F, 1.0F);
					Vec3 v = e.run.at("silla7_3");
					e.run.level.sendParticles(net.minecraft.core.particles.ParticleTypes.CAMPFIRE_COSY_SMOKE, v.x, v.y + 1, v.z - 2, 60, 3, 1, 0.5, 0.01);
					girls(e.run, "silla7_", ApparitionEntity.POSE_FACE_WALL);
				}),
				delay(50),
				run(e -> {
					for (int i = 0; i < 7; i++) {
						Entity g = e.run.actor("alumna_" + i);
						if (g instanceof ApparitionEntity a) {
							a.setAction(ApparitionEntity.POSE_TURN);
							ServerPlayer p = e.target();
							if (p != null) {
								a.setYRot(Props.yawTowards(a.position(), p.position()));
								a.setYBodyRot(a.getYRot());
								a.setYHeadRot(a.getYRot());
							}
						}
					}
				}),
				delay(10),
				say("colegio.alumnas.corre", "silla7_3"),
				run(e -> {
					for (int i = 0; i < 7; i++) {
						Props.action(e.run, "alumna_" + i, ApparitionEntity.POSE_RUN);
					}
					// she is right behind you
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "silla7_3", true);
					if (m != null) {
						m.scripted = false;
						m.setNoAi(false);
						ServerPlayer p = e.target();
						if (p != null) {
							m.setTarget(p);
						}
					}
				}),
				// the girls run ahead to the sacristy lighting the candle islands
				loop(e -> {
					Vec3 goal = e.run.at("cripta_entrada");
					for (int i = 0; i < 7; i++) {
						Entity g = e.run.actor("alumna_" + i);
						if (g != null) {
							Vec3 d = goal.subtract(g.position());
							double len = d.length();
							if (len > 0.5) {
								Vec3 step = d.scale(Math.min(0.32, len) / len);
								g.setPos(g.getX() + step.x, g.getY(), g.getZ() + step.z);
								g.setYRot(Props.yawTowards(g.position(), goal));
							}
						}
					}
					if (e.t % 25 == 0 && e.t / 25 < 4) {
						e.run.light("cripta_islas", e.t / 25, true);
						e.run.sound(ModSounds.ALUMNA_PASOS, goal, 1.2F, 1.0F);
					}
					return e.t > 130;
				}),
				run(e -> despawnGirls(e.run)),
				flag("persecucion"));

		s.beat("volver").chapter(7).requires("persecucion").when(enter("capilla")).then(
				complete("volver"),
				run(e -> Props.burnAway(e.run, NUN)),
				delay(30),
				chapter(8));
	}

	// ================================================================== 8. matins: 7 candles, the prayer, break the ruler
	private void matins(Script s) {
		s.beat("falta_voz").chapter(8).when(chapterTime(40)).then(say("colegio.clara.falta_voz", null));
		for (int i = 0; i < 7; i++) {
			final int k = i;
			s.beat("vela_" + i).chapter(8).when(event("use:vela_" + i)).then(
					run(e -> {
						e.run.light("coro_velas", k, true);
						ApparitionEntity g = Props.spawn(e.run, "alumna_" + k, ModEntities.ALUMNA, "atril_" + k, false);
						if (g != null) {
							g.setVariant(k);
							g.setAction(ApparitionEntity.POSE_SING);
						}
						ServerPlayer p = e.target();
						if (p != null) {
							Props.commend(e.run, p);
						}
						if (e.run.inc("velas") >= 7) {
							e.run.complete("velas");
							e.run.flag("velas");
						}
					}));
			// a candle she blew out during the prayer can be lit again
			s.beat("revela_" + i).chapter(8).requires("velas").repeat(10).when(event("use:vela_" + i)).then(
					run(e -> e.run.light("coro_velas", k, true)));
		}
		s.beat("rezar").chapter(8).requires("velas").when(enter("atril8")).then(
				prayer(1), flash(0.8F), sound(ModSounds.CORO_AVE_DERECHO_1, "coro_alto", 2.0F), run(e -> wave(e.run)), delay(20 * 12), run(e -> Props.burnAway(e.run, NUN)),
				prayer(2), flash(0.9F), sound(ModSounds.CORO_AVE_DERECHO_2, "coro_alto", 2.2F), run(e -> wave(e.run)), delay(20 * 12), run(e -> Props.burnAway(e.run, NUN)),
				prayer(3), flash(1.0F), sound(ModSounds.CORO_AVE_DERECHO_3, "coro_alto", 2.4F),
				run(e -> {
					MonjaEntity m = Props.spawn(e.run, NUN, ModEntities.MONJA, "coro_pared", false);
					if (m != null) {
						m.setAction(MonjaEntity.ACT_KNEEL_WALL);
					}
				}),
				complete("rezar"),
				flag("arrodillada"));

		s.beat("romper").chapter(8).requires("arrodillada").when((r, p) -> r.event("item:deadline:regla_quebracho")
				&& r.actor(NUN) != null && r.actor(NUN).distanceTo(p) < 5).then(
				sound(ModSounds.REGLA_ROMPE, "coro_pared", 2.2F),
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						var inv = p.getInventory();
						for (int i = 0; i < inv.getContainerSize(); i++) {
							if (inv.getItem(i).is(ModItems.REGLA_QUEBRACHO)) {
								inv.getItem(i).shrink(1);
								break;
							}
						}
					}
					Props.action(e.run, NUN, MonjaEntity.ACT_REVEAL);
				}),
				flash(1.0F),
				shake(1.0F, 30),
				delay(40),
				run(e -> {
					Entity nun = e.run.actor(NUN);
					if (nun != null) {
						e.run.level.sendParticles(ModParticles.DEMON_SMOKE, nun.getX(), nun.getY() + 1.5, nun.getZ(), 120, 0.6, 1.2, 0.6, 0.05);
					}
					e.run.sound(ModSounds.JAR_CAPTURE, e.run.at("coro_pared"), 1.8F, 0.8F);
				}),
				delay(20),
				despawn(NUN),
				complete("romper"),
				delay(30),
				chapter(9));
	}

	// ================================================================== 9. lauds: Clara, the choir with mouths, "SHHH"
	private void lauds(Script s) {
		s.beat("laudes").chapter(9).when(chapterTime(5)).then(
				sound(ModSounds.CORO_ACORDE_FINAL, "coro_alto", 2.0F),
				run(e -> {
					girls(e.run, "atril_", ApparitionEntity.POSE_FREED);
					ApparitionEntity clara = Props.spawn(e.run, "clara", ModEntities.CLARA, "coro_monja", true);
					if (clara != null) {
						clara.setAction(ApparitionEntity.POSE_RISE);
					}
				}),
				delay(40),
				say("colegio.clara.gracias", "coro_monja"),
				delay(20),
				run(e -> {
					ApparitionEntity madre = Props.spawn(e.run, "madre", ModEntities.MADRE, "coro_pared", true);
					if (madre != null) {
						madre.setAction(ApparitionEntity.POSE_WRITE);
					}
				}),
				say("colegio.madre.aja", "coro_pared"),
				delay(10),
				run(e -> {
					for (int i = 0; i < 7; i++) {
						Entity g = e.run.actor("alumna_" + i);
						Entity m = e.run.actor("madre");
						if (g != null && m != null) {
							float yaw = Props.yawTowards(g.position(), m.position());
							g.setYRot(yaw);
							if (g instanceof net.minecraft.world.entity.LivingEntity l) {
								l.setYBodyRot(yaw);
								l.setYHeadRot(yaw);
							}
						}
					}
				}),
				say("colegio.alumnas.shhh", "coro_alto"),
				run(e -> Props.burnAway(e.run, "madre")),
				delay(60),
				run(e -> {
					Props.action(e.run, "clara", ApparitionEntity.POSE_BOW);
					for (ServerPlayer p : e.run.hunters()) {
						Fx.title(p, "deadline.title.solved", 100);
					}
				}),
				complete("volver_casa"),
				delay(120),
				run(e -> {
					for (ServerPlayer p : e.run.hunters()) {
						com.deadline.caseload.CaseManager.returnHome(p, true);
					}
				}));
	}

	/** Lets the nun loose (real AI) for `ticks`, then sits her back on her chair. */
	static void wakeNun(Run r, int ticks) {
		if (r.actor(NUN) instanceof MonjaEntity m) {
			r.flag("persigue");
			m.scripted = false;
			m.setNoAi(false);
			m.setAction(MonjaEntity.ACT_HUNT);
			ServerPlayer p = r.star();
			if (p != null) {
				m.setTarget(p);
			}
			r.vars.put("despierta_hasta", r.now() + ticks);
		}
	}

	/** 15 seconds of silence (voice) or stillness (no microphone) in the Silence Room; Paloma tries to make you laugh. */
	static Step silence() {
		return loop(e -> {
			ServerPlayer p = e.target();
			if (p == null) {
				return true;
			}
			if (e.t == 0) {
				e.run.counters.remove("silencio");
				e.run.vars.remove("quieto_pos");
			}
			Vec3 last = (Vec3) e.run.vars.get("quieto_pos");
			boolean noisy = com.deadline.voice.Voice.enabled(p)
					? com.deadline.voice.Voice.speaking(p, e.run.now())
					: last != null && p.position().distanceTo(last) > 0.08;
			e.run.vars.put("quieto_pos", p.position());
			int n = noisy ? 0 : e.run.count("silencio") + 1;
			e.run.counters.put("silencio", n);
			if (e.t % 4 == 0) {
				Fx.bigText(p, "deadline.text.colegio.silencio", 24, n / 300F);
			}
			if (e.t == 120) {
				e.run.say("colegio.paloma.chiste1", e.run.at("rendija"));
			} else if (e.t == 420) {
				e.run.say("colegio.paloma.chiste2", e.run.at("rendija"));
			}
			return n >= 300;
		});
	}

	/**
	 * The 15th reprimand: when she catches a hunter with 15 or more she does not hit, she takes them to the Silence Room
	 * (chapters 6-7, while she is loose). Out again after 15 s of silence, with the tally back at 10.
	 */
	static void capture(Run r, ServerPlayer p) {
		r.flag("captura");
		r.unflag("persigue");
		r.vars.remove("despierta_hasta");
		if (r.chapter() == 6 && r.actor(NUN) instanceof MonjaEntity m) {
			// the dormitory still needs her on her chair
			m.scripted = true;
			m.setNoAi(true);
			m.setTarget(null);
			m.getNavigation().stop();
			m.setAction(MonjaEntity.ACT_SIT);
			Props.place(r, NUN, "dorm_silla_" + r.vars.getOrDefault("silla", 0), true);
		} else {
			Props.burnAway(r, NUN);
		}
		r.start("captura", p, List.of(
				say("colegio.monja.a_la_pared", null),
				jumpscare("monja"),
				fade(60),
				delay(30),
				teleport("cuarto_silencio"),
				door("cuarto_silencio", false, true),
				delay(30),
				say("colegio.madre.pensa", null),
				silence(),
				run(e -> {
					ServerPlayer q = e.target();
					if (q != null) {
						e.run.counters.put("conduct:" + q.getUUID(), 10);
						Props.commend(e.run, q);
					}
				}),
				door("cuarto_silencio", true, false),
				unflag("captura")));
	}

	/** One prayer phrase: speak it aloud (Simple Voice Chat) or hold the ritual book still; 6 s of progress. */
	static Step prayer(int n) {
		return e -> {
			ServerPlayer p = e.target();
			if (p == null) {
				return true;
			}
			String key = "rezo" + n;
			// out loud (Simple Voice Chat), kneeling (crouch) or holding the ritual book: any of them counts
			boolean voice = com.deadline.voice.Voice.enabled(p) && com.deadline.voice.Voice.speaking(p, e.run.now())
					&& com.deadline.voice.Voice.relative(p) > -8F;
			boolean praying = voice || p.isShiftKeyDown() || p.getMainHandItem().is(ModItems.RITUAL_BOOK)
					|| p.getOffhandItem().is(ModItems.RITUAL_BOOK);
			int v = Math.max(0, e.run.count(key) + (praying ? 2 : (e.t % 2 == 0 ? -1 : 0)));
			e.run.counters.put(key, v);
			if (e.t % 3 == 0) {
				Fx.bigText(p, "deadline.text.colegio.oracion." + n, 20, Math.min(1F, v / 240F));
			}
			return v >= 240;
		};
	}

	/** Between prayer phrases she comes for you (real AI, from the far side of the choir). */
	static void wave(Run r) {
		MonjaEntity m = Props.spawn(r, NUN, ModEntities.MONJA, "coro_monja", true);
		if (m != null) {
			m.scripted = false;
			m.setNoAi(false);
			ServerPlayer p = r.star();
			if (p != null) {
				m.setTarget(p);
			}
			r.sound(ModSounds.MONJA_SCREAM, m.position(), 2.0F, 1.0F);
		}
	}

	/** The seven choir girls at points prefix0..prefix6, each with her own hair. */
	static void girls(Run r, String prefix, int pose) {
		for (int i = 0; i < 7; i++) {
			ApparitionEntity g = Props.spawn(r, "alumna_" + i, ModEntities.ALUMNA, prefix + i, false);
			if (g != null) {
				g.setVariant(i);
				g.setAction(pose);
			}
		}
	}

	static void despawnGirls(Run r) {
		for (int i = 0; i < 7; i++) {
			r.despawn("alumna_" + i);
		}
	}

	/** The warden's chair in the dormitory aisle: only one stands, at dorm_silla_<to>; the others are bare floor. */
	static void moveChair(Run r, int to) {
		Block chair = BuiltInRegistries.BLOCK.getOptional(DeadLine.id("colegio_silla_monja")).orElse(null);
		if (chair == null) {
			return;
		}
		for (int i = 0; i <= 4; i++) {
			BlockPos pos = r.block("dorm_silla_" + i);
			boolean here = r.level.getBlockState(pos).is(chair);
			if (i == to && !here) {
				r.setBlock(pos, chair.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.NORTH));
			} else if (i != to && here) {
				r.setBlock(pos, Blocks.AIR.defaultBlockState());
			}
		}
		r.vars.put("silla", to);
	}

	@Override
	public void onLeave(Run r, ServerPlayer p) {
		// whatever Paloma and the great silence took from you comes back when you leave the school
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack st = inv.getItem(i);
			if (st.is(ModItems.AGUA_CANILLA)) {
				inv.setItem(i, new ItemStack(ModItems.HOLY_WATER, st.getCount()));
			}
		}
		if (r.chapter() == 6 || r.chapter() == 7) {
			for (int i = 0; i < inv.getContainerSize(); i++) {
				ItemStack st = inv.getItem(i);
				if (st.is(ModItems.FLASHLIGHT)) {
					st.setDamageValue(0);
				}
			}
		}
	}

	/** Paloma's trick: every holy water becomes tap water (true) and back (false). */
	static void swapHolyWater(Run r, boolean toTap) {
		for (ServerPlayer p : r.hunters()) {
			var inv = p.getInventory();
			for (int i = 0; i < inv.getContainerSize(); i++) {
				ItemStack st = inv.getItem(i);
				if (toTap && st.is(ModItems.HOLY_WATER)) {
					inv.setItem(i, new ItemStack(ModItems.AGUA_CANILLA, st.getCount()));
				} else if (!toTap && st.is(ModItems.AGUA_CANILLA)) {
					inv.setItem(i, new ItemStack(ModItems.HOLY_WATER, st.getCount()));
				}
			}
			if (!toTap && !inv.contains(new ItemStack(ModItems.HOLY_WATER))) {
				inv.add(new ItemStack(ModItems.HOLY_WATER, 2));
			}
			if (toTap && !inv.contains(new ItemStack(ModItems.AGUA_CANILLA))) {
				inv.add(new ItemStack(ModItems.AGUA_CANILLA, 1));  // the gag needs a bottle even if you used yours up
			}
		}
	}

	/** The flashlight dies in the great silence (battery drained) and comes back for matins. */
	static void flashlights(Run r, boolean charged) {
		for (ServerPlayer p : r.hunters()) {
			var inv = p.getInventory();
			for (int i = 0; i < inv.getContainerSize(); i++) {
				ItemStack st = inv.getItem(i);
				if (st.is(ModItems.FLASHLIGHT)) {
					st.setDamageValue(charged ? 0 : st.getMaxDamage() - 1);
					if (!charged) {
						com.deadline.item.ItemUtil.setFlags(st, false, false);
					}
				}
			}
			if (!charged) {
				r.sound(ModSounds.FLASHLIGHT_FLICKER, p.position(), 1.0F, 1.0F);
			}
		}
	}

	@Override
	public void tick(Run r) {
		// 15 reprimands and she is on you: the Silence Room instead of a hit
		if ((r.chapter() == 6 || r.chapter() == 7) && !r.has("captura") && !r.has("encerrado")
				&& r.actor(NUN) instanceof MonjaEntity nun && !nun.scripted && nun.isAlive()) {
			for (ServerPlayer p : r.hunters()) {
				if (Props.conduct(r, p) >= 15 && nun.distanceTo(p) < 2.0) {
					capture(r, p);
					break;
				}
			}
		}
		// a woken nun sits back down after a while (dormitory)
		Object until = r.vars.get("despierta_hasta");
		if (until instanceof Long t && r.now() > t && r.chapter() == 6) {
			r.vars.remove("despierta_hasta");
			r.unflag("persigue");
			if (r.actor(NUN) instanceof MonjaEntity m && !r.has("dormitorio_hecho")) {
				m.scripted = true;
				m.setNoAi(true);
				m.setTarget(null);
				m.getNavigation().stop();
				m.setDeltaMovement(Vec3.ZERO);
				m.setAction(MonjaEntity.ACT_SIT);
				Props.place(r, NUN, "dorm_silla_" + r.vars.getOrDefault("silla", 0), true);
			}
		}
	}

	// ================================================================== the corridor rule (all chapters)
	private void corridorRule(Script s) {
		s.beat("grito").from(2).repeat(20 * 20).when((r, p) -> r.event("shout:" + p.getUUID())).then(
				run(e -> {
					ServerPlayer p = e.target();
					if (p != null) {
						Props.reprimand(e.run, p, "gritar", 1);
						com.deadline.voice.NoiseMeter.heard(p);
					}
				}),
				sound(ModSounds.MONJA_SHH, null, 0.9F));
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
