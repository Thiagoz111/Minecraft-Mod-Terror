package com.deadline.horror.casa.blood;

import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * 51 diente (acts 2-6, intensity 2): something small rattles inside a drawer of his room. The next drawer he opens
 * there holds human teeth and the Nona's dentures, bloody ({@link Teeth#spill}). If he opens none in 45 s, nothing.
 * <p>While it waits the event is "armed" for that hunter: BloodEvents' first-look use-block hook gives it the click on
 * a drawer before the interactables do ({@link #opened}).
 */
public class Diente extends HorrorEvent {
	/** Kit furniture with drawers (tools/sites/casa.py DRAWERS), in case the site has no `cajones` group. */
	private static final Set<String> KEYS = Set.of("casa_mesa_luz", "casa_mesa_luz_nona", "casa_comoda_izq", "casa_comoda_der",
			"casa_mesada_cajones", "casa_aparador_izq", "casa_aparador_der", "casa_mesita_auxiliar", "casa_escritorio_lucia",
			"casa_escritorio_lucia_apagada", "casa_mesa_comedor_extremo");
	private static final Map<UUID, Ctx> ARMED = new HashMap<>();

	public Diente() {
		super("diente", Kind.BLOOD);
		this.acts(2, 6).intensity(2).cooldown(240).weight(7);
	}

	/** True for a drawer piece of the casa kit (the `cajones` group of the site, or a drawer kit block). */
	public static boolean isDrawer(Run r, BlockPos pos, BlockState st) {
		return KEYS.contains(HouseQuery.key(st)) || r.def.group("cajones").contains(pos.subtract(r.origin));
	}

	/** Drawers of a room (absolute positions). */
	static List<BlockPos> drawers(Run r, String room) {
		List<BlockPos> out = new ArrayList<>();
		for (BlockPos rel : r.def.group("cajones")) {
			BlockPos pos = r.origin.offset(rel);
			if (room.equals(HouseQuery.roomAt(r, Vec3.atCenterOf(pos)))) {
				out.add(pos);
			}
		}
		if (out.isEmpty() && Apparitions.hasArea(r, room)) {
			out.addAll(HouseQuery.blocks(r, room, st -> KEYS.contains(HouseQuery.key(st))));
		}
		return out;
	}

	/** A hunter opened a drawer: if this event waits for him, it takes the click (true). */
	public static boolean opened(ServerPlayer p, Run r, BlockPos pos) {
		Ctx c = ARMED.get(p.getUUID());
		if (c == null || c.run != r || c.get("open") != null) {
			return false;
		}
		c.put("open", pos.immutable());
		return true;
	}

	public static boolean armed(ServerPlayer p) {
		return ARMED.containsKey(p.getUUID());
	}

	public static void forget(ServerPlayer p) {
		ARMED.remove(p.getUUID());
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c) || ARMED.containsKey(c.p.getUUID())) {
			return false;
		}
		String room = c.room();
		if (room == null) {
			return false;
		}
		List<BlockPos> near = new ArrayList<>();
		for (BlockPos pos : drawers(c.run, room)) {
			if (Apparitions.dist(c, Vec3.atCenterOf(pos)) < 7.0) {
				near.add(pos);
			}
		}
		if (near.isEmpty()) {
			return false;
		}
		c.put("lure", near.get(c.rnd.nextInt(near.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("lure") == null && !canRun(c)) {
			return;
		}
		ARMED.put(c.p.getUUID(), c);
		BlockPos lure = c.get("lure");
		Apparitions.sound(c, ModSounds.SANGRE_DIENTES, Vec3.atCenterOf(lure), 0.3F, 0.9F);
	}

	@Override
	public boolean tick(Ctx c) {
		BlockPos lure = c.get("lure");
		if (lure == null) {
			return true;
		}
		BlockPos open = c.get("open");
		if (open != null) {
			Integer at = c.get("openAt");
			if (at == null) {
				c.put("openAt", c.t);
				Vec3 mid = Vec3.atCenterOf(open);
				Apparitions.sound(c, ModSounds.SANGRE_CAJON, mid, 0.9F, 0.95F);
				Teeth.spill(c.run, open, c.p.getEyePosition(), true, c.rnd);
				Apparitions.sound(c, ModSounds.SANGRE_DIENTES, mid.add(0, 0.4, 0), 0.8F, 1.0F);
				Apparitions.noise(c, mid, 15F);
				SanityManager.add(c.p, -4F);
				return false;
			}
			return c.t - at > 10;
		}
		if (c.t == 20 * 14 && !Apparitions.hidden(c.p)) {
			Apparitions.sound(c, ModSounds.SANGRE_DIENTES, Vec3.atCenterOf(lure), 0.35F, 0.85F);  // again, in there
		}
		return c.t > 20 * 45;
	}

	@Override
	public void stop(Ctx c) {
		if (ARMED.get(c.p.getUUID()) == c) {
			ARMED.remove(c.p.getUUID());
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 50;
	}
}
