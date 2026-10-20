package com.deadline.director;

import com.deadline.DeadLine;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.Reader;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.packs.resources.Resource;

/** Length in ticks of every recorded line (data/deadline/lines.json, written by tools/audio/snd_voices.py). */
public final class LineBook {
	private static Map<String, Integer> ticks;

	private LineBook() {
	}

	public static int ticks(MinecraftServer server, String id) {
		if (ticks == null) {
			load(server);
		}
		Integer t = ticks.get(id);
		return t != null ? t : 60;
	}

	public static boolean has(MinecraftServer server, String id) {
		if (ticks == null) {
			load(server);
		}
		return ticks.containsKey(id);
	}

	public static void clear() {
		ticks = null;
	}

	private static void load(MinecraftServer server) {
		ticks = new HashMap<>();
		Optional<Resource> res = server.getResourceManager().getResource(DeadLine.id("lines.json"));
		if (res.isEmpty()) {
			DeadLine.LOGGER.warn("data/deadline/lines.json not found: voice lines will use default lengths");
			return;
		}
		try (Reader r = res.get().openAsReader()) {
			JsonObject o = JsonParser.parseReader(r).getAsJsonObject();
			for (Map.Entry<String, JsonElement> e : o.entrySet()) {
				ticks.put(e.getKey(), e.getValue().getAsInt());
			}
		} catch (Exception e) {
			DeadLine.LOGGER.error("Could not read lines.json", e);
		}
	}
}
