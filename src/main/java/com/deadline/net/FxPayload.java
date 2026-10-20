package com.deadline.net;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Generic server -> client effect trigger (screen shake, flashes, jumpscares, positional hallucinations...). */
public record FxPayload(int kind, float a, int b, double x, double y, double z, String s) implements CustomPacketPayload {
	public static final int SHAKE = 1, FLASH = 2, RED_FLASH = 3, JUMPSCARE = 4, STATIC = 5, FADE = 6, SOUND_AT = 7,
			TITLE = 8, INCOMING_CALL = 9, HALLUCINATION = 10, SANITY = 11, OBJECTIVE = 12, CASE_END = 13,
			CHECKLIST = 14, SUBTITLE = 15, STAMP = 16, NOISE = 17, BIG_TEXT = 18, CHAPTER = 19;

	public static final Type<FxPayload> TYPE = new Type<>(DeadLine.id("fx"));
	public static final StreamCodec<RegistryFriendlyByteBuf, FxPayload> CODEC = CustomPacketPayload.codec(FxPayload::write, FxPayload::new);

	private FxPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readVarInt(), buf.readFloat(), buf.readVarInt(), buf.readDouble(), buf.readDouble(), buf.readDouble(), buf.readUtf());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeVarInt(kind);
		buf.writeFloat(a);
		buf.writeVarInt(b);
		buf.writeDouble(x);
		buf.writeDouble(y);
		buf.writeDouble(z);
		buf.writeUtf(s);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
