package com.deadline.casa;

import com.deadline.DeadLine;
import com.deadline.director.Director;
import com.deadline.director.Run;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Casa Morales items and their thrown entities: the choripán chain (raw chorizo, grilled chorizo, bread, choripán,
 * blessed choripán), the Nona's cookie tin with what is really inside, and her slipper.
 */
public final class CasaItems {
	private static final List<Item> TAB = new ArrayList<>();

	public static final EntityType<ChoripanBenditoEntity> CHORIPAN_BENDITO_ENTITY = entity("choripan_bendito",
			EntityType.Builder.<ChoripanBenditoEntity>of(ChoripanBenditoEntity::new, MobCategory.MISC).sized(0.3F, 0.3F).clientTrackingRange(6).updateInterval(5));
	public static final EntityType<ChancletaEntity> CHANCLETA_ENTITY = entity("chancleta",
			EntityType.Builder.<ChancletaEntity>of(ChancletaEntity::new, MobCategory.MISC).sized(0.4F, 0.3F).clientTrackingRange(8).updateInterval(1));

	public static final Item CHORIZO_CRUDO = register("chorizo_crudo", p -> new HintItem(p, "chorizo_crudo"), new Item.Properties().stacksTo(16));
	public static final Item CHORIZO_ASADO = register("chorizo_asado", p -> new HintItem(p, "chorizo_asado"), new Item.Properties().stacksTo(16));
	public static final Item PAN = register("pan", p -> new HintItem(p, "pan"), new Item.Properties().stacksTo(16));
	public static final Item CHORIPAN = register("choripan", p -> new HintItem(p, "choripan"), new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON));
	public static final Item CHORIPAN_BENDITO = register("choripan_bendito", ChoripanBenditoItem::new, new Item.Properties().stacksTo(16)
			.rarity(Rarity.RARE).component(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true).component(DataComponents.LORE, lore("choripan_bendito")));
	public static final Item LATA_GALLETITAS = register("lata_galletitas", LataItem::new, new Item.Properties().stacksTo(1)
			.component(DataComponents.LORE, lore("lata_galletitas")));
	public static final Item HILO_BENDITO = register("hilo_bendito", Item::new, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)
			.component(DataComponents.LORE, lore("hilo_bendito")));
	public static final Item AGUJA = register("aguja", Item::new, new Item.Properties().stacksTo(1).component(DataComponents.LORE, lore("aguja")));
	public static final Item FOTO_1960 = register("foto_1960", FotoItem::new, new Item.Properties().stacksTo(1)
			.component(DataComponents.LORE, new ItemLore(List.of(Component.translatable("deadline.text.casa.foto")))));
	/** The Nona's slipper: trophy of the case (thrown, it comes back and stuns the first haunt it touches). */
	public static final Item CHANCLETA = register("chancleta", ChancletaItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)
			.component(DataComponents.LORE, lore("chancleta")));

	/** Ticks before the slipper can be thrown again (it is a once-in-a-while trick, not a weapon). */
	public static final int CHANCLETA_COOLDOWN = 1200;

	private CasaItems() {
	}

	private static <T extends Item> T register(String name, Function<Item.Properties, T> factory, Item.Properties props) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, DeadLine.id(name));
		T item = factory.apply(props.setId(key));
		Registry.register(BuiltInRegistries.ITEM, key, item);
		TAB.add(item);
		return item;
	}

	private static <T extends Entity> EntityType<T> entity(String name, EntityType.Builder<T> builder) {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, DeadLine.id(name));
		return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
	}

	private static ItemLore lore(String key) {
		return new ItemLore(List.of(Component.translatable("deadline.lore.casa." + key)));
	}

	/** Registers the items, the thrown entities and the grill (one call from DeadLine.onInitialize). */
	public static void init() {
		ItemGroupEvents.modifyEntriesEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, DeadLine.id("deadline"))).register(entries -> {
			for (Item item : TAB) {
				entries.accept(item);
			}
		});
		GrillSpot.register();
	}

	// ------------------------------------------------------------------ helpers for the other casa packages
	/** Raw or grilled chorizo, a choripán (blessed or not): what makes the demon dog sit and beg. */
	public static boolean isTreat(ItemStack s) {
		return s.is(CHORIZO_CRUDO) || s.is(CHORIZO_ASADO) || s.is(CHORIPAN) || s.is(CHORIPAN_BENDITO);
	}

	public static boolean holdsTreat(LivingEntity e) {
		return isTreat(e.getMainHandItem()) || isTreat(e.getOffhandItem());
	}

	/** True when the item is anywhere in the player's inventory. */
	public static boolean has(Player p, Item item) {
		Inventory inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			if (inv.getItem(i).is(item)) {
				return true;
			}
		}
		return false;
	}

	/** Blessed thread and needle (from the Nona's tin): what the stitches need. */
	public static boolean hasSewingKit(Player p) {
		return has(p, HILO_BENDITO) && has(p, AGUJA);
	}

	/** Adds a stack to the inventory, or drops it at the player's feet when full. */
	public static void give(Player p, ItemStack stack) {
		if (!p.getInventory().add(stack)) {
			p.drop(stack, false);
		}
	}

	/** The scripted run of the hunter nearest to a point (within 64 blocks, same level), or null. */
	public static Run runNear(ServerLevel level, Vec3 pos) {
		ServerPlayer best = null;
		double bd = 64 * 64;
		for (ServerPlayer p : level.players()) {
			double d = p.distanceToSqr(pos);
			if (d < bd) {
				bd = d;
				best = p;
			}
		}
		Run r = best == null ? null : Director.of(best);
		return r != null && r.level == level ? r : null;
	}

	/** Posts a story event to the run playing near a point (nothing outside a scripted case). */
	public static void post(ServerLevel level, Vec3 pos, String event) {
		Run r = runNear(level, pos);
		if (r != null) {
			r.post(event);
		}
	}

	// ------------------------------------------------------------------ item behaviours
	/** A story ingredient: used in the air it says what it is for (raw chorizo: to the grill; choripán: bless it...). */
	public static class HintItem extends Item {
		private final String hint;

		public HintItem(Item.Properties props, String hint) {
			super(props);
			this.hint = "deadline.msg.casa." + hint;
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			if (player instanceof ServerPlayer sp) {
				Run r = Director.of(sp);
				if (r == null || !GrillSpot.cooking(r)) {  // a click on the grill also arrives here as a use in the air
					sp.displayClientMessage(Component.translatable(hint), true);
				}
			}
			return InteractionResult.PASS;
		}
	}

	/** Thrown like holy water; the demon dog snatches it out of the air (see {@link ChoripanBenditoEntity}). */
	public static class ChoripanBenditoItem extends Item {
		public ChoripanBenditoItem(Item.Properties props) {
			super(props);
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			ItemStack stack = player.getItemInHand(hand);
			level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.HOLY_WATER_THROW, SoundSource.PLAYERS, 0.7F, 1.2F + level.getRandom().nextFloat() * 0.2F);
			if (level instanceof ServerLevel server) {
				Projectile.spawnProjectileFromRotation(ChoripanBenditoEntity::new, server, stack, player, -5.0F, 1.25F, 0.5F);
			}
			player.getCooldowns().addCooldown(stack, 10);
			stack.consume(1, player);
			return InteractionResult.SUCCESS;
		}
	}

	/** The Nona's "Galletitas" tin. Opened: blessed thread, a needle and the 1960 photo. Never cookies. Event "lata:abierta". */
	public static class LataItem extends Item {
		public LataItem(Item.Properties props) {
			super(props);
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			if (!(player instanceof ServerPlayer sp)) {
				return InteractionResult.SUCCESS;
			}
			player.getItemInHand(hand).consume(1, player);
			give(sp, new ItemStack(HILO_BENDITO));
			give(sp, new ItemStack(AGUJA));
			give(sp, new ItemStack(FOTO_1960));
			level.playSound(null, sp.getX(), sp.getY(), sp.getZ(), SoundEvents.CHEST_OPEN, SoundSource.PLAYERS, 0.6F, 1.7F);
			Fx.subtitle(sp, "deadline.speaker.tu", "deadline.line.casa.tu.galletitas", 90);
			Run r = Director.of(sp);
			if (r != null) {
				r.post("lata:abierta");
			}
			return InteractionResult.SUCCESS;
		}
	}

	/** "Nélida y Ofelia, 1960": used, the caption fills the screen. Event "foto:vista". */
	public static class FotoItem extends Item {
		public FotoItem(Item.Properties props) {
			super(props);
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			if (player instanceof ServerPlayer sp) {
				Fx.bigText(sp, "deadline.text.casa.foto", 80, -1F);
				level.playSound(null, sp.getX(), sp.getY(), sp.getZ(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.8F, 1.0F);
				Run r = Director.of(sp);
				if (r != null) {
					r.post("foto:vista");
				}
			}
			return InteractionResult.SUCCESS;
		}
	}

	/** Trophy slipper: a boomerang that stuns the first haunt it touches for 2 s and comes back to the hand. */
	public static class ChancletaItem extends Item {
		public ChancletaItem(Item.Properties props) {
			super(props);
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			ItemStack stack = player.getItemInHand(hand);
			if (level instanceof ServerLevel server) {
				ChancletaEntity.boomerang(server, player, !player.getAbilities().instabuild);
			}
			player.getCooldowns().addCooldown(stack, CHANCLETA_COOLDOWN);
			stack.consume(1, player);
			return InteractionResult.SUCCESS;
		}
	}
}
