package com.deadline.entity;

import com.deadline.director.Props;
import com.deadline.net.Fx;
import com.deadline.registry.ModParticles;
import com.deadline.registry.ModSounds;
import com.deadline.voice.NoiseMeter;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Sor Agonía hunts by SOUND (docs/design/BIBLIA.md 2.1 g): loud hunters (the noise meter) draw her to where the noise
 * was; she chases what she can see in the dark with an elastic speed. The flashlight beam burns her: she recoils, sinks
 * into the floor and comes back from another dark spot. Strong light (candles, lamps) blocks her way, and she blows
 * candles out when she passes them. A little hand-bell rings before she appears behind someone.
 */
public class MonjaEntity extends HauntEntity {
	public static final int ACT_IDLE = 0, ACT_HUNT = 1, ACT_BURN = 2, ACT_SCREAM = 3, ACT_CONDUCT = 4, ACT_SIT = 5, ACT_CEILING = 6,
			ACT_BLOW = 7, ACT_WET = 8, ACT_KNEEL_WALL = 9, ACT_REVEAL = 10;

	private Vec3 noiseMark;
	private int searchTicks;
	private int sinkTicks;
	private int burnTicks;
	private int blowCooldown = 200;
	private int teleportCooldown = 20 * 180;
	private int bellTicks;
	private int tapCooldown = 40;
	private ServerPlayer behindTarget;

