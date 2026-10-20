package com.deadline.caseload;

import com.deadline.DeadLine;
import com.deadline.caseload.sites.ConventSite;
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
	COLEGIO("colegio", 3, 4, 1800, ConventSite::new, () -> ModEntities.MONJA, () -> ModItems.INVERTED_ROSARY),
	CASA_MORALES("casa", 4, 5, 1600, MoralesHouseSite::new, () -> ModEntities.POSEIDA, () -> ModItems.CURSED_DOLL);

	public static final Codec<CaseType> CODEC = Codec.STRING.xmap(CaseType::byKey, CaseType::key);

	private final String key;
	private final int difficulty;
	private final int callers;
	private final int reward;
	private final Supplier<SiteBuilder> builder;
	private final Supplier<EntityType<?>> boss;
	private final Supplier<Item> anchor;
	private final ResourceKey<Level> level;

	CaseType(String key, int difficulty, int callers, int reward, Supplier<SiteBuilder> builder, Supplier<EntityType<?>> boss, Supplier<Item> anchor) {
		this.key = key;
		this.difficulty = difficulty;
		this.callers = callers;
		this.reward = reward;
		this.builder = builder;
		this.boss = boss;
		this.anchor = anchor;
		this.level = ResourceKey.create(Registries.DIMENSION, DeadLine.id("caso_" + key));
	}

	public String key() {
		return key;
	}

	public int difficulty() {
		return difficulty;
	}

	/** Number of distinct caller variants (lang keys deadline.case.KEY.caller.N / msg.N). */
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

	public ResourceKey<Level> levelKey() {
		return level;
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

	public static CaseType forLevel(ResourceKey<Level> dim) {
		for (CaseType t : values()) {
			if (t.level.equals(dim)) {
				return t;
			}
		}
		return null;
	}
}
