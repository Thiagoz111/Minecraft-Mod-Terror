package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;

/**
 * The case a hunter is currently working.
 * stage: 0 = find the anchor, 1 = weaken the entity, 2 = banish it, 3 = solved.
 */
public final class ActiveCase {
	public static final Codec<ActiveCase> CODEC = RecordCodecBuilder.create(i -> i.group(
			CaseType.CODEC.fieldOf("type").forGetter(c -> c.type),
			Codec.INT.fieldOf("site").forGetter(c -> c.site),
			Codec.INT.fieldOf("caller").forGetter(c -> c.caller),
			Codec.INT.fieldOf("stage").forGetter(c -> c.stage),
			Codec.INT.fieldOf("evidence").forGetter(c -> c.evidence),
			Identifier.CODEC.fieldOf("return_dim").forGetter(c -> c.returnDim),
			BlockPos.CODEC.fieldOf("return_pos").forGetter(c -> c.returnPos),
			Codec.LONG.fieldOf("started").forGetter(c -> c.startedAt),
			Codec.INT.optionalFieldOf("solved_timer", 0).forGetter(c -> c.solvedTimer)
	).apply(i, ActiveCase::new));

	public final CaseType type;
	public final int site;
	public final int caller;
	public int stage;
	public int evidence;
	public final Identifier returnDim;
	public final BlockPos returnPos;
	public final long startedAt;
	public int solvedTimer;

	public ActiveCase(CaseType type, int site, int caller, int stage, int evidence, Identifier returnDim, BlockPos returnPos, long startedAt, int solvedTimer) {
		this.type = type;
		this.site = site;
		this.caller = caller;
		this.stage = stage;
		this.evidence = evidence;
		this.returnDim = returnDim;
		this.returnPos = returnPos;
		this.startedAt = startedAt;
		this.solvedTimer = solvedTimer;
	}
}
