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
			if (++idle == 20 * 300) {
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

	private static void frameSubject(Minecraft mc, double dist, double angle, double eye) {
		server(mc, p -> {
			if (subject != null) {
				frame(p, subject, dist, angle, eye);
			}
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
			ClientState.objCase = "rio";
			ClientState.objStage = 1;
			ClientState.callCase = "parque";
			ClientState.callCaller = 1;
			ClientState.callTicks = 20 * 20;
		});
		shot(30, "hud_call");
		step(1, mc -> {
			ClientState.vhs = true;
			ClientState.vhsStart = ClientState.ticks - 20 * 83;
		});
		shot(20, "hud_vhs");
		step(1, mc -> {
			ClientState.vhs = false;
			ClientState.callTicks = 0;
			ClientState.phone = new PhoneDataPayload(false, 1250, 3, 64F, 0b10111,
					List.of(new PhoneDataPayload.Request("parque", 1, 95), new PhoneDataPayload.Request("convento", 0, 620),
							new PhoneDataPayload.Request("rio", 3, 1800)), "", 0, 0, 0);
			mc.setScreen(PhoneScreen.at("home", 0));
		});
		shot(20, "phone_home");
		step(1, mc -> mc.setScreen(PhoneScreen.at("calls", 0)));
		shot(10, "phone_calls");
		step(1, mc -> mc.setScreen(PhoneScreen.at("call", 0)));
		shot(10, "phone_call");
		step(1, mc -> mc.setScreen(PhoneScreen.at("shop", 0)));
		shot(10, "phone_shop");
		step(1, mc -> mc.setScreen(PhoneScreen.at("bestiary", 0)));
		shot(10, "phone_bestiary");
		step(1, mc -> mc.setScreen(PhoneScreen.at("beast", 1)));
		shot(10, "phone_beast");
		step(1, mc -> {
			ClientState.phone = new PhoneDataPayload(false, 1250, 3, 18F, 0b10111, List.of(), "rio", 0, 1, 2);
			mc.setScreen(PhoneScreen.at("case", 0));
		});
		shot(10, "phone_case");
		step(1, mc -> {
			mc.setScreen(null);
			ClientState.jumpscareKey = "payaso";
			ClientState.jumpscareTicks = 16;
		});
		shot(2, "jumpscare");
		step(30, mc -> {
			ClientState.reset();
			mc.options.hideGui = true;
		});

		// --- creature studio (daylight, flat world)
		String[] keys = {"llorona", "wendigo", "poseida", "payaso", "monja", "sombra", "muneca", "anima"};
		List<EntityType<?>> types = List.of(ModEntities.LLORONA, ModEntities.WENDIGO, ModEntities.POSEIDA, ModEntities.PAYASO,
				ModEntities.MONJA, ModEntities.SOMBRA, ModEntities.MUNECA, ModEntities.ANIMA);
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
		step(5, mc -> server(mc, p -> {
			if (subject != null) {
				subject.discard();
				subject = null;
			}
			((ServerLevel) p.level()).setDayTime(18000);
		}));
		step(5, mc -> mc.options.hideGui = false);

		// --- every case site, at night, with the real lighting
		for (CaseType t : CaseType.values()) {
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
