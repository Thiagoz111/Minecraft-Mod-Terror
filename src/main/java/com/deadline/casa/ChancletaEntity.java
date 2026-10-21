package com.deadline.casa;

import com.deadline.director.Props;
import com.deadline.entity.HauntEntity;
import com.deadline.net.Fx;
import com.deadline.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;

/**
 * The Nona's slipper. Scripted ({@link #throwFrom}): it flies in an arc from her hand and always lands on its target
 * (chancletazo: {@link #STUN_SCRIPTED} ticks of stun, event "chancleta:hit"). Trophy ({@link #boomerang}): thrown by
 * a hunter it comes back like a boomerang and stuns the first haunt it touches for {@link #STUN_BOOMERANG} ticks.
 * Moved by the server only (no physics), never saved.
 */
public class ChancletaEntity extends Entity {
	public static final int STUN_SCRIPTED = 60;
	public static final int STUN_BOOMERANG = 40;
	private static final int ARC = 0, OUT = 1, BACK = 2;

	private int mode = ARC;
	private Vec3 start = Vec3.ZERO;
	private Vec3 targetPos = Vec3.ZERO;
	/** Scripted target (followed while in the air), or the boomerang's thrower. */
	private Entity target;
	private Vec3 velocity = Vec3.ZERO;
	private int flight = 12;
	private int age;
	private boolean dropOnHit;
	private boolean returnItem;
	private boolean struck;

	public ChancletaEntity(EntityType<? extends ChancletaEntity> type, Level level) {
		super(type, level);
		this.setNoGravity(true);
	}

	// ------------------------------------------------------------------ launching
	/** The Nona throws: from `from`'s hand to `to` (chest height), following it while in the air. Null on the client. */
	public static ChancletaEntity throwFrom(Entity from, Entity to) {
		ChancletaEntity c = launch(from, aim(to));
		if (c != null) {
			c.target = to;
		}
		return c;
	}

	/** The Nona throws at a point (stuns any haunt within 1.5 blocks of it on landing). Null on the client. */
	public static ChancletaEntity throwFrom(Entity from, Vec3 to) {
		return launch(from, to);
	}

	/** Leaves the slipper on the ground where it lands (the trophy to pick up). */
	public ChancletaEntity dropOnHit(boolean drop) {
		this.dropOnHit = drop;
		return this;
	}

	private static ChancletaEntity launch(Entity from, Vec3 to) {
		if (!(from.level() instanceof ServerLevel level)) {
			return null;
		}
		Vec3 base = from.position();
		Vec3 flat = new Vec3(to.x - base.x, 0, to.z - base.z);
		flat = flat.lengthSqr() < 1.0E-4 ? Vec3.ZERO : flat.normalize();
		Vec3 s = base.add(0, from.getBbHeight() * 0.8, 0).add(flat.scale(0.45));
		ChancletaEntity c = new ChancletaEntity(CasaItems.CHANCLETA_ENTITY, level);
		c.mode = ARC;
		c.start = s;
		c.targetPos = to;
		c.flight = Mth.clamp((int) Math.ceil(s.distanceTo(to) / 0.85), 6, 40);
		c.snapTo(s.x, s.y, s.z, Props.yawTowards(s, to), 0F);
		level.addFreshEntity(c);
		level.playSound(null, s.x, s.y, s.z, ModSounds.CHANCLETA_WHIP, SoundSource.HOSTILE, 1.4F, 1.0F);
		return c;
	}

	/** A hunter throws the trophy along the look direction; it comes back (and returns to the inventory when returnItem). */
	public static ChancletaEntity boomerang(ServerLevel level, Player owner, boolean returnItem) {
		Vec3 look = owner.getViewVector(1.0F);
		Vec3 s = owner.getEyePosition().add(look.scale(0.6)).add(0, -0.25, 0);
		ChancletaEntity c = new ChancletaEntity(CasaItems.CHANCLETA_ENTITY, level);
		c.mode = OUT;
		c.start = s;
		c.target = owner;
		c.velocity = look.scale(0.95);
		c.returnItem = returnItem;
		c.snapTo(s.x, s.y, s.z, owner.getYRot(), 0F);
		level.addFreshEntity(c);
		level.playSound(null, s.x, s.y, s.z, ModSounds.CHANCLETA_WHIP, SoundSource.PLAYERS, 1.0F, 1.15F);
		return c;
	}

	private static Vec3 aim(Entity e) {
		return e.position().add(0, e.getBbHeight() * 0.7, 0);
	}

