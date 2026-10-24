package com.deadline.horror.casa.events.polter;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Interactables;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 30 persianas (acts 3-5, intensity 3): every roller blind of the floor he is on comes crashing down at the same
 * moment. They stay down while he is on this floor (he can pull them up again by hand) and go back up once he has
 * left it.
 */
public class Persianas extends HorrorEvent {
	public Persianas() {
		super("persianas", Kind.POLTER);
		this.acts(3, 5).intensity(3).cooldown(260).weight(7);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String floor = Polter.floor(c.run, c.p.position());
		String group = floor.equals("pb") ? "persianas_pb" : floor.equals("1p") ? "persianas_1p" : null;
		if (group == null) {
			return false;
		}
		List<BlockPos> open = new ArrayList<>();
		for (BlockPos rel : c.run.def.group(group)) {
			BlockPos p = c.run.origin.offset(rel);
			String k = Polter.key(c.level().getBlockState(p));
			if ((k.startsWith("casa_ventana_inf_") || k.startsWith("casa_ventana_sup_")) && !k.endsWith("_cerrada")) {
				open.add(p);
			}
		}
		if (open.size() < 4) {
			return false;
		}
		c.put("floor", floor);
		c.put("cells", open);
		return true;
	}

	@Override
	public void start(Ctx c) {
		List<BlockPos> cells = c.get("cells");
		for (BlockPos p : cells) {
			Interactables.blind(c.run, p, true);
		}
		// the crash comes from every window: the three nearest, and the middle of the floor
		Vec3 me = c.p.position();
		cells.sort((a, b) -> Double.compare(Vec3.atCenterOf(a).distanceToSqr(me), Vec3.atCenterOf(b).distanceToSqr(me)));
		for (int i = 0; i < Math.min(3, cells.size()); i += 1) {
			Vec3 at = Vec3.atCenterOf(cells.get(i * Math.max(1, cells.size() / 3) % cells.size()));
			c.run.sound(ModSounds.POLTER_PERSIANAS, at, 1.4F, Polter.pitch(c, 0.9F, 1.1F));
			Polter.noise(c.run, at, 60F);
		}
		Fx.shake(c.p, 0.3F, 8);
	}

	@Override
	public boolean tick(Ctx c) {
		String floor = c.get("floor");
		return !floor.equals(Polter.floor(c.run, c.p.position())) && c.t > 40 || c.t > 20 * 75;
	}

	@Override
	public void stop(Ctx c) {
		List<BlockPos> cells = c.get("cells");
		if (cells != null) {
			for (BlockPos p : cells) {
				Interactables.blind(c.run, p, false);
			}
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 80;
	}
}
