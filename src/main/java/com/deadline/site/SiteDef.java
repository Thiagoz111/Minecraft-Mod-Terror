package com.deadline.site;

import com.deadline.DeadLine;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.Reader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.zip.Inflater;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * A case location authored in Python (tools/sites) and shipped as data/deadline/sites/&lt;key&gt;.json: a palette, a
 * compressed block array and named markers. All marker coordinates are relative to the site origin.
 */
public final class SiteDef {
	public record Point(double x, double y, double z, float yaw) {
		public Vec3 at(BlockPos origin) {
			return new Vec3(origin.getX() + x + 0.5, origin.getY() + y, origin.getZ() + z + 0.5);
		}
	}

	public record Area(int x1, int y1, int z1, int x2, int y2, int z2) {
		public AABB at(BlockPos o) {
			return new AABB(o.getX() + x1, o.getY() + y1, o.getZ() + z1, o.getX() + x2 + 1, o.getY() + y2 + 1, o.getZ() + z2 + 1);
		}
	}

	public record Prop(BlockPos pos, BlockState state) {
	}

	public record Write(BlockPos pos, Direction facing, float width) {
	}

	private static final Map<String, SiteDef> CACHE = new HashMap<>();

	public final String key;
	public final int w, h, d;
	public final BlockPos min;
	public final BlockState[] palette;
	public final short[] data;
	public final Map<String, Point> points = new LinkedHashMap<>();
	public final Map<String, Area> areas = new LinkedHashMap<>();
	public final Map<String, List<BlockPos>> groups = new LinkedHashMap<>();
	public final Map<String, BlockPos> doors = new LinkedHashMap<>();
	public final Map<String, Prop> props = new LinkedHashMap<>();
	public final Map<String, Write> writes = new LinkedHashMap<>();

	private SiteDef(String key, JsonObject o) throws Exception {
		this.key = key;
		JsonArray size = o.getAsJsonArray("size");
		w = size.get(0).getAsInt();
		h = size.get(1).getAsInt();
		d = size.get(2).getAsInt();
		min = pos(o.getAsJsonArray("min"));
		JsonArray pal = o.getAsJsonArray("palette");
		palette = new BlockState[pal.size()];
		for (int i = 1; i < pal.size(); i++) {
			palette[i] = parseState(pal.get(i).getAsString());
		}
		byte[] comp = Base64.getDecoder().decode(o.get("data").getAsString());
		byte[] raw = new byte[w * h * d * 2];
		Inflater inf = new Inflater();
		inf.setInput(comp);
		int n = 0;
		while (!inf.finished() && n < raw.length) {
			int k = inf.inflate(raw, n, raw.length - n);
			if (k == 0 && (inf.needsInput() || inf.needsDictionary())) {
				break;
			}
			n += k;
		}
		inf.end();
		data = new short[w * h * d];
		ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(data);

		JsonObject m = o.getAsJsonObject("markers");
		for (Map.Entry<String, JsonElement> e : obj(m, "points").entrySet()) {
			JsonArray a = e.getValue().getAsJsonArray();
			points.put(e.getKey(), new Point(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble(), a.size() > 3 ? a.get(3).getAsFloat() : 0F));
		}
		for (Map.Entry<String, JsonElement> e : obj(m, "areas").entrySet()) {
			JsonArray a = e.getValue().getAsJsonArray();
			areas.put(e.getKey(), new Area(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt(), a.get(3).getAsInt(), a.get(4).getAsInt(), a.get(5).getAsInt()));
		}
		for (Map.Entry<String, JsonElement> e : obj(m, "groups").entrySet()) {
			List<BlockPos> list = new ArrayList<>();
			for (JsonElement p : e.getValue().getAsJsonArray()) {
				list.add(pos(p.getAsJsonArray()));
			}
			groups.put(e.getKey(), list);
		}
		for (Map.Entry<String, JsonElement> e : obj(m, "doors").entrySet()) {
			doors.put(e.getKey(), pos(e.getValue().getAsJsonArray()));
		}
		for (Map.Entry<String, JsonElement> e : obj(m, "props").entrySet()) {
			JsonObject p = e.getValue().getAsJsonObject();
			props.put(e.getKey(), new Prop(pos(p.getAsJsonArray("pos")), parseState(p.get("state").getAsString())));
		}
		for (Map.Entry<String, JsonElement> e : obj(m, "writes").entrySet()) {
			JsonObject p = e.getValue().getAsJsonObject();
			Direction f = Direction.byName(p.get("facing").getAsString());
			writes.put(e.getKey(), new Write(pos(p.getAsJsonArray("pos")), f == null ? Direction.NORTH : f, p.has("width") ? p.get("width").getAsFloat() : 3F));
		}
	}

