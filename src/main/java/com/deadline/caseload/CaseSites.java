package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;

/** Hands out a fresh site slot (location) for every accepted case, per case dimension. */
public final class CaseSites extends SavedData {
	public static final int SPACING = 1024;
	public static final int GROUND_Y = 63;

	public static final Codec<CaseSites> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.unboundedMap(Codec.STRING, Codec.INT).optionalFieldOf("next", Map.of()).forGetter(s -> s.next)
	).apply(i, CaseSites::new));

	public static final SavedDataType<CaseSites> TYPE = new SavedDataType<>("deadline_sites", CaseSites::new, CODEC, null);

	private final Map<String, Integer> next;

	public CaseSites() {
		this(Map.of());
	}

	private CaseSites(Map<String, Integer> next) {
		this.next = new HashMap<>(next);
	}

	public static CaseSites get(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(TYPE);
	}

	public int allocate(CaseType type) {
		int idx = next.getOrDefault(type.key(), 0);
		next.put(type.key(), idx + 1);
		this.setDirty();
		return idx;
	}

	public static BlockPos origin(int site) {
		return new BlockPos(site * SPACING, GROUND_Y, 0);
	}
}
