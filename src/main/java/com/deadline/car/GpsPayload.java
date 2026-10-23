package com.deadline.car;

import com.deadline.DeadLine;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Server -> client: the GPS target of the overworld case the hunter works (the site's arrival marker), or "off".
 * The HUD shows an arrow + distance while the hunter is farther than 30 blocks from it (client hud GpsHud); caseKey
 * ("casa") lets the client play that case's ambience near the house.
 */
public record GpsPayload(boolean on, double x, double y, double z, String caseKey) implements CustomPacketPayload {
	public static final Type<GpsPayload> TYPE = new Type<>(DeadLine.id("gps"));
	public static final StreamCodec<RegistryFriendlyByteBuf, GpsPayload> CODEC = CustomPacketPayload.codec(GpsPayload::write, GpsPayload::new);

	private GpsPayload(RegistryFriendlyByteBuf buf) {
		this(buf.readBoolean(), buf.readDouble(), buf.readDouble(), buf.readDouble(), buf.readUtf());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeBoolean(on);
		buf.writeDouble(x);
		buf.writeDouble(y);
		buf.writeDouble(z);
		buf.writeUtf(caseKey);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
