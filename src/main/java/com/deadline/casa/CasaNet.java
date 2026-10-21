package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.caseload.CaseManager;
import com.deadline.director.Director;
import com.deadline.director.Exec;
import com.deadline.director.LineBook;
import com.deadline.director.Run;
import com.deadline.director.Step;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;

/**
 * Casa Morales UI over the network: Marta's family chat, the stitch ring, the name choice (LEMAZA / AZAMEL / OFELIA)
 * and the scripted spirit box question wheel. The client side lives in {@code client/casa} (CasaClientNet).
 * Run events: "chat:closed", "name:&lt;option&gt;" + "name:right" | "name:wrong" (+ "name:timeout"),
 * "spirit:&lt;question&gt;" (after the answer is heard).
 */
public final class CasaNet {
	/** Name options, in screen order. AZAMEL is the right one (LEMAZA is how Lucía writes it, backwards). */
	public static final List<String> NAMES = List.of("lemaza", "azamel", "ofelia");
	public static final String NAME_RIGHT = "azamel";
	/** Spirit box questions -> answer line casa.spirit.&lt;answer&gt; (in wheel order). */
	public static final Map<String, String> SPIRIT_ANSWERS = new LinkedHashMap<>();
	/** Ticks of radio sweep before the answer comes through (the football one makes you wait). */
	private static final int SPIRIT_WAIT = 30, SPIRIT_WAIT_LONG = 70;
	private static final int SPIRIT_COOLDOWN = 60;
	private static final String WHEEL_VAR = "spirit:wheel", ASKED_VAR = "spirit:asked";

	static {
		SPIRIT_ANSWERS.put("nombre", "azamel");
		SPIRIT_ANSWERS.put("que_queres", "al_perro");
		SPIRIT_ANSWERS.put("alquiler", "nunca");
		SPIRIT_ANSWERS.put("futbol", "temperley");
	}

	private static final Set<UUID> CHAT_OPEN = new HashSet<>();
	private static final Set<UUID> NAME_PENDING = new HashSet<>();
	private static final Set<UUID> WHEEL_PENDING = new HashSet<>();

	private CasaNet() {
	}

	// ------------------------------------------------------------------ payloads
	/**
	 * One chat message. from: member id (marta, jorge, nona, toti, lucia, unknown; lang key deadline.casa.chat.from.&lt;id&gt;)
	 * or "#literal name"; text: lang key or "#literal"; date "29/09" ("" = today) and time "03:07" ("" = now, the phone clock).
	 */
	public record ChatMsg(String from, String text, String date, String time, int flags) {
		/** Sent from this phone (right side, green); the DEAD LINE logo as avatar; a photo above the caption. */
		public static final int MINE = 1, LOGO = 2, PHOTO = 4;

		public static ChatMsg of(String from, String date, String time, String text) {
			return new ChatMsg(from, text, date, time, 0);
		}

		public static ChatMsg mine(String date, String time, String text) {
			return new ChatMsg("marta", text, date, time, MINE);
		}

		public boolean is(int flag) {
			return (flags & flag) != 0;
		}

		static ChatMsg read(RegistryFriendlyByteBuf buf) {
			return new ChatMsg(buf.readUtf(), buf.readUtf(), buf.readUtf(), buf.readUtf(), buf.readVarInt());
		}

		void write(RegistryFriendlyByteBuf buf) {
			buf.writeUtf(from);
			buf.writeUtf(text);
			buf.writeUtf(date);
			buf.writeUtf(time);
			buf.writeVarInt(flags);
		}
	}

