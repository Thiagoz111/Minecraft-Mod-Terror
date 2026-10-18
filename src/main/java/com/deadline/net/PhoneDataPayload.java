package com.deadline.net;

import com.deadline.DeadLine;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Everything the phone UI shows. Sent when the phone opens and whenever the state changes. */
public record PhoneDataPayload(boolean open, int money, int solved, float sanity, int bestiary,
		List<Request> requests, String activeCase, int activeCaller, int stage, int evidence) implements CustomPacketPayload {

	public record Request(String caseKey, int caller, int ageSeconds) {
	}

	public static final Type<PhoneDataPayload> TYPE = new Type<>(DeadLine.id("phone_data"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PhoneDataPayload> CODEC = CustomPacketPayload.codec(PhoneDataPayload::write, PhoneDataPayload::read);

	private static PhoneDataPayload read(RegistryFriendlyByteBuf buf) {
		boolean open = buf.readBoolean();
		int money = buf.readVarInt();
		int solved = buf.readVarInt();
		float sanity = buf.readFloat();
		int bestiary = buf.readVarInt();
		int n = buf.readVarInt();
		List<Request> reqs = new ArrayList<>();
		for (int i = 0; i < n; i++) {
			reqs.add(new Request(buf.readUtf(), buf.readVarInt(), buf.readVarInt()));
		}
		return new PhoneDataPayload(open, money, solved, sanity, bestiary, reqs, buf.readUtf(), buf.readVarInt(), buf.readVarInt(), buf.readVarInt());
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeBoolean(open);
		buf.writeVarInt(money);
		buf.writeVarInt(solved);
		buf.writeFloat(sanity);
		buf.writeVarInt(bestiary);
		buf.writeVarInt(requests.size());
		for (Request r : requests) {
			buf.writeUtf(r.caseKey());
			buf.writeVarInt(r.caller());
			buf.writeVarInt(r.ageSeconds());
		}
		buf.writeUtf(activeCase);
		buf.writeVarInt(activeCaller);
		buf.writeVarInt(stage);
		buf.writeVarInt(evidence);
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
