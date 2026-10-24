package com.deadline.horror.casa;

import com.deadline.DeadLine;
import com.deadline.caseload.HunterData;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.horror.HorrorEvents;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.blood.Banera;
import com.deadline.horror.casa.blood.Diente;
import com.deadline.horror.casa.blood.Escritura;
import com.deadline.horror.casa.blood.GoteaTecho;
import com.deadline.horror.casa.blood.Huellas;
import com.deadline.horror.casa.blood.LinternaMuere;
import com.deadline.horror.casa.blood.MsgDesconocido;
import com.deadline.horror.casa.blood.MsgMarta;
import com.deadline.horror.casa.blood.Pisadas;
import com.deadline.horror.casa.lore.LoreDocs;
import com.deadline.horror.casa.lore.LorePayload;
import com.deadline.item.FlashlightItem;
import com.deadline.item.ItemUtil;
import com.deadline.registry.ModAttachments;
import com.deadline.registry.ModItems;
import net.fabricmc.fabric.api.event.Event;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * "Sangre y cuerpo" and "Celular" of the Casa catalogue (docs/design/casa_terror.md 5, entries 46-54), the blood
 * decals (6.5, {@link BloodDecals}) and the lore documents (2, Act 3, {@link LoreDocs}). Call {@link #register()} once
 * from the mod initializer. It registers the events, the lore payload, and two use hooks in a phase that runs BEFORE
 * every default-phase listener (the director, the hiding places, the interactables), so the order of the register
 * calls in DeadLine does not matter:
 * <ul>
 *   <li>use block: which drawer he opens while 'diente' waits (noted, passed on); a lore document (kit block or
 *   laid-out prop: taken);</li>
 *   <li>use item: the flashlight clicked while 'linterna_muere' holds it dead.</li>
 * </ul>
 * Everything else passes through untouched.
 */
public final class BloodEvents {
	/** Listener phase of the hooks (ordered before Event.DEFAULT_PHASE). */
	private static final Identifier FIRST = DeadLine.id("blood_first");
	private static boolean done;

	private BloodEvents() {
	}

	public static void register() {
		if (done) {
			return;
		}
		done = true;
		PayloadTypeRegistry.playS2C().register(LorePayload.TYPE, LorePayload.CODEC);
		BloodDecals.init();

		UseBlockCallback.EVENT.addPhaseOrdering(FIRST, Event.DEFAULT_PHASE);
		UseBlockCallback.EVENT.register(FIRST, BloodEvents::onUseBlock);
		UseItemCallback.EVENT.addPhaseOrdering(FIRST, Event.DEFAULT_PHASE);
		UseItemCallback.EVENT.register(FIRST, BloodEvents::onUseItem);
		ServerTickEvents.END_SERVER_TICK.register(BloodEvents::tick);
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> forget(handler.getPlayer()));

		HorrorEvents.register("casa", new Escritura());       // 46
		HorrorEvents.register("casa", new Huellas());         // 47
		HorrorEvents.register("casa", new Pisadas());         // 48
		HorrorEvents.register("casa", new GoteaTecho());      // 49
		HorrorEvents.register("casa", new Banera());          // 50
		HorrorEvents.register("casa", new Diente());          // 51
		HorrorEvents.register("casa", new MsgMarta());        // 52
		HorrorEvents.register("casa", new MsgDesconocido());  // 53
		HorrorEvents.register("casa", new LinternaMuere());   // 54
	}

	/** The Casa run this hunter is working (without creating one), or null. */
	public static Run casaRun(ServerPlayer p) {
		HunterData d = ModAttachments.get(p);
		if (d.active == null || !"casa".equals(d.active.type.key())) {
			return null;
		}
		Run r = Director.get(d.active.type, d.active.site);
		return r != null && r.level == p.level() ? r : null;
	}

	private static InteractionResult onUseBlock(Player player, Level world, InteractionHand hand, BlockHitResult hit) {
		if (world.isClientSide()) {
			// the client takes the click on a document block too, so it does not go on to use the item in hand (the
			// flashlight would toggle); the server opens it
			return !player.isSpectator() && LoreDocs.KIT.containsKey(HouseQuery.key(world.getBlockState(hit.getBlockPos())))
					? InteractionResult.SUCCESS : InteractionResult.PASS;
		}
		if (!(player instanceof ServerPlayer sp) || sp.isSpectator()) {
			return InteractionResult.PASS;
		}
		Run r = casaRun(sp);
		if (r == null) {
			return InteractionResult.PASS;
		}
		BlockPos pos = hit.getBlockPos();
		BlockState st = world.getBlockState(pos);
		if (Diente.armed(sp) && Diente.isDrawer(r, pos, st)) {
			Diente.clicked(sp, r, pos);  // noted; the drawer itself opens as usual (the interactables)
		}
		String doc = LoreDocs.docAt(r, pos, st, hit.getLocation());
		if (doc != null) {
			if (hand == InteractionHand.MAIN_HAND) {
				LoreDocs.open(sp, r, doc, hit.getLocation());
				String m = r.markerAt(pos);
				if (m != null) {
					r.post("use:" + m);  // a marked prop: the script still hears the click the director would have posted
				}
			}
			return InteractionResult.SUCCESS;
		}
		return InteractionResult.PASS;
	}

	private static InteractionResult onUseItem(Player player, Level world, InteractionHand hand) {
		if (!(player instanceof ServerPlayer sp)) {
			return InteractionResult.PASS;
		}
		ItemStack st = sp.getItemInHand(hand);
		if (LinternaMuere.dead(sp) && st.is(ModItems.FLASHLIGHT)) {
			LinternaMuere.deadClick(sp, st);
			return InteractionResult.FAIL;
		}
		if (LoreDocs.justOpened(sp)) {
			// the same click that opened a paper lying on a prop: the item in hand is not used (the client already
			// guessed it was; a touched flashlight is sent back to it as it really is)
			if (st.is(ModItems.FLASHLIGHT)) {
				ItemUtil.setFlags(st, FlashlightItem.isOn(st), FlashlightItem.isUv(st), !ItemUtil.getFlag(st, 2));
			}
			return InteractionResult.FAIL;
		}
		return InteractionResult.PASS;
	}

	private static void tick(MinecraftServer server) {
		BloodDecals.tick(server);
		int t = server.getTickCount();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			Run r = casaRun(p);
			if (r == null) {
				continue;
			}
			if (t % 4 == 0) {
				Escritura.watch(r, p);
			}
			if (t % 40 == 0 && r.siteBox().contains(p.position())) {
				LoreDocs.ensure(r, p);
			}
		}
	}

	private static void forget(ServerPlayer p) {
		LinternaMuere.revive(p);
		Diente.forget(p);
		Escritura.forget(p);
		LoreDocs.forgetPlayer(p);
	}
}
