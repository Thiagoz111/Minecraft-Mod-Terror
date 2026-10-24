package com.deadline.horror.casa;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.horror.casa.lore.LoreDocs;
import com.deadline.site.SiteDef;
import com.mojang.math.Transformation;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.WeakHashMap;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix3f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Blood of the Casa (docs/design/casa_terror.md 6.5): flat decals made of item displays whose item model is a
 * two-sided textured quad (assets/deadline/items/sangre/*.json, painted by tools/art/sangre.py): splatters, pools that
 * grow, hand prints, bare footprints, runs and drips, and blood writing on the site's `writes` markers, one decal per
 * letter so the hand shakes. Nothing here changes a block of the house.
 *
 * <p>Blood is the one thing the events leave behind on purpose: every decal is tracked per {@link Run} and only goes
 * away with {@link #clear(Run)}, which the act script calls when the hunter leaves the case (CasaScript.onLeave). As a
 * safety net a run that the director no longer holds is cleared by itself, and a decal that loads from disk with no
 * live run behind it (a crash, a restart mid-case) is discarded the tick after it loads.
 *
 * <p>Model space of every decal: the texture lies in the XY plane, facing +Z, its top towards +Y, centred on the
 * entity; {@link #basis} turns it so its face looks along a surface normal.
 */
public final class BloodDecals {
	/** Tag of every blood/lore display (the orphan sweeper looks for it). */
	public static final String TAG = "deadline_blood";
	/** Decals one run may hold; past it the oldest go first. */
	private static final int MAX_PER_RUN = 700;
	/** Lifts a decal off its surface so it never z-fights the wall or the floor. */
	public static final double LIFT = 0.012;

	// texture/model ids (deadline:sangre/<name>)
	public static final String[] SPLATS = {"sangre/splat_0", "sangre/splat_1", "sangre/splat_2"};
	public static final String POOL = "sangre/charco";
	public static final String HAND_L = "sangre/mano_izq", HAND_R = "sangre/mano_der", HAND_DRAG = "sangre/mano_arrastre";
	public static final String FOOT_L = "sangre/pie_izq", FOOT_R = "sangre/pie_der";
	public static final String[] RUNS = {"sangre/chorreado_0", "sangre/chorreado_1"};
	public static final String CEILING = "sangre/mancha_techo";
	public static final String TUB = "sangre/banera", TUB_RING = "sangre/banera_aro";
	public static final String DENTURE = "sangre/dentadura";
	public static final String[] TEETH = {"sangre/diente_0", "sangre/diente_1", "sangre/diente_2"};

	private static final class State {
		final LinkedHashMap<UUID, Entity> live = new LinkedHashMap<>();
		final Set<String> written = new HashSet<>();
		final List<String> texts = new ArrayList<>();
	}

	private static final Map<Run, State> STATES = new WeakHashMap<>();
	/** Tagged entities that just loaded; the ones no live run claims are discarded on the next tick. */
	private static final List<Entity> LOADED = new ArrayList<>();
	private static boolean done;

	private BloodDecals() {
	}

	/** Hooks of the decal tracker (called once by {@link BloodEvents#register()}). */
	static void init() {
		if (done) {
			return;
		}
		done = true;
		ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
			if (entity.getTags().contains(TAG)) {
				LOADED.add(entity);
			}
		});
	}

	// ------------------------------------------------------------------ spawning
	/**
	 * A decal: model `model` (deadline:&lt;model&gt;) centred on `at`, its face looking along `normal`, the texture's top
	 * towards `up` (any vector not parallel to the normal), w x h blocks.
	 */
	public static Display.ItemDisplay spawn(Run r, String model, Vec3 at, Vec3 normal, Vec3 up, float w, float h) {
		Display.ItemDisplay d = EntityType.ITEM_DISPLAY.create(r.level, EntitySpawnReason.EVENT);
		if (d == null) {
			return null;
		}
		d.snapTo(at.x, at.y, at.z, 0F, 0F);
		d.setItemStack(stack(model));
		d.setTransformation(new Transformation(new Vector3f(), basis(normal, up), new Vector3f(w, h, 1F), new Quaternionf()));
		d.setPosRotInterpolationDuration(2);
		d.addTag(TAG);
		track(r, d);
		r.level.addFreshEntity(d);
		return d;
	}

	/** Flat on the floor (at.y = the floor surface), the texture's top pointing at yaw degrees (0 = south, like mobs). */
	public static Display.ItemDisplay floor(Run r, String model, Vec3 at, float yawDeg, float w, float h) {
		return spawn(r, model, at.add(0, LIFT, 0), new Vec3(0, 1, 0), dirOf(yawDeg), w, h);
	}

	/** On the underside of a ceiling (at.y = the ceiling surface). */
	public static Display.ItemDisplay ceiling(Run r, String model, Vec3 at, float yawDeg, float w, float h) {
		return spawn(r, model, at.add(0, -LIFT, 0), new Vec3(0, -1, 0), dirOf(yawDeg), w, h);
	}

	/** On a wall whose face looks towards `face` (at = a point of the wall surface), turned rollDeg about the normal. */
	public static Display.ItemDisplay wall(Run r, String model, Vec3 at, Direction face, float rollDeg, float w, float h) {
		Vec3 n = new Vec3(face.getStepX(), face.getStepY(), face.getStepZ());
		Vec3 up = roll(n, new Vec3(0, 1, 0), rollDeg);
		return spawn(r, model, at.add(n.scale(LIFT)), n, up, w, h);
	}

	/** An item model to show on a display (any item: only the model id matters). */
	public static ItemStack stack(String model) {
		ItemStack st = new ItemStack(Items.PAPER);
		st.set(DataComponents.ITEM_MODEL, DeadLine.id(model));
		return st;
	}

	/** Re-poses a decal (same orientation) to a new size, interpolated over `ticks` on the client (a pool growing). */
	public static void resize(Display.ItemDisplay d, Vec3 normal, Vec3 up, float w, float h, Vector3f offset, int ticks) {
		if (d == null || d.isRemoved()) {
			return;
		}
		d.setTransformationInterpolationDuration(Math.max(0, ticks));
		d.setTransformationInterpolationDelay(0);
		d.setTransformation(new Transformation(offset == null ? new Vector3f() : new Vector3f(offset), basis(normal, up),
				new Vector3f(w, h, 1F), new Quaternionf()));
	}

	/** Rotation taking model +Z to `normal` and model +Y to `up` (made perpendicular to the normal). */
	public static Quaternionf basis(Vec3 normal, Vec3 up) {
		Vec3 z = normal.normalize();
		Vec3 y = up.subtract(z.scale(up.dot(z)));
		if (y.lengthSqr() < 1.0E-6) {
			y = Math.abs(z.y) < 0.9 ? new Vec3(0, 1, 0) : new Vec3(0, 0, -1);
			y = y.subtract(z.scale(y.dot(z)));
		}
		y = y.normalize();
		Vec3 x = y.cross(z);
		Matrix3f m = new Matrix3f((float) x.x, (float) x.y, (float) x.z, (float) y.x, (float) y.y, (float) y.z, (float) z.x,
				(float) z.y, (float) z.z);
		return new Quaternionf().setFromNormalized(m);
	}

	/** `v` turned deg degrees about the axis `n` (Rodrigues, for v perpendicular-ish to n). */
	public static Vec3 roll(Vec3 n, Vec3 v, float deg) {
		double a = Math.toRadians(deg);
		Vec3 k = n.normalize();
		return v.scale(Math.cos(a)).add(k.cross(v).scale(Math.sin(a))).add(k.scale(k.dot(v) * (1 - Math.cos(a))));
	}

	/** Horizontal unit vector of a yaw (Minecraft convention: 0 = +Z south, 90 = -X west). */
	public static Vec3 dirOf(float yawDeg) {
		double a = Math.toRadians(yawDeg);
		return new Vec3(-Math.sin(a), 0, Math.cos(a));
	}

	public static String splat(RandomSource rnd) {
		return SPLATS[rnd.nextInt(SPLATS.length)];
	}

	/** A splatter on any surface: `face` is the way the surface looks (UP a floor, DOWN a ceiling, else a wall). */
	public static Display.ItemDisplay splatter(Run r, Vec3 at, Direction face, float size, RandomSource rnd) {
		float spin = rnd.nextFloat() * 360F;
		return switch (face) {
			case UP -> floor(r, splat(rnd), at, spin, size, size);
			case DOWN -> ceiling(r, splat(rnd), at, spin, size, size);
			default -> wall(r, splat(rnd), at, face, spin, size, size);
		};
	}

	/** A pool on the floor (at.y = the floor) that spreads to `size` blocks over `growTicks` (a tap, a drip, a body). */
	public static Display.ItemDisplay pool(Run r, Vec3 at, float size, int growTicks, RandomSource rnd) {
		float yaw = rnd.nextFloat() * 360F;
		Display.ItemDisplay d = floor(r, POOL, at, yaw, size * 0.06F, size * 0.06F);
		if (d != null) {
			GROW.add(new Grow(d, dirOf(yaw), size, Math.max(1, growTicks), r.now() + 2));
		}
		return d;
	}

	/** A pool waiting to start spreading (the growth must be a change after the spawn to be interpolated). */
	private record Grow(Display.ItemDisplay d, Vec3 up, float size, int ticks, long at) {
	}

	private static final List<Grow> GROW = new ArrayList<>();

	// ------------------------------------------------------------------ blood writing
	/** The writing markers the events write on (the special ones, cuaderno and the mirror, are not blood walls). */
	public static List<String> walls(Run r) {
		List<String> out = new ArrayList<>();
		for (String k : r.def.writes.keySet()) {
			if (k.startsWith("escritura_") || k.equals("lemaza")) {
				out.add(k);
			}
		}
		return out;
	}

	/** The middle of a write marker's text area, on the wall surface (null if the site lacks it). */
	public static Vec3 wallCenter(Run r, String marker) {
		SiteDef.Write w = r.def.writes.get(marker);
		if (w == null) {
			return null;
		}
		Direction f = w.facing();
		Vec3 c = Vec3.atCenterOf(r.origin.offset(w.pos()));
		return new Vec3(c.x - f.getStepX() * 0.5, r.origin.getY() + w.pos().getY() + 1.0, c.z - f.getStepZ() * 0.5);
	}

	public static boolean written(Run r, String marker) {
		State s = STATES.get(r);
		return s != null && s.written.contains(marker);
	}

	/** Texts already written in this run (most recent last). */
	public static List<String> texts(Run r) {
		State s = STATES.get(r);
		return s == null ? List.of() : List.copyOf(s.texts);
	}

	/**
	 * Writes `text` in blood on a write marker: one decal per letter (A-Z, Á É Í Ó Ú Ñ; others are skipped), finger
	 * painted, uneven, two lines when it does not fit the wall. Returns the letters, left to right.
	 */
	public static List<Display.ItemDisplay> write(Run r, String marker, String text, RandomSource rnd) {
		List<Display.ItemDisplay> out = new ArrayList<>();
		SiteDef.Write w = r.def.writes.get(marker);
		Vec3 center = wallCenter(r, marker);
		if (w == null || center == null || text == null || text.isBlank()) {
			return out;
		}
		Direction f = w.facing();
		Vec3 right = new Vec3(f.getStepZ(), 0, -f.getStepX());
		float h = 0.56F;
		float adv = 0.40F;
		float space = 0.30F;
		double limit = Math.max(1.2, w.width() * 0.94);
		List<String> lines = new ArrayList<>(List.of(text.trim()));
		if (width(text.trim(), adv, space) > limit && text.trim().contains(" ")) {
			// two lines, split at the space nearest the middle
			String t = text.trim();
			int best = -1;
			for (int i = 0; i < t.length(); i++) {
				if (t.charAt(i) == ' ' && (best < 0 || Math.abs(i - t.length() / 2) < Math.abs(best - t.length() / 2))) {
					best = i;
				}
			}
			lines = List.of(t.substring(0, best), t.substring(best + 1));
		}
		double lineGap = 0.72;
		double top = (lines.size() - 1) * lineGap / 2.0;
		for (int li = 0; li < lines.size(); li++) {
			String line = lines.get(li);
			double lw = width(line, adv, space);
			double scale = lw > limit ? limit / lw : 1.0;
			double slope = (rnd.nextFloat() - 0.5F) * 0.12;
			double x = -lw * scale / 2.0 + adv * scale / 2.0;
			double y = top - li * lineGap + (rnd.nextFloat() - 0.5F) * 0.06;
			for (int i = 0; i < line.length(); i++) {
				char ch = line.charAt(i);
				if (ch == ' ') {
					x += (space - adv) * scale + adv * scale;
					continue;
				}
				String model = letter(ch);
				if (model != null) {
					float k = (float) scale * (0.92F + rnd.nextFloat() * 0.18F);
					double dy = y + x * slope + (rnd.nextFloat() - 0.5F) * 0.05;
					Vec3 at = center.add(right.scale(x)).add(0, dy, 0);
					// tilted with the line (a positive roll turns it counter-clockwise as seen from the room)
					float rollDeg = (rnd.nextFloat() - 0.5F) * 13F + (float) Math.toDegrees(Math.atan(slope));
					Display.ItemDisplay d = wall(r, model, at, f, rollDeg, h * 0.82F * k, h * k);
					if (d != null) {
						out.add(d);
					}
				}
				x += adv * scale;
			}
		}
		State s = state(r);
		s.written.add(marker);
		s.texts.add(text);
		return out;
	}

	private static double width(String line, float adv, float space) {
		double wsum = 0;
		for (int i = 0; i < line.length(); i++) {
			wsum += line.charAt(i) == ' ' ? space : adv;
		}
		return wsum;
	}

	/** Model of one blood letter, or null for characters there is no letter for. */
	public static String letter(char c) {
		char u = Character.toUpperCase(c);
		return switch (u) {
			case 'Á' -> "sangre/letra_a_acento";
			case 'É' -> "sangre/letra_e_acento";
			case 'Í' -> "sangre/letra_i";
			case 'Ó' -> "sangre/letra_o";
			case 'Ú' -> "sangre/letra_u";
			case 'Ñ' -> "sangre/letra_n";
			default -> u >= 'A' && u <= 'Z' ? "sangre/letra_" + Character.toLowerCase(u) : null;
		};
	}

	// ------------------------------------------------------------------ tracking
	/** Keeps an entity (a decal, a tooth, a lore prop) until {@link #clear(Run)}; tag it with {@link #TAG} first. */
	public static void track(Run r, Entity e) {
		if (r == null || e == null) {
			return;
		}
		State s = state(r);
		s.live.put(e.getUUID(), e);
		while (s.live.size() > MAX_PER_RUN) {
			Iterator<Map.Entry<UUID, Entity>> it = s.live.entrySet().iterator();
			Entity old = it.next().getValue();
			it.remove();
			if (old != null && !old.isRemoved()) {
				old.discard();
			}
		}
	}

	/** Removes one tracked entity now. */
	public static void remove(Run r, Entity e) {
		if (e == null) {
			return;
		}
		State s = STATES.get(r);
		if (s != null) {
			s.live.remove(e.getUUID());
		}
		if (!e.isRemoved()) {
			e.discard();
		}
	}

	public static int count(Run r) {
		State s = STATES.get(r);
		return s == null ? 0 : s.live.size();
	}

	/**
	 * Washes the house: every decal, tooth and lore prop of the run goes away and the lore documents forget where they
	 * were. The act script calls it when the hunter leaves the case (CasaScript.onLeave). Safe to call twice.
	 */
	public static void clear(Run r) {
		if (r == null) {
			return;
		}
		State s = STATES.remove(r);
		if (s != null) {
			for (Entity e : s.live.values()) {
				if (e != null && !e.isRemoved()) {
					e.discard();
				}
			}
			s.live.clear();
		}
		LoreDocs.forget(r);
	}

	private static State state(Run r) {
		return STATES.computeIfAbsent(r, k -> new State());
	}

	private static boolean claimed(Entity e) {
		for (State s : STATES.values()) {
			if (s.live.containsKey(e.getUUID())) {
				s.live.put(e.getUUID(), e);  // the same decal reloaded with its chunk: keep it, as this new instance
				return true;
			}
		}
		return false;
	}

	/** Server tick (from {@link BloodEvents}): orphans out, and the blood of runs that ended washed away. */
	static void tick(MinecraftServer server) {
		if (!GROW.isEmpty()) {
			for (Iterator<Grow> it = GROW.iterator(); it.hasNext();) {
				Grow g = it.next();
				if (g.d().isRemoved()) {
					it.remove();
				} else if (g.d().level().getGameTime() >= g.at()) {
					resize(g.d(), new Vec3(0, 1, 0), g.up(), g.size(), g.size(), null, g.ticks());
					it.remove();
				}
			}
		}
		if (!LOADED.isEmpty()) {
			List<Entity> now = new ArrayList<>(LOADED);
			LOADED.clear();
			for (Entity e : now) {
				if (!e.isRemoved() && !claimed(e)) {
					e.discard();
				}
			}
		}
		if (server.getTickCount() % 100 == 0 && !STATES.isEmpty()) {
			for (Run r : new ArrayList<>(STATES.keySet())) {
				if (r != null && Director.get(r.type, r.site) != r) {
					clear(r);
				}
			}
		}
	}

	/** A block position on the floor under a point (feet block) with the height of its surface. */
	public static Vec3 onFloor(Run r, Vec3 at) {
		BlockPos feet = BlockPos.containing(at.x, at.y + 0.2, at.z);
		return new Vec3(at.x, Apparitions.floorY(r, feet), at.z);
	}
}
