package com.deadline.client.phone;

import com.deadline.client.ClientFx;
import com.deadline.client.screen.PhoneScreen;
import com.deadline.phone.PhoneMessageActionPayload;
import com.deadline.phone.PhoneMessagesPayload;
import com.deadline.phone.PhoneMsg;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;

/**
 * Client copy of the phone's text threads (com.deadline.phone.PhoneMessages): what the "Mensajes" app draws, the
 * "escribiendo..." countdowns, and the incoming-message toast (vibration + short tone + banner top right).
 */
public final class ClientMessages {
	/** Threads, most recent first (as the server sends them). */
	public static final List<PhoneMessagesPayload.View> THREADS = new ArrayList<>();
	private static final Map<String, Integer> TYPING = new HashMap<>();

	public static final int TOAST_LEN = 110;
	public static String toastThread = "";
	public static PhoneMsg toastMsg;
	public static int toastTicks;
	private static int toneIn;

	private ClientMessages() {
	}

	public static void onPayload(PhoneMessagesPayload p) {
		THREADS.clear();
		THREADS.addAll(p.threads());
		TYPING.clear();
		for (PhoneMessagesPayload.View v : p.threads()) {
			if (v.typing() > 0) {
				TYPING.put(v.id(), v.typing());
			}
		}
		if (p.notify().isEmpty()) {
			return;
		}
		PhoneMessagesPayload.View t = find(p.notify());
		if (t == null || t.messages().isEmpty()) {
			return;
		}
		Minecraft mc = Minecraft.getInstance();
		if (mc.screen instanceof PhoneScreen ps && ps.viewing(t.id())) {
			markRead(t.id());  // it lands in the open conversation
		} else {
			toastThread = t.id();
			toastMsg = t.messages().get(t.messages().size() - 1);
			toastTicks = TOAST_LEN;
		}
		// the buzz in your pocket, then the short tone
		mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.PHONE_VIBRATE, 1.0F, 0.9F));
		toneIn = 7;
		ClientFx.shake(0.18F, 8);
	}

	/** Every client tick: typing countdowns, the toast, the delayed tone. */
	public static void tick(Minecraft mc) {
		if (!TYPING.isEmpty()) {
			TYPING.replaceAll((k, v) -> v - 1);
			TYPING.values().removeIf(v -> v <= 0);
		}
		if (toastTicks > 0) {
			toastTicks--;
		}
		if (toneIn > 0 && --toneIn == 0) {
			mc.getSoundManager().play(SimpleSoundInstance.forUI(ModSounds.PHONE_NOTIFY, 1.0F, 0.8F));
		}
	}

	public static void reset() {
		THREADS.clear();
		TYPING.clear();
		toastThread = "";
		toastMsg = null;
		toastTicks = 0;
		toneIn = 0;
	}

	public static PhoneMessagesPayload.View find(String id) {
		for (PhoneMessagesPayload.View v : THREADS) {
			if (v.id().equals(id)) {
				return v;
			}
		}
		return null;
	}

	public static PhoneMessagesPayload.View at(int index) {
		return index >= 0 && index < THREADS.size() ? THREADS.get(index) : null;
	}

	/** Ticks of "escribiendo..." left in a thread (0 = not typing). */
	public static int typing(String id) {
		return TYPING.getOrDefault(id, 0);
	}

	public static int unreadTotal() {
		int n = 0;
		for (PhoneMessagesPayload.View v : THREADS) {
			n += v.unread();
		}
		return n;
	}

	/** The thread was opened: unread to 0 here and on the server. */
	public static void markRead(String id) {
		for (int i = 0; i < THREADS.size(); i++) {
			PhoneMessagesPayload.View v = THREADS.get(i);
			if (v.id().equals(id) && v.unread() != 0) {
				THREADS.set(i, new PhoneMessagesPayload.View(v.id(), 0, v.typing(), v.messages()));
				send(PhoneMessageActionPayload.READ, id, 0);
			}
		}
		if (id.equals(toastThread)) {
			toastTicks = 0;
		}
	}

	/** "Aceptar caso" on bubble `index` of a thread. */
	public static void accept(String id, int index) {
		send(PhoneMessageActionPayload.ACCEPT, id, index);
	}

	private static void send(int action, String thread, int index) {
		if (ClientPlayNetworking.canSend(PhoneMessageActionPayload.TYPE)) {
			ClientPlayNetworking.send(new PhoneMessageActionPayload(action, thread, index));
		}
	}

	// ------------------------------------------------------------------ text helpers
	/** Contact name (lang key deadline.thread.&lt;id&gt;). */
	public static Component name(String id) {
		return Component.translatable("deadline.thread." + id);
	}

	/** One-line preview of a bubble (list rows, toast). */
	public static Component preview(PhoneMsg m) {
		return switch (m.kind()) {
			case PhoneMsg.PHOTO -> Component.translatable("deadline.phone.photo");
			case PhoneMsg.CASE -> Component.translatable("deadline.phone.location");
			default -> Component.translatable(m.value());
		};
	}

	/** "hh:mm" of a phone timestamp (overworld day time). */
	public static String clock(long dayTime) {
		long tod = Math.floorMod(dayTime + 6000L, 24000L);
		return String.format(Locale.ROOT, "%02d:%02d", tod / 1000, (tod % 1000) * 60 / 1000);
	}

	/** Day number (1-based) of a phone timestamp. */
	public static long day(long dayTime) {
		return Math.floorDiv(dayTime, 24000L) + 1;
	}

	/** Sample threads for the CI screenshots (ClientSmoke): Marta's act 0 with the photo and the location. */
	public static void demo() {
		reset();
		long t = 13000L;
		List<PhoneMsg> marta = List.of(
				new PhoneMsg(PhoneMsg.TEXT, "deadline.sms.marta.numero", t, 0),
				new PhoneMsg(PhoneMsg.TEXT, "deadline.sms.marta.suegra", t + 80, 0),
				new PhoneMsg(PhoneMsg.TEXT, "deadline.sms.marta.no_llame", t + 160, 0),
				new PhoneMsg(PhoneMsg.PHOTO, "pasillo_nona", t + 240, 0),
				new PhoneMsg(PhoneMsg.TEXT, "deadline.sms.marta.ubicacion", t + 320, 0),
				new PhoneMsg(PhoneMsg.CASE, "casa", t + 330, 0));
		List<PhoneMsg> clara = List.of(
				new PhoneMsg(PhoneMsg.TEXT, "deadline.sms.clara.hora", t - 30000, 0),
				new PhoneMsg(PhoneMsg.CASE, "colegio", t - 29900, PhoneMsg.ACCEPTED));
		THREADS.add(new PhoneMessagesPayload.View("marta", 6, 0, marta));
		THREADS.add(new PhoneMessagesPayload.View("desconocido", 0, 0, List.of()));
		THREADS.add(new PhoneMessagesPayload.View("clara", 0, 0, clara));
		TYPING.put("desconocido", 20 * 60);
		toastThread = "marta";
		toastMsg = marta.get(2);
		toastTicks = TOAST_LEN;
	}
}
