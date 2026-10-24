package com.deadline.net;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Everything the phone UI shows except the text threads (those come in com.deadline.phone.PhoneMessagesPayload).
 * Sent when the phone opens and whenever the state changes.
 */
public record PhoneDataPayload(boolean open, int money, int solved, int bestiary,
		String activeCase, int stage, int evidence) implements CustomPacketPayload {

	public static final Type<PhoneDataPayload> TYPE = new Type<>(DeadLine.id("phone_data"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PhoneDataPayload> CODEC = CustomPacketPayload.codec(PhoneDataPayload::write, PhoneDataPayload::read);

	private static PhoneDataPayload read(RegistryFriendlyByteBuf buf) {
		return new PhoneDataPayload(buf.readBoolean(), buf.readVarInt(), buf.readVarInt(), buf.readVarInt(),
				buf.readUtf(), buf.readVarInt(), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeBoolean(open);
		buf.writeVarInt(money);
		buf.writeVarInt(solved);
		buf.writeVarInt(bestiary);
		buf.writeUtf(activeCase);
		buf.writeVarInt(stage);
		buf.writeVarInt(evidence);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
