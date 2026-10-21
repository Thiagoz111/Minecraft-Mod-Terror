package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Exec;
import com.deadline.director.Run;
import com.deadline.director.Step;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.List;
import net.fabricmc.fabric.api.event.Event;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;

/**
 * The Morales grill: a raw chorizo cooks in {@link #COOK_TICKS} (sizzle, smoke, a progress bar) while the hunter stays
 * inside the Nona's salt circle and within {@link #MAX_DIST} blocks of the fire; leaving cuts it. Clicking the grill
 * with a raw chorizo starts it ({@link #register}); scripts can call {@link #cook} directly.
 * Events: "grill:start", "grill:cocido" (the raw chorizo became a grilled one), "grill:cortado".
 */
public final class GrillSpot {
	/** Marker point of the cooking spot (inside the salt circle) and the area inside the circle. */
	public static final String POINT = "parrilla";
	public static final String AREA = "parrilla_circulo";
	public static final int COOK_TICKS = 100;
	public static final double MAX_DIST = 3.0;
	private static final String VAR = "grill:cook";
	private static final String KEY = "deadline.casa.grill";
	/** Kit grill: the empty grill shows the chorizo while it cooks. */
	private static final String EMPTY = "casa_parrilla_sin_carne", FULL = "casa_parrilla";

	private GrillSpot() {
	}

	/** One cooking in progress. */
	private static final class Cook {
		final BlockPos grill;
		final long started;
		boolean swapped;
		boolean over;

		Cook(BlockPos grill, long started) {
			this.grill = grill;
			this.started = started;
		}
	}

	/** Right click on the grill holding a raw chorizo (runs before the director's marker clicks). */
	public static void register() {
		Identifier early = DeadLine.id("grill");
		UseBlockCallback.EVENT.addPhaseOrdering(early, Event.DEFAULT_PHASE);
		UseBlockCallback.EVENT.register(early, (player, world, hand, hit) -> {
			if (!(player instanceof ServerPlayer sp) || !holdsRaw(sp)) {
				return InteractionResult.PASS;
			}
			Run r = Director.of(sp);
			if (r == null || !r.def.points.containsKey(POINT)) {
				return InteractionResult.PASS;
			}
			BlockPos grill = grill(r);
			BlockPos pos = hit.getBlockPos();
			if (Math.abs(pos.getX() - grill.getX()) > 2 || Math.abs(pos.getY() - grill.getY()) > 2 || Math.abs(pos.getZ() - grill.getZ()) > 2) {
				return InteractionResult.PASS;
			}
			if (!cooking(r) && cook(r, sp, grill) == null) {
				sp.displayClientMessage(Component.translatable(KEY + ".afuera"), true);
			}
			return InteractionResult.SUCCESS;
		});
	}

	/**
	 * Starts cooking one raw chorizo of the player on the grill. Returns the running sequence, or null when the
	 * player has no raw chorizo, is not by the grill, or the grill is already busy.
	 */
	public static Exec cook(Run run, ServerPlayer p, BlockPos grill) {
		if (cooking(run) || !holdsRaw(p) || !inside(run, p, grill)) {
			return null;
		}
		Cook c = new Cook(grill.immutable(), run.now());
		run.vars.put(VAR, c);
		if (blockId(run.level.getBlockState(grill)).equals(EMPTY)) {
			c.swapped = swap(run, grill, FULL);
		}
		run.post("grill:start");
		return run.start("grill", p, List.of(step(c)));
	}

	/** True while a chorizo is on the grill. */
	public static boolean cooking(Run run) {
		return run.vars.get(VAR) instanceof Cook c && !c.over && run.now() - c.started <= COOK_TICKS + 40;
	}

	/** Takes the chorizo off without cooking it (a scene cut). */
	public static void cancel(Run run) {
		if (run.vars.get(VAR) instanceof Cook c && !c.over) {
			c.over = true;
			if (c.swapped) {
				swap(run, c.grill, EMPTY);
			}
		}
	}

