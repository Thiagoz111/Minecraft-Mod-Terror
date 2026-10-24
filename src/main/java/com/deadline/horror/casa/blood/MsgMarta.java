package com.deadline.horror.casa.blood;

import com.deadline.caseload.HunterData;
import com.deadline.horror.Ctx;
import com.deadline.horror.HorrorEvent;
import com.deadline.phone.PendingMsg;
import com.deadline.phone.PhoneMessages;
import com.deadline.phone.PhoneMsg;
import com.deadline.phone.PhoneThread;
import com.deadline.registry.ModAttachments;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;

/**
 * 52 msg_marta (acts 0-6, intensity 1): Marta writes, a text that belongs to the act and has not been sent yet
 * (docs/design/casa_terror.md 8, in her voice: short, "usted", never a question she waits for). The act script sends
 * the fixed messages of 8 on its own clock; this event draws from a second pool of the same acts so the two never
 * repeat each other: lang keys deadline.sms.marta.&lt;id&gt; of {@link #POOL}.
 */
public class MsgMarta extends HorrorEvent {
	/** Her extra texts per act (index = act). */
	public static final String[][] POOL = {
			{},
			{"solo", "no_pare"},
			{"no_mire", "cubiertos"},
			{"fotos_nono", "cuaderno", "cura", "perro_parado"},
			{"luz_bano", "quien_camina", "roperos", "cual_chico"},
			{"no_corra", "pantalla", "perdon"},
			{"no_baje", "no_soy_yo"}};

	public MsgMarta() {
		super("msg_marta", Kind.PHONE);
		this.acts(0, 6).intensity(1).cooldown(80).weight(7);
	}

	/** True when a thread already holds (or is about to receive) a bubble with this value. */
	public static boolean sent(ServerPlayer p, String thread, String value) {
		HunterData d = ModAttachments.get(p);
		for (PhoneThread t : d.threads) {
			if (t.id.equals(thread)) {
				for (PhoneMsg m : t.messages) {
					if (m.value().equals(value)) {
						return true;
					}
				}
			}
		}
		for (PendingMsg m : d.pending) {
			if (m.thread().equals(thread) && m.value().equals(value)) {
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean canRun(Ctx c) {
		int act = Math.max(0, Math.min(POOL.length - 1, c.haunt.act()));
		List<String> fresh = new ArrayList<>();
		for (String id : POOL[act]) {
			String key = "deadline.sms.marta." + id;
			if (!sent(c.p, PhoneMessages.MARTA, key)) {
				fresh.add(key);
			}
		}
		if (fresh.isEmpty()) {
			return false;
		}
		c.put("key", fresh.get(0));  // in order: each act's texts read as a sequence
		return true;
	}

	@Override
	public void start(Ctx c) {
		if (c.get("key") == null && !canRun(c)) {
			return;
		}
		String key = c.get("key");
		PhoneMessages.typing(c.p, PhoneMessages.MARTA, 30);
		PhoneMessages.textLater(c.p, PhoneMessages.MARTA, key, 30);
	}
}
