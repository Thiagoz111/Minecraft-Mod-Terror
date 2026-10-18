package com.deadline.item;

import java.util.List;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomModelData;

/** custom_model_data helpers used to drive item model variants (EMF LEDs, flashlight on/UV, ringing phone). */
public final class ItemUtil {
	private ItemUtil() {
	}

	public static float getFloat(ItemStack stack, int i) {
		CustomModelData d = stack.get(DataComponents.CUSTOM_MODEL_DATA);
		if (d == null || d.floats().size() <= i) {
			return 0;
		}
		return d.floats().get(i);
	}

	public static boolean getFlag(ItemStack stack, int i) {
		CustomModelData d = stack.get(DataComponents.CUSTOM_MODEL_DATA);
		return d != null && d.flags().size() > i && d.flags().get(i);
	}

	public static void setFloat(ItemStack stack, float value) {
		if (getFloat(stack, 0) != value || stack.get(DataComponents.CUSTOM_MODEL_DATA) == null) {
			CustomModelData d = stack.get(DataComponents.CUSTOM_MODEL_DATA);
			List<Boolean> flags = d == null ? List.of() : d.flags();
			stack.set(DataComponents.CUSTOM_MODEL_DATA, new CustomModelData(List.of(value), flags, List.of(), List.of()));
		}
	}

	public static void setFlags(ItemStack stack, boolean... flags) {
		CustomModelData d = stack.get(DataComponents.CUSTOM_MODEL_DATA);
		List<Boolean> list = new java.util.ArrayList<>();
		for (boolean f : flags) {
			list.add(f);
		}
		if (d != null && d.flags().equals(list)) {
			return;
		}
		stack.set(DataComponents.CUSTOM_MODEL_DATA, new CustomModelData(d == null ? List.of() : d.floats(), list, List.of(), List.of()));
	}
}
