package com.deadline.horror.casa.hunt;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Server -> client, a few times a second while it matters: breath (0-100), the kind of hiding place the player is in
 * ({@link HideSpots.Type} ordinal, 0 = none), the distance to the hunter (negative = none) and flags
 * ({@link #CHASED}, {@link #HUNT}, {@link #SEARCHED}, {@link #HOLDING}, {@link #SPENT}).
 */
public record HuntHudPayload(float breath, int hide, float nona, int flags) implements CustomPacketPayload {
	/** She is chasing this player (chase music). */
	public static final int CHASED = 1;
	/** A hunt is running in his case. */
	public static final int HUNT = 2;
	/** She is searching his hiding place right now (her face at the slats). */
	public static final int SEARCHED = 4;
	/** He is holding his breath. */
	public static final int HOLDING = 8;
	/** Out of breath (gasped): the key does nothing for a moment. */
	public static final int SPENT = 16;

	public static final Type<HuntHudPayload> TYPE = new Type<>(DeadLine.id("hunt_hud"));
	public static final StreamCodec<RegistryFriendlyByteBuf, HuntHudPayload> CODEC = CustomPacketPayload.codec(HuntHudPayload::write, HuntHudPayload::new);

	private HuntHudPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readFloat(), buf.readVarInt(), buf.readFloat(), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeFloat(breath);
		buf.writeVarInt(hide);
		buf.writeFloat(nona);
		buf.writeVarInt(flags);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
