package com.deadline;

import com.deadline.caseload.CaseManager;
import com.deadline.command.DeadLineCommands;
import com.deadline.item.FlashlightLights;
import com.deadline.net.ModNetworking;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModBlocks;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DeadLine implements ModInitializer {
	public static final String MOD_ID = "deadline";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}

	@Override
	public void onInitialize() {
		ModSounds.init();
		ModParticles.init();
		ModBlocks.init();
		com.deadline.registry.gen.ModBlocksGen.init();
		ModItems.init();
		ModEntities.init();
		ModAttachments.init();
		ModNetworking.init();
		// the phone's text threads (WhatsApp-like): how every case reaches the hunter
		com.deadline.phone.PhoneMessages.init();
		// case 2: the Morales house
		com.deadline.casa.CasaSetEntities.init();
		com.deadline.casa.FamilyEntities.init();
		// B3: Choripán (the dog, the long dog) and the apparitions of the catalogue (events 33-45 + their small entities)
		com.deadline.horror.casa.dog.DogEntities.init();
		com.deadline.horror.casa.ApparitionEvents.register();
		// B2: the hunt of Act 5 (the broken Nona, hiding places, holding the breath); before Director.register()
		com.deadline.horror.casa.hunt.HuntEntities.init();
		// the car, its keys and the GPS; overworld cases (the house in the real world, the frozen night)
		com.deadline.car.Cars.init();
		com.deadline.caseload.OverworldCase.register();

		CommandRegistrationCallback.EVENT.register(DeadLineCommands::register);
		// /deadline horror status|event|act|tension|pause (the horror director's debug tools)
		CommandRegistrationCallback.EVENT.register((dispatcher, ctx, env) -> com.deadline.horror.HorrorCommands.register(dispatcher));
		SmokeTest.register();
		com.deadline.director.Director.register();
		// scripted actors (the nun, chalk text...) go away before the final save, so they are never saved as orphans
		net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.SERVER_STOPPING.register(server -> com.deadline.director.Director.clear());
		net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
			com.deadline.director.Director.clear();
			com.deadline.site.SiteDef.clearCache();
		});

		ServerTickEvents.END_SERVER_TICK.register(server -> {
			CaseManager.tick(server);
			SanityManager.tick(server);
			FlashlightLights.tick(server);
			com.deadline.site.SitePlacer.tick(server);
			com.deadline.voice.Voice.tick(server);
			com.deadline.voice.NoiseMeter.tick(server);
			com.deadline.director.Director.tick(server);
		});
		ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> CaseManager.onJoin(handler.getPlayer()));
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> FlashlightLights.clear(handler.getPlayer()));
		ServerPlayerEvents.AFTER_RESPAWN.register((oldPlayer, newPlayer, alive) -> CaseManager.onRespawn(newPlayer, alive));
		net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents.ALLOW_DEATH.register((entity, source, amount) ->
				!(entity instanceof net.minecraft.server.level.ServerPlayer p) || !CaseManager.failForward(p));

		LOGGER.info("DEAD LINE: la línea está abierta...");
	}
}
