package com.deadline.horror.casa.blood;

import com.deadline.director.Run;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.BloodDecals;
import com.deadline.registry.ModSounds;
import com.deadline.sanity.SanityManager;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;

/**
 * 47 huellas (acts 3-6, intensity 3): bloody hand prints appear on a window of his room, one by one, from OUTSIDE --
 * a wet slap on the glass each time, faster and faster, climbing -- and the last hand drags itself down the pane.
 * Nothing is out there when he looks. The prints stay ({@link BloodDecals#clear}).
 */
public class Huellas extends HorrorEvent {
	public Huellas() {
		super("huellas", Kind.BLOOD);
		this.acts(3, 6).intensity(3).cooldown(180).weight(8);
	}

	/** A window: its lower block, the middle of its glass, the way out, the face towards the room, its lateral axis,
	 * its height (1 or 2 blocks). */
	record Win(BlockPos pos, Vec3 center, Vec3 out, Direction into, Vec3 side, double height) {
	}

	record Print(int t, Vec3 at, String model, float roll, float size) {
	}

	/** Window blocks of the house (the window groups of the site; only kit window blocks). */
	static Set<BlockPos> windows(Run r) {
		Set<BlockPos> out = new LinkedHashSet<>();
		for (String g : new String[] {"ventanas_1p", "persianas_pb", "ventanas_altillo", "persianas_1p"}) {
			for (BlockPos rel : r.def.group(g)) {
				out.add(r.origin.offset(rel));
			}
		}
		return out;
	}

	static boolean isWindow(BlockState st) {
		return HouseQuery.key(st).startsWith("casa_ventana");
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Apparitions.canScare(c)) {
			return false;
		}
		String room = c.room();
		if (room == null) {
			return false;
		}
		List<Win> ok = new ArrayList<>();
		for (BlockPos pos : windows(c.run)) {
			BlockState st = c.level().getBlockState(pos);
			if (!isWindow(st) || isWindow(c.level().getBlockState(pos.below()))) {
				continue;  // the lower block of each window only
			}
			Direction f = st.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? st.getValue(BlockStateProperties.HORIZONTAL_FACING)
					: Direction.NORTH;
			Vec3 n = new Vec3(f.getStepX(), 0, f.getStepZ());
			Vec3 mid = Vec3.atCenterOf(pos);
			String a = HouseQuery.roomAt(c.run, mid.add(n));
			String b = HouseQuery.roomAt(c.run, mid.subtract(n));
			Vec3 out;
			Direction into;
			if (room.equals(a) && !room.equals(b)) {
				out = n.scale(-1);
				into = f;
			} else if (room.equals(b) && !room.equals(a)) {
				out = n;
				into = f.getOpposite();
			} else {
				continue;
			}
			boolean tall = isWindow(c.level().getBlockState(pos.above()));
			Vec3 center = mid.add(0, tall ? 0.5 : 0.0, 0);
			double d = Apparitions.dist(c, center);
			if (d < 2.0 || d > 10.0 || !Apparitions.sees(c, center, 55F)) {
				continue;
			}
			ok.add(new Win(pos, center, out, into, new Vec3(out.z, 0, -out.x), tall ? 2.0 : 1.0));
		}
		if (ok.isEmpty()) {
			return false;
		}
		c.put("win", ok.get(c.rnd.nextInt(ok.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("win") == null && !canRun(c)) {
			return;  // fired by hand with no window in sight
		}
		Win w = c.get("win");
		// the hands come up the glass from below, left, right, faster each time
		int n = c.between(6, 9);
		double half = w.height() * 0.5;
		double lo = -half + 0.32;
		double hi = half - 0.22;
		List<Print> plan = new ArrayList<>();
		int t = 8;
		double u = (c.rnd.nextFloat() - 0.5F) * 0.3;
		for (int i = 0; i < n; i++) {
			double v = lo + (hi - lo) * (i / (double) Math.max(1, n - 1)) + (c.rnd.nextFloat() - 0.5F) * 0.18;
			u = Math.max(-0.33, Math.min(0.33, u + (i % 2 == 0 ? 0.22 : -0.22) + (c.rnd.nextFloat() - 0.5F) * 0.16));
			Vec3 at = w.center().add(w.out().scale(0.13)).add(w.side().scale(u)).add(0, v, 0);
			boolean left = (i % 2 == 0) == (u < 0);
			float roll = (left ? 14F : -14F) + (c.rnd.nextFloat() - 0.5F) * 22F;
			plan.add(new Print(t, at, left ? BloodDecals.HAND_L : BloodDecals.HAND_R, roll, 0.36F + c.rnd.nextFloat() * 0.08F));
			t += Math.max(7, 20 - i * 2) + c.rnd.nextInt(4);
		}
		c.put("plan", plan);
		c.put("end", t);
	}

	@Override
	public boolean tick(Ctx c) {
		if (Apparitions.hidden(c.p)) {
			return true;  // he hid: the hands stop (what is there stays)
		}
		Win w = c.get("win");
		List<Print> plan = c.get("plan");
		if (w == null || plan == null) {
			return true;
		}
		int end = c.get("end");
		Direction into = w.into();
		for (int i = 0; i < plan.size(); i++) {
			Print p = plan.get(i);
			if (p.t() != c.t) {
				continue;
			}
			BloodDecals.wall(c.run, p.model(), p.at(), into, p.roll(), p.size(), p.size() * 1.2F);
			Vec3 outside = p.at().add(w.out().scale(0.4));
			Apparitions.sound(c, ModSounds.SANGRE_MANO_VIDRIO, outside, 1.0F, Apparitions.pitch(c, 0.85F, 1.1F));
			Apparitions.noise(c, outside, 18F);
			if (i == 0 && Apparitions.sees(c, w.center(), 50F)) {
				SanityManager.add(c.p, -3F);
			}
		}
		if (c.t == end + 6 && !plan.isEmpty()) {
			// the last hand slides down the glass, slowly
			Print last = plan.get(plan.size() - 1);
			Vec3 at = last.at().add(0, -0.34, 0);
			BloodDecals.wall(c.run, BloodDecals.HAND_DRAG, at, into, last.roll() * 0.3F, last.size() * 0.95F, 0.95F);
			Apparitions.sound(c, ModSounds.SANGRE_ARRASTRE, at.add(w.out().scale(0.4)), 0.9F, 0.9F);
		}
		return c.t > end + 40;
	}

	@Override
	public int maxTicks() {
		return 20 * 20;
	}
}
