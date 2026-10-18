package com.deadline.net;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Client -> server: a tap on the phone. */
public record PhoneActionPayload(int action, int arg) implements CustomPacketPayload {
	public static final int REFRESH = 0, ACCEPT = 1, DECLINE = 2, RETURN_HOME = 3, BUY = 4, ABANDON = 5;

	public static final Type<PhoneActionPayload> TYPE = new Type<>(DeadLine.id("phone_action"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PhoneActionPayload> CODEC = CustomPacketPayload.codec(PhoneActionPayload::write, PhoneActionPayload::new);

	private PhoneActionPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readVarInt(), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeVarInt(action);
		buf.writeVarInt(arg);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
