package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.FlyingProp;
import com.deadline.horror.casa.Polter;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/**
 * 24 cuchillos (acts 4-6, intensity 5): the kitchen knives lift off their rack, hang in the air in a fan pointing at
 * him, trembling, and then fly at him one after another, and every one of them sinks into the wall right beside his
 * head (if he steps into one, it cuts: a little). They stay there, quivering, until he has gone.
 */
public class Cuchillos extends HorrorEvent {
	private static final int KNIVES = 6, RISE = 22, AIM = 48, EVERY = 9;
	private static final Vector3f PIVOT = new Vector3f(0.5F, 0.03F, 0.5F);

	public Cuchillos() {
		super("cuchillos", Kind.POLTER);
		this.acts(4, 6).intensity(5).cooldown(420).weight(6);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		BlockPos rack = rack(c);
		if (rack == null) {
			return false;
		}
		Vec3 rc = Vec3.atCenterOf(rack);
		double d = Apparitions.dist(c, rc);
		if (d < 2.5 || d > 9.0 || !Apparitions.clear(c.run, rc, c.p.getEyePosition(), c.p)) {
			return false;
		}
		c.put("rack", rack);
		return true;
	}

	private static BlockPos rack(Ctx c) {
		CasaProps.sweep(c.run);
		for (BlockPos rel : c.run.def.group("cuchillos")) {
			BlockPos p = c.run.origin.offset(rel);
			if (Polter.key(c.level().getBlockState(p)).equals("casa_cuchillos") && !CasaProps.held(c.run, p)) {
				return p;
			}
		}
		if (Apparitions.has(c.run, "cuchillos")) {
			for (BlockPos p : Polter.kitNear(c.run, c.run.at("cuchillos"), 2, 2, k -> k.equals("casa_cuchillos"))) {
				if (!CasaProps.held(c.run, p)) {
					return p;
				}
			}
		}
		return null;
	}

	@Override
	public void start(Ctx c) {
		BlockPos rack = c.get("rack");
		BlockState rs = c.level().getBlockState(rack);
		Direction f = Polter.facing(rs);
		Direction side = f.getClockWise();
		Vec3 base = Vec3.atBottomCenterOf(rack).add(-f.getStepX() * 0.3, 0.45, -f.getStepZ() * 0.3);
		BlockState knife = CasaProps.kitOr("casa_cuchillo", Blocks.TRIPWIRE_HOOK.defaultBlockState());
		List<FlyingProp> knives = new ArrayList<>();
		List<Vec3> from = new ArrayList<>();
		List<Vec3> slots = new ArrayList<>();
		List<String> actors = new ArrayList<>();
		Vec3 out = new Vec3(f.getStepX(), 0, f.getStepZ());
		for (int i = 0; i < KNIVES; i++) {
			double off = (i - 2.5) * 0.12;
			Vec3 p = base.add(side.getStepX() * off, 0, side.getStepZ() * off);
			FlyingProp k = FlyingProp.spawn(c.run, p, knife, 0F, PIVOT);
			if (k == null) {
				continue;
			}
			k.stick().gravity(0).drag(1.0).radius(0.08).damage(2.0F).loud(50F).hitSound(ModSounds.KNIFE_IMPACT);
			k.hold(p, p.add(0, -1, 0));
			knives.add(k);
			from.add(p);
			// the fan they hang in: a half circle 1.3 blocks out from the rack, a head higher
			double a = (i - 2.5) / 2.5 * 1.1;
			Vec3 lat = new Vec3(side.getStepX(), 0, side.getStepZ());
			slots.add(base.add(out.scale(0.9 + 0.4 * Math.cos(a))).add(lat.scale(Math.sin(a) * 1.2)).add(0, 0.55 + 0.1 * Math.cos(a * 2), 0));
			actors.add(k.actor());
		}
		if (Polter.key(rs).equals("casa_cuchillos") && !actors.isEmpty()) {
			CasaProps.swap(c.run, rack, CasaProps.kit("casa_cuchillos_vacio", rs), actors);
		}
		c.put("knives", knives);
		c.put("from", from);
		c.put("slots", slots);
		c.put("thrown", 0);
		c.run.sound(ModSounds.KNIFE_LIFT, base, 1.4F, 1.0F);
		Polter.noise(c.run, base, 30F);
	}

	@Override
	public boolean tick(Ctx c) {
		List<FlyingProp> knives = c.get("knives");
		List<Vec3> from = c.get("from");
		List<Vec3> slots = c.get("slots");
		int thrown = c.get("thrown");
		Vec3 eye = c.p.getEyePosition();
		for (int i = 0; i < knives.size(); i++) {
			FlyingProp k = knives.get(i);
			if (i < thrown) {
				if (k.moving()) {
					k.tick();
					if (!k.moving() && k.hit() == null) {
						Fx.shake(c.p, 0.3F, 5);  // it sank into the wall right beside his head
					}
				}
				continue;
			}
			if (c.t <= RISE) {
				double u = CasaProps.ease(c.t / (double) RISE);
				Vec3 p = from.get(i).lerp(slots.get(i), u).add(0, Math.sin(u * Math.PI) * 0.25, 0);
				if (c.t % 2 == 0) {
					k.hold(p, c.t < RISE / 2 ? p.add(0, -1, 0) : eye);
				}
			} else if (c.t % 2 == 0) {
				// trembling, every point on him
				Vec3 s = slots.get(i);
				double j = 0.015 + 0.01 * Math.min(1.0, (c.t - RISE) / 40.0);
				k.hold(s.add(c.rnd.nextGaussian() * j, c.rnd.nextGaussian() * j, c.rnd.nextGaussian() * j), eye);
			}
		}
		if (c.t >= AIM && thrown < knives.size() && (c.t - AIM) % EVERY == 0) {
			FlyingProp k = knives.get(thrown);
			Vec3 at = k.pos();
			// just past his head, left or right in turn, and on into the wall behind him
			Vec3 to = eye.subtract(at);
			Vec3 lat = new Vec3(-to.z, 0, to.x).normalize();
			double sideOff = (thrown % 2 == 0 ? 1 : -1) * (0.55 + c.rnd.nextDouble() * 0.3);
			Vec3 aim = eye.add(lat.scale(sideOff)).add(0, c.rnd.nextDouble() * 0.5 - 0.3, 0);
			k.launch(aim.subtract(at).normalize().scale(1.15));
			c.run.sound(ModSounds.KNIFE_WHOOSH, at, 1.3F, Polter.pitch(c, 0.9F, 1.1F));
			c.put("thrown", thrown + 1);
		}
		if (thrown >= knives.size()) {
			boolean moving = false;
			boolean seen = false;
			for (FlyingProp k : knives) {
				moving |= k.moving();
				seen |= k.seen(55F);
			}
			Apparitions.Gaze g = Apparitions.gaze(c);
			g.update(seen);
			return !moving && (g.lost > 80 || c.t > 20 * 45 && !seen);
		}
		return knives.isEmpty();
	}

	@Override
	public void stop(Ctx c) {
		FlyingProp.restoreAll(c.get("knives"));
		BlockPos rack = c.get("rack");
		if (rack != null) {
			CasaProps.settleAt(c.run, rack);
		}
	}

	@Override
	public int maxTicks() {
		return 20 * 75;
	}
}
