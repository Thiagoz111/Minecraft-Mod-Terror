package com.deadline.client.lore;

import com.deadline.horror.casa.lore.LoreBook;
import com.deadline.horror.casa.lore.LorePayload;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;

/**
 * Client side of the lore documents (B1b): the server says "read this" ({@link LorePayload}) and the page opens full
 * screen ({@link LoreScreen}). Wired from DeadLineClient with {@link #init()}.
 */
public final class LoreClient {
	private static boolean done;

	private LoreClient() {
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		ClientPlayNetworking.registerGlobalReceiver(LorePayload.TYPE, (payload, ctx) -> open(payload));
	}

	static void open(LorePayload p) {
		Minecraft mc = Minecraft.getInstance();
		LoreBook.Doc doc = LoreBook.get(p.doc());
		if (mc.player == null || doc == null || doc.pages(p.late()).isEmpty()) {
			return;
		}
		mc.setScreen(new LoreScreen(doc, p.late()));
	}
}
