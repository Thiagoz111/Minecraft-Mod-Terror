package com.deadline.horror.casa;

import com.deadline.DeadLine;
import com.deadline.casa.CasaProps;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The things of the Casa that answer a right click (docs/design/casa_terror.md 6.3), on the kit blocks of the
 * casona: drawers (random contents: nothing, a photo, a broken rosary, teeth, a letter), the fridge (its light and
 * what is inside), the TV (on, off, static), the Nona's radio (static with a lullaby hummed inside it), the taps
 * (water; from act 4 sometimes blood), the light switches (the lights of the room; from act 4 they sometimes ignore you
 * or come back on by themselves), the rocking chair, Lucía's music box, the landline, the Singer, the blinds, and the
 * breaker panel of the laundry, which after the blackout brings the lights back for 40-90 s. During event 2
 * 'tres_golpes' a click on a wall within reach is a knock (and the wall answers).
 *
 * <p>The callback is registered before the director's (see DeadLine.onInitialize) so these clicks reach it; when it
 * handles a click on a marked block it posts the director's "use:&lt;marker&gt;" itself. Wardrobes, beds and other hiding
 * places belong to the hunt (HideSpots, registered first); doors to the director. Changes the hunter makes that would
 * outlive the moment (a blind pulled down, the TV left on) are remembered and undone by {@link #clear} when the case is
 * left; everything else undoes itself.
 */
public final class Interactables {
	/** Drawer contents (lang keys deadline.casa.cajon.&lt;kind&gt;; the run gets "cajon:&lt;kind&gt;"). */
	public static final String NADA = "nada", FOTO = "foto", ROSARIO = "rosario", DIENTES = "dientes", CARTA = "carta";
	private static final Map<Run, State> STATES = new WeakHashMap<>();
	private static boolean done;

	/** Something that animates for a while and undoes itself. */
	interface Anim {
		/** True when finished (and undone). */
		boolean tick(Run r);

		/** Undo now (the case is left). */
		void end(Run r);

		default BlockPos at() {
			return null;
		}
	}

	private static final class State {
		final List<Anim> anims = new ArrayList<>();
		final Map<Long, String> contents = new HashMap<>();
		final Map<BlockPos, BlockState> kept = new HashMap<>();
		final Map<BlockPos, Long> lastUse = new HashMap<>();
		final List<long[]> later = new ArrayList<>();
		final List<List<String>> laterGroups = new ArrayList<>();
		String forcedDrawer;
		long poweredUntil = -1;
		int poweredAct = -1;
		boolean flickered;
	}

	private Interactables() {
	}

	public static void init() {
		if (done) {
			return;
		}
		done = true;
		UseBlockCallback.EVENT.register(Interactables::onUse);
		ServerTickEvents.END_SERVER_TICK.register(Interactables::tick);
	}

	private static State state(Run r) {
		return STATES.computeIfAbsent(r, k -> new State());
	}

	// ------------------------------------------------------------------ public API
	/** The next drawer the hunter opens holds this (e.g. event 51 'diente': {@link #DIENTES}); null clears it. */
	public static void forceNextDrawer(Run r, String kind) {
		state(r).forcedDrawer = kind;
	}

	/**
	 * True while the house has power: always before the blackout of act 4, then only for the 40-90 s after the
	 * breaker panel was reset (switches, the TV and the radio do nothing without it).
	 */
	public static boolean powered(Run r) {
		int act = Polter.act(r);
		if (act < 4) {
			return true;
		}
		State s = STATES.get(r);
		return s != null && s.poweredAct == act && r.now() < s.poweredUntil;
	}

	/**
	 * Sets a block the hunter (or an event) changed so that it is put back when the case is left: the first change of
	 * a position remembers the original (CasaProps), going back to the original forgets it.
	 */
	public static void setKept(Run r, BlockPos pos, BlockState to) {
		if (to == null) {
			return;
		}
		State s = state(r);
		BlockPos p = pos.immutable();
		BlockState orig = s.kept.get(p);
		if (orig == null) {
			if (CasaProps.held(r, p)) {
				r.setBlock(p, to);  // another set piece holds it: it will put its own original back
				return;
			}
			orig = r.level.getBlockState(p);
			if (orig == to) {
				return;
			}
			s.kept.put(p, orig);
			CasaProps.remember(r, p, orig, List.of());
			r.setBlock(p, to);
			return;
		}
		if (to == orig) {
			s.kept.remove(p);
			CasaProps.settleAt(r, p);
		} else {
			r.setBlock(p, to);
		}
	}

	/** The state a kept block had before anyone touched it (the block itself when untouched). */
	public static BlockState original(Run r, BlockPos pos) {
		State s = STATES.get(r);
		BlockState o = s == null ? null : s.kept.get(pos);
		return o != null ? o : r.level.getBlockState(pos);
	}

	/** Puts back everything the interactables changed and stops what they animate (the case is left). */
	public static void clear(Run r) {
		State s = STATES.remove(r);
		if (s == null) {
			return;
		}
		for (Anim a : s.anims) {
			try {
				a.end(r);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Casa interactable failed to end", ex);
			}
		}
		for (BlockPos p : s.kept.keySet()) {
			CasaProps.settleAt(r, p);
		}
		Polter.stopSound(r, ModSounds.CASA_TV_STATIC);
		Polter.stopSound(r, ModSounds.POLTER_RADIO);
		Polter.stopSound(r, ModSounds.POLTER_CAJA_MUSICA);
	}

	// ------------------------------------------------------------------ the click
	static InteractionResult onUse(Player player, Level level, InteractionHand hand, BlockHitResult hit) {
		if (!(player instanceof ServerPlayer sp) || hand != InteractionHand.MAIN_HAND || sp.isSpectator() || sp.isShiftKeyDown()) {
			return InteractionResult.PASS;
		}
		Run r = Director.of(sp);
		if (r == null || r.level != level || !"casa".equals(r.type.key()) || Apparitions.hidden(sp)) {
			return InteractionResult.PASS;
		}
		BlockPos pos = hit.getBlockPos();
		boolean handled;
		try {
			handled = use(r, sp, pos, level.getBlockState(pos), hit);
		} catch (RuntimeException ex) {
			DeadLine.LOGGER.error("Casa interactable at {} failed", pos, ex);
			handled = false;
		}
		if (!handled) {
			return InteractionResult.PASS;
		}
		// the director would have posted this for a marked block: the script still hears the click
		String m = r.markerAt(pos);
		if (m == null) {
			m = r.markerAt(pos.above());
		}
		if (m != null && !r.def.doors.containsKey(m)) {
			r.post("use:" + m);
		}
		return InteractionResult.SUCCESS;
	}

	private static boolean use(Run r, ServerPlayer p, BlockPos pos, BlockState s, BlockHitResult hit) {
		State st = state(r);
		String k = Polter.key(s);
		double fy = hit.getLocation().y - pos.getY();
		Long last = st.lastUse.get(pos);
		boolean known = !k.isEmpty() && (Drawers.is(s) || Fridge.lowerOf(r, pos) != null || k.startsWith("casa_tele_vieja")
				|| Tap.is(s) || k.equals("casa_llave_luz") || Rocker.is(s) || k.equals("casa_estante_munecas_2")
				|| k.equals("casa_telefono") || k.equals("casa_maquina_coser") || blind(k) || k.startsWith("casa_tablero")
				|| k.equals("casa_estante_herramientas"));
		if (known && last != null && r.now() - last < 6) {
			return true;  // a double click: swallow it
		}
		if (known) {
			st.lastUse.put(pos.immutable(), r.now());
		}
		if (k.equals("casa_mesa_luz_nona") && fy > 0.72 || k.equals("casa_estante_herramientas")) {
			return radio(r, st, pos);
		}
		if (Drawers.is(s)) {
			return drawer(r, st, p, pos, s, fy);
		}
		BlockPos fridge = Fridge.lowerOf(r, pos);
		if (fridge != null) {
			return fridge(r, st, fridge);
		}
		if (k.startsWith("casa_tele_vieja")) {
			return tv(r, st, pos, s);
		}
		if (Tap.is(s)) {
			return tap(r, st, pos);
		}
		if (k.equals("casa_llave_luz")) {
			return lightSwitch(r, st, pos);
		}
		if (Rocker.is(s)) {
			Rocker k2 = Rocker.gentle(r, pos, 80);
			if (k2 != null) {
				st.anims.add(new RockAnim(k2));
				Polter.noise(r, Vec3.atCenterOf(pos), 12F);
			}
			return true;
		}
		if (k.equals("casa_estante_munecas_2")) {
			return musicBox(r, st, pos);
		}
		if (k.equals("casa_telefono")) {
			return phone(r, p, pos);
		}
		if (k.equals("casa_maquina_coser")) {
			return singer(r, st, pos);
		}
		if (blind(k)) {
			return blinds(r, pos, s);
		}
		if (k.startsWith("casa_tablero")) {
			return breaker(r, st, pos);
		}
		// event 2: knocking on the wall answers the knocks inside it
		if (Polter.running(r, "tres_golpes") && Polter.wall(r, pos) && hit.getLocation().distanceTo(p.getEyePosition()) < 2.7) {
			Vec3 at = hit.getLocation();
			r.sound(ModSounds.POLTER_GOLPE, at, 0.7F, 1.15F);
			Polter.noise(r, at, 20F);
			r.post(Polter.SIGNAL + "knock");
			r.vars.put("polter:knock_at", at);
			return true;
		}
		return false;
	}

	// ------------------------------------------------------------------ drawers
	private static boolean drawer(Run r, State st, ServerPlayer p, BlockPos pos, BlockState s, double fy) {
		int which = Drawers.at(s, fy);
		for (Anim a : st.anims) {
			if (a instanceof DrawerAnim d && d.pos.equals(pos) && d.which == which) {
				d.close(r);
				return true;
			}
		}
		List<String> actors = Drawers.open(r, pos, which);
		if (actors.isEmpty()) {
			return false;
		}
		String kind = content(r, st, pos, which);
		Drawers.content(r, actors, pos, which, stackFor(kind, r.level.getRandom()), r.level.getRandom().nextFloat() * 6.28F);
		Vec3 at = Drawers.inside(r, pos, which);
		r.sound(ModSounds.POLTER_CAJON, at, 0.8F, 1.0F + r.level.getRandom().nextFloat() * 0.15F);
		Polter.noise(r, at, 12F);
		p.displayClientMessage(Component.translatable("deadline.casa.cajon." + kind), true);
		r.post("cajon:" + kind);
		st.anims.add(new DrawerAnim(pos.immutable(), which, actors, r.now() + 20 * 4));
		return true;
	}

	private static String content(Run r, State st, BlockPos pos, int which) {
		long key = pos.asLong() * 7 + which;
		if (st.forcedDrawer != null) {
			String f = st.forcedDrawer;
			st.forcedDrawer = null;
			st.contents.put(key, f);
			return f;
		}
		String have = st.contents.get(key);
		if (have != null) {
			return have;
		}
		int act = Polter.act(r);
		int roll = r.level.getRandom().nextInt(100);
		String kind = roll < 40 ? NADA : roll < 55 ? FOTO : roll < 70 ? ROSARIO : roll < 90 ? CARTA : act >= 3 ? DIENTES : NADA;
		st.contents.put(key, kind);
		return kind;
	}

	private static ItemStack stackFor(String kind, RandomSource rnd) {
		return switch (kind) {
			case FOTO -> new ItemStack(Items.PAINTING);
			case ROSARIO -> new ItemStack(rnd.nextBoolean() ? ModItems.ROSARY : ModItems.INVERTED_ROSARY);
			case DIENTES -> new ItemStack(Items.BONE_MEAL);
			case CARTA -> new ItemStack(Items.PAPER);
			default -> ItemStack.EMPTY;
		};
	}

	private static final class DrawerAnim implements Anim {
		final BlockPos pos;
		final int which;
		final List<String> actors;
		final long until;

		DrawerAnim(BlockPos pos, int which, List<String> actors, long until) {
			this.pos = pos;
			this.which = which;
			this.actors = actors;
			this.until = until;
		}

		void close(Run r) {
			if (!actors.isEmpty()) {
				r.sound(ModSounds.POLTER_CAJON, Drawers.inside(r, pos, which), 0.7F, 0.8F);
				Drawers.close(r, actors);
			}
		}

		@Override
		public boolean tick(Run r) {
			if (r.now() >= until) {
				close(r);
			}
			return actors.isEmpty();
		}

		@Override
		public void end(Run r) {
			Drawers.close(r, actors);
		}

		@Override
		public BlockPos at() {
			return pos;
		}
	}

	// ------------------------------------------------------------------ the fridge
	private static boolean fridge(Run r, State st, BlockPos lower) {
		for (Anim a : st.anims) {
			if (a instanceof FridgeAnim f && f.fridge.lower.equals(lower)) {
				f.fridge.close();
				return true;
			}
		}
		if (Polter.running(r, "heladera")) {
			Polter.signal(r, "heladera");
			return true;
		}
		Fridge f = Fridge.open(r, lower);
		if (f == null) {
			return true;
		}
		int act = Polter.act(r);
		RandomSource rnd = r.level.getRandom();
		String bundle = null;
		if (act >= 4 && rnd.nextFloat() < 0.4F) {
			bundle = f.addBlock(Blocks.WHITE_WOOL.defaultBlockState(), 4.0, 9.4, 4.5, 11.5, 12.6, 11.0);
		} else {
			f.addItem(new ItemStack(Items.GLASS_BOTTLE), 4.5, 2.6, 8.0, 0.35F);
			f.addItem(new ItemStack(rnd.nextBoolean() ? Items.APPLE : Items.BREAD), 10.0, 9.4, 8.0, 0.3F);
			if (act >= 3 && rnd.nextFloat() < 0.3F) {
				f.addItem(new ItemStack(Items.BEEF), 8.0, 17.0, 8.0, 0.35F);
			}
		}
		Polter.noise(r, Vec3.atCenterOf(lower), 15F);
		st.anims.add(new FridgeAnim(f, bundle, r.now() + 20 * 5, act >= 4));
		return true;
	}

	private static final class FridgeAnim implements Anim {
		final Fridge fridge;
		final String bundle;
		final long until;
		final boolean flicker;
		Vec3 bundleAt;

		FridgeAnim(Fridge fridge, String bundle, long until, boolean flicker) {
			this.fridge = fridge;
			this.bundle = bundle;
			this.until = until;
			this.flicker = flicker;
		}

		@Override
		public boolean tick(Run r) {
			RandomSource rnd = r.level.getRandom();
			if (fridge.open()) {
				if (flicker) {
					fridge.light(rnd.nextFloat() < 0.25F ? 3 + rnd.nextInt(4) : 11);
				}
				if (bundle != null && r.actor(bundle) != null) {
					if (bundleAt == null) {
						bundleAt = r.actor(bundle).position();
					}
					if (rnd.nextFloat() < 0.12F) {
						CasaProps.move(r.actor(bundle), bundleAt.add((rnd.nextFloat() - 0.5) * 0.04, rnd.nextFloat() * 0.03, (rnd.nextFloat() - 0.5) * 0.04));
						if (rnd.nextFloat() < 0.4F) {
							r.sound(ModSounds.POLTER_PAPEL, bundleAt, 0.6F, 0.9F + rnd.nextFloat() * 0.2F);
						}
					}
				}
				if (r.now() >= until) {
					fridge.close();
				}
			}
			return fridge.tick();
		}

		@Override
		public void end(Run r) {
			fridge.end();
		}

		@Override
		public BlockPos at() {
			return fridge.lower;
		}
	}

	// ------------------------------------------------------------------ the TV
	private static boolean tv(Run r, State st, BlockPos pos, BlockState s) {
		String k = Polter.key(s);
		Vec3 at = Vec3.atCenterOf(pos).add(0, 0.3, 0);
		if (Polter.running(r, "tele_sola")) {
			Polter.signal(r, "tele");
			return true;
		}
		if (!k.equals("casa_tele_vieja_apagada")) {
			setKept(r, pos, CasaProps.kit("casa_tele_vieja_apagada", s));
			Polter.stopSound(r, ModSounds.CASA_TV_STATIC);
			r.sound(ModSounds.POLTER_TELE_OFF, at, 0.9F, 1.0F);
			return true;
		}
		boolean power = powered(r);
		int act = Polter.act(r);
		if (!power && r.level.getRandom().nextFloat() > 0.15F) {
			r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.6F, 0.7F);  // no power: the knob clicks, nothing
			return true;
		}
		// before the night the soap opera (no sound: the volume knob is broken); after, only static
		boolean stat = act >= 4 || !power;
		setKept(r, pos, CasaProps.kit(stat ? "casa_tele_vieja_estatica" : "casa_tele_vieja", s));
		r.sound(ModSounds.POLTER_TELE_ON, at, 1.0F, 1.0F);
		if (stat) {
			st.anims.add(new TvAnim(pos.immutable()));
			Polter.noise(r, at, 45F);
		}
		return true;
	}

	/** The static of a TV left on, looped while it stays on static. */
	static final class TvAnim implements Anim {
		final BlockPos pos;
		int t;

		TvAnim(BlockPos pos) {
			this.pos = pos;
		}

		@Override
		public boolean tick(Run r) {
			if (!Polter.key(r.level.getBlockState(pos)).equals("casa_tele_vieja_estatica")) {
				return true;
			}
			if (t++ % 160 == 0) {
				r.sound(ModSounds.CASA_TV_STATIC, Vec3.atCenterOf(pos).add(0, 0.3, 0), 1.2F, 1.0F);
			}
			return false;
		}

		@Override
		public void end(Run r) {
			Polter.stopSound(r, ModSounds.CASA_TV_STATIC);
		}

		@Override
		public BlockPos at() {
			return pos;
		}
	}

	// ------------------------------------------------------------------ the radio
	private static boolean radio(Run r, State st, BlockPos pos) {
		for (Iterator<Anim> it = st.anims.iterator(); it.hasNext(); ) {
			Anim a = it.next();
			if (a instanceof SoundAnim sa && sa.pos.equals(pos) && sa.sound == ModSounds.POLTER_RADIO) {
				a.end(r);
				it.remove();
				r.sound(ModSounds.POLTER_LLAVE_LUZ, Vec3.atCenterOf(pos), 0.6F, 0.8F);
				return true;
			}
		}
		Vec3 at = Vec3.atCenterOf(pos).add(0, 0.6, 0);
		r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.6F, 0.8F);
		// a battery radio: it plays without power. Static, and inside it, very far, a child humming a lullaby
		st.anims.add(new SoundAnim(pos.immutable(), ModSounds.POLTER_RADIO, at, 1.0F, 120, 240));
		Polter.noise(r, at, 30F);
		return true;
	}

	/** A sound played at a block every `every` ticks for `length` ticks (the radio, the music box), cut when it ends. */
	static final class SoundAnim implements Anim {
		final BlockPos pos;
		final net.minecraft.sounds.SoundEvent sound;
		final Vec3 at;
		final float volume;
		final int every;
		final int length;
		int t;

		SoundAnim(BlockPos pos, net.minecraft.sounds.SoundEvent sound, Vec3 at, float volume, int every, int length) {
			this.pos = pos;
			this.sound = sound;
			this.at = at;
			this.volume = volume;
			this.every = every;
			this.length = length;
		}

		@Override
		public boolean tick(Run r) {
			if (t % every == 0 && t < length) {
				r.sound(sound, at, volume, 1.0F);
			}
			if (++t >= length) {
				end(r);
				return true;
			}
			return false;
		}

		@Override
		public void end(Run r) {
			Polter.stopSound(r, sound);
		}

		@Override
		public BlockPos at() {
			return pos;
		}
	}

	// ------------------------------------------------------------------ taps
	private static boolean tap(Run r, State st, BlockPos pos) {
		Polter.signal(r, "canilla");
		for (Anim a : st.anims) {
			if (a instanceof TapAnim t && t.tap.pos.equals(pos)) {
				t.tap.stop();
				return true;
			}
		}
		if (Polter.running(r, "canilla_sangre")) {
			return true;
		}
		int act = Polter.act(r);
		boolean blood = act >= 4 && r.level.getRandom().nextFloat() < 0.5F;
		Tap t = Tap.open(r, pos, blood ? 30 + r.level.getRandom().nextInt(30) : -1, blood ? 20 * 7 : 20 * 4);
		if (t != null) {
			st.anims.add(new TapAnim(t));
			Polter.noise(r, t.spout(), 20F);
		}
		return true;
	}

	private record TapAnim(Tap tap) implements Anim {
		@Override
		public boolean tick(Run r) {
			return tap.tick();
		}

		@Override
		public void end(Run r) {
			tap.stop();
		}

		@Override
		public BlockPos at() {
			return tap.pos;
		}
	}

	// ------------------------------------------------------------------ light switches and the breaker
	private static boolean lightSwitch(Run r, State st, BlockPos pos) {
		Vec3 at = Vec3.atCenterOf(pos);
		r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.8F, 0.95F + r.level.getRandom().nextFloat() * 0.1F);
		List<String> groups = Polter.lightGroups(r, at);
		if (groups.isEmpty() || !powered(r)) {
			return true;  // the breaker is down: a dead click in the dark
		}
		boolean on = false;
		for (String g : groups) {
			on |= Polter.anyLit(r, g);
		}
		RandomSource rnd = r.level.getRandom();
		float roll = rnd.nextFloat();
		if (Polter.act(r) >= 4 && roll < 0.22F) {
			return true;  // it does not answer
		}
		for (String g : groups) {
			r.lights(g, !on);
		}
		if (on && Polter.act(r) >= 4 && roll > 0.75F) {
			// you turn it off... and a moment later it clicks back on by itself
			st.later.add(new long[] {r.now() + 30 + rnd.nextInt(50), pos.asLong()});
			st.laterGroups.add(groups);
		}
		return true;
	}

	private static boolean breaker(Run r, State st, BlockPos pos) {
		Vec3 at = Vec3.atCenterOf(pos);
		int act = Polter.act(r);
		if (act < 4) {
			r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.9F, 0.6F);  // the lights are on: the lever does not move
			return true;
		}
		if (powered(r)) {
			trip(r, st, true);
			return true;
		}
		RandomSource rnd = r.level.getRandom();
		r.sound(ModSounds.CASA_BREAKER_RESET, at, 1.2F, 1.0F);
		for (String g : Polter.allLights(r)) {
			r.lights(g, true);
		}
		if (r.def.groups.containsKey("tablero")) {
			r.lights("tablero", true);
		}
		st.poweredAct = act;
		st.poweredUntil = r.now() + 20 * (40 + rnd.nextInt(51));
		st.flickered = false;
		Polter.noise(r, at, 30F);
		return true;
	}

	/** The breaker trips again: every light goes out (with the trip and the hum dying). */
	private static void trip(Run r, State st, boolean byHand) {
		st.poweredUntil = -1;
		for (String g : Polter.allLights(r)) {
			r.lights(g, false);
		}
		if (r.def.groups.containsKey("tablero")) {
			r.lights("tablero", false);
		}
		if (r.def.points.containsKey("tablero")) {
			r.sound(ModSounds.CASA_BREAKER_TRIP, r.at("tablero"), 1.2F, byHand ? 1.0F : 0.9F);
			Polter.noise(r, r.at("tablero"), 35F);
		}
		if (!byHand) {
			r.sound(ModSounds.LUCES_FUERA, null, 0.7F, 0.8F);
		}
	}

	// ------------------------------------------------------------------ the music box, the phone, the Singer
	private static boolean musicBox(Run r, State st, BlockPos pos) {
		if (Polter.running(r, "caja_musica")) {
			Polter.signal(r, "caja");
			return true;
		}
		for (Iterator<Anim> it = st.anims.iterator(); it.hasNext(); ) {
			Anim a = it.next();
			if (a instanceof SoundAnim sa && sa.sound == ModSounds.POLTER_CAJA_MUSICA) {
				a.end(r);
				it.remove();
				return true;
			}
		}
		// wound up, it plays a few bars and the spring gives out
		Vec3 at = Vec3.atCenterOf(pos).add(0, -0.1, 0);
		st.anims.add(new SoundAnim(pos.immutable(), ModSounds.POLTER_CAJA_MUSICA, at, 0.7F, 1000, 20 * 6));
		return true;
	}

	private static boolean phone(Run r, ServerPlayer p, BlockPos pos) {
		Vec3 at = Vec3.atCenterOf(pos);
		if (Polter.running(r, "telefono_fijo")) {
			Polter.signal(r, "telefono");
			return true;
		}
		r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.6F, 0.5F);
		if (Polter.act(r) >= 4 && r.level.getRandom().nextFloat() < 0.35F) {
			Polter.heard(p, ModSounds.POLTER_TELEFONO_RESPIRA, Polter.ear(p, 1, 0.3), 0.8F);  // somebody is on the line
		} else {
			Polter.heard(p, ModSounds.TELEFONO_LINEA, Polter.ear(p, 1, 0.3), 0.7F);  // the line is dead
		}
		return true;
	}

	private static boolean singer(Run r, State st, BlockPos pos) {
		Vec3 at = Vec3.atCenterOf(pos).add(0, 0.4, 0);
		r.sound(ModSounds.POLTER_MAQUINA_COSER, at, 0.9F, 1.0F);
		Polter.noise(r, at, 25F);
		if (Polter.act(r) >= 4 && r.level.getRandom().nextFloat() < 0.3F) {
			// you let go of the treadle and it keeps going by itself, faster
			st.anims.add(new LaterSound(ModSounds.POLTER_MAQUINA_COSER, at, 1.1F, 1.35F, r.now() + 50));
		}
		return true;
	}

	/** One sound played once at a given tick (the Singer running on by itself). */
	private record LaterSound(net.minecraft.sounds.SoundEvent sound, Vec3 at, float volume, float pitch, long when) implements Anim {
		@Override
		public boolean tick(Run r) {
			if (r.now() >= when) {
				r.sound(sound, at, volume, pitch);
				Polter.noise(r, at, 30F);
				return true;
			}
			return false;
		}

		@Override
		public void end(Run r) {
		}
	}

	// ------------------------------------------------------------------ blinds
	private static boolean blind(String k) {
		return k.startsWith("casa_ventana_inf_") || k.startsWith("casa_ventana_sup_");
	}

	/** The cells of the 2x2 window (both columns, both rows) around a clicked window block. */
	public static List<BlockPos> window(Run r, BlockPos pos) {
		BlockState s = r.level.getBlockState(pos);
		Direction f = Polter.facing(s);
		Direction side = f.getClockWise();
		List<BlockPos> out = new ArrayList<>();
		for (int dy = -1; dy <= 1; dy++) {
			for (int dl = -1; dl <= 1; dl++) {
				BlockPos q = pos.above(dy).relative(side, dl);
				BlockState qs = r.level.getBlockState(q);
				if (blind(Polter.key(qs)) && Polter.facing(qs) == f) {
					out.add(q.immutable());
				}
			}
		}
		return out;
	}

	/** Pulls the blind of a window cell down (true) or up (false), keeping its facing and side. */
	public static void blind(Run r, BlockPos cell, boolean down) {
		BlockState s = r.level.getBlockState(cell);
		String k = Polter.key(s);
		if (!blind(k)) {
			return;
		}
		String base = k.endsWith("_cerrada") ? k.substring(0, k.length() - "_cerrada".length()) : k;
		BlockState to = CasaProps.kit(down ? base + "_cerrada" : base, s);
		if (to != null && to != s) {
			setKept(r, cell, to);
		}
	}

	public static boolean blindDown(BlockState s) {
		return Polter.key(s).endsWith("_cerrada");
	}

	private static boolean blinds(Run r, BlockPos pos, BlockState s) {
		boolean down = !blindDown(s);
		for (BlockPos c : window(r, pos)) {
			blind(r, c, down);
		}
		Vec3 at = Vec3.atCenterOf(pos);
		r.sound(ModSounds.POLTER_PERSIANA, at, 0.9F, down ? 1.0F : 0.9F);
		Polter.noise(r, at, 15F);
		return true;
	}

	// ------------------------------------------------------------------ the rocking chair
	private record RockAnim(Rocker rocker) implements Anim {
		@Override
		public boolean tick(Run r) {
			return rocker.tick();
		}

		@Override
		public void end(Run r) {
			rocker.stop();
		}

		@Override
		public BlockPos at() {
			return rocker.pos;
		}
	}

	// ------------------------------------------------------------------ ticking
	private static void tick(MinecraftServer server) {
		if (STATES.isEmpty()) {
			return;
		}
		Set<Run> seen = new HashSet<>();
		for (Map.Entry<Run, State> e : new ArrayList<>(STATES.entrySet())) {
			Run r = e.getKey();
			State st = e.getValue();
			if (r == null || !seen.add(r)) {
				continue;
			}
			if (Director.get(r.type, r.site) != r) {
				clear(r);  // the run is over: put back what is still out
				continue;
			}
			try {
				tickRun(r, st);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Casa interactables tick failed", ex);
			}
		}
	}

	private static void tickRun(Run r, State st) {
		for (Iterator<Anim> it = st.anims.iterator(); it.hasNext(); ) {
			Anim a = it.next();
			boolean end;
			try {
				end = a.tick(r);
			} catch (RuntimeException ex) {
				DeadLine.LOGGER.error("Casa interactable crashed", ex);
				a.end(r);
				end = true;
			}
			if (end) {
				it.remove();
			}
		}
		// switches that turn themselves back on
		for (int i = st.later.size() - 1; i >= 0; i--) {
			long[] l = st.later.get(i);
			if (r.now() >= l[0]) {
				List<String> groups = st.laterGroups.get(i);
				st.later.remove(i);
				st.laterGroups.remove(i);
				if (powered(r)) {
					Vec3 at = Vec3.atCenterOf(BlockPos.of(l[1]));
					r.sound(ModSounds.POLTER_LLAVE_LUZ, at, 0.9F, 0.9F);
					for (String g : groups) {
						r.lights(g, true);
					}
				}
			}
		}
		// the breaker: the lights it brought back flicker, then it trips again
		if (st.poweredUntil > 0) {
			int act = Polter.act(r);
			if (act != st.poweredAct) {
				st.poweredUntil = -1;  // a new act set the house its own way
			} else if (!st.flickered && r.now() >= st.poweredUntil - 30) {
				st.flickered = true;
				ServerPlayer p = r.star();
				if (p != null) {
					for (String g : Polter.lightGroups(r, p.position())) {
						r.lights(g, false);
						st.anims.add(new FlickerAnim(g, 4));
					}
					r.sound(ModSounds.POLTER_ZUMBIDO, p.position().add(0, 2.0, 0), 0.8F, 0.9F);
				}
			} else if (r.now() >= st.poweredUntil) {
				trip(r, st, false);
			}
		}
	}

	/** A group of lights off for a few ticks, then back on (if the house still has power). */
	private record FlickerAnim(String group, int ticks, int[] t) implements Anim {
		FlickerAnim(String group, int ticks) {
			this(group, ticks, new int[1]);
		}

		@Override
		public boolean tick(Run r) {
			if (++t[0] >= ticks) {
				if (powered(r)) {
					r.lights(group, true);
				}
				return true;
			}
			return false;
		}

		@Override
		public void end(Run r) {
		}
	}
}
