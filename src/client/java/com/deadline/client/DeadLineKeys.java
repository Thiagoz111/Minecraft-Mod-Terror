package com.deadline.client;

import com.deadline.DeadLine;
import com.deadline.client.screen.PhoneScreen;
import com.deadline.net.PhoneActionPayload;
import com.deadline.registry.ModItems;
import com.mojang.blaze3d.platform.InputConstants;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import org.lwjgl.glfw.GLFW;

public final class DeadLineKeys {
	private DeadLineKeys() {
	}

	public static final KeyMapping.Category CATEGORY = KeyMapping.Category.register(DeadLine.id("deadline"));
	public static final KeyMapping PHONE = KeyBindingHelper.registerKeyBinding(
			new KeyMapping("key.deadline.phone", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G, CATEGORY));
	public static final KeyMapping VHS = KeyBindingHelper.registerKeyBinding(
			new KeyMapping("key.deadline.vhs", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H, CATEGORY));
	/** B2 hunt: hold to hold your breath (client/hunt/HuntClient sends the held state to the server). */
	public static final KeyMapping BREATH = KeyBindingHelper.registerKeyBinding(
			new KeyMapping("key.deadline.breath", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, CATEGORY));

	public static void init() {
	}

	public static void tick(Minecraft mc) {
		while (PHONE.consumeClick()) {
			if (mc.player != null && mc.screen == null && mc.player.getInventory().contains(s -> s.is(ModItems.PHONE))) {
				mc.setScreen(new PhoneScreen());
				if (ClientPlayNetworking.canSend(PhoneActionPayload.TYPE)) {
					ClientPlayNetworking.send(new PhoneActionPayload(PhoneActionPayload.REFRESH, 0));
				}
			}
		}
		while (VHS.consumeClick()) {
			ClientState.vhs = !ClientState.vhs;
			ClientState.vhsStart = ClientState.ticks;
		}
	}
}
