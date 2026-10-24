package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.FlyingProp;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.Vec3;

/**
 * 18 apagon_cuarto (acts 2-5, intensity 3): the room he is in goes dark for a few seconds. When the light comes back
 * something has moved: a chair, the rocking chair, the walker, the slippers, a toy, now a couple of blocks closer to
 * him and turned towards him. It goes back to its place once he is not looking (or has left).
 */
public class ApagonCuarto extends HorrorEvent {
	/** Loose things of the kit that can be somewhere else when the lights come back. */
	public static final Set<String> MOVABLE = Set.of("casa_silla_comedor", "casa_silla_cocina", "casa_silla_nena", "casa_silla_jorge",
			"casa_silla_gamer", "casa_mecedora", "casa_andador", "casa_pantuflas", "casa_zapatillas", "casa_pelota", "casa_mochila",
			"casa_juguetes", "casa_canasta_lana", "casa_tacho_basura", "casa_zapatitos", "casa_balde_secador");

	public ApagonCuarto() {
		super("apagon_cuarto", Kind.POLTER);
		this.acts(2, 5).intensity(3).cooldown(200).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String room = c.room();
		String g = Polter.roomLights(c.run, room);
		if (g == null || room.startsWith("pasillo") || !Polter.anyLit(c.run, g)) {
			return false;
		}
		CasaProps.sweep(c.run);
		List<BlockPos> things = Polter.kitIn(c.run, room, MOVABLE::contains);
		BlockPos feet = c.p.blockPosition();
		for (BlockPos t : things) {
			if (CasaProps.held(c.run, t) || t.distSqr(feet) < 4) {
				continue;
			}
			BlockPos dest = closer(c, t, feet);
			if (dest != null) {
				c.put("group", g);
				c.put("thing", t);
				c.put("dest", dest);
				return true;
			}
		}
		return false;
	}

	/** A free floor cell 1-2 blocks from the thing, closer to him (never his own cell). */
	private static BlockPos closer(Ctx c, BlockPos from, BlockPos feet) {
		BlockPos best = null;
		double bd = from.distSqr(feet);
		for (int dx = -2; dx <= 2; dx++) {
			for (int dz = -2; dz <= 2; dz++) {
				BlockPos q = from.offset(dx, 0, dz);
				if ((dx == 0 && dz == 0) || q.equals(feet) || q.distSqr(feet) < 2 || !c.level().getBlockState(q).isAir()
						|| !HouseQuery.standable(c.run, q) || CasaProps.held(c.run, q)) {
					continue;
				}
				if (!c.run.area(c.room()).contains(Vec3.atCenterOf(q))) {
					continue;
				}
				double d = q.distSqr(feet);
				if (d < bd) {
					bd = d;
					best = q.immutable();
				}
			}
		}
		return best;
	}

	@Override
	public void start(Ctx c) {
		String g = c.get("group");
		List<Integer> lit = new ArrayList<>();
		for (int i = 0; i < c.run.def.group(g).size(); i++) {
			if (Polter.lit(c.run, g, i)) {
				lit.add(i);
				c.run.light(g, i, false);
			}
		}
		c.put("lit", lit);
		c.put("back", 60 + c.rnd.nextInt(30));
		c.put("props", new ArrayList<FlyingProp>());
		c.run.sound(ModSounds.LUCES_FUERA, c.p.position().add(0, 2.0, 0), 0.6F, 1.1F);
		Polter.noise(c.run, c.p.position(), 15F);
	}

	@Override
	public boolean tick(Ctx c) {
		List<FlyingProp> props = c.get("props");
		int back = c.get("back");
		if (c.t == 14) {
			// in the dark: it is somewhere else now, turned to him
			BlockPos thing = c.get("thing");
			BlockPos dest = c.get("dest");
			FlyingProp f = FlyingProp.lift(c.run, thing);
			if (f != null) {
				Vec3 to = Vec3.atCenterOf(dest);
				Direction face = com.deadline.director.Props.towards(to, c.p.position());
				f.placeAt(to, Polter.yawRad(face));
				props.add(f);
				c.run.sound(ModSounds.SILLA_ARRASTRA, to, 0.35F, 0.7F);
			}
		}
		if (c.t == back) {
			String g = c.get("group");
			List<Integer> lit = c.get("lit");
			for (int i : lit) {
				c.run.light(g, i, true);
			}
			c.run.sound(ModSounds.POLTER_ZUMBIDO, c.p.position().add(0, 2.0, 0), 0.7F, 1.0F);
			lit.clear();
		}
		if (c.t <= back || props.isEmpty()) {
			return c.t > back;
		}
		FlyingProp f = props.get(0);
		Apparitions.Gaze gz = Apparitions.gaze(c);
		gz.update(f.seen(35F));
		boolean left = !c.run.area(roomOf(c, f)).contains(c.p.position());
		return (gz.lookedAway(60) || left || c.t > 20 * 50) && !f.seen(60F);
	}

	private static String roomOf(Ctx c, FlyingProp f) {
		String r = HouseQuery.roomAt(c.run, f.pos());
		return r != null ? r : "casa";
	}

	@Override
	public void stop(Ctx c) {
		String g = c.get("group");
		List<Integer> lit = c.get("lit");
		if (g != null && lit != null) {
			for (int i : lit) {
				c.run.light(g, i, true);
			}
		}
		FlyingProp.restoreAll(c.get("props"));
	}

	@Override
	public int maxTicks() {
		return 20 * 75;
	}
}
