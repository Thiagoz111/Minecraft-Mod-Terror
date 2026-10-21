package com.deadline.voice.svc;

import com.deadline.DeadLine;
import com.deadline.voice.Voice;
import com.deadline.voice.VoiceBackend;
import de.maxhenkel.voicechat.api.VoicechatApi;
import de.maxhenkel.voicechat.api.VoicechatConnection;
import de.maxhenkel.voicechat.api.VoicechatServerApi;
import de.maxhenkel.voicechat.api.audiochannel.AudioChannel;
import de.maxhenkel.voicechat.api.audiochannel.LocationalAudioChannel;
import de.maxhenkel.voicechat.api.events.MicrophonePacketEvent;
import de.maxhenkel.voicechat.api.opus.OpusDecoder;
import de.maxhenkel.voicechat.api.opus.OpusEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * Simple Voice Chat bridge: decodes every microphone packet (loudness), captures tagged utterances and plays clips
 * back through audio channels (in the head of the listener, or from a point in the world) with simple DSP.
 * Only this package imports de.maxhenkel.*.
 */
final class SvcBackend implements VoiceBackend {
	static final int FRAME = 960; // 20 ms at 48 kHz
	private static SvcBackend instance;

	private final VoicechatApi api;
	private volatile VoicechatServerApi server;
	private final ConcurrentLinkedQueue<Frame> frames = new ConcurrentLinkedQueue<>();
	private final Map<UUID, OpusDecoder> decoders = new ConcurrentHashMap<>();
	private final Map<UUID, Capture> captures = new ConcurrentHashMap<>();
	private final Map<UUID, Map<String, short[]>> clips = new ConcurrentHashMap<>();
	private final ScheduledExecutorService player = Executors.newSingleThreadScheduledExecutor(r -> {
		Thread t = new Thread(r, "deadline-voice");
		t.setDaemon(true);
		return t;
	});

	/** An open capture window: the next utterance (voiced frames + 300 ms hangover, max 4 s) becomes the clip. */
	private static final class Capture {
		final String tag;
		final long deadline;
		final List<short[]> pcm = new ArrayList<>();
		int silentFrames;
		volatile boolean started;
		volatile long lastMs;

		Capture(String tag, long deadline) {
			this.tag = tag;
			this.deadline = deadline;
		}
	}

	private SvcBackend(VoicechatApi api) {
		this.api = api;
	}

	static void install(VoicechatApi api) {
		instance = new SvcBackend(api);
		Voice.backend = instance;
	}

	static void serverStarted(VoicechatServerApi s) {
		if (instance != null) {
			instance.server = s;
		}
	}

	static void onMic(MicrophonePacketEvent e) {
		SvcBackend b = instance;
		VoicechatConnection c = e.getSenderConnection();
		if (b == null || c == null) {
			return;
		}
		UUID id = c.getPlayer().getUuid();
		byte[] opus = e.getPacket().getOpusEncodedData();
		if (opus == null || opus.length == 0) {
			// push-to-talk released: the utterance is over
			Capture c0 = b.captures.get(id);
			if (c0 != null && c0.started) {
				b.finish(id, c0);
			}
			return;
		}
		short[] pcm;
		try {
			pcm = b.decoders.computeIfAbsent(id, k -> b.api.createDecoder()).decode(opus);
		} catch (RuntimeException ex) {
			return;
		}
		float db = dbfs(pcm);
		b.frames.add(new Frame(id, db, e.getPacket().isWhispering(), System.currentTimeMillis()));
		Capture cap = b.captures.get(id);
		if (cap != null) {
			b.capture(id, cap, pcm, db);
		}
	}

	private void capture(UUID id, Capture cap, short[] pcm, float db) {
		long now = System.currentTimeMillis();
		boolean voiced = db > -48F;
		if (!cap.started) {
			if (now > cap.deadline) {
				captures.remove(id);
				return;
			}
			if (!voiced) {
				return;
			}
			cap.lastMs = now;  // before started: drain() must never see a started capture with no timestamp
			cap.started = true;
		}
		synchronized (cap) {
			cap.pcm.add(pcm.clone());
			cap.silentFrames = voiced ? 0 : cap.silentFrames + 1;
			cap.lastMs = now;
		}
		if (cap.silentFrames > 15 || cap.pcm.size() > 200) {
			finish(id, cap);
		}
	}

