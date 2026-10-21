package com.deadline.director;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/** The compiled definition of a scripted case: its chapters and beats. */
public final class Script {
	public final String caseKey;
	final Map<Integer, Chapter> chapters = new TreeMap<>();
	final List<Beat> beats = new ArrayList<>();
	final Map<String, int[]> locks = new java.util.HashMap<>();

	public Script(String caseKey) {
		this.caseKey = caseKey;
	}

	public Chapter chapter(int n, String checkpoint) {
		Chapter c = new Chapter(n, checkpoint);
		chapters.put(n, c);
		return c;
	}

	public Beat beat(String id) {
		Beat b = new Beat(caseKey + "." + id);
		beats.add(b);
		return b;
	}

	/** A door marker that cannot be opened by hand from chapter `from` until chapter `until` (the script still can). */
	public Script lock(String door, int from, int until) {
		locks.put(door, new int[] {from, until});
		return this;
	}

	public Chapter chapter(int n) {
		return chapters.get(n);
	}

	public int lastChapter() {
		return chapters.isEmpty() ? 0 : ((TreeMap<Integer, Chapter>) chapters).lastKey();
	}

	public Beat find(String id) {
		for (Beat b : beats) {
			if (b.id.equals(id) || b.id.equals(caseKey + "." + id)) {
				return b;
			}
		}
		return null;
	}

	public java.util.Collection<Chapter> chapters() {
		return chapters.values();
	}

	public List<Beat> beats() {
		return beats;
	}
}
