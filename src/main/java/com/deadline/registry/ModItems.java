package com.deadline.registry;

import com.deadline.DeadLine;
import com.deadline.item.AnchorItem;
import com.deadline.item.CameraItem;
import com.deadline.item.CrucifixItem;
import com.deadline.item.EmfItem;
import com.deadline.item.FlareItem;
import com.deadline.item.FlashlightItem;
import com.deadline.item.HolyWaterItem;
import com.deadline.item.PhoneItem;
import com.deadline.item.PillsItem;
import com.deadline.item.RitualBookItem;
import com.deadline.item.SaltItem;
import com.deadline.item.SpiritBoxItem;
import com.deadline.item.SpiritJarItem;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.entity.player.Player;

public final class ModItems {
	private static final List<Item> TAB_ORDER = new ArrayList<>();

	public static final PhoneItem PHONE = register("phone", PhoneItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
	public static final CrucifixItem CRUCIFIX = register("crucifix", CrucifixItem::new, new Item.Properties().durability(240));
	public static final HolyWaterItem HOLY_WATER = register("holy_water", HolyWaterItem::new, new Item.Properties().stacksTo(16));
	public static final SaltItem SALT = register("salt", SaltItem::new, new Item.Properties().durability(64));
	public static final EmfItem EMF = register("emf", EmfItem::new, new Item.Properties().stacksTo(1));
	public static final FlashlightItem FLASHLIGHT = register("flashlight", FlashlightItem::new, new Item.Properties().durability(2400));
	public static final SpiritBoxItem SPIRIT_BOX = register("spirit_box", SpiritBoxItem::new, new Item.Properties().stacksTo(1));
	public static final CameraItem CAMERA = register("camera", CameraItem::new, new Item.Properties().durability(40));
	public static final RitualBookItem RITUAL_BOOK = register("ritual_book", RitualBookItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
	public static final SpiritJarItem SPIRIT_JAR = register("spirit_jar", p -> new SpiritJarItem(p, false), new Item.Properties().stacksTo(4));
	public static final SpiritJarItem SPIRIT_JAR_FULL = register("spirit_jar_full", p -> new SpiritJarItem(p, true), new Item.Properties().stacksTo(1).rarity(Rarity.EPIC));
	public static final PillsItem PILLS = register("pills", PillsItem::new, new Item.Properties().stacksTo(8));
	public static final Item SILVER_DAGGER = register("silver_dagger", Item::new, new Item.Properties().sword(ToolMaterial.IRON, 3.0F, -2.2F).rarity(Rarity.UNCOMMON));
	public static final Item ROSARY = register("rosary", Item::new, new Item.Properties().stacksTo(1));
	public static final FlareItem FLARE = register("flare", FlareItem::new, new Item.Properties().stacksTo(16));

	/** The exorcist's suit: cassock, skirt and boots use the `deadline:exorcista` equipment asset; the hat is a 3D item model. */
	public static final ArmorMaterial EXORCIST = new ArmorMaterial(25,
			Map.of(ArmorType.BOOTS, 2, ArmorType.LEGGINGS, 4, ArmorType.CHESTPLATE, 5, ArmorType.HELMET, 2, ArmorType.BODY, 5),
			18, SoundEvents.ARMOR_EQUIP_LEATHER, 0.5F, 0.0F, ItemTags.REPAIRS_LEATHER_ARMOR,
			ResourceKey.create(EquipmentAssets.ROOT_ID, DeadLine.id("exorcista")));
	public static final Item EXORCIST_HAT = register("exorcist_hat", Item::new, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)
			.equippable(EquipmentSlot.HEAD).attributes(EXORCIST.createAttributes(ArmorType.HELMET)));
	public static final Item EXORCIST_CASSOCK = register("exorcist_cassock", Item::new, new Item.Properties().rarity(Rarity.UNCOMMON).humanoidArmor(EXORCIST, ArmorType.CHESTPLATE));
	public static final Item EXORCIST_SKIRT = register("exorcist_skirt", Item::new, new Item.Properties().rarity(Rarity.UNCOMMON).humanoidArmor(EXORCIST, ArmorType.LEGGINGS));
	public static final Item EXORCIST_BOOTS = register("exorcist_boots", Item::new, new Item.Properties().rarity(Rarity.UNCOMMON).humanoidArmor(EXORCIST, ArmorType.BOOTS));

	public static final Item LLAVE_CAPILLA = register("llave_capilla", Item::new, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));

	public static final AnchorItem INVERTED_ROSARY = register("inverted_rosary", AnchorItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.RARE));
	public static final AnchorItem CURSED_DOLL = register("cursed_doll", AnchorItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.RARE));

	public static final Item POSEIDA_SPAWN_EGG = egg("poseida", ModEntities.POSEIDA);
	public static final Item MONJA_SPAWN_EGG = egg("monja", ModEntities.MONJA);
	public static final Item SOMBRA_SPAWN_EGG = egg("sombra", ModEntities.SOMBRA);
	public static final Item MUNECA_SPAWN_EGG = egg("muneca", ModEntities.MUNECA);
	public static final Item ANIMA_SPAWN_EGG = egg("anima", ModEntities.ANIMA);

	public static final CreativeModeTab TAB = Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, DeadLine.id("deadline"),
			FabricItemGroup.builder()
					.title(Component.translatable("itemGroup.deadline"))
					.icon(() -> new ItemStack(PHONE))
					.displayItems((params, output) -> {
						for (Item item : TAB_ORDER) {
							output.accept(item);
						}
						output.accept(ModBlocks.RITUAL_CANDLE);
						output.accept(ModBlocks.BLOOD_STAIN);
					})
					.build());

	private ModItems() {
	}

	private static <T extends Item> T register(String name, Function<Item.Properties, T> factory, Item.Properties props) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, DeadLine.id(name));
		T item = factory.apply(props.setId(key));
		Registry.register(BuiltInRegistries.ITEM, key, item);
		TAB_ORDER.add(item);
		return item;
	}

	private static Item egg(String name, EntityType<?> type) {
		return register(name + "_spawn_egg", SpawnEggItem::new, new Item.Properties().spawnEgg(type));
	}

	/** True when the player wears the four pieces of the exorcist's suit (set bonus: slower sanity loss). */
	public static boolean wearsSuit(Player p) {
		return p.getItemBySlot(EquipmentSlot.HEAD).is(EXORCIST_HAT) && p.getItemBySlot(EquipmentSlot.CHEST).is(EXORCIST_CASSOCK)
				&& p.getItemBySlot(EquipmentSlot.LEGS).is(EXORCIST_SKIRT) && p.getItemBySlot(EquipmentSlot.FEET).is(EXORCIST_BOOTS);
	}

	public static void init() {
	}
}
