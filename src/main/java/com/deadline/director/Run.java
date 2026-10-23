package com.deadline.director;

import com.deadline.DeadLine;
import com.deadline.caseload.CaseType;
import com.deadline.caseload.HunterData;
import com.deadline.net.Fx;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModSounds;
import com.deadline.site.Fixtures;
import com.deadline.site.SiteDef;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** One live scripted case at one site: chapter, objectives, flags, running sequences and actors. */
public final class Run {
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE;

	public final CaseType type;
	public final int site;
	public final ServerLevel level;
	public final BlockPos origin;
	public final SiteDef def;
	public final CaseScript script;
	public final Script compiled;

	int chapter;
	long chapterStart;
	boolean hintShown;
	final Set<String> flags = new HashSet<>();
	Set<String> chapterFlags;
	final Map<String, Long> flagAt = new HashMap<>();
	final Set<String> done = new LinkedHashSet<>();
	final Set<String> fired = new HashSet<>();
	final Map<String, Long> lastEnd = new HashMap<>();
	final Map<Beat, Exec> active = new HashMap<>();
	final List<Exec> execs = new ArrayList<>();
	final Set<String> events = new HashSet<>();
	final Set<String> nextEvents = new HashSet<>();
	public final Map<String, Integer> counters = new HashMap<>();
	public final Map<String, Entity> actors = new LinkedHashMap<>();
	public final Map<String, Object> vars = new HashMap<>();
	final Map<BlockPos, String> markerAt = new HashMap<>();
	/** Flags as they were when each chapter first started (for /deadline chapter retakes). */
	private final Map<Integer, Set<String>> flagsAtStart = new HashMap<>();

	Run(CaseType type, int site, ServerLevel level, BlockPos origin, SiteDef def, CaseScript script) {
		this.type = type;
		this.site = site;
		this.level = level;
		this.origin = origin;
		this.def = def;
		this.script = script;
		this.compiled = new Script(type.key());
		script.define(compiled);
		for (Map.Entry<String, SiteDef.Point> e : def.points.entrySet()) {
			markerAt.put(BlockPos.containing(e.getValue().at(origin)), e.getKey());
		}
		for (Map.Entry<String, BlockPos> e : def.doors.entrySet()) {
			markerAt.put(origin.offset(e.getValue()), e.getKey());
			markerAt.put(origin.offset(e.getValue()).above(), e.getKey());
		}
		for (Map.Entry<String, SiteDef.Prop> e : def.props.entrySet()) {
			markerAt.put(origin.offset(e.getValue().pos()), e.getKey());
		}
	}

	// ------------------------------------------------------------------ hunters
	public List<ServerPlayer> hunters() {
		List<ServerPlayer> out = new ArrayList<>();
		for (ServerPlayer p : level.getServer().getPlayerList().getPlayers()) {
			HunterData d = ModAttachments.get(p);
			if (d.active != null && d.active.type == type && d.active.site == site && p.level() == level && p.isAlive()) {
				out.add(p);
			}
		}
		return out;
	}

	/** The protagonist (first hunter): the one scripted scares target. */
	public ServerPlayer star() {
		List<ServerPlayer> h = hunters();
		return h.isEmpty() ? null : h.get(0);
	}

	public long now() {
		return level.getGameTime();
	}

	public int chapter() {
		return chapter;
	}

	public long chapterTicks() {
		return now() - chapterStart;
	}

	// ------------------------------------------------------------------ ticking
	void tick() {
		events.clear();
		events.addAll(nextEvents);
		nextEvents.clear();
		List<ServerPlayer> hunters = hunters();
		if (hunters.isEmpty()) {
			return; // paused: nobody is here (logged out, dead, in another dimension)
		}
		for (Entity a : actors.values()) {
			if (a != null && a.getRemovalReason() == Entity.RemovalReason.UNLOADED_TO_CHUNK) {
				// a scene lost its actor to a chunk unload: replay the chapter from its checkpoint
				ServerPlayer s0 = star();
				if (s0 != null) {
					checkpoint(s0);
				}
				return;
			}
		}
		{
			for (Beat b : compiled.beats) {
				if (!eligible(b)) {
					continue;
				}
				for (ServerPlayer p : hunters) {
					boolean hit;
					try {
						hit = b.trigger.test(this, p);
					} catch (RuntimeException ex) {
						DeadLine.LOGGER.error("Trigger of {} failed", b.id, ex);
						hit = false;
					}
					if (hit) {
						fire(b, p);
						break;
					}
				}
			}
			Chapter c = compiled.chapter(chapter);
			if (c != null && !hintShown && !c.hint.isEmpty() && chapterTicks() > c.hintAfter) {
				hintShown = true;
				for (ServerPlayer p : hunters) {
					Fx.subtitle(p, "", "deadline." + type.key() + ".hint." + c.hint, 120);
				}
			}
		}
		for (Exec e : new ArrayList<>(execs)) {
			e.tick();
		}
		execs.removeIf(e -> e.done);
		active.entrySet().removeIf(en -> {
			if (en.getValue().done) {
				lastEnd.put(en.getKey().id, now());
				return true;
			}
			return false;
		});
		script.tick(this);
	}

