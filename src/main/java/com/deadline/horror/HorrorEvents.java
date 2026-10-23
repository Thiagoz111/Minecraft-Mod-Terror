package com.deadline.horror;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Event catalogue per case key ("casa", "colegio"). Cases register theirs once at mod init. */
public final class HorrorEvents {
	private static final Map<String, Map<String, HorrorEvent>> BY_CASE = new HashMap<>();

	private HorrorEvents() {
	}

	public static <T extends HorrorEvent> T register(String caseKey, T event) {
		Map<String, HorrorEvent> m = BY_CASE.computeIfAbsent(caseKey, k -> new LinkedHashMap<>());
		if (m.containsKey(event.id)) {
			throw new IllegalStateException("Duplicate horror event " + caseKey + ":" + event.id);
		}
		m.put(event.id, event);
		return event;
	}

	public static List<HorrorEvent> of(String caseKey) {
		Map<String, HorrorEvent> m = BY_CASE.get(caseKey);
		return m == null ? Collections.emptyList() : new ArrayList<>(m.values());
	}

	public static HorrorEvent get(String caseKey, String id) {
		Map<String, HorrorEvent> m = BY_CASE.get(caseKey);
		return m == null ? null : m.get(id);
	}

	public static List<String> ids(String caseKey) {
		Map<String, HorrorEvent> m = BY_CASE.get(caseKey);
		return m == null ? Collections.emptyList() : new ArrayList<>(m.keySet());
	}
}
