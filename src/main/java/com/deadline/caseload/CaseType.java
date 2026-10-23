package com.deadline.caseload;

import com.deadline.DeadLine;
import com.deadline.caseload.sites.ConventSite;
import com.deadline.director.CaseScript;
import com.deadline.director.colegio.ColegioScript;
import com.deadline.caseload.sites.MoralesHouseSite;
import com.deadline.caseload.sites.SiteBuilder;
import com.deadline.registry.ModEntities;
import com.deadline.registry.ModItems;
import com.mojang.serialization.Codec;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;

/** Every haunted location the hotline can send you to (case 1: the girls' school, case 2: the Morales house). */
public enum CaseType {
	COLEGIO("colegio", 3, 4, 1800, ConventSite::new, () -> ModEntities.MONJA, () -> ModItems.INVERTED_ROSARY, ColegioScript::new),
	CASA_MORALES("casa", 4, 5, 1600, MoralesHouseSite::new, () -> ModEntities.POSEIDA, () -> ModItems.CURSED_DOLL,
			com.deadline.director.casa.CasaScript::new);

	public static final Codec<CaseType> CODEC = Codec.STRING.xmap(CaseType::byKey, CaseType::key);

	private final String key;
	private final int difficulty;
	private final int callers;
	private final int reward;
	private final Supplier<SiteBuilder> builder;
	private final Supplier<EntityType<?>> boss;
	private final Supplier<Item> anchor;
	private final ResourceKey<Level> level;
	private final Supplier<CaseScript> scriptFactory;
	private CaseScript script;

	CaseType(String key, int difficulty, int callers, int reward, Supplier<SiteBuilder> builder, Supplier<EntityType<?>> boss, Supplier<Item> anchor,
			Supplier<CaseScript> script) {
		this.key = key;
		this.difficulty = difficulty;
		this.callers = callers;
		this.reward = reward;
		this.builder = builder;
		this.boss = boss;
		this.anchor = anchor;
		this.level = ResourceKey.create(Registries.DIMENSION, DeadLine.id("caso_" + key));
		this.scriptFactory = script;
	}

	public String key() {
		return key;
	}

	/** Cases run by the director (Python-authored site, chapters and beats) instead of the classic anchor loop. */
	public boolean scripted() {
		return scriptFactory != null;
	}

	public CaseScript script() {
		if (script == null && scriptFactory != null) {
			script = scriptFactory.get();
		}
		return script;
	}

	public int difficulty() {
		return difficulty;
	}

	/** Number of caller variants of the old call system (kept for CaseRequest.caller; no lang keys any more). */
	public int callers() {
		return callers;
	}

	public int reward() {
		return reward;
	}

	public SiteBuilder newBuilder() {
		return builder.get();
	}

	public EntityType<?> boss() {
		return boss.get();
	}

	public Item anchor() {
		return anchor.get();
	}

	/** The level the case is played in: its own dimension, or the real overworld for an overworld case. */
	public ResourceKey<Level> levelKey() {
		return overworld() ? Level.OVERWORLD : level;
	}

	/**
	 * Cases that happen in the player's real overworld (reached by car; the site is placed once and stays): no
	 * teleport in or out, one stored origin (CaseSites), site index always 0.
	 */
	public boolean overworld() {
		return this == CASA_MORALES;
	}

	public String langKey(String suffix) {
		return "deadline.case." + key + "." + suffix;
	}

	public static CaseType byKey(String key) {
		for (CaseType t : values()) {
			if (t.key.equals(key)) {
				return t;
			}
		}
		return COLEGIO;
	}

	/** The case whose OWN dimension this is (never an overworld case: the overworld is not a case level). */
	public static CaseType forLevel(ResourceKey<Level> dim) {
		for (CaseType t : values()) {
			if (!t.overworld() && t.level.equals(dim)) {
				return t;
			}
		}
		return null;
	}
}
