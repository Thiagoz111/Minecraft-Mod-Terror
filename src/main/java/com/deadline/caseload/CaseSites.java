package com.deadline.caseload;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;

/**
 * Where every case lives. Dimension cases (the Colegio) get a fresh site slot per acceptance in their own dimension;
 * overworld cases (the Casa Morales) have ONE origin in the real overworld, chosen the first time the case is accepted
 * (see {@link OverworldSite}) and reused afterwards. Also remembers the world clock an overworld case froze, so it can
 * be given back when the case ends.
 */
public final class CaseSites extends SavedData {
	public static final int SPACING = 1024;
	public static final int GROUND_Y = 63;

	public static final Codec<CaseSites> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.unboundedMap(Codec.STRING, Codec.INT).optionalFieldOf("next", Map.of()).forGetter(s -> s.next),
			Codec.unboundedMap(Codec.STRING, BlockPos.CODEC).optionalFieldOf("origins", Map.of()).forGetter(s -> s.origins),
			Codec.STRING.listOf().optionalFieldOf("placing", List.of()).forGetter(s -> s.placing),
			Codec.BOOL.optionalFieldOf("time_frozen", false).forGetter(s -> s.timeFrozen),
			Codec.BOOL.optionalFieldOf("saved_advance_time", true).forGetter(s -> s.savedAdvanceTime),
			Codec.LONG.optionalFieldOf("saved_day_time", 0L).forGetter(s -> s.savedDayTime)
	).apply(i, CaseSites::new));

	public static final SavedDataType<CaseSites> TYPE = new SavedDataType<>("deadline_sites", CaseSites::new, CODEC, null);

	private final Map<String, Integer> next;
	/** Overworld case key -> site origin (y = first air layer above the pad). */
	private final Map<String, BlockPos> origins;
	/** Overworld case keys whose site is being levelled/placed right now (chunks force-loaded). */
	private final List<String> placing;
	boolean timeFrozen;
	boolean savedAdvanceTime;
	long savedDayTime;

	public CaseSites() {
		this(Map.of(), Map.of(), List.of(), false, true, 0L);
	}

	private CaseSites(Map<String, Integer> next, Map<String, BlockPos> origins, List<String> placing, boolean timeFrozen, boolean savedAdvanceTime,
			long savedDayTime) {
		this.next = new HashMap<>(next);
		this.origins = new HashMap<>(origins);
		this.placing = new ArrayList<>(placing);
		this.timeFrozen = timeFrozen;
		this.savedAdvanceTime = savedAdvanceTime;
		this.savedDayTime = savedDayTime;
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

	/** Origin of a site slot in a case dimension. */
	public static BlockPos origin(int site) {
		return new BlockPos(site * SPACING, GROUND_Y, 0);
	}

	/** Origin of a case site wherever it lives: the stored overworld origin (null before the first acceptance) or the slot. */
	public static BlockPos originOf(MinecraftServer server, CaseType type, int site) {
		return type.overworld() ? get(server).overworldOrigin(type) : origin(site);
	}

	/** The stored overworld origin of a case (null when it has never been placed). */
	public BlockPos overworldOrigin(CaseType type) {
		return origins.get(type.key());
	}

	public void setOverworldOrigin(CaseType type, BlockPos origin) {
		origins.put(type.key(), origin.immutable());
		this.setDirty();
	}

	public boolean placing(CaseType type) {
		return placing.contains(type.key());
	}

	public void setPlacing(CaseType type, boolean on) {
		placing.remove(type.key());
		if (on) {
			placing.add(type.key());
		}
		this.setDirty();
	}

	/** Case keys whose placement was interrupted by a shutdown (their chunks may still be force-loaded). */
	public List<String> placingKeys() {
		return List.copyOf(placing);
	}
}
