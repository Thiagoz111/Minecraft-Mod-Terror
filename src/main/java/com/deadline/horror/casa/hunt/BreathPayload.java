package com.deadline.horror.casa.hunt;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Client -> server: the hold-breath key went down (true) or up (false). */
public record BreathPayload(boolean hold) implements CustomPacketPayload {
	public static final Type<BreathPayload> TYPE = new Type<>(DeadLine.id("hunt_breath"));
	public static final StreamCodec<RegistryFriendlyByteBuf, BreathPayload> CODEC = CustomPacketPayload.codec(BreathPayload::write, BreathPayload::new);

	private BreathPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readBoolean());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeBoolean(hold);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