	/** Closes a capture into a clip (end of speech, push-to-talk released, or packets stopped); only once. */
	private void finish(UUID id, Capture cap) {
		if (!captures.remove(id, cap)) {
			return;
		}
		synchronized (cap) {
			int n = cap.pcm.size() - Math.min(cap.silentFrames, 10);
			if (n <= 0) {
				return;
			}
			short[] all = new short[Math.max(0, n) * FRAME];
			for (int i = 0; i < n; i++) {
				short[] f = cap.pcm.get(i);
				System.arraycopy(f, 0, all, i * FRAME, Math.min(FRAME, f.length));
			}
			clips.computeIfAbsent(id, k -> new ConcurrentHashMap<>()).put(cap.tag, all);
			DeadLine.LOGGER.info("Voice clip '{}' captured ({} ms)", cap.tag, n * 20);
		}
	}

	static float dbfs(short[] pcm) {
		double sum = 0;
		for (short s : pcm) {
			sum += (double) s * s;
		}
		double rms = Math.sqrt(sum / Math.max(1, pcm.length)) / 32768.0;
		return (float) (20 * Math.log10(rms + 1e-9));
	}

	@Override
	public List<Frame> drain() {
		// no packets for 300 ms after speaking (push-to-talk with no end packet): close the clip
		long now = System.currentTimeMillis();
		captures.forEach((id, c) -> {
			if (c.started && now - c.lastMs > 300) {
				finish(id, c);
			}
		});
		List<Frame> out = new ArrayList<>();
		Frame f;
		while ((f = frames.poll()) != null) {
			out.add(f);
		}
		return out;
	}

	@Override
	public void tagNext(UUID player, String tag, int ms) {
		captures.put(player, new Capture(tag, System.currentTimeMillis() + ms));
	}

	@Override
	public boolean hasClip(UUID player, String tag) {
		Map<String, short[]> m = clips.get(player);
		return m != null && m.containsKey(tag);
	}

	@Override
	public void clear(UUID player) {
		clips.remove(player);
		captures.remove(player);
		OpusDecoder d = decoders.remove(player);
		if (d != null) {
			d.close();
		}
	}

	@Override
	public void play(ServerPlayer listener, UUID owner, String tag, Effect effect, Vec3 at) {
		VoicechatServerApi s = server;
		Map<String, short[]> m = clips.get(owner);
		short[] clip = m == null ? null : m.get(tag);
		if (s == null || clip == null) {
			return;
		}
		short[] pcm = Dsp.apply(clip, effect);
		AudioChannel channel;
		if (at == null) {
			VoicechatConnection conn = s.getConnectionOf(listener.getUUID());
			if (conn == null) {
				return;
			}
			channel = s.createStaticAudioChannel(UUID.randomUUID(), s.fromServerLevel(listener.level()), conn);
		} else {
			LocationalAudioChannel lc = s.createLocationalAudioChannel(UUID.randomUUID(), s.fromServerLevel(listener.level()),
					s.createPosition(at.x, at.y, at.z));
			if (lc != null) {
				lc.setDistance(24F);
			}
			channel = lc;
		}
		if (channel == null) {
			return;
		}
		OpusEncoder enc = api.createEncoder();
		List<byte[]> packets = new ArrayList<>();
		for (int i = 0; i + FRAME <= pcm.length; i += FRAME) {
			short[] f = new short[FRAME];
			System.arraycopy(pcm, i, f, 0, FRAME);
			packets.add(enc.encode(f));
		}
		enc.close();
		final AudioChannel ch = channel;
		final int[] k = {0};
		final java.util.concurrent.ScheduledFuture<?>[] task = new java.util.concurrent.ScheduledFuture<?>[1];
		task[0] = this.player.scheduleAtFixedRate(() -> {
			if (k[0] >= packets.size()) {
				ch.flush();
				task[0].cancel(false);
				return;
			}
			ch.send(packets.get(k[0]++));
		}, 0, 20, TimeUnit.MILLISECONDS);
	}
}
