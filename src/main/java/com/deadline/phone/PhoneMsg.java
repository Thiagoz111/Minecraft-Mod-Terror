package com.deadline.phone;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.FriendlyByteBuf;

/**
 * One bubble of a phone thread (always incoming: the hunter never writes back).
 * kind {@link #TEXT}: value = lang key; {@link #PHOTO}: value = photo id (textures/gui/photo/&lt;id&gt;.png);
 * {@link #CASE}: value = case key (CaseType.key()), a location with the "Aceptar caso" button.
 * time = overworld day time when it arrived (the phone shows it as day + hh:mm); flags: {@link #ACCEPTED}.
 */
public record PhoneMsg(int kind, String value, long time, int flags) {
	public static final int TEXT = 0, PHOTO = 1, CASE = 2;
	/** A case offer that was already accepted (the button is spent). */
	public static final int ACCEPTED = 1;

	public static final Codec<PhoneMsg> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.INT.optionalFieldOf("kind", TEXT).forGetter(PhoneMsg::kind),
			Codec.STRING.fieldOf("value").forGetter(PhoneMsg::value),
			Codec.LONG.optionalFieldOf("time", 0L).forGetter(PhoneMsg::time),
			Codec.INT.optionalFieldOf("flags", 0).forGetter(PhoneMsg::flags)
	).apply(i, PhoneMsg::new));

	public boolean is(int flag) {
		return (flags & flag) != 0;
	}

	public PhoneMsg with(int flag) {
		return new PhoneMsg(kind, value, time, flags | flag);
	}

	static PhoneMsg read(FriendlyByteBuf buf) {
		return new PhoneMsg(buf.readVarInt(), buf.readUtf(), buf.readLong(), buf.readVarInt());
	}

	void write(FriendlyByteBuf buf) {
		buf.writeVarInt(kind);
		buf.writeUtf(value);
		buf.writeLong(time);
		buf.writeVarInt(flags);
	}
}