	// ------------------------------------------------------------------ flight
	@Override
	public void tick() {
		super.tick();
		age++;
		if (!(this.level() instanceof ServerLevel level)) {
			return;
		}
		switch (mode) {
			case ARC -> arc(level);
			case OUT -> out(level);
			default -> back(level);
		}
	}

	private void arc(ServerLevel level) {
		if (target != null && target.isAlive() && target.level() == level) {
			targetPos = aim(target);
		}
		float t = Math.min(1.0F, (float) age / flight);
		double h = 0.6 + start.distanceTo(targetPos) * 0.12;
		Vec3 p = start.lerp(targetPos, t).add(0, 4 * h * t * (1 - t), 0);
		moveTo(p);
		if (t >= 1.0F) {
			land(level);
		}
	}

	private void land(ServerLevel level) {
		Vec3 at = this.position();
		level.playSound(null, at.x, at.y, at.z, ModSounds.CHANCLETA_HIT, SoundSource.HOSTILE, 1.8F, 1.0F);
		level.sendParticles(ParticleTypes.CRIT, at.x, at.y, at.z, 14, 0.3, 0.3, 0.3, 0.25);
		level.sendParticles(ParticleTypes.POOF, at.x, at.y, at.z, 6, 0.2, 0.2, 0.2, 0.02);
		if (target instanceof HauntEntity h) {
			h.stun(STUN_SCRIPTED);
		} else if (target == null) {
			for (Entity e : level.getEntities(this, this.getBoundingBox().inflate(1.5), e -> e instanceof HauntEntity)) {
				((HauntEntity) e).stun(STUN_SCRIPTED);
			}
		}
		for (ServerPlayer p : level.players()) {
			if (p.distanceToSqr(at) < 16 * 16) {
				Fx.shake(p, 0.25F, 6);
			}
		}
		CasaItems.post(level, at, "chancleta:hit");
		if (dropOnHit) {
			this.spawnAtLocation(level, new ItemStack(CasaItems.CHANCLETA));
		}
		this.discard();
	}

	private void out(ServerLevel level) {
		if (age > 14 || !level.noCollision(this, this.getBoundingBox().move(velocity))) {
			mode = BACK;
			return;
		}
		moveTo(this.position().add(velocity));
		strike(level);
	}

	private void back(ServerLevel level) {
		if (target == null || !target.isAlive() || target.level() != level || age > 120) {
			if (returnItem) {
				this.spawnAtLocation(level, new ItemStack(CasaItems.CHANCLETA));
			}
			this.discard();
			return;
		}
		Vec3 d = target.position().add(0, target.getBbHeight() * 0.6, 0).subtract(this.position());
		double dist = d.length();
		if (dist < 1.2) {
			if (returnItem && target instanceof Player p) {
				CasaItems.give(p, new ItemStack(CasaItems.CHANCLETA));
			}
			level.playSound(null, target.getX(), target.getY(), target.getZ(), SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 0.5F, 1.3F);
			this.discard();
			return;
		}
		moveTo(this.position().add(d.scale(Math.min(1.1, dist) / dist)));
		strike(level);
	}

	/** The boomerang stuns the first haunt it touches, then heads home. */
	private void strike(ServerLevel level) {
		if (struck) {
			return;
		}
		for (Entity e : level.getEntities(this, this.getBoundingBox().inflate(0.35), e -> e instanceof HauntEntity && e.isAlive())) {
			HauntEntity h = (HauntEntity) e;
			h.stun(STUN_BOOMERANG);
			struck = true;
			mode = BACK;
			level.playSound(null, h.getX(), h.getY(), h.getZ(), ModSounds.CHANCLETA_HIT, SoundSource.PLAYERS, 1.4F, 1.1F);
			level.sendParticles(ParticleTypes.CRIT, this.getX(), this.getY(), this.getZ(), 10, 0.2, 0.2, 0.2, 0.2);
			CasaItems.post(level, this.position(), "chancleta:boomerang");
			return;
		}
	}

	private void moveTo(Vec3 p) {
		if (p.distanceToSqr(this.position()) > 1.0E-6) {
			this.setYRot(Props.yawTowards(this.position(), p));
		}
		this.setPos(p.x, p.y, p.z);
	}

	// ------------------------------------------------------------------ entity plumbing
	@Override
	protected void defineSynchedData(SynchedEntityData.Builder builder) {
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean shouldBeSaved() {
		return false;
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
	}
}
