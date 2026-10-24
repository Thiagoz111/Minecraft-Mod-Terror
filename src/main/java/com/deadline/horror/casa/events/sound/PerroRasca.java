package com.deadline.horror.casa.events.sound;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Polter;
import com.deadline.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * 10 perro_rasca (acts 2-5, intensity 2): something scratches at the door of the room he is in, from the other side,
 * low down, like a dog asking to come in. A whine. If he opens the door there is nothing in the hall.
 */
public class PerroRasca extends HorrorEvent {
	public PerroRasca() {
		super("perro_rasca", Kind.SOUND);
		this.acts(2, 5).intensity(2).cooldown(150).weight(9);
	}

	@Override
	public boolean canRun(Ctx c) {
		if (!Polter.canHaunt(c)) {
			return false;
		}
		String room = c.room();
		String door = Polter.roomDoor(c.run, room, c.p.position());
		if (door == null || !Polter.isDoor(c.run, door) || c.run.doorOpen(door)) {
			return false;
		}
		Vec3 out = outside(c, door, room, 1.8);
		if (out == null || out.distanceTo(c.p.position()) < 1.5 || out.distanceTo(c.p.position()) > 12) {
			return false;
		}
		c.put("door", door);
		c.put("at", out.add(0, -0.1, 0));
		return true;
	}

	/** A point just outside a room's door, `d` blocks from it, at the height of the door's lower block. */
	public static Vec3 outside(Ctx c, String door, String room, double d) {
		Vec3 dp = HouseQuery.doorPos(c.run, door);
		if (dp == null || room == null || !c.run.def.areas.containsKey(room)) {
			return null;
		}
		BlockState s = c.level().getBlockState(BlockPos.containing(dp));
		if (!(s.getBlock() instanceof DoorBlock)) {
			return null;
		}
		Direction f = s.getValue(DoorBlock.FACING);
		Vec3 n = new Vec3(f.getStepX(), 0, f.getStepZ());
		Vec3 centre = c.run.area(room).getCenter();
		double sign = dp.subtract(centre).dot(n) >= 0 ? 1 : -1;
		return dp.add(n.scale(sign * d));
	}

	@Override
	public void start(Ctx c) {
	}

	@Override
	public boolean tick(Ctx c) {
		String door = c.get("door");
		Vec3 at = c.get("at");
		if (c.run.doorOpen(door)) {
			return true;  // nothing there
		}
		if (c.t == 0 || c.t == 52) {
			c.run.sound(ModSounds.POLTER_RASGUNO_PUERTA, at, 1.0F, Polter.pitch(c, 0.9F, 1.05F));
			Polter.noise(c.run, at, 15F);
		}
		if (c.t == 100) {
			c.run.sound(ModSounds.CHORIPAN_WHINE, at, 0.7F, 0.75F);
		}
		return c.t >= 130;
	}

	@Override
	public int maxTicks() {
		return 20 * 10;
	}
}
