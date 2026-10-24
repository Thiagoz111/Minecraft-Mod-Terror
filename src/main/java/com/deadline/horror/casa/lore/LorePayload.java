package com.deadline.horror.casa.lore;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Server -&gt; client: read a document of {@link LoreBook} (the client opens it full screen). flags: {@link #LATE}
 * = the house is in Act 4 or later (late pages show).
 */
public record LorePayload(String doc, int flags) implements CustomPacketPayload {
	public static final int LATE = 1;

	public static final Type<LorePayload> TYPE = new Type<>(DeadLine.id("lore"));
	public static final StreamCodec<RegistryFriendlyByteBuf, LorePayload> CODEC = CustomPacketPayload.codec(LorePayload::write, LorePayload::new);

	private LorePayload(RegistryFriendlyByteBuf buf) {
		this(buf.readUtf(), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeUtf(doc);
		buf.writeVarInt(flags);
	}

	public boolean late() {
		return (flags & LATE) != 0;
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