	/** S2C: the chat screen. OPEN replaces the history and opens it, LIVE adds messages as they arrive, CLOSE closes it. */
	public record ChatPayload(int mode, String title, List<ChatMsg> messages) implements CustomPacketPayload {
		public static final int OPEN = 0, LIVE = 1, CLOSE = 2;
		public static final Type<ChatPayload> TYPE = new Type<>(DeadLine.id("casa_chat"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ChatPayload> CODEC = CustomPacketPayload.codec(ChatPayload::write, ChatPayload::read);

		private static ChatPayload read(RegistryFriendlyByteBuf buf) {
			int mode = buf.readVarInt();
			String title = buf.readUtf();
			int n = buf.readVarInt();
			List<ChatMsg> msgs = new ArrayList<>();
			for (int i = 0; i < n; i++) {
				msgs.add(ChatMsg.read(buf));
			}
			return new ChatPayload(mode, title, msgs);
		}

		private void write(RegistryFriendlyByteBuf buf) {
			buf.writeVarInt(mode);
			buf.writeUtf(title);
			buf.writeVarInt(messages.size());
			for (ChatMsg m : messages) {
				m.write(buf);
			}
		}

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** S2C: the stitch ring around the crosshair. progress 0..1 (negative hides it); stitch n of total; flags below. */
	public record StitchPayload(float progress, int stitch, int total, int flags) implements CustomPacketPayload {
		/** Aim is on the mouth; the stitch went through; it slipped; recovering after a slip; no thread and needle. */
		public static final int ON_TARGET = 1, SUCCESS = 2, FAIL = 4, COOLDOWN = 8, NO_KIT = 16;
		public static final Type<StitchPayload> TYPE = new Type<>(DeadLine.id("casa_stitch"));
		public static final StreamCodec<RegistryFriendlyByteBuf, StitchPayload> CODEC = CustomPacketPayload.codec(StitchPayload::write, StitchPayload::new);

		private StitchPayload(RegistryFriendlyByteBuf buf) {
			this(buf.readFloat(), buf.readVarInt(), buf.readVarInt(), buf.readVarInt());
		}

		private void write(RegistryFriendlyByteBuf buf) {
			buf.writeFloat(progress);
			buf.writeVarInt(stitch);
			buf.writeVarInt(total);
			buf.writeVarInt(flags);
		}

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/**
	 * S2C: a choice screen. NAME: options = names, ticks = time limit (0 none). SPIRIT: options = question ids,
	 * flags = bit per already asked question. CLOSE: closes whichever choice screen is open.
	 */
	public record ChoicePayload(int kind, List<String> options, int ticks, int flags) implements CustomPacketPayload {
		public static final int NAME = 0, SPIRIT = 1, CLOSE = 2;
		public static final Type<ChoicePayload> TYPE = new Type<>(DeadLine.id("casa_choice"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ChoicePayload> CODEC = CustomPacketPayload.codec(ChoicePayload::write, ChoicePayload::read);

		private static ChoicePayload read(RegistryFriendlyByteBuf buf) {
			int kind = buf.readVarInt();
			int n = buf.readVarInt();
			List<String> opts = new ArrayList<>();
			for (int i = 0; i < n; i++) {
				opts.add(buf.readUtf());
			}
			return new ChoicePayload(kind, opts, buf.readVarInt(), buf.readVarInt());
		}

		private void write(RegistryFriendlyByteBuf buf) {
			buf.writeVarInt(kind);
			buf.writeVarInt(options.size());
			for (String o : options) {
				buf.writeUtf(o);
			}
			buf.writeVarInt(ticks);
			buf.writeVarInt(flags);
		}

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** C2S: the chat was closed, a name was chosen ("" = time ran out), a spirit box question was asked. */
	public record ActionPayload(int action, String arg) implements CustomPacketPayload {
		public static final int CHAT_CLOSED = 0, NAME = 1, SPIRIT = 2;
		public static final Type<ActionPayload> TYPE = new Type<>(DeadLine.id("casa_action"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ActionPayload> CODEC = CustomPacketPayload.codec(ActionPayload::write, ActionPayload::new);

		private ActionPayload(RegistryFriendlyByteBuf buf) {
			this(buf.readVarInt(), buf.readUtf(64));
		}

		private void write(RegistryFriendlyByteBuf buf) {
			buf.writeVarInt(action);
			buf.writeUtf(arg, 64);
		}

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** Registers the payloads and the server receiver (one call from DeadLine.onInitialize). */
	public static void init() {
		PayloadTypeRegistry.playS2C().register(ChatPayload.TYPE, ChatPayload.CODEC);
		PayloadTypeRegistry.playS2C().register(StitchPayload.TYPE, StitchPayload.CODEC);
		PayloadTypeRegistry.playS2C().register(ChoicePayload.TYPE, ChoicePayload.CODEC);
		PayloadTypeRegistry.playC2S().register(ActionPayload.TYPE, ActionPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(ActionPayload.TYPE, (payload, ctx) -> onAction(ctx.player(), payload));
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> forget(handler.getPlayer()));
		ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
			CHAT_OPEN.clear();
			NAME_PENDING.clear();
			WHEEL_PENDING.clear();
		});
	}

	private static void send(ServerPlayer p, CustomPacketPayload payload) {
		if (p != null && !p.isRemoved() && ServerPlayNetworking.canSend(p, payload.type())) {
			ServerPlayNetworking.send(p, payload);
		}
	}

	private static void forget(ServerPlayer p) {
		UUID id = p.getUUID();
		CHAT_OPEN.remove(id);
		NAME_PENDING.remove(id);
		WHEEL_PENDING.remove(id);
	}

	private static void onAction(ServerPlayer p, ActionPayload a) {
		Run r = Director.of(p);
		switch (a.action()) {
			case ActionPayload.CHAT_CLOSED -> {
				if (CHAT_OPEN.remove(p.getUUID()) && r != null) {
					r.post("chat:closed");
				}
			}
			case ActionPayload.NAME -> {
				if (!NAME_PENDING.remove(p.getUUID())) {
					return;
				}
				String name = a.arg();
				boolean right = NAME_RIGHT.equals(name);
				if (!right) {
					// she laughs with Lucía's voice
					Fx.voice(p, ModSounds.POSEIDA_GIGGLE, 1.0F);
					Fx.shake(p, 0.8F, 12);
				}
				if (r != null) {
					r.post(NAMES.contains(name) ? "name:" + name : "name:timeout");
					r.post(right ? "name:right" : "name:wrong");
				}
			}
			case ActionPayload.SPIRIT -> {
				if (WHEEL_PENDING.remove(p.getUUID())) {
					ask(p, r, a.arg());
				}
			}
			default -> {
			}
		}
	}

	// ------------------------------------------------------------------ family chat
	/** Opens Marta's phone on the family group with this history (see {@link #familyChat()}). */
	public static void openChat(ServerPlayer p, List<ChatMsg> history) {
		openChat(p, "deadline.casa.chat.title", "deadline.casa.chat.members", history);
	}

	/**
	 * Opens a chat screen: title and subtitle (members) are lang keys or "#literal". If the name / spirit box choice is
	 * on screen (or the hunter is dead) it does not open and "chat:closed" is posted right away.
	 */
	public static void openChat(ServerPlayer p, String titleKey, String membersKey, List<ChatMsg> history) {
		CHAT_OPEN.add(p.getUUID());
		send(p, new ChatPayload(ChatPayload.OPEN, titleKey + "\n" + membersKey, List.copyOf(history)));
	}

	/**
	 * A message arriving now ("escribiendo..." first, then the bubble with PHONE_NOTIFY). Opens the chat if it was closed,
	 * over any other screen except the name / spirit box choice (or a dead hunter): then it only lands with the
	 * notification and "chat:closed" is posted right away.
	 */
	public static void liveMessage(ServerPlayer p, ChatMsg msg) {
		CHAT_OPEN.add(p.getUUID());
		send(p, new ChatPayload(ChatPayload.LIVE, "", List.of(msg)));
	}

	/** Takes the phone away (no "chat:closed" event). */
	public static void closeChat(ServerPlayer p) {
		CHAT_OPEN.remove(p.getUUID());
		send(p, new ChatPayload(ChatPayload.CLOSE, "", List.of()));
	}

	/** True while the chat screen is open on that hunter's screen (as far as the server knows). */
	public static boolean chatOpen(ServerPlayer p) {
		return CHAT_OPEN.contains(p.getUUID());
	}

	/** The Morales family group as Marta's phone shows it: it ends with Lucía, 29/09 03:07, "ya le saqué los hilos". */
	public static List<ChatMsg> familyChat() {
		String k = "deadline.casa.chat.m";
		List<ChatMsg> l = new ArrayList<>();
		l.add(ChatMsg.mine("26/09", "17:42", k + 1));
		l.add(new ChatMsg("marta", k + 2, "26/09", "17:42", ChatMsg.MINE | ChatMsg.PHOTO));
		l.add(ChatMsg.of("jorge", "26/09", "17:50", k + 3));
		l.add(ChatMsg.of("toti", "26/09", "17:51", k + 4));
		l.add(ChatMsg.of("nona", "26/09", "18:03", k + 5));
		l.add(ChatMsg.mine("26/09", "18:04", k + 6));
		l.add(ChatMsg.of("nona", "26/09", "18:20", k + 7));
		l.add(ChatMsg.of("nona", "26/09", "18:21", k + 8));
		l.add(ChatMsg.of("toti", "26/09", "18:21", k + 9));
		l.add(ChatMsg.mine("27/09", "22:15", k + 10));
		l.add(ChatMsg.of("jorge", "27/09", "22:31", k + 11));
		l.add(ChatMsg.mine("28/09", "08:02", k + 12));
		l.add(ChatMsg.of("toti", "28/09", "08:10", k + 13));
		l.add(ChatMsg.of("jorge", "28/09", "08:11", k + 14));
		l.add(ChatMsg.mine("28/09", "23:48", k + 15));
		l.add(ChatMsg.of("nona", "28/09", "23:59", k + 16));
		l.add(ChatMsg.of("lucia", "29/09", "03:07", k + 17));
		return l;
	}

	/** The live one: an unknown number with the DEAD LINE logo, "ya llegó?". */
	public static ChatMsg yaLlego() {
		return new ChatMsg("unknown", "deadline.casa.chat.ya_llego", "", "", ChatMsg.LOGO);
	}

	// ------------------------------------------------------------------ stitches
	/** Stitch ring with only a progress (0..1, negative hides). */
	public static void stitchRing(ServerPlayer p, float progress) {
		stitchRing(p, progress, 0, 0);
	}

	/** Stitch ring: progress 0..1 (negative hides), stitch number (1..{@link Stitch#TOTAL}, 0 = no label), {@link StitchPayload} flags. */
	public static void stitchRing(ServerPlayer p, float progress, int stitch, int flags) {
		send(p, new StitchPayload(progress, stitch, Stitch.TOTAL, flags));
	}

	// ------------------------------------------------------------------ the name
	/** LEMAZA / AZAMEL / OFELIA, no time limit. The answer arrives as "name:&lt;option&gt;" + "name:right|wrong". */
	public static void askName(ServerPlayer p) {
		askName(p, 0);
	}

	/**
	 * The name screen with a time limit (a thread running out); when it runs out, or another screen pushes it away
	 * (death...): "name:timeout" + "name:wrong".
	 */
	public static void askName(ServerPlayer p, int ticks) {
		NAME_PENDING.add(p.getUUID());
		send(p, new ChoicePayload(ChoicePayload.NAME, NAMES, Math.max(0, ticks), 0));
	}

	/** Closes the name screen or the spirit wheel if one is open (no answer is posted). */
	public static void closeChoice(ServerPlayer p) {
		NAME_PENDING.remove(p.getUUID());
		WHEEL_PENDING.remove(p.getUUID());
		send(p, new ChoicePayload(ChoicePayload.CLOSE, List.of(), 0, 0));
	}

	public static boolean namePending(ServerPlayer p) {
		return NAME_PENDING.contains(p.getUUID());
	}

	// ------------------------------------------------------------------ scripted spirit box
	/**
	 * Turns the spirit box into the question wheel for the rest of the current chapter (run vars are cleared when a
	 * chapter starts). No questions = all four. Ids: nombre, que_queres, alquiler, futbol.
	 */
	public static void spiritWheel(Run run, String... questions) {
		List<String> qs = new ArrayList<>();
		for (String q : questions.length == 0 ? SPIRIT_ANSWERS.keySet().toArray(new String[0]) : questions) {
			if (SPIRIT_ANSWERS.containsKey(q)) {
				qs.add(q);
			} else {
				DeadLine.LOGGER.warn("Unknown spirit box question '{}'", q);
			}
		}
		run.vars.put(WHEEL_VAR, qs);
	}

	/** Step version of {@link #spiritWheel(Run, String...)}. */
	public static Step spiritWheelStep(String... questions) {
		return e -> {
			spiritWheel(e.run, questions);
			return true;
		};
	}

	public static void spiritWheelOff(Run run) {
		run.vars.remove(WHEEL_VAR);
	}

	/** True once that question was asked (and answered) in this chapter. */
	public static boolean spiritAsked(Run run, String question) {
		return run.vars.get(ASKED_VAR) instanceof Set<?> s && s.contains(question);
	}

	@SuppressWarnings("unchecked")
	private static List<String> questions(Run r) {
		return r != null && r.vars.get(WHEEL_VAR) instanceof List<?> l && !l.isEmpty() ? (List<String>) l : List.of();
	}

	/**
	 * Hook of {@link com.deadline.item.SpiritBoxItem}: when the hunter's chapter asks for it, the box opens the question
	 * wheel instead of sweeping. Returns true when it did (the item then stops being used).
	 */
	public static boolean spiritHook(ServerPlayer p) {
		Run r = Director.of(p);
		List<String> qs = questions(r);
		if (qs.isEmpty() || r.vars.get("spirit:busy") instanceof Long t && r.now() - t < SPIRIT_WAIT_LONG + 200) {
			return false;
		}
		int asked = 0;
		for (int i = 0; i < qs.size(); i++) {
			if (spiritAsked(r, qs.get(i))) {
				asked |= 1 << i;
			}
		}
		WHEEL_PENDING.add(p.getUUID());
		send(p, new ChoicePayload(ChoicePayload.SPIRIT, qs, 0, asked));
		return true;
	}

	private static ItemStack spiritBox(ServerPlayer p) {
		for (InteractionHand h : InteractionHand.values()) {
			if (p.getItemInHand(h).is(ModItems.SPIRIT_BOX)) {
				return p.getItemInHand(h);
			}
		}
		return ItemStack.EMPTY;
	}

	/** The hunter asked: the question as a subtitle, radio sweep, then the answer line through the static. */
	private static void ask(ServerPlayer p, Run r, String q) {
		List<String> qs = questions(r);
		ItemStack box = spiritBox(p);
		if (!qs.contains(q) || box.isEmpty() || p.getCooldowns().isOnCooldown(box)) {
			return;
		}
		String answer = SPIRIT_ANSWERS.get(q);
		int wait = q.equals("futbol") ? SPIRIT_WAIT_LONG : SPIRIT_WAIT;
		p.getCooldowns().addCooldown(box, SPIRIT_COOLDOWN + wait);
		r.vars.put("spirit:busy", r.now());
		Fx.subtitle(p, "deadline.speaker.tu", "deadline.casa.spirit.q." + q, wait + 10);
		Step sweep = e -> {
			if (p.isRemoved()) {
				return true;
			}
			if (e.t % 12 == 0) {
				r.level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.SPIRIT_BOX_STATIC, SoundSource.PLAYERS, 0.8F,
						0.85F + r.level.getRandom().nextFloat() * 0.3F);
			}
			if (e.t % 10 == 0) {
				Fx.staticNoise(p, e.t > wait - 25 ? 0.45F : 0.25F, 14);
			}
			return e.t >= wait;
		};
		Step answerLine = e -> {
			if (p.isRemoved()) {
				return true;
			}
			if (e.t == 0) {
				// like any spirit box answer: the phrase on screen (deadline.spiritbox.*) and the voice through the radio
				String id = "casa.spirit." + answer;
				e.n = LineBook.ticks(r.level.getServer(), id);
				SoundEvent voice = ModSounds.line(id);
				if (voice != null) {
					r.level.playSound(null, p.getX(), p.getY(), p.getZ(), voice, SoundSource.PLAYERS, 1.3F, 1.0F);
				}
				for (ServerPlayer h : r.hunters()) {
					if (h == p || h.distanceToSqr(p) < 12 * 12) {
						Fx.title(h, "deadline.spiritbox.casa." + answer, e.n + 30);
					}
				}
				Fx.staticNoise(p, 0.6F, 30);
				Fx.shake(p, 0.5F, 12);
				SanityManager.add(p, -4.0F);
				CaseManager.evidence(p, 2);
			}
			return e.t >= e.n;
		};
		Step done = e -> {
			markAsked(e, q);
			e.run.vars.remove("spirit:busy");
			e.run.post("spirit:" + q);
			return true;
		};
		r.start("spirit " + q, p, List.of(sweep, answerLine, done));
	}

	@SuppressWarnings("unchecked")
	private static void markAsked(Exec e, String q) {
		Object o = e.run.vars.get(ASKED_VAR);
		Set<String> s = o instanceof Set<?> ? (Set<String>) o : new HashSet<>();
		s.add(q);
		e.run.vars.put(ASKED_VAR, s);
	}
}
