package com.deadline.phone;

import com.deadline.caseload.CaseManager;
import com.deadline.caseload.CaseRequest;
import com.deadline.caseload.CaseType;
import com.deadline.caseload.HunterData;
import com.deadline.registry.ModAttachments;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * The hunter's phone gets TEXT MESSAGES (WhatsApp-like threads), never calls: nobody speaks in DEAD LINE
 * ("ella escucha todo", docs/design/casa_terror.md 0, 1, 8). Server side API:
 * <ul>
 *   <li>{@link #text}: a text bubble (lang key) in a thread; the client vibrates, plays a short tone and shows a toast
 *   (contact name + first line) even with the phone closed.</li>
 *   <li>{@link #photo}: a photo bubble (textures/gui/photo/&lt;id&gt;.png, 128x96).</li>
 *   <li>{@link #typing}: "escribiendo..." for a while, and then nothing (unless a message arrives).</li>
 *   <li>{@link #offerCase}: a location bubble with "Aceptar caso" (CaseManager.startCase on press).</li>
 *   <li>{@link #clear}: deletes a thread.</li>
 *   <li>{@link #textLater} (and {@link #photoLater}, {@link #offerCaseLater}): the same, after a delay; queued per player,
 *   saved with the player, and announced by a few seconds of "escribiendo..." before they land.</li>
 * </ul>
 * Thread ids are free strings; the contact name is the lang key deadline.thread.&lt;id&gt; (marta, desconocido,
 * ignacio, clara). Threads are kept in {@link HunterData#threads} (survive relog) and synced with
 * {@link PhoneMessagesPayload}.
 */
public final class PhoneMessages {
	public static final String MARTA = "marta", DESCONOCIDO = "desconocido", IGNACIO = "ignacio", CLARA = "clara";
	/** Ticks of "escribiendo..." before a scheduled message lands. */
	private static final int TYPING_LEAD = 50;
	/** Oldest bubbles are dropped past this many per thread. */
	private static final int MAX_MESSAGES = 60;

	private PhoneMessages() {
	}

	/** Payloads, the action receiver, the delivery tick and the sync on join (one call from DeadLine.onInitialize). */
	public static void init() {
		PayloadTypeRegistry.playS2C().register(PhoneMessagesPayload.TYPE, PhoneMessagesPayload.CODEC);
		PayloadTypeRegistry.playC2S().register(PhoneMessageActionPayload.TYPE, PhoneMessageActionPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(PhoneMessageActionPayload.TYPE, (payload, ctx) -> onAction(ctx.player(), payload));
		ServerTickEvents.END_SERVER_TICK.register(PhoneMessages::tick);
		ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> sync(handler.getPlayer(), ""));
	}

	// ------------------------------------------------------------------ API
	/** A text bubble (translatable key) in a thread, now. */
	public static void text(ServerPlayer p, String thread, String langKey) {
		add(p, thread, new PhoneMsg(PhoneMsg.TEXT, langKey, clock(p), 0));
	}

	/** A photo bubble: texture deadline:textures/gui/photo/&lt;photoId&gt;.png (128x96). */
	public static void photo(ServerPlayer p, String thread, String photoId) {
		add(p, thread, new PhoneMsg(PhoneMsg.PHOTO, photoId, clock(p), 0));
	}

	/** "escribiendo..." in a thread for `ticks`; nothing is sent (a message arriving cuts it short). */
	public static void typing(ServerPlayer p, String thread, int ticks) {
		HunterData d = ModAttachments.get(p);
		PhoneThread t = thread(d, thread, true);
		t.typingUntil = now(p) + Math.max(0, ticks);
		sync(p, "");
	}

	/** A location bubble with the "Aceptar caso" button: pressing it starts the case (CaseManager.startCase). */
	public static void offerCase(ServerPlayer p, String thread, CaseType type) {
		add(p, thread, new PhoneMsg(PhoneMsg.CASE, type.key(), clock(p), 0));
	}

	/** Deletes a thread (and whatever was still scheduled for it). */
	public static void clear(ServerPlayer p, String thread) {
		HunterData d = ModAttachments.get(p);
		d.threads.removeIf(t -> t.id.equals(thread));
		d.pending.removeIf(m -> m.thread().equals(thread));
		sync(p, "");
	}

	/** {@link #text}, delayTicks from now (queued per player, saved with the player). */
	public static void textLater(ServerPlayer p, String thread, String langKey, int delayTicks) {
		later(p, thread, PhoneMsg.TEXT, langKey, delayTicks);
	}

	/** {@link #photo}, delayTicks from now. */
	public static void photoLater(ServerPlayer p, String thread, String photoId, int delayTicks) {
		later(p, thread, PhoneMsg.PHOTO, photoId, delayTicks);
	}

	/** {@link #offerCase}, delayTicks from now. */
	public static void offerCaseLater(ServerPlayer p, String thread, CaseType type, int delayTicks) {
		later(p, thread, PhoneMsg.CASE, type.key(), delayTicks);
	}

	/** Unread bubbles over every thread. */
	public static int unread(HunterData d) {
		int n = 0;
		for (PhoneThread t : d.threads) {
			n += t.unread;
		}
		return n;
	}

	// ------------------------------------------------------------------ internals
	private static long now(ServerPlayer p) {
		return p.level().getServer().overworld().getGameTime();
	}

	/** The phone clock: overworld day time (the client shows day + hh:mm). */
	private static long clock(ServerPlayer p) {
		return p.level().getServer().overworld().getDayTime();
	}

	private static PhoneThread thread(HunterData d, String id, boolean create) {
		for (PhoneThread t : d.threads) {
			if (t.id.equals(id)) {
				return t;
			}
		}
		if (!create) {
			return null;
		}
		PhoneThread t = new PhoneThread(id);
		d.threads.add(0, t);
		return t;
	}

	private static void later(ServerPlayer p, String thread, int kind, String value, int delayTicks) {
		HunterData d = ModAttachments.get(p);
		d.pending.add(new PendingMsg(thread, kind, value, now(p) + Math.max(0, delayTicks)));
	}

	private static void add(ServerPlayer p, String thread, PhoneMsg msg) {
		put(ModAttachments.get(p), thread, msg);
		sync(p, thread);
	}

	/** Appends a bubble: the thread goes to the top, one more unread, its "escribiendo..." ends. */
	private static void put(HunterData d, String thread, PhoneMsg msg) {
		PhoneThread t = thread(d, thread, true);
		t.messages.add(msg);
		while (t.messages.size() > MAX_MESSAGES) {
			t.messages.remove(0);
		}
		t.unread++;
		t.typingUntil = 0;
		d.threads.remove(t);
		d.threads.add(0, t);
	}

	/** Every tick: scheduled messages land (after their "escribiendo..."). */
	public static void tick(MinecraftServer server) {
		long now = server.overworld().getGameTime();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			HunterData d = ModAttachments.get(p);
			if (d.pending.isEmpty()) {
				continue;
			}
			String landed = null;
			boolean typing = false;
			Iterator<PendingMsg> it = d.pending.iterator();
			while (it.hasNext()) {
				PendingMsg m = it.next();
				if (m.due() <= now) {
					it.remove();
					put(d, m.thread(), new PhoneMsg(m.kind(), m.value(), clock(p), 0));
					landed = m.thread();
				} else if (m.due() - now <= TYPING_LEAD) {
					PhoneThread t = thread(d, m.thread(), true);
					if (t.typingUntil < m.due()) {
						t.typingUntil = m.due();
						typing = true;
					}
				}
			}
			if (landed != null || typing) {
				sync(p, landed == null ? "" : landed);
			}
		}
	}

	/** Sends every thread to the client; notify = the thread that just got a message ("" = silent refresh). */
	public static void sync(ServerPlayer p, String notify) {
		if (!ServerPlayNetworking.canSend(p, PhoneMessagesPayload.TYPE)) {
			return;
		}
		HunterData d = ModAttachments.get(p);
		long now = now(p);
		List<PhoneMessagesPayload.View> views = new ArrayList<>();
		for (PhoneThread t : d.threads) {
			int typing = (int) Math.max(0L, Math.min(20L * 60L, t.typingUntil - now));
			views.add(new PhoneMessagesPayload.View(t.id, t.unread, typing, List.copyOf(t.messages)));
		}
		ServerPlayNetworking.send(p, new PhoneMessagesPayload(notify == null ? "" : notify, views));
	}

	private static void onAction(ServerPlayer p, PhoneMessageActionPayload a) {
		HunterData d = ModAttachments.get(p);
		PhoneThread t = thread(d, a.thread(), false);
		if (t == null) {
			return;
		}
		switch (a.action()) {
			case PhoneMessageActionPayload.READ -> {
				if (t.unread != 0) {
					t.unread = 0;
					sync(p, "");
				}
			}
			case PhoneMessageActionPayload.ACCEPT -> accept(p, d, t, a.index());
			default -> {
			}
		}
	}

	/** "Aceptar caso": the case-accept path (CaseManager.startCase), once per offer. */
	private static void accept(ServerPlayer p, HunterData d, PhoneThread t, int index) {
		if (index < 0 || index >= t.messages.size()) {
			return;
		}
		PhoneMsg m = t.messages.get(index);
		if (m.kind() != PhoneMsg.CASE || m.is(PhoneMsg.ACCEPTED)) {
			return;
		}
		if (d.active != null) {
			p.displayClientMessage(Component.translatable("deadline.phone.busy"), true);
			return;
		}
		CaseType type = CaseType.byKey(m.value());
		if (CaseManager.startCase(p, new CaseRequest(type, 0, p.level().getGameTime()))) {
			// the thread may have changed while the case started: find the offer again
			int i = t.messages.indexOf(m);
			if (i >= 0) {
				t.messages.set(i, m.with(PhoneMsg.ACCEPTED));
			}
		}
		sync(p, "");
	}
}
