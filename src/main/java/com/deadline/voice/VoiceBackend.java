package com.deadline.voice;

import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/** What the mod needs from a voice-chat mod. The only implementation lives in voice.svc (Simple Voice Chat). */
public interface VoiceBackend {
	/** One decoded 20 ms microphone frame: loudness in dBFS and whether the player used the whisper key. */
	record Frame(UUID player, float db, boolean whisper, long time) {
	}

	/** Frames received since the last call (thread-safe hand-over from the voice thread). */
	java.util.List<Frame> drain();

	/** Opens a capture window: the next utterance of this player within `ms` is stored under `tag`. */
	void tagNext(UUID player, String tag, int ms);

	boolean hasClip(UUID player, String tag);

	/** Plays a stored clip. at == null: inside the listener's head (phone, thoughts); otherwise from that position. */
	void play(ServerPlayer listener, UUID owner, String tag, Effect effect, Vec3 at);

	/** Forgets every clip and buffer of a player (case over / opt-out). */
	void clear(UUID player);

	enum Effect {
		DRY, PHONE, REVERSED, PHONE_REVERSED, SLOW, DEMON
	}
}