	boolean eligible(Beat b) {
		if (b.chapter >= 0 && b.chapter != chapter) {
			return false;
		}
		if (b.fromChapter >= 0 && chapter < b.fromChapter) {
			return false;
		}
		if (b.once ? fired.contains(b.id) : (active.containsKey(b) || now() - lastEnd.getOrDefault(b.id, -100000L) < b.cooldown)) {
			return false;
		}
		for (String f : b.requires) {
			if (!flags.contains(f)) {
				return false;
			}
		}
		for (String f : b.unless) {
			if (flags.contains(f)) {
				return false;
			}
		}
		return true;
	}

	/** Fires a beat now (force ignores its conditions). */
	public void fire(Beat b, ServerPlayer p) {
		fired.add(b.id);
		Exec e = start(b.id, p, b.steps);
		active.put(b, e);
		DeadLine.LOGGER.info("Beat {} fired (chapter {})", b.id, chapter);
	}

	public Exec start(String label, ServerPlayer p, List<Step> steps) {
		Exec e = new Exec(this, p, label, new ArrayList<>(steps));
		execs.add(e);
		return e;
	}

	/** Event for event triggers; visible to triggers during the next tick. */
	public void post(String event) {
		nextEvents.add(event);
	}

	public boolean event(String name) {
		return events.contains(name);
	}

	/** Name of the marker (point, door or prop) at an absolute block position, or null. */
	public String markerAt(BlockPos pos) {
		return markerAt.get(pos);
	}

	// ------------------------------------------------------------------ chapters, objectives, flags
	public void startChapter(int n, boolean fromCheckpoint) {
		Chapter c = compiled.chapter(n);
		if (c == null) {
			DeadLine.LOGGER.warn("{} has no chapter {}", type.key(), n);
			return;
		}
		if (fromCheckpoint) {
			// replay the chapter from its start: stop sequences, remove actors, forget this chapter's beats and flags
			for (Exec e : execs) {
				e.cancel();
			}
			execs.clear();
			active.clear();
			for (Entity e : actors.values()) {
				if (e != null && !e.isRemoved()) {
					e.discard();
				}
			}
			actors.clear();
			for (Beat b : compiled.beats) {
				if (b.chapter == n) {
					fired.remove(b.id);
				}
			}
			if (chapterFlags != null && chapter == n) {
				flags.clear();
				flags.addAll(chapterFlags);
			}
		}
		if (!fromCheckpoint) {
			flagsAtStart.put(n, new HashSet<>(flags));
		} else {
			flagsAtStart.putIfAbsent(n, new HashSet<>(flags));  // a run restored after a restart
		}
		chapterFlags = new HashSet<>(flags);
		chapter = n;
		chapterStart = now();
		hintShown = false;
		done.clear();
		// chapter progress (candles lit, prayer seconds, silence, answers...) starts over; reprimands and their cooldowns stay
		counters.keySet().removeIf(k -> !k.startsWith("conduct:"));
		vars.keySet().removeIf(k -> !k.startsWith("stampcd:"));
		for (ServerPlayer p : hunters()) {
			HunterData d = ModAttachments.get(p);
			d.active.stage = n;
			if (c.card) {
				Fx.chapterCard(p, "deadline." + type.key() + ".ch." + n, "deadline." + type.key() + ".ch." + n + ".sub", 110);
			}
			sync(p);
		}
		if (c.card) {
			sound(ModSounds.COLEGIO_CAMPANA, null, 0.9F, 1.0F);
		}
		start("chapter " + n, star(), c.setup);
	}

	/** Sends a hunter back to the checkpoint of the current chapter and replays it (death, /deadline chapter). */
	public void checkpoint(ServerPlayer p) {
		Chapter c = compiled.chapter(chapter);
		String cp = c != null ? c.checkpoint : "spawn";
		Vec3 v = at(cp);
		// an overworld case replays its chapter where the hunter is while away from the site (driving there, after a
		// restart): only hunters at the house go back to the checkpoint
		boolean away = type.overworld() && (p.level() != level || !siteBox().inflate(32).contains(p.position()));
		if (!away) {
			p.teleportTo(level, v.x, v.y, v.z, java.util.Set.of(), yaw(cp), 0F, false);
		}
		startChapter(chapter, true);
		script.onCheckpoint(this, p);
	}

