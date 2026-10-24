package com.deadline.caseload;

import com.deadline.phone.PendingMsg;
import com.deadline.phone.PhoneThread;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Per-player progress: money, the active case and the phone's text threads (com.deadline.phone). Mutable, persisted
 * with the player. Keys of older saves that are no longer read are simply ignored by the codec.
 */
public final class HunterData {
	public static final Codec<HunterData> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.INT.optionalFieldOf("money", 250).forGetter(d -> d.money),
			Codec.INT.optionalFieldOf("solved", 0).forGetter(d -> d.solved),
			Codec.INT.optionalFieldOf("bestiary", 0).forGetter(d -> d.bestiary),
			ActiveCase.CODEC.optionalFieldOf("active").forGetter(d -> Optional.ofNullable(d.active)),
			Codec.LONG.optionalFieldOf("next_call", 0L).forGetter(d -> d.nextCall),
			Codec.BOOL.optionalFieldOf("welcomed", false).forGetter(d -> d.welcomed),
			PhoneThread.CODEC.listOf().optionalFieldOf("threads", List.of()).forGetter(d -> d.threads),
			PendingMsg.CODEC.listOf().optionalFieldOf("pending_msgs", List.of()).forGetter(d -> d.pending),
			Codec.INT.optionalFieldOf("intros", 0).forGetter(d -> d.intros)
	).apply(i, HunterData::new));

	public int money;
	public int solved;
	/** Bit set of CaseType ordinals whose entity the hunter has met (unlocks bestiary pages). */
	public int bestiary;
	public ActiveCase active;
	/** Game time of the next story message hook (the case intro threads; see CaseManager.tick). */
	public long nextCall;
	public boolean welcomed;
	/** The phone's text threads, most recent first. */
	public final List<PhoneThread> threads;
	/** Messages scheduled with PhoneMessages.textLater & co., in order. */
	public final List<PendingMsg> pending;
	/** Bit set of CaseType ordinals whose intro thread was already sent. */
	public int intros;

	public HunterData() {
		this(250, 0, 0, Optional.empty(), 0L, false, List.of(), List.of(), 0);
	}

	private HunterData(int money, int solved, int bestiary, Optional<ActiveCase> active, long nextCall, boolean welcomed,
			List<PhoneThread> threads, List<PendingMsg> pending, int intros) {
		this.money = money;
		this.solved = solved;
		this.bestiary = bestiary;
		this.active = active.orElse(null);
		this.nextCall = nextCall;
		this.welcomed = welcomed;
		this.threads = new ArrayList<>(threads);
		this.pending = new ArrayList<>(pending);
		this.intros = intros;
	}

	public boolean inCase() {
		return active != null;
	}
}
