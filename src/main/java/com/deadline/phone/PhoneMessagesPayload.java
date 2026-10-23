package com.deadline.phone;

import com.deadline.DeadLine;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * Server -> client: every thread of the hunter's phone (most recent first). notify = the thread whose last message just
 * arrived (vibration, tone and toast on the client), "" for a silent refresh.
 */
public record PhoneMessagesPayload(String notifyThread, List<View> threads) implements CustomPacketPayload {
	/** One thread as the phone draws it; typing = ticks of "escribiendo..." left. */
	public record View(String id, int unread, int typing, List<PhoneMsg> messages) {
	}

	public static final Type<PhoneMessagesPayload> TYPE = new Type<>(DeadLine.id("phone_messages"));
	public static final StreamCodec<RegistryFriendlyByteBuf, PhoneMessagesPayload> CODEC = CustomPacketPayload.codec(PhoneMessagesPayload::write, PhoneMessagesPayload::read);

	private static PhoneMessagesPayload read(RegistryFriendlyByteBuf buf) {
		String notify = buf.readUtf();
		int n = buf.readVarInt();
		List<View> threads = new ArrayList<>();
		for (int i = 0; i < n; i++) {
			String id = buf.readUtf();
			int unread = buf.readVarInt();
			int typing = buf.readVarInt();
			int m = buf.readVarInt();
			List<PhoneMsg> msgs = new ArrayList<>();
			for (int j = 0; j < m; j++) {
				msgs.add(PhoneMsg.read(buf));
			}
			threads.add(new View(id, unread, typing, msgs));
		}
		return new PhoneMessagesPayload(notify, threads);
	}

	private void write(RegistryFriendlyByteBuf buf) {
		buf.writeUtf(notifyThread);
		buf.writeVarInt(threads.size());
		for (View t : threads) {
			buf.writeUtf(t.id());
			buf.writeVarInt(t.unread());
			buf.writeVarInt(t.typing());
			buf.writeVarInt(t.messages().size());
			for (PhoneMsg m : t.messages()) {
				m.write(buf);
			}
		}
	}

	@Override
	public Type<? extends CustomPacketPayload> type() {
		return TYPE;
	}
}
