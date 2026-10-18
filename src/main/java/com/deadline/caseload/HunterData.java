package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Per-player progress: sanity, money, pending calls and the active case. Mutable, persisted with the player. */
public final class HunterData {
	public static final Codec<HunterData> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.FLOAT.optionalFieldOf("sanity", 100f).forGetter(d -> d.sanity),
			Codec.INT.optionalFieldOf("money", 250).forGetter(d -> d.money),
			Codec.INT.optionalFieldOf("solved", 0).forGetter(d -> d.solved),
			Codec.INT.optionalFieldOf("bestiary", 0).forGetter(d -> d.bestiary),
			CaseRequest.CODEC.listOf().optionalFieldOf("requests", List.of()).forGetter(d -> d.requests),
			ActiveCase.CODEC.optionalFieldOf("active").forGetter(d -> Optional.ofNullable(d.active)),
			Codec.LONG.optionalFieldOf("next_call", 0L).forGetter(d -> d.nextCall),
			Codec.BOOL.optionalFieldOf("welcomed", false).forGetter(d -> d.welcomed)
	).apply(i, HunterData::new));

	public float sanity;
	public int money;
	public int solved;
	/** Bit set of CaseType ordinals whose entity the hunter has met (unlocks bestiary pages). */
	public int bestiary;
	public final List<CaseRequest> requests;
	public ActiveCase active;
	public long nextCall;
	public boolean welcomed;

	public HunterData() {
		this(100f, 250, 0, 0, List.of(), Optional.empty(), 0L, false);
	}

	private HunterData(float sanity, int money, int solved, int bestiary, List<CaseRequest> requests, Optional<ActiveCase> active, long nextCall, boolean welcomed) {
		this.sanity = sanity;
		this.money = money;
		this.solved = solved;
		this.bestiary = bestiary;
		this.requests = new ArrayList<>(requests);
		this.active = active.orElse(null);
		this.nextCall = nextCall;
		this.welcomed = welcomed;
	}

	public boolean inCase() {
		return active != null;
	}
}
