package com.deadline.entity;

import com.deadline.caseload.CaseManager;
import com.deadline.net.Fx;
import com.deadline.registry.ModItems;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/**
 * The cursed object that binds an entity to its haunt. Floats above the ground wrapped in a dark aura.
 * Douse it with holy water (throw it, or use it on the anchor) to break the bond.
 */
public class AnchorEntity extends Entity {
	private static final EntityDataAccessor<ItemStack> ITEM = SynchedEntityData.defineId(AnchorEntity.class, EntityDataSerializers.ITEM_STACK);
	private int siteIndex = -1;

	public AnchorEntity(EntityType<? extends AnchorEntity> type, Level level) {
		super(type, level);
		this.setNoGravity(true);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
		builder.define(ITEM, ItemStack.EMPTY);
	}

	public ItemStack getItem() {
		return this.entityData.get(ITEM);
	}

	public void setItem(ItemStack stack) {
		this.entityData.set(ITEM, stack.copy());
	}

	public int siteIndex() {
		return siteIndex;
	}

	public void setSiteIndex(int site) {
		this.siteIndex = site;
	}

	@Override
	public void tick() {
		super.tick();
		if (this.level().isClientSide()) {
			if (this.random.nextInt(3) == 0) {
				this.level().addParticle(ModParticles.DEMON_SMOKE, this.getRandomX(0.8), this.getY() + 0.2 + this.random.nextDouble() * 0.6, this.getRandomZ(0.8), 0, 0.015, 0);
			}
			if (this.random.nextInt(5) == 0) {
				this.level().addParticle(new DustParticleOptions(0x8A0A12, 1.2F), this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0), 0, 0, 0);
			}
			return;
		}
		if (this.tickCount % 90 == 0) {
			this.level().playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.ANCHOR_PULSE, SoundSource.HOSTILE, 1.2F, 0.9F + this.random.nextFloat() * 0.2F);
		}
	}

	@Override
	public InteractionResult interact(Player player, InteractionHand hand) {
		ItemStack held = player.getItemInHand(hand);
		if (!held.is(ModItems.HOLY_WATER)) {
			if (player instanceof ServerPlayer sp) {
				sp.displayClientMessage(net.minecraft.network.chat.Component.translatable("deadline.msg.anchor_hint"), true);
			}
			return InteractionResult.PASS;
		}
		if (this.level() instanceof ServerLevel level && player instanceof ServerPlayer sp) {
			held.consume(1, player);
			purify(level, sp);
		}
		return InteractionResult.SUCCESS;
	}

	public void purify(ServerLevel level, ServerPlayer by) {
		if (this.isRemoved()) {
			return;
		}
		level.sendParticles(ParticleTypes.END_ROD, this.getX(), this.getY() + 0.5, this.getZ(), 30, 0.2, 0.3, 0.2, 0.15);
		level.sendParticles(ModParticles.HOLY_SPARK, this.getX(), this.getY() + 0.5, this.getZ(), 60, 0.4, 0.6, 0.4, 0.2);
		level.sendParticles(ParticleTypes.LARGE_SMOKE, this.getX(), this.getY() + 0.5, this.getZ(), 25, 0.3, 0.3, 0.3, 0.05);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.ANCHOR_PURIFY, SoundSource.PLAYERS, 3.0F, 1.0F);
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(this) < 32 * 32) {
				Fx.flash(p, 0.8F);
				Fx.shake(p, 0.8F, 25);
			}
		}
		CaseManager.onAnchorPurified(level, this, by);
		this.spawnAtLocation(level, this.getItem().copy());
		this.discard();
	}

	@Override
	public boolean isPickable() {
		return true;
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (source.getDirectEntity() instanceof HolyWaterEntity && source.getEntity() instanceof ServerPlayer p) {
			purify(level, p);
		}
		return false;
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		this.siteIndex = in.getIntOr("Site", -1);
		in.read("Item", ItemStack.CODEC).ifPresent(this::setItem);
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		out.putInt("Site", this.siteIndex);
		if (!this.getItem().isEmpty()) {
			out.store("Item", ItemStack.CODEC, this.getItem());
		}
	}
}
