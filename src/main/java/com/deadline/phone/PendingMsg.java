package com.deadline.phone;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

/** A message scheduled for later (PhoneMessages.textLater &amp; co.): delivered when the game time reaches due. */
public record PendingMsg(String thread, int kind, String value, long due) {
	public static final Codec<PendingMsg> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.STRING.fieldOf("thread").forGetter(PendingMsg::thread),
			Codec.INT.optionalFieldOf("kind", PhoneMsg.TEXT).forGetter(PendingMsg::kind),
			Codec.STRING.fieldOf("value").forGetter(PendingMsg::value),
			Codec.LONG.fieldOf("due").forGetter(PendingMsg::due)
	).apply(i, PendingMsg::new));
}
