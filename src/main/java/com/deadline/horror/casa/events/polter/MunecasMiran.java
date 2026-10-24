package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.casa.DollShelf;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.Polter;
import com.deadline.sanity.SanityManager;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;

/**
 * 28 munecas_miran (acts 2-5, intensity 2): the porcelain dolls on Lucía's shelf have turned their heads towards him.
 * They only move while nobody looks at them (DollShelf, here never leaving the shelf); a porcelain click each time.
 * Back as they were once he has looked and gone.
 */
public class MunecasMiran extends HorrorEvent {
	public MunecasMiran() {
		super("munecas_miran", Kind.POLTER);
		this.acts(2, 5).intensity(2).cooldown(200).weight(8);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		List<BlockPos> g = c.run.def.group("estante_munecas");
		if (g.isEmpty()) {
			return false;
		}
		CasaProps.sweep(c.run);
		int full = 0;
		double x = 0, y = 0, z = 0;
		for (BlockPos rel : g) {
			BlockPos p = c.run.origin.offset(rel);
			String k = Polter.key(c.level().getBlockState(p));
			if (CasaProps.held(c.run, p)) {
				return false;
			}
			if (k.startsWith("casa_estante_munecas_") && !k.endsWith("vacio")) {
				full++;
			}
			x += p.getX() + 0.5;
			y += p.getY() + 1.0;
			z += p.getZ() + 0.5;
		}
		Vec3 mid = new Vec3(x / g.size(), y / g.size(), z / g.size());
		double d = Apparitions.dist(c, mid);
		if (full == 0 || d < 3.0 || d > 14.0 || Apparitions.sees(c, mid, 60F)) {
			return false;
		}
		c.put("mid", mid);
		return true;
	}

	@Override
	public void start(Ctx c) {
		// they turn while unseen and never hop down: the shelf's "advance" never comes
		DollShelf s = DollShelf.start(c.run, "estante_munecas").advanceEvery(Integer.MAX_VALUE / 4);
		c.put("shelf", s);
	}

	@Override
	public boolean tick(Ctx c) {
		DollShelf s = c.get("shelf");
		Vec3 mid = c.get("mid");
		if (s == null || !s.active()) {
			return true;
		}
		Apparitions.Gaze g = Apparitions.gaze(c);
		boolean was = g.ever;
		g.update(Apparitions.dist(c, mid) < 16 && Apparitions.sees(c, mid, 35F));
		if (!was && g.ever) {
			SanityManager.add(c.p, -3F);
		}
		return g.lookedAway(60) && !Apparitions.sees(c, mid, 70F) || !g.ever && c.t > 20 * 80;
	}

	@Override
	public void stop(Ctx c) {
		DollShelf s = c.get("shelf");
		if (s != null) {
			s.clear();
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 110;
	}
}
