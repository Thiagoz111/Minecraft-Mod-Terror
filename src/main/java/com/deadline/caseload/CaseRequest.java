package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

/** A pending call on the hotline. */
public record CaseRequest(CaseType type, int caller, long createdAt) {
	public static final Codec<CaseRequest> CODEC = RecordCodecBuilder.create(i -> i.group(
			CaseType.CODEC.fieldOf("type").forGetter(CaseRequest::type),
			Codec.INT.fieldOf("caller").forGetter(CaseRequest::caller),
			Codec.LONG.fieldOf("created").forGetter(CaseRequest::createdAt)
	).apply(i, CaseRequest::new));
}
