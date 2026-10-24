package com.deadline.horror.casa.events.polter;

import com.deadline.casa.CasaProps;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.casa.Apparitions;
import com.deadline.horror.casa.FlyingProp;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * 32 vuela_objeto (acts 3-6, intensity 3): a thing (a book, a glass, a jar) lifts off a shelf or a table at the edge
 * of his sight, hangs there trembling for a moment, and flies straight at his head. It hits (a little). The glass and
 * the jar shatter; the book lies where it fell until he is gone.
 */
public class VuelaObjeto extends HorrorEvent {
	private static final int LIFT = 10;

	public VuelaObjeto() {
		super("vuela_objeto", Kind.POLTER);
		this.acts(3, 6).intensity(3).cooldown(150).weight(9);
	}

	private static boolean surface(String k) {
		return k.startsWith("casa_estante") || k.startsWith("casa_mesa") || k.startsWith("casa_comoda") || k.startsWith("casa_escritorio")
				|| k.startsWith("casa_aparador") || k.startsWith("casa_mesita") || k.startsWith("casa_mesada") || k.startsWith("casa_alacena")
				|| k.equals("casa_botiquin") || k.startsWith("casa_baul");
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		Vec3 eye = c.p.getEyePosition();
		List<Vec3> ok = new ArrayList<>();
		for (BlockPos p : Polter.kitNear(c.run, c.p.position(), 7, 2, VuelaObjeto::surface)) {
			BlockPos above = p.above();
			if (!c.level().getBlockState(above).isAir()) {
				continue;
			}
			VoxelShape sh = c.level().getBlockState(p).getCollisionShape(c.level(), p);
			double top = sh.isEmpty() ? p.getY() + 0.75 : p.getY() + sh.max(Direction.Axis.Y);
			Vec3 at = new Vec3(p.getX() + 0.5, top + 0.18, p.getZ() + 0.5);
			double d = at.distanceTo(eye);
			if (d < 2.8 || d > 7.5 || !Apparitions.clear(c.run, at, eye, c.p)) {
				continue;
			}
			// at the edge of his sight: not in the middle of the screen, not behind him
			boolean centre = Apparitions.sees(c, at, 25F);
			boolean edge = Apparitions.sees(c, at, 75F);
			if (edge && !centre) {
				ok.add(at);
			}
		}
		if (ok.isEmpty()) {
			return false;
		}
		c.put("at", ok.get(c.rnd.nextInt(ok.size())));
		return true;
	}

	@Override
	public void start(Ctx c) {
		Vec3 at = c.get("at");
		int kind = c.rnd.nextInt(3);
		ItemStack stack = new ItemStack(kind == 0 ? Items.BOOK : Items.GLASS_BOTTLE);
		FlyingProp f = FlyingProp.spawnItem(c.run, at, stack, kind == 0 ? 0.55F : 0.45F);
		List<FlyingProp> props = new ArrayList<>();
		if (f != null) {
			f.damage(kind == 0 ? 2.0F : 1.5F).loud(40F).hitSound(ModSounds.POLTER_OBJETO).gravity(0.02);
			if (kind != 0) {
				f.breakable(ModSounds.POLTER_VIDRIO);
			}
			f.hold(at, null);
			props.add(f);
		}
		c.put("props", props);
		c.put("from", at);
	}

	@Override
	public boolean tick(Ctx c) {
		List<FlyingProp> props = c.get("props");
		if (props.isEmpty()) {
			return true;
		}
		FlyingProp f = props.get(0);
		Vec3 from = c.get("from");
		if (c.t < LIFT) {
			// it rises a hand's width, trembling
			double u = c.t / (double) LIFT;
			f.hold(from.add(c.rnd.nextGaussian() * 0.015, 0.2 * u, c.rnd.nextGaussian() * 0.015), null);
			return false;
		}
		if (c.t == LIFT) {
			Vec3 head = c.p.getEyePosition().add(0, -0.15, 0);
			f.spin(new Vec3(c.rnd.nextDouble() - 0.5, 0.3, c.rnd.nextDouble() - 0.5), 0.35F).throwAt(head, 0.62);
			c.run.sound(ModSounds.PLATE_WHOOSH, from, 0.9F, 1.3F);
		}
		if (f.moving()) {
			f.tick();
			return false;
		}
		if (f.broken()) {
			return c.t > LIFT + 20;
		}
		// the book lies there until he is not looking at it
		return !f.seen(60F) && c.t > LIFT + 60 || c.t > 20 * 45;
	}

	@Override
	public void stop(Ctx c) {
		FlyingProp.restoreAll(c.get("props"));
	}

	@Override
	public int maxTicks() {
		return 20 * 50;
	}
}