	/** Jumps to a chapter at its checkpoint (testing / filming retakes). */
	public void jump(int n, ServerPlayer p) {
		// a retake: flags as they were when chapter n first started, and this chapter's and every later chapter's beats
		// forgotten, so the story replays from here (a jump ahead keeps the current flags)
		Set<String> snap = flagsAtStart.getOrDefault(n, n <= chapter ? Set.of() : null);
		if (snap != null) {
			flags.clear();
			flags.addAll(snap);
		}
		flagsAtStart.keySet().removeIf(k -> k > n);
		for (Beat b : compiled.beats) {
			if (b.chapter >= n) {
				fired.remove(b.id);
				lastEnd.remove(b.id);
			}
		}
		chapterFlags = new HashSet<>(flags);
		chapter = n;
		checkpoint(p);
	}

	public void advance() {
		startChapter(chapter + 1, false);
	}

	public void complete(String objective) {
		if (done.add(objective)) {
			for (ServerPlayer p : hunters()) {
				sync(p);
			}
		}
	}

	public boolean completed(String objective) {
		return done.contains(objective);
	}

	public void flag(String f) {
		if (flags.add(f)) {
			flagAt.put(f, now());
		}
	}

	public void unflag(String f) {
		flags.remove(f);
	}

	public boolean has(String f) {
		return flags.contains(f);
	}

	/** Ticks since a flag was raised (Long.MAX_VALUE if never). */
	public long since(String f) {
		Long t = flagAt.get(f);
		return t == null || !flags.contains(f) ? Long.MAX_VALUE : now() - t;
	}

	public int count(String key) {
		return counters.getOrDefault(key, 0);
	}

	public int inc(String key) {
		return counters.merge(key, 1, Integer::sum);
	}

	/** Sends the objective checklist to a hunter. */
	public void sync(ServerPlayer p) {
		Chapter c = compiled.chapter(chapter);
		List<String> objs = new ArrayList<>();
		if (c != null) {
			for (String o : c.objectives) {
				objs.add("deadline." + type.key() + ".obj." + o + "=" + (done.contains(o) ? 1 : 0));
			}
		}
		if (objs.isEmpty()) {
			// a chapter without objectives (the Casa: no missions on screen) clears the HUD checklist entirely
			Fx.checklist(p, "", "", chapter, objs);
			return;
		}
		Fx.checklist(p, type.langKey("place"), "deadline." + type.key() + ".ch." + chapter, chapter, objs);
	}

	// ------------------------------------------------------------------ markers
	public Vec3 at(String point) {
		return def.point(point).at(origin);
	}

	public float yaw(String point) {
		return def.point(point).yaw();
	}

	public BlockPos block(String point) {
		return BlockPos.containing(at(point));
	}

	public AABB area(String name) {
		return def.area(name).at(origin);
	}

	public boolean inside(Entity e, String area) {
		return area(area).contains(e.position());
	}

	/** True when the player looks at `target` within maxDeg degrees, closer than maxDist, with a clear line of sight. */
	public boolean looking(ServerPlayer p, Vec3 target, float maxDeg, double maxDist) {
		Vec3 eye = p.getEyePosition();
		Vec3 to = target.subtract(eye);
		double dist = to.length();
		if (dist > maxDist || dist < 0.01) {
			return dist < 0.01;
		}
		double cos = p.getViewVector(1.0F).dot(to.scale(1.0 / dist));
		if (cos < Math.cos(Math.toRadians(maxDeg))) {
			return false;
		}
		BlockHitResult hit = level.clip(new ClipContext(eye, target, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, p));
		return hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(eye) >= dist - 1.2;
	}

	// ------------------------------------------------------------------ world changes
	/** Switches a fixture group: light blocks go dark (air), lamps and candles swap to their unlit form. */
	public void lights(String group, boolean on) {
		for (int i = 0; i < def.group(group).size(); i++) {
			light(group, i, on);
		}
	}

	/** Lights one fixture of a group (index order as authored); "on" lights it even if it was authored unlit. */
	public void light(String group, int index, boolean on) {
		List<BlockPos> g = def.group(group);
		if (index < 0 || index >= g.size()) {
			return;
		}
		BlockPos rel = g.get(index);
		BlockState authored = authored(rel);
		if (authored == null) {
			return;
		}
		BlockState st = on ? Fixtures.lit(authored) : Fixtures.dark(authored);
		if (st != null) {
			level.setBlock(origin.offset(rel), st, FLAGS);
		}
	}

	/** The block state the site authored at a relative position (null outside the site). */
	public BlockState authored(BlockPos rel) {
		int x = rel.getX() - def.min.getX();
		int y = rel.getY() - def.min.getY();
		int z = rel.getZ() - def.min.getZ();
		if (x < 0 || y < 0 || z < 0 || x >= def.w || y >= def.h || z >= def.d) {
			return null;
		}
		int idx = def.data[(y * def.d + z) * def.w + x] & 0xFFFF;
		return idx == 0 ? null : def.palette[idx];
	}

