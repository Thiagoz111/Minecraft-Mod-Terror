package com.deadline.horror.casa.blood;

import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.horror.HouseQuery;
import com.deadline.horror.casa.Apparitions;
import com.deadline.phone.PhoneMessages;
import com.deadline.registry.ModSounds;
import net.minecraft.world.phys.Vec3;

/**
 * 53 msg_desconocido (acts 2-6, intensity 3): an unknown number. Mostly it only types -- "escribiendo..." for a long
 * while -- and nothing ever arrives. Once per case, while he is inside the house, it sends a photo: HIM, from behind,
 * taken from inside the house (photo id {@link #PHOTO}); as it lands, a phone camera shutter clicks a few steps behind
 * his back.
 */
public class MsgDesconocido extends HorrorEvent {
	public static final String PHOTO = "espalda_jugador";
	private static final int LAND = 46;

	public MsgDesconocido() {
		super("msg_desconocido", Kind.PHONE);
		this.acts(2, 6).intensity(3).cooldown(150).weight(6);
	}

	@Override
	public boolean canRun(Ctx c) {
		boolean photo = !MsgMarta.sent(c.p, PhoneMessages.DESCONOCIDO, PHOTO) && HouseQuery.inHouse(c.run, c.p)
				&& !Apparitions.hidden(c.p) && HouseQuery.behind(c.run, c.p, 2.5) != null && c.chance(0.6F);
		c.put("photo", photo);
		return true;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("photo") == null) {
			canRun(c);
		}
		boolean photo = c.get("photo");
		if (photo) {
			PhoneMessages.photoLater(c.p, PhoneMessages.DESCONOCIDO, PHOTO, LAND);
		} else {
			// it types... and types... and nothing comes
			PhoneMessages.typing(c.p, PhoneMessages.DESCONOCIDO, c.between(20 * 6, 20 * 12));
		}
	}

	@Override
	public boolean tick(Ctx c) {
		Boolean photo = c.get("photo");
		if (photo == null || !photo) {
			return true;
		}
		if (c.t == LAND) {
			Vec3 back = HouseQuery.behind(c.run, c.p, 2.5);
			if (back != null) {
				Apparitions.sound(c, ModSounds.CELULAR_OBTURADOR, back.add(0, 1.5, 0), 0.4F, 1.0F);
			}
		}
		return c.t > LAND + 2;
	}

	@Override
	public int maxTicks() {
		return 20 * 6;
	}
}