	private static JsonObject obj(JsonObject m, String name) {
		return m != null && m.has(name) ? m.getAsJsonObject(name) : new JsonObject();
	}

	private static BlockPos pos(JsonArray a) {
		return new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt());
	}

	/** "ns:id[prop=value,...]" -> BlockState. Unknown blocks become air (logged), unknown properties are ignored. */
	public static BlockState parseState(String s) {
		String id = s;
		String props = null;
		int b = s.indexOf('[');
		if (b >= 0) {
			id = s.substring(0, b);
			props = s.substring(b + 1, s.length() - 1);
		}
		Identifier rid = Identifier.parse(id);
		Optional<Block> block = BuiltInRegistries.BLOCK.getOptional(rid);
		if (block.isEmpty()) {
			DeadLine.LOGGER.warn("Site block {} is not registered; using air", id);
			return Blocks.AIR.defaultBlockState();
		}
		BlockState st = block.get().defaultBlockState();
		if (props != null && !props.isEmpty()) {
			for (String kv : props.split(",")) {
				String[] p = kv.split("=", 2);
				Property<?> prop = block.get().getStateDefinition().getProperty(p[0]);
				if (prop != null && p.length == 2) {
					st = with(st, prop, p[1]);
				}
			}
		}
		return st;
	}

	private static <T extends Comparable<T>> BlockState with(BlockState s, Property<T> p, String v) {
		return p.getValue(v).map(val -> s.setValue(p, val)).orElse(s);
	}

	public int volume() {
		return data.length;
	}

	/** Relative position of the n-th cell of the block array. */
	public BlockPos cell(int n) {
		int x = n % w;
		int z = (n / w) % d;
		int y = n / (w * d);
		return new BlockPos(min.getX() + x, min.getY() + y, min.getZ() + z);
	}

	public Point point(String name) {
		Point p = points.get(name);
		if (p == null) {
			DeadLine.LOGGER.warn("Site {} has no point '{}'", key, name);
			return new Point(0, 0, 0, 0);
		}
		return p;
	}

	public Area area(String name) {
		Area a = areas.get(name);
		if (a == null) {
			DeadLine.LOGGER.warn("Site {} has no area '{}'", key, name);
			return new Area(0, -100, 0, 0, -100, 0);
		}
		return a;
	}

	public List<BlockPos> group(String name) {
		return groups.getOrDefault(name, List.of());
	}

	public static void clearCache() {
		CACHE.clear();
	}

	/** Loads (and caches) a site definition from the server's data packs; null when missing or broken. */
	public static SiteDef get(MinecraftServer server, String key) {
		if (CACHE.containsKey(key)) {
			return CACHE.get(key);
		}
		SiteDef def = null;
		Optional<Resource> res = server.getResourceManager().getResource(DeadLine.id("sites/" + key + ".json"));
		if (res.isPresent()) {
			try (Reader r = res.get().openAsReader()) {
				def = new SiteDef(key, JsonParser.parseReader(r).getAsJsonObject());
				DeadLine.LOGGER.info("Loaded site {} ({}x{}x{}, {} states)", key, def.w, def.h, def.d, def.palette.length - 1);
			} catch (Exception e) {
				DeadLine.LOGGER.error("Could not load site {}", key, e);
			}
		} else {
			DeadLine.LOGGER.warn("Site data deadline:sites/{}.json not found", key);
		}
		CACHE.put(key, def);
		return def;
	}
}
