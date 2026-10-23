package com.deadline.car;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Client -> server: car controls that are not movement (movement is client-authoritative through the vanilla vehicle
 * packets): horn, headlights, radio, and the steering angle (so other players see the front wheels turn).
 */
public record CarInputPayload(int action, float value) implements CustomPacketPayload {
	public static final int HORN = 0, LIGHTS = 1, RADIO = 2, STEER = 3;

	public static final Type<CarInputPayload> TYPE = new Type<>(DeadLine.id("car_input"));
	public static final StreamCodec<RegistryFriendlyByteBuf, CarInputPayload> CODEC = CustomPacketPayload.codec(CarInputPayload::write, CarInputPayload::new);

	private CarInputPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readVarInt(), buf.readFloat());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeVarInt(action);
		buf.writeFloat(value);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
