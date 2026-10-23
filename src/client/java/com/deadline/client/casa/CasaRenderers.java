package com.deadline.client.casa;

/** Client side of the Casa Morales case: every casa renderer in one place (the family). */
public final class CasaRenderers {
	private CasaRenderers() {
	}

	public static void init() {
		FamilyRenderers.init();
	}
}
