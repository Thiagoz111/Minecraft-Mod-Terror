package com.deadline.phone;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;

/** A conversation on the hunter's phone: a contact (name = lang key deadline.thread.&lt;id&gt;) and its bubbles. */
public final class PhoneThread {
	public static final Codec<PhoneThread> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.STRING.fieldOf("id").forGetter(t -> t.id),
			PhoneMsg.CODEC.listOf().optionalFieldOf("messages", List.of()).forGetter(t -> t.messages),
			Codec.INT.optionalFieldOf("unread", 0).forGetter(t -> t.unread)
	).apply(i, PhoneThread::new));

	public final String id;
	public final List<PhoneMsg> messages;
	public int unread;
	/** Game time until which the contact shows "escribiendo..." (not saved). */
	public long typingUntil;

	public PhoneThread(String id) {
		this(id, List.of(), 0);
	}

	private PhoneThread(String id, List<PhoneMsg> messages, int unread) {
		this.id = id;
		this.messages = new ArrayList<>(messages);
		this.unread = unread;
	}
}
