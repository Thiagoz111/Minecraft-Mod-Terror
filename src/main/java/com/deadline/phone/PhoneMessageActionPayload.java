package com.deadline.phone;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Client -> server: a thread was opened ({@link #READ}), or "Aceptar caso" was pressed on bubble `index` ({@link #ACCEPT}). */
public record PhoneMessageActionPayload(int action, String thread, int index) implements CustomPacketPayload {
	public static final int READ = 0, ACCEPT = 1;

	public static final Type<PhoneMessageActionPayload> TYPE = new Type<>(DeadLine.id("phone_message_action"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PhoneMessageActionPayload> CODEC = CustomPacketPayload.codec(PhoneMessageActionPayload::write, PhoneMessageActionPayload::new);

	private PhoneMessageActionPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readVarInt(), buf.readUtf(64), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeVarInt(action);
		buf.writeUtf(thread, 64);
		buf.writeVarInt(index);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