	public MonjaEntity(EntityType<? extends Monster> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return Monster.createMonsterAttributes()
				.add(Attributes.MAX_HEALTH, 110.0)
				.add(Attributes.MOVEMENT_SPEED, 0.3)
				.add(Attributes.ATTACK_DAMAGE, 5.0)
				.add(Attributes.FOLLOW_RANGE, 48.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, 0.9);
	}

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
	}

	public static int lightAt(Level level, BlockPos pos) {
		return Math.max(level.getBrightness(LightLayer.BLOCK, pos), level.getBrightness(LightLayer.BLOCK, pos.above()));
	}

	@Override
	public void tick() {
		super.tick();
		if (HauntEntity.SHOWCASE) {
			return;
		}
		if (this.scripted) {
			// the script took her mid-burn or mid-sink: make her whole again where it put her
			if (sinkTicks > 0 || burnTicks > 0) {
				sinkTicks = 0;
				burnTicks = 0;
				this.setInvisible(false);
				this.noPhysics = false;
			}
			bellTicks = 0;
			behindTarget = null;
			noiseMark = null;
			return;
		}
		if (!(this.level() instanceof ServerLevel level) || this.isWeakened()) {
			return;
		}
		if (sinkTicks > 0) {
			sinking(level);
			return;
		}
		// the flashlight beam or strong light burns her
		if (burnTicks > 0) {
			burnTicks--;
			this.getNavigation().stop();
			this.setAction(ACT_BURN);
			if (burnTicks % 4 == 0) {
				level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 1.6, this.getZ(), 5, 0.25, 0.4, 0.25, 0.02);
			}
			if (burnTicks == 0) {
				sink(level, 60 + this.random.nextInt(60));
			}
			return;
		}
		for (ServerPlayer p : level.players()) {
			if (!p.isSpectator() && Props.beamOn(p, this)) {
				burn(level, p);
				return;
			}
		}
		if (lightAt(level, this.blockPosition()) >= 8) {
			// stepped into strong light: back off towards the dark
			burn(level, null);
			return;
		}
		hunt(level);
		blowCandles(level);
		if (--tapCooldown <= 0) {
			tapCooldown = 50 + this.random.nextInt(40);
			level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_REGLA_TAP, SoundSource.HOSTILE, 0.9F, 1.0F);
		}
	}

	// ------------------------------------------------------------------ hunting by sound and sight
	private void hunt(ServerLevel level) {
		ServerPlayer seen = null;
		ServerPlayer loudest = null;
		float loud = 0F;
		for (ServerPlayer p : level.players()) {
			if (p.isSpectator() || p.isCreative() || p.distanceToSqr(this) > 40 * 40) {
				continue;
			}
			float n = NoiseMeter.get(p);
			double d = p.distanceTo(this);
			float threshold = d < 12 ? 30F : 55F;
			if (n > threshold && n > loud) {
				loud = n;
				loudest = p;
			}
			if (d < 14 && lightAt(level, p.blockPosition()) < 8 && canSee(level, p)) {
				seen = p;
			}
		}
		if (seen != null) {
			if (this.getTarget() != seen) {
				NoiseMeter.heard(seen);
				level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_HISS, SoundSource.HOSTILE, 1.6F, 1.0F);
			}
			this.setTarget(seen);
			noiseMark = null;
			double d = seen.distanceTo(this);
			// elastic chase: faster far away, eases off when close, never a one-shot
			double speed = d < 3 ? 0.26 : 0.30 + 0.12 * Mth.clamp((d - 3) / 12.0, 0.0, 1.0);
			this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(speed);
			this.setAction(ACT_HUNT);
			return;
		}
		if (this.getTarget() != null && (!(this.getTarget() instanceof ServerPlayer tp) || !canSee(level, tp))) {
			noiseMark = this.getTarget().position();
			this.setTarget(null);
		}
		if (loudest != null) {
			noiseMark = loudest.position().add(this.random.nextGaussian() * 1.5, 0, this.random.nextGaussian() * 1.5);
			searchTicks = 100;
			NoiseMeter.heard(loudest);
		}
		this.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.3);
		if (noiseMark != null) {
			this.setAction(ACT_HUNT);
			if (this.tickCount % 10 == 0) {
				this.getNavigation().moveTo(noiseMark.x, noiseMark.y, noiseMark.z, 1.0);
			}
			if (this.position().distanceTo(noiseMark) < 2.0 && --searchTicks <= 0) {
				noiseMark = null;
			}
		} else {
			this.setAction(ACT_IDLE);
			if (this.tickCount % 120 == 0 && this.random.nextInt(3) == 0) {
				Vec3 v = this.position().add(this.random.nextGaussian() * 8, 0, this.random.nextGaussian() * 8);
				if (lightAt(level, BlockPos.containing(v)) < 8) {
					this.getNavigation().moveTo(v.x, v.y, v.z, 0.6);
				}
			}
		}
		teleportBehindIfQuiet(level);
	}

	private boolean canSee(ServerLevel level, ServerPlayer p) {
		Vec3 from = this.getEyePosition();
		Vec3 to = p.getEyePosition();
		return level.clip(new ClipContext(from, to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, this)).getType() == HitResult.Type.MISS;
	}

	/** At most once every 3 minutes: the bell rings, then she is standing behind a hunter in the dark. */
	private void teleportBehindIfQuiet(ServerLevel level) {
		if (bellTicks > 0) {
			if (--bellTicks == 0 && behindTarget != null && !behindTarget.isRemoved()) {
				Vec3 from = this.position();
				boolean there = this.teleportBehind(behindTarget, 3.0);
				if (there && !this.canWalkTo(behindTarget)) {
					this.teleportTo(from.x, from.y, from.z);  // behind a wall or on a roof: not worth the scream
					there = false;
				}
				if (there) {
					level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_SCREAM, SoundSource.HOSTILE, 2.0F, 1.0F);
					Fx.shake(behindTarget, 0.6F, 12);
					this.setTarget(behindTarget);
				}
				behindTarget = null;
			}
			return;
		}
		if (--teleportCooldown > 0) {
			return;
		}
		for (ServerPlayer p : level.players()) {
			if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < 50 * 50 && lightAt(level, p.blockPosition()) < 6) {
				teleportCooldown = 20 * 180;
				behindTarget = p;
				bellTicks = 40;
				Fx.soundAt(p, ModSounds.MONJA_CAMPANITA, p.position().add(p.getLookAngle().scale(-3)), 1.0F);
				return;
			}
		}
		teleportCooldown = 200;
	}

	// ------------------------------------------------------------------ light
	private void burn(ServerLevel level, ServerPlayer by) {
		burnTicks = 16;
		this.setTarget(null);
		noiseMark = null;
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_BURN, SoundSource.HOSTILE, 1.8F, 1.0F);
		level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.MONJA_HISS, SoundSource.HOSTILE, 1.6F, 0.9F);
		if (by != null) {
			Vec3 away = this.position().subtract(by.position()).normalize().scale(0.6);
			this.setDeltaMovement(away.x, 0.15, away.z);
			if (!this.isAnchored()) {
				this.hurtServer(level, this.damageSources().magic(), 1.0F);
			}
		}
	}

	private void sink(ServerLevel level, int ticks) {
		sinkTicks = ticks;
		level.sendParticles(ModParticles.DEMON_SMOKE, this.getX(), this.getY() + 0.5, this.getZ(), 30, 0.3, 0.3, 0.3, 0.02);
		this.setInvisible(true);
		this.noPhysics = true;
		this.getNavigation().stop();
	}

	private void sinking(ServerLevel level) {
		this.setDeltaMovement(Vec3.ZERO);
		if (--sinkTicks > 0) {
			return;
		}
		// come back from a dark spot at least 10 blocks from every hunter, out of their sight
		ServerPlayer near = null;
		double best = Double.MAX_VALUE;
		for (ServerPlayer p : level.players()) {
			double d = p.distanceToSqr(this);
			if (d < best && !p.isSpectator()) {
				best = d;
				near = p;
			}
		}
		Vec3 center = near != null ? near.position() : this.position();
		Vec3 home = this.position();
		boolean found = false;
		for (int i = 0; i < 20 && !found; i++) {
			found = this.teleportNear(center, 10.0, 18.0) && lightAt(level, this.blockPosition()) < 6
					&& (near == null || !this.isWatchedBy(near, 0.2)) && this.canWalkTo(near);
		}
		if (!found) {
			// nowhere dark and connected: stay sunk a little longer and try again
			this.teleportTo(home.x, home.y, home.z);
			sinkTicks = 20;
			return;
		}
		this.setInvisible(false);
		this.noPhysics = false;
	}

	/** Candles near her go out, one every 10-14 s. */
	/** Candles and candle-like kit fixtures (candlesticks, chandelier, sanctuary lamp); not the electric globes. */
	private static boolean blowable(BlockState s) {
		if (s.getBlock() instanceof net.minecraft.world.level.block.CandleBlock) {
			return s.getValue(BlockStateProperties.LIT);
		}
		String path = net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(s.getBlock()).getPath();
		return path.startsWith("colegio_") && !path.contains("globo") && com.deadline.site.Fixtures.burning(s);
	}

	private void blowCandles(ServerLevel level) {
		if (--blowCooldown > 0) {
			return;
		}
		blowCooldown = 200 + this.random.nextInt(80);
		BlockPos c = this.blockPosition();
		for (BlockPos p : BlockPos.betweenClosed(c.offset(-6, -1, -6), c.offset(6, 3, 6))) {
			BlockState s = level.getBlockState(p);
			if (blowable(s)) {
				level.setBlock(p, com.deadline.site.Fixtures.dark(s), 3);
				level.playSound(null, p.getX(), p.getY(), p.getZ(), ModSounds.MONJA_SOPLIDO, SoundSource.HOSTILE, 1.0F, 1.0F);
				level.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE, p.getX() + 0.5, p.getY() + 0.6, p.getZ() + 0.5, 6, 0.05, 0.1, 0.05, 0.01);
				this.setAction(ACT_BLOW);
				return;
			}
		}
	}

	@Override
	public float holyWeakness() {
		return 1.6F;
	}

	@Override
	public float fearAura() {
		return 0.75F;
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return null;
	}

	@Override
	public SoundEvent getHurtSoundEvent() {
		return ModSounds.MONJA_HURT;
	}

	@Override
	public SoundEvent getDeathSoundEvent() {
		return ModSounds.MONJA_DEATH;
	}
}
