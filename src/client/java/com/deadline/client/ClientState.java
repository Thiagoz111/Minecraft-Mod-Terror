package com.deadline.client;

import com.deadline.caseload.CaseType;
import com.deadline.net.PhoneDataPayload;

/** Everything the HUD and the phone need to draw, updated from server packets. */
public final class ClientState {
	private ClientState() {
	}

	public static long ticks;

	// sanity
	public static float sanity = 100F;
	public static float sanityShown = 100F;

	// screen effects
	public static float shakeIntensity;
	public static int shakeTicks;
	public static int shakeTotal = 1;
	public static float flash;
	public static float redFlash;
	public static int fadeTicks;
	public static int fadeTotal = 1;
	public static float staticStrength;
	public static int staticTicks;
	public static int staticTotal = 1;

	// jumpscare
	public static String jumpscareKey = "";
	public static int jumpscareTicks;
	public static final int JUMPSCARE_LEN = 26;

	// big centred title
	public static String titleKey = "";
	public static int titleTicks;
	public static int titleTotal = 1;

	// objective panel
	public static String objCase = "";
	public static int objStage = -1;
	public static int objFlash;

	// end-of-case banner
	public static int endTicks;
	public static boolean endSolved;
	public static int endReward;

	// hallucinated figure at the edge of the screen
	public static int figureTicks;
	public static boolean figureLeft;

	// recording overlay
	public static boolean vhs;
	public static long vhsStart;

	// last phone snapshot
	public static PhoneDataPayload phone = new PhoneDataPayload(false, 0, 0, 100F, 0, "", 0, 0);

	public static void reset() {
		sanity = sanityShown = 100F;
		shakeTicks = fadeTicks = staticTicks = jumpscareTicks = titleTicks = endTicks = figureTicks = objFlash = 0;
		flash = redFlash = 0F;
		objCase = "";
		objStage = -1;
		phone = new PhoneDataPayload(false, 0, 0, 100F, 0, "", 0, 0);
		com.deadline.client.hud.StoryHud.reset();
		com.deadline.client.phone.ClientMessages.reset();
	}

	/** Lang key of the current objective line for a case stage. */
	public static String objectiveKey(String caseKey, int stage) {
		if (stage == 2 && "casa".equals(caseKey)) {
			return "deadline.objective.2x";
		}
		return "deadline.objective." + Math.max(0, Math.min(3, stage));
	}

	/** Row of a case in phone/avatars.png. */
	public static int caseRow(String caseKey) {
		return switch (caseKey) {
			case "colegio" -> 4;
			default -> 0;
		};
	}

	/** Entity hunted in a case (bestiary / jumpscare key). */
	public static String caseEntity(String caseKey) {
		return switch (caseKey) {
			case "colegio" -> "monja";
			default -> "poseida";
		};
	}

	public static CaseType caseType(String caseKey) {
		CaseType t = CaseType.byKey(caseKey);
		return t == null ? CaseType.COLEGIO : t;
	}
}
