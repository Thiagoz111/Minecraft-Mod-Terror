package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

/** A case to start (accepted from a phone thread, or a command). caller is a leftover of the old calls (0). */
public record CaseRequest(CaseType type, int caller, long createdAt) {
	public static final Codec<CaseRequest> CODEC = RecordCodecBuilder.create(i -> i.group(
			CaseType.CODEC.fieldOf("type").forGetter(CaseRequest::type),
			Codec.INT.fieldOf("caller").forGetter(CaseRequest::caller),
			Codec.LONG.fieldOf("created").forGetter(CaseRequest::createdAt)
	).apply(i, CaseRequest::new));
}
