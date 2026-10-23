package com.deadline.client.car;

import com.deadline.DeadLine;
import com.deadline.car.CarEntity;
import com.deadline.car.CarInputPayload;
import com.deadline.car.Cars;
import com.deadline.car.GpsPayload;
import com.deadline.client.DeadLineKeys;
import com.deadline.client.model.gen.AutoModelBase;
import com.mojang.blaze3d.platform.InputConstants;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelLayerLocation;
import org.lwjgl.glfw.GLFW;

/**
 * Client side of the car and the GPS: renderer + model layer, the controls that are not movement (headlights J,
 * radio R, horn = middle click while driving: pick-block is useless at the wheel), the steering angle for other
 * players, the engine/tyre/radio loops and the GPS payload. Default keys avoid DEAD LINE's G (phone) and H (VHS).
 */
public final class CarClient {
	public static final ModelLayerLocation LAYER = new ModelLayerLocation(DeadLine.id("auto"), "main");
	public static final KeyMapping LIGHTS = KeyBindingHelper.registerKeyBinding(
			new KeyMapping("key.deadline.car_lights", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_J, DeadLineKeys.CATEGORY));
	public static final KeyMapping RADIO = KeyBindingHelper.registerKeyBinding(
			new KeyMapping("key.deadline.car_radio", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, DeadLineKeys.CATEGORY));
	private static float sentSteer;

	private CarClient() {
	}

	public static void init() {
		EntityModelLayerRegistry.registerModelLayer(LAYER, AutoModelBase::createBodyLayer);
		EntityRendererRegistry.register(Cars.CAR, CarRenderer::new);
		ClientPlayNetworking.registerGlobalReceiver(GpsPayload.TYPE, (payload, ctx) -> GpsHud.onPayload(payload));
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> {
			GpsHud.reset();
			CarSounds.clear();
		});
		// the horn steals the middle click before vanilla handles it as pick-block (only while driving)
		ClientTickEvents.START_CLIENT_TICK.register(mc -> {
			if (driving(mc) != null) {
				boolean honk = false;
				while (mc.options.keyPickItem.consumeClick()) {
					honk = true;
				}
				if (honk) {
					send(CarInputPayload.HORN, 0F);
				}
			}
		});
		ClientTickEvents.END_CLIENT_TICK.register(CarClient::tick);
	}

	/** The car the local player drives (driver seat), or null. */
	public static CarEntity driving(Minecraft mc) {
		return mc.player != null && mc.player.getVehicle() instanceof CarEntity car && car.getControllingPassenger() == mc.player ? car : null;
	}

	private static void tick(Minecraft mc) {
		CarEntity car = driving(mc);
		while (LIGHTS.consumeClick()) {
			if (car != null) {
				send(CarInputPayload.LIGHTS, 0F);
			}
		}
		while (RADIO.consumeClick()) {
			if (mc.player != null && mc.player.getVehicle() instanceof CarEntity) {
				send(CarInputPayload.RADIO, 0F);
			}
		}
		if (car != null) {
			float s = car.steerAngle();
			if (Math.abs(s - sentSteer) > 0.08F || s == 0F && sentSteer != 0F) {
				sentSteer = s;
				send(CarInputPayload.STEER, s);
			}
		} else {
			sentSteer = 0F;
		}
		CarSounds.tick(mc);
	}

	private static void send(int action, float value) {
		if (ClientPlayNetworking.canSend(CarInputPayload.TYPE)) {
			ClientPlayNetworking.send(new CarInputPayload(action, value));
		}
	}
}