	/** Opens or closes a door marker (both halves), with a slam when closing hard. */
	public void door(String name, boolean open, boolean slam) {
		BlockPos rel = def.doors.get(name);
		if (rel == null) {
			DeadLine.LOGGER.warn("Site {} has no door '{}'", def.key, name);
			return;
		}
		BlockPos pos = origin.offset(rel);
		BlockState lower = level.getBlockState(pos);
		List<BlockPos> leaves = new ArrayList<>(List.of(pos));
		if (lower.getBlock() instanceof DoorBlock) {
			// the other leaf of a double door: same door block and facing, opposite hinge, side by side
			for (net.minecraft.core.Direction d : net.minecraft.core.Direction.Plane.HORIZONTAL) {
				BlockState n = level.getBlockState(pos.relative(d));
				if (n.getBlock() == lower.getBlock() && n.getValue(DoorBlock.FACING) == lower.getValue(DoorBlock.FACING)
						&& n.getValue(DoorBlock.HINGE) != lower.getValue(DoorBlock.HINGE)
						&& n.getValue(DoorBlock.HALF) == DoubleBlockHalf.LOWER) {
					leaves.add(pos.relative(d));
				}
			}
		}
		for (BlockPos leaf : leaves) {
			for (BlockPos p : new BlockPos[] {leaf, leaf.above()}) {
				BlockState s = level.getBlockState(p);
				if (s.getBlock() instanceof DoorBlock && s.hasProperty(BlockStateProperties.OPEN)) {
					level.setBlock(p, s.setValue(BlockStateProperties.OPEN, open), FLAGS);
				}
			}
		}
		if (slam && !open) {
			sound(ModSounds.DOOR_SLAM, Vec3.atCenterOf(pos), 1.6F, 0.9F + level.random.nextFloat() * 0.15F);
		}
	}

	/** Locked doors rattle instead of opening by hand (see {@link Script#lock}). */
	public boolean locked(String door) {
		int[] l = compiled.locks.get(door);
		return l != null && chapter >= l[0] && chapter < l[1];
	}

	public boolean doorOpen(String name) {
		BlockPos rel = def.doors.get(name);
		if (rel == null) {
			return false;
		}
		BlockState s = level.getBlockState(origin.offset(rel));
		return s.hasProperty(BlockStateProperties.OPEN) && s.getValue(BlockStateProperties.OPEN)
				&& s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF) == DoubleBlockHalf.LOWER;
	}

	public void setBlock(BlockPos abs, BlockState s) {
		level.setBlock(abs, s, FLAGS);
	}

	// ------------------------------------------------------------------ sound
	/** A world sound (everyone nearby hears it); at == null plays it on every hunter. */
	public void sound(SoundEvent s, Vec3 at, float volume, float pitch) {
		if (s == null) {
			return;
		}
		if (at == null) {
			for (ServerPlayer p : hunters()) {
				level.playSound(null, p.getX(), p.getY(), p.getZ(), s, SoundSource.HOSTILE, volume, pitch);
			}
		} else {
			level.playSound(null, at.x, at.y, at.z, s, SoundSource.HOSTILE, volume, pitch);
		}
	}

	/**
	 * Nobody speaks in DEAD LINE (docs/design/casa_terror.md 0.3): the spoken lines were removed. Kept so old script
	 * steps compile; plays nothing and returns 0 ticks. Tell the story with phone messages
	 * ({@link com.deadline.phone.PhoneMessages}), the set and what the characters do.
	 */
	public int say(String lineId, Vec3 at) {
		return 0;
	}

	public SoundEvent soundById(String id) {
		return BuiltInRegistries.SOUND_EVENT.getValue(DeadLine.id(id));
	}

	// ------------------------------------------------------------------ actors
	public void actor(String name, Entity e) {
		Entity old = actors.put(name, e);
		if (old != null && old != e && !old.isRemoved()) {
			old.discard();
		}
	}

	public Entity actor(String name) {
		Entity e = actors.get(name);
		return e == null || e.isRemoved() ? null : e;
	}

	public void despawn(String name) {
		Entity e = actors.remove(name);
		if (e != null && !e.isRemoved()) {
			e.discard();
		}
	}

	/** Stops every sequence and removes every actor (case over or site restart). */
	public void end() {
		for (Exec e : execs) {
			e.cancel();
		}
		execs.clear();
		active.clear();
		for (Entity e : actors.values()) {
			if (e != null && !e.isRemoved()) {
				e.discard();
			}
		}
		actors.clear();
	}

	public AABB siteBox() {
		return new AABB(origin.offset(def.min)).expandTowards(def.w, def.h, def.d).inflate(16);
	}
}
