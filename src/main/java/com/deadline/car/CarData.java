package com.deadline.car;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;

/** Which car belongs to whom (owner uuid -> car uuid). A car that loads while its owner has another one is discarded. */
public final class CarData extends SavedData {
	public static final Codec<CarData> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.unboundedMap(Codec.STRING, Codec.STRING).optionalFieldOf("cars", Map.of()).forGetter(d -> d.cars)
	).apply(i, CarData::new));

	public static final SavedDataType<CarData> TYPE = new SavedDataType<>("deadline_cars", CarData::new, CODEC, null);

	private final Map<String, String> cars;

	public CarData() {
		this(Map.of());
	}

	private CarData(Map<String, String> cars) {
		this.cars = new HashMap<>(cars);
	}

	public static CarData get(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(TYPE);
	}

	/** The current car of an owner (null: none). */
	public UUID car(UUID owner) {
		String s = cars.get(owner.toString());
		try {
			return s == null ? null : UUID.fromString(s);
		} catch (IllegalArgumentException ex) {
			return null;
		}
	}

	public void setCar(UUID owner, UUID car) {
		cars.put(owner.toString(), car.toString());
		this.setDirty();
	}
}
