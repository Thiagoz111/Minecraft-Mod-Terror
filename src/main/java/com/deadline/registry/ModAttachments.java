package com.deadline.registry;

import com.deadline.DeadLine;
import com.deadline.caseload.HunterData;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.world.entity.player.Player;

public final class ModAttachments {
	public static final AttachmentType<HunterData> HUNTER = AttachmentRegistry.create(
			DeadLine.id("hunter"),
			builder -> builder.initializer(HunterData::new).persistent(HunterData.CODEC).copyOnDeath()
	);

	private ModAttachments() {
	}

	public static HunterData get(Player player) {
		return player.getAttachedOrCreate(HUNTER);
	}

	public static void init() {
	}
}
