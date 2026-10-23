package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.caseload.CaseType;
import com.deadline.client.screen.PhoneScreen;
import com.deadline.entity.AnimaEntity;
import com.deadline.entity.HauntEntity;
import com.deadline.net.PhoneDataPayload;
import com.deadline.registry.ModEntities;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Dev-only scripted client run (-Ddeadline.clientsmoke=true): visits every case, photographs the creatures,
 * HUD and phone, then quits. Used by CI to produce real in-game screenshots.
 */
public final class ClientSmoke {
	private ClientSmoke() {
	}

	private record Step(int delay, Consumer<Minecraft> action) {
	}

	private static final List<Step> STEPS = new ArrayList<>();
	private static int index;
	private static int timer;
	private static int failures;
	private static Entity subject;
	private static int idle;

	public static void register() {
		if (!Boolean.getBoolean("deadline.clientsmoke")) {
			return;
		}
		HauntEntity.SHOWCASE = true;
		build();
		ClientTickEvents.END_CLIENT_TICK.register(ClientSmoke::tick);
	}

	private static void tick(Minecraft mc) {
		if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null) {
			++idle;
			if (idle % 200 == 0) {
				DeadLine.LOGGER.info("DEADLINE-CLIENT waiting, screen={}", mc.screen == null ? "none" : mc.screen.getClass().getName());
			}
			if (idle % 20 == 0 && mc.screen != null && pressConfirm(mc)) {
				return;
			}
			if (idle == 600 && mc.level == null && mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen) {
				// quick-play did not start: open the world the way the world list does (dev-only, via reflection)
				try {
					Object flows = mc.createWorldOpenFlows();
					java.lang.reflect.Method m = flows.getClass().getMethod("openWorld", String.class, Runnable.class);
					m.invoke(flows, "smoke", (Runnable) () -> DeadLine.LOGGER.error("DEADLINE-CLIENT openWorld cancelled"));
					DeadLine.LOGGER.info("DEADLINE-CLIENT opening world via WorldOpenFlows");
				} catch (Throwable t) {
					DeadLine.LOGGER.error("DEADLINE-CLIENT openWorld failed", t);
				}
			}
			if (idle == 20 * 300) {
				DeadLine.LOGGER.error("DEADLINE-CLIENT FAIL never joined a world");
				mc.stop();
			}
			return;
		}
		if (subject != null) {
			IntegratedServer server = mc.getSingleplayerServer();
			Entity e = subject;
			server.execute(() -> {
				e.setInvisible(false);
				if (e instanceof AnimaEntity a) {
					a.reveal(40);
				}
			});
		}
		if (index >= STEPS.size()) {
			if (index++ == STEPS.size() + 40) {
				DeadLine.LOGGER.info("DEADLINE-CLIENT DONE failures={}", failures);
				mc.stop();
			}
			return;
		}
		Step s = STEPS.get(index);
		if (++timer >= s.delay) {
			timer = 0;
			index++;
			try {
				s.action.accept(mc);
			} catch (Throwable t) {
				failures++;
				DeadLine.LOGGER.error("DEADLINE-CLIENT FAIL step {}", index, t);
			}
		}
	}

	private static final java.util.Set<String> CONFIRM_KEYS = java.util.Set.of("selectWorld.backupJoinSkipButton", "gui.proceed",
			"gui.continue", "gui.yes", "selectWorld.edit.backupCreated");

	/** Clicks through "backup first?" / experimental-settings style prompts that block quick play. */
	private static boolean pressConfirm(Minecraft mc) {
		String cls = mc.screen.getClass().getSimpleName();
		if (!(cls.contains("Confirm") || cls.contains("Backup") || cls.contains("Warning") || cls.contains("Experimental"))) {
			return false;
		}
		for (var child : mc.screen.children()) {
			if (child instanceof net.minecraft.client.gui.components.AbstractWidget w
					&& w.getMessage().getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents tc
					&& CONFIRM_KEYS.contains(tc.getKey())) {
				double x = w.getX() + w.getWidth() / 2.0;
				double y = w.getY() + w.getHeight() / 2.0;
				var ev = new net.minecraft.client.input.MouseButtonEvent(x, y, new net.minecraft.client.input.MouseButtonInfo(0, 0));
				mc.screen.mouseClicked(ev, false);
				if (mc.screen != null) {
					mc.screen.mouseReleased(ev);
				}
				DeadLine.LOGGER.info("DEADLINE-CLIENT pressed {} on {}", tc.getKey(), cls);
				return true;
			}
		}
		return false;
	}

	private static void step(int wait, Consumer<Minecraft> a) {
		STEPS.add(new Step(wait, a));
	}

	private static void shot(int wait, String name) {
		step(wait, mc -> Screenshot.grab(mc.gameDirectory, name + ".png", mc.getMainRenderTarget(), 1,
				msg -> DeadLine.LOGGER.info("DEADLINE-CLIENT SHOT {} {}", name, msg.getString())));
	}

	private static void server(Minecraft mc, Consumer<ServerPlayer> a) {
		IntegratedServer server = mc.getSingleplayerServer();
		server.execute(() -> {
			ServerPlayer p = server.getPlayerList().getPlayers().get(0);
			a.accept(p);
		});
	}

	private static void cmd(Minecraft mc, String command) {
		IntegratedServer server = mc.getSingleplayerServer();
		server.execute(() -> server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), command));
	}

	/** Puts the player at dist blocks in front of the entity (along its facing + angle offset), looking at its face. */
	private static void frame(ServerPlayer p, Entity e, double dist, double angleDeg, double eyeFrac) {
		ServerLevel level = (ServerLevel) e.level();
		float yaw = e.getYRot() + (float) angleDeg;
		double rad = Math.toRadians(yaw);
		double x = e.getX() - Math.sin(rad) * dist;
		double z = e.getZ() + Math.cos(rad) * dist;
		double y = e.getY();
		Vec3 target = new Vec3(e.getX(), e.getY() + e.getBbHeight() * eyeFrac, e.getZ());
		double dx = target.x - x;
		double dz = target.z - z;
		double dy = target.y - (y + p.getEyeHeight());
		float pyaw = (float) (Math.toDegrees(Math.atan2(-dx, dz)));
		float ppitch = (float) (-Math.toDegrees(Math.atan2(dy, Math.sqrt(dx * dx + dz * dz))));
		p.teleportTo(level, x, y, z, Set.of(), pyaw, Mth.clamp(ppitch, -60F, 60F), false);
	}

	private static void spawnSubject(Minecraft mc, EntityType<?> type) {
		server(mc, p -> {
			ServerLevel level = (ServerLevel) p.level();
			if (subject != null) {
				subject.discard();
				subject = null;
			}
			Entity e = type.create(level, EntitySpawnReason.COMMAND);
			if (e == null) {
				return;
			}
			double x = p.getX() + 0.5;
			double z = p.getZ() - 6.5;
			int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (int) Math.floor(x), (int) Math.floor(z));
			e.snapTo(x, y, z, 0F, 0F);
			if (e instanceof HauntEntity h) {
				h.setNoAi(true);
				h.setYHeadRot(0F);
				h.setYBodyRot(0F);
			}
			e.setNoGravity(true);
			level.addFreshEntity(e);
			subject = e;
			frame(p, e, 4.2 + e.getBbHeight() * 0.6, 0, 0.62);
		});
	}

	/** The car (com.deadline.car): outside in daylight, then the view from the driver's seat by day and at night with the lights. */
	private static void carStudio() {
		step(10, mc -> spawnSubject(mc, com.deadline.car.Cars.CAR));
		step(1, mc -> frameSubject(mc, 9.0, 35, 0.45));
		shot(25, "car_34");
		step(1, mc -> frameSubject(mc, 9.5, 150, 0.45));
		shot(15, "car_back34");
		step(1, mc -> server(mc, p -> {
			if (subject instanceof com.deadline.car.CarEntity car) {
				car.setNoGravity(false);
				// face where the car faces first (a teleport carries the view to the client), then take the wheel
				p.teleportTo((ServerLevel) p.level(), car.getX(), car.getY(), car.getZ(), Set.of(), car.getYRot(), 8F, false);
				car.seat(p, com.deadline.car.CarEntity.DRIVER);
			}
		}));
		shot(30, "car_driver");
		step(1, mc -> server(mc, p -> {
			((ServerLevel) p.level()).setDayTime(18000);
			if (subject instanceof com.deadline.car.CarEntity car) {
				car.setLights(true);
			}
		}));
		shot(40, "car_driver_night");
		step(1, mc -> server(mc, p -> {
			p.stopRiding();
			((ServerLevel) p.level()).setDayTime(6000);
		}));
	}

	private static void frameSubject(Minecraft mc, double dist, double angle, double eye) {
		server(mc, p -> {
			if (subject != null) {
				frame(p, subject, dist, angle, eye);
			}
		});
	}

	/** Places the hunter at a site marker of the running scripted case, looking at yaw/pitch. */
	private static void at(Minecraft mc, String point, float yaw, float pitch) {
		server(mc, p -> {
			com.deadline.director.Run r = com.deadline.director.Director.of(p);
			if (r == null) {
				DeadLine.LOGGER.warn("DEADLINE-CLIENT no director run for {}", point);
				return;
			}
			net.minecraft.world.phys.Vec3 v = r.at(point);
			p.teleportTo((ServerLevel) p.level(), v.x, v.y, v.z, Set.of(), yaw, pitch, false);
		});
	}

	private static void director(Minecraft mc, java.util.function.Consumer<com.deadline.director.Run> code) {
		server(mc, p -> {
			com.deadline.director.Run r = com.deadline.director.Director.of(p);
			if (r != null) {
				code.accept(r);
			} else {
				DeadLine.LOGGER.warn("DEADLINE-CLIENT no director run");
			}
		});
	}

	/** Teleports to a position relative to the case site's origin. */
	private static void atSite(Minecraft mc, double x, double y, double z, float yaw, float pitch) {
		server(mc, p -> {
			com.deadline.director.Run r = com.deadline.director.Director.of(p);
			if (r != null) {
				p.teleportTo((ServerLevel) p.level(), r.origin.getX() + x, r.origin.getY() + y, r.origin.getZ() + z, Set.of(), yaw, pitch, false);
			}
		});
	}

	/** Architecture pass: every room of the Colegio with night vision and no HUD (to check the building kit in game). */
	private static void colegioRooms() {
		step(1, mc -> {
			mc.options.hideGui = true;
			server(mc, p -> p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 20 * 60, 0, false, false)));
		});
		Object[][] views = {
				{"colegio_room_portico", 0.5, 0.0, -17.5, 0F, -14F},
				{"colegio_room_hall", -4.5, 0.0, 1.5, -55F, -18F},
				{"colegio_room_aula", -7.5, 0.0, 6.5, 115F, 6F},
				{"colegio_room_direccion", 11.5, 0.0, 7.3, 180F, 8F},
				{"colegio_room_pasillo", 18.5, 0.0, 10.5, 90F, 0F},
				{"colegio_room_refectorio", -12.0, 0.0, 13.6, 0F, 14F},
				{"colegio_room_cocina", -19.6, 0.0, 19.4, 125F, 12F},
				{"colegio_room_capilla", 10.5, 0.0, 19.5, 0F, -4F},
				{"colegio_room_coro", 10.5, 0.0, 26.5, 180F, -26F},
				{"colegio_room_dormitorio", -11.5, 6.0, 13.5, 0F, 6F},
				{"colegio_room_banos", -11.5, 6.0, 37.5, 0F, 0F},
				{"colegio_room_cripta", 10.5, -6.0, 21.5, 0F, 2F},
		};
		for (Object[] v : views) {
			step(1, mc -> atSite(mc, (double) v[1], (double) v[2], (double) v[3], (float) v[4], (float) v[5]));
			shot(25, (String) v[0]);
		}
		step(1, mc -> {
			mc.options.hideGui = false;
			server(mc, p -> p.removeEffect(MobEffects.NIGHT_VISION));
		});
	}

	/** Walks the scripted Colegio case through its first set pieces and screenshots each one. */
	private static void colegioTour() {
		step(10, mc -> cmd(mc, "deadline start colegio " + mc.player.getName().getString()));
		shot(80, "colegio_1_arrive");
		step(1, mc -> at(mc, "spawn", 0F, -8F));
		shot(30, "colegio_1_facade");
		// crossing the threshold: door slam, bell, then the chapter card of chapter 2
		step(1, mc -> at(mc, "hall_centro", 180F, 0F));
		shot(25, "colegio_2_hall");
		shot(65, "colegio_2_card");
		// the blackboard (roll call skipped): NO MIRES ATRÁS
		step(1, mc -> {
			cmd(mc, "deadline flag lista_done");
			at(mc, "aula_centro", 90F, 2F);
		});
		shot(60, "colegio_3_board");
		step(1, mc -> at(mc, "aula_centro", -90F, 2F));
		step(15, mc -> at(mc, "aula_centro", 90F, 2F));
		shot(20, "colegio_3_te_dije");
		step(1, mc -> {
			at(mc, "aula_centro", -90F, 4F);
			server(mc, p -> p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 100, 0, false, false)));
		});
		shot(10, "colegio_3_nun_behind");
		step(1, mc -> server(mc, p -> p.removeEffect(MobEffects.NIGHT_VISION)));
		// dinner: the dining hall and the hatch
		step(1, mc -> cmd(mc, "deadline chapter 3"));
		shot(40, "colegio_4_dinner_card");
		step(1, mc -> at(mc, "refectorio", 90F, 6F));
		shot(30, "colegio_4_refectorio");
		// office
		step(1, mc -> cmd(mc, "deadline chapter 4"));
		step(5, mc -> at(mc, "hall", 0F, 0F));
		shot(60, "colegio_5_office_card");
		// chapel and the upper choir
		step(1, mc -> cmd(mc, "deadline chapter 5"));
		step(5, mc -> at(mc, "capilla_puerta", 0F, -10F));
		shot(30, "colegio_6_chapel");
		step(1, mc -> director(mc, r -> {
			net.minecraft.world.phys.Vec3 v = r.at("coro_alto");
			ServerPlayer p = r.star();
			if (p != null) {
				p.teleportTo(r.level, v.x, v.y - 6, v.z + 10, Set.of(), 180F, -28F, false);
			}
		}));
		shot(30, "colegio_6_choir_loft");
		colegioRooms();
		step(1, mc -> cmd(mc, "deadline home " + mc.player.getName().getString()));
		step(40, mc -> {
		});
	}

	private static void build() {
		// --- setup: creative, clear day, then night look
		step(80, mc -> server(mc, p -> {
			p.setGameMode(GameType.CREATIVE);
			((ServerLevel) p.level()).setDayTime(6000);
			((ServerLevel) p.level()).setWeatherParameters(6000, 0, false, false);
			p.teleportTo((ServerLevel) p.level(), 0.5, p.level().getHeight(Heightmap.Types.MOTION_BLOCKING, 0, 0), 0.5, Set.of(), 180F, 0F, false);
		}));

		// --- HUD + phone
		step(40, mc -> {
			ClientState.sanity = ClientState.sanityShown = 24F;
			ClientState.objCase = "colegio";
			ClientState.objStage = 1;
			com.deadline.client.phone.ClientMessages.demo();
		});
		shot(30, "hud_message");
		step(1, mc -> {
			ClientState.vhs = true;
			ClientState.vhsStart = ClientState.ticks - 20 * 83;
		});
		shot(20, "hud_vhs");
		step(1, mc -> {
			ClientState.vhs = false;
			com.deadline.client.phone.ClientMessages.toastTicks = 0;
			ClientState.phone = new PhoneDataPayload(false, 1250, 3, 64F, 0b10111, "", 0, 0);
			mc.setScreen(PhoneScreen.at("home", 0));
		});
		shot(20, "phone_home");
		step(1, mc -> mc.setScreen(PhoneScreen.at("messages", 0)));
		shot(10, "phone_messages");
		step(1, mc -> mc.setScreen(PhoneScreen.at("thread", 0)));
		shot(10, "phone_thread");
		step(1, mc -> mc.setScreen(PhoneScreen.at("shop", 0)));
		shot(10, "phone_shop");
		step(1, mc -> mc.setScreen(PhoneScreen.at("bestiary", 0)));
		shot(10, "phone_bestiary");
		step(1, mc -> mc.setScreen(PhoneScreen.at("beast", 1)));
		shot(10, "phone_beast");
		step(1, mc -> {
			ClientState.phone = new PhoneDataPayload(false, 1250, 3, 18F, 0b10111, "colegio", 1, 2);
			mc.setScreen(PhoneScreen.at("case", 0));
		});
		shot(10, "phone_case");
		step(1, mc -> {
			mc.setScreen(null);
			ClientState.jumpscareKey = "monja";
			ClientState.jumpscareTicks = 16;
		});
		shot(2, "jumpscare");
		step(30, mc -> {
			ClientState.reset();
			mc.options.hideGui = true;
		});

		// --- exorcist suit: third person front/back and the sleeve in first person
		step(5, mc -> server(mc, p -> {
			com.deadline.caseload.CaseManager.suitUp(p);
			p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, net.minecraft.world.item.ItemStack.EMPTY);
			p.setYRot(180F);
			p.setXRot(10F);
		}));
		step(10, mc -> mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_FRONT));
		shot(20, "suit_front");
		step(1, mc -> mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_BACK));
		shot(15, "suit_back");
		step(1, mc -> {
			mc.options.setCameraType(net.minecraft.client.CameraType.FIRST_PERSON);
			mc.options.hideGui = false;
		});
		shot(15, "suit_first_person");
		step(1, mc -> mc.options.hideGui = true);

		// --- creature studio (daylight, flat world)
		String[] keys = {"monja", "poseida", "sombra", "muneca", "anima", "alumna", "madre", "clara", "marta", "jorge", "nona", "toti"};
		List<EntityType<?>> types = List.of(ModEntities.MONJA, ModEntities.POSEIDA, ModEntities.SOMBRA, ModEntities.MUNECA, ModEntities.ANIMA,
				ModEntities.ALUMNA, ModEntities.MADRE, ModEntities.CLARA, com.deadline.casa.FamilyEntities.MARTA, com.deadline.casa.FamilyEntities.JORGE,
				com.deadline.casa.FamilyEntities.NONA, com.deadline.casa.FamilyEntities.TOTI);
		for (int i = 0; i < keys.length; i++) {
			EntityType<?> type = types.get(i);
			String key = keys[i];
			step(10, mc -> spawnSubject(mc, type));
			shot(30, "mob_" + key);
			step(1, mc -> frameSubject(mc, 4.0, 40, 0.6));
			shot(15, "mob_" + key + "_34");
			step(1, mc -> frameSubject(mc, 1.6, 0, 0.86));
			shot(15, "mob_" + key + "_face");
		}
		carStudio();
		step(5, mc -> server(mc, p -> {
			if (subject != null) {
				subject.discard();
				subject = null;
			}
			((ServerLevel) p.level()).setDayTime(18000);
		}));
		step(5, mc -> mc.options.hideGui = false);

		// --- every case site, at night, with the real lighting
		colegioTour();
		for (CaseType t : CaseType.values()) {
			if (t.scripted()) {
				continue;
			}
			step(10, mc -> cmd(mc, "deadline start " + t.key() + " " + mc.player.getName().getString()));
			shot(70, "case_" + t.key() + "_arrive");
			shot(90, "case_" + t.key());
			step(1, mc -> server(mc, p -> {
				ServerLevel level = (ServerLevel) p.level();
				HauntEntity boss = null;
				for (Entity e : level.getAllEntities()) {
					if (e.getType() == t.boss() && e instanceof HauntEntity h) {
						boss = h;
						break;
					}
				}
				if (boss != null) {
					boss.setNoAi(true);
					boss.setInvisible(false);
					subject = boss;
					frame(p, boss, 3.6 + boss.getBbHeight() * 0.5, 0, 0.62);
				} else {
					DeadLine.LOGGER.warn("DEADLINE-CLIENT no boss found in {}", t.key());
				}
			}));
			step(1, mc -> mc.options.hideGui = true);
			shot(30, "case_" + t.key() + "_boss");
			step(1, mc -> server(mc, p -> p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 200, 0, false, false))));
			shot(10, "case_" + t.key() + "_boss_nv");
			step(1, mc -> {
				mc.options.hideGui = false;
				subject = null;
				server(mc, p -> p.removeEffect(MobEffects.NIGHT_VISION));
			});
			step(1, mc -> cmd(mc, "deadline home " + mc.player.getName().getString()));
			step(40, mc -> {
			});
		}
	}
}