	private static Step step(Cook c) {
		return e -> {
			Run r = e.run;
			ServerPlayer p = e.player;
			if (c.over) {
				return true;
			}
			if (p == null || p.isRemoved() || !p.isAlive() || p.level() != r.level || !inside(r, p, c.grill) || !hasRaw(p)) {
				end(r, c);
				r.post("grill:cortado");
				if (p != null && !p.isRemoved()) {
					Fx.bigText(p, KEY + ".cortado", 60, -1F);
				}
				return true;
			}
			Vec3 top = Vec3.atCenterOf(c.grill).add(0, 0.6, 0);
			if (e.t % 2 == 0) {
				Fx.bigText(p, KEY, 10, Math.min(1F, (float) e.t / COOK_TICKS));
			}
			if (e.t % 40 == 0) {
				r.sound(ModSounds.GRILL_SIZZLE, top, 0.9F, 0.95F + r.level.random.nextFloat() * 0.1F);
			}
			if (e.t % 3 == 0) {
				r.level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, top.x, top.y + 0.2, top.z, 1, 0.15, 0.05, 0.15, 0.01);
				r.level.sendParticles(ParticleTypes.SMOKE, top.x, top.y, top.z, 3, 0.25, 0.05, 0.25, 0.01);
			}
			if (r.level.random.nextInt(5) == 0) {
				r.level.sendParticles(ParticleTypes.LAVA, top.x, top.y, top.z, 1, 0.2, 0.0, 0.2, 0.0);  // grease popping
			}
			if (e.t < COOK_TICKS) {
				return false;
			}
			takeRaw(p);
			ItemStack done = new ItemStack(CasaItems.CHORIZO_ASADO);
			if (p.getMainHandItem().isEmpty()) {
				p.setItemInHand(InteractionHand.MAIN_HAND, done);
			} else {
				CasaItems.give(p, done);
			}
			end(r, c);
			r.sound(ModSounds.GRILL_SIZZLE, top, 1.2F, 1.25F);
			r.level.sendParticles(ParticleTypes.FLAME, top.x, top.y, top.z, 12, 0.25, 0.1, 0.25, 0.03);
			Fx.bigText(p, KEY + ".listo", 40, 1F);
			r.post("grill:cocido");
			return true;
		};
	}

	private static void end(Run r, Cook c) {
		c.over = true;
		if (c.swapped) {
			swap(r, c.grill, EMPTY);
		}
	}

	// ------------------------------------------------------------------ the place
	/**
	 * The grill's fire: the kit grill block (or a campfire) nearest the "parrilla" point, else the point itself.
	 */
	public static BlockPos grill(Run r) {
		BlockPos c = r.block(POINT);
		BlockPos best = null;
		double bd = Double.MAX_VALUE;
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-4, -1, -4), c.offset(4, 2, 4))) {
			BlockState s = r.level.getBlockState(p);
			String id = blockId(s);
			boolean fire = s.getBlock() instanceof CampfireBlock || id.equals(FULL) || id.equals(EMPTY)
					|| id.equals("casa_parrilla_azul") || id.equals("casa_parrilla_apagada");
			if (fire && p.distSqr(c) < bd) {
				bd = p.distSqr(c);
				best = p.immutable();
			}
		}
		return best != null ? best : c;
	}

	/** Inside the salt circle (its area marker, when the site has one) and within reach of the fire. */
	public static boolean inside(Run r, ServerPlayer p, BlockPos grill) {
		double dx = p.getX() - (grill.getX() + 0.5);
		double dz = p.getZ() - (grill.getZ() + 0.5);
		if (dx * dx + dz * dz > MAX_DIST * MAX_DIST || Math.abs(p.getY() - grill.getY()) > 2.5) {
			return false;
		}
		return !r.def.areas.containsKey(AREA) || r.area(AREA).inflate(0.3).contains(p.position());
	}

	// ------------------------------------------------------------------ the chorizo
	public static boolean holdsRaw(ServerPlayer p) {
		return p.getMainHandItem().is(CasaItems.CHORIZO_CRUDO) || p.getOffhandItem().is(CasaItems.CHORIZO_CRUDO);
	}

	private static boolean hasRaw(ServerPlayer p) {
		return CasaItems.has(p, CasaItems.CHORIZO_CRUDO);
	}

	/** Removes one raw chorizo, from the hands first. */
	private static void takeRaw(ServerPlayer p) {
		for (InteractionHand h : InteractionHand.values()) {
			ItemStack s = p.getItemInHand(h);
			if (s.is(CasaItems.CHORIZO_CRUDO)) {
				s.shrink(1);
				return;
			}
		}
		Inventory inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			if (inv.getItem(i).is(CasaItems.CHORIZO_CRUDO)) {
				inv.getItem(i).shrink(1);
				return;
			}
		}
	}

	private static String blockId(BlockState s) {
		return BuiltInRegistries.BLOCK.getKey(s.getBlock()).getPath();
	}

	/** Swaps the grill block for another kit grill (with or without chorizos), keeping its facing. */
	private static boolean swap(Run r, BlockPos pos, String id) {
		Block b = BuiltInRegistries.BLOCK.getOptional(DeadLine.id(id)).orElse(null);
		if (b == null) {
			return false;
		}
		BlockState old = r.level.getBlockState(pos);
		BlockState st = b.defaultBlockState();
		if (old.hasProperty(BlockStateProperties.HORIZONTAL_FACING) && st.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
			st = st.setValue(BlockStateProperties.HORIZONTAL_FACING, old.getValue(BlockStateProperties.HORIZONTAL_FACING));
		}
		r.setBlock(pos, st);
		return true;
	}
}
