package com.deadline.horror.casa.lore;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The papers of the Casa Morales (docs/design/casa_terror.md 2, Act 3: "lore para el que mira"): what the house
 * tells whoever looks, since nobody in it speaks. Shared by both sides: the server opens a document by id
 * ({@link LoreDocs#open}) and the client draws its pages full screen (com.deadline.client.lore.LoreScreen).
 *
 * <p>A page is a texture (assets/deadline/&lt;texture&gt;, painted by tools/art/sangre.py) with, optionally, a text
 * (lang key) laid over it in the given ink, inside the box x, y, width (texture pixels), one line every `line` pixels.
 * Pages marked `late` only show from Act 4 on (the notebook knows it is being read).
 */
public final class LoreBook {
	public enum Kind {
		/** Paper (letter, notebook, clipping, the back of a photo): the texture with the text written on it. */
		PAPER,
		/** A photograph: the texture inside a white border, slightly askew. */
		PHOTO,
		/** An object seen close (the broken rosary): the texture, and the text under it as a caption. */
		OBJECT
	}

	public record Page(Kind kind, String texture, int w, int h, String text, int ink, int x, int y, int width, int line,
			boolean late) {
	}

	public record Doc(String id, List<Page> pages) {
		/** The pages to show (late pages only when late). */
		public List<Page> pages(boolean late) {
			List<Page> out = new ArrayList<>();
			for (Page p : pages) {
				if (!p.late() || late) {
					out.add(p);
				}
			}
			return out;
		}
	}

	// inks
	public static final int PENCIL = 0xFF3A3A48, CRAYON = 0xFF9E1414, INK = 0xFF1E2238, SEPIA = 0xFF4A3220, PRINT = 0xFF1A1A1A,
			CAPTION = 0xFFC9C0AE;

	// documents
	public static final String CUADERNO = "cuaderno_lucia", NONA_CURA = "foto_nona_cura", NELIDA = "foto_nelida",
			FOTOS_61 = "fotos_1961", CARTAS = "cartas_anselmo", MISAL = "misal_anselmo", ROSARIO = "rosario_roto";

	private static final Map<String, Doc> DOCS = new LinkedHashMap<>();

	static {
		doc(CUADERNO,
				notebook("1", PENCIL, false), notebook("2", PENCIL, false), notebook("3", CRAYON, false),
				notebook("4", PENCIL, false), notebook("5", PENCIL, false), notebook("6", CRAYON, false),
				notebook("7", CRAYON, true));
		doc(NONA_CURA, photo("textures/gui/lore/foto_nona_cura.png", 160, 120), back(NONA_CURA + ".1"));
		doc(NELIDA, photo("textures/gui/lore/foto_nelida.png", 160, 120), back(NELIDA + ".1"));
		doc(FOTOS_61,
				photo("textures/gui/photo/foto_familia_61.png", 128, 96), back(FOTOS_61 + ".1"),
				photo("textures/gui/lore/foto_cama_61.png", 160, 120), back(FOTOS_61 + ".2"),
				new Page(Kind.PAPER, "textures/gui/lore/recorte.png", 192, 256, key(FOTOS_61 + ".3"), PRINT, 14, 16, 164, 10, false));
		doc(CARTAS, letter(CARTAS + ".1"), letter(CARTAS + ".2"), letter(CARTAS + ".3"));
		doc(MISAL, new Page(Kind.PAPER, "textures/gui/lore/misal.png", 192, 256, key(MISAL + ".1"), SEPIA, 22, 26, 148, 11, false));
		doc(ROSARIO, new Page(Kind.OBJECT, "textures/gui/lore/rosario.png", 192, 144, key(ROSARIO + ".1"), CAPTION, 0, 0, 220, 11, false));
	}

	private LoreBook() {
	}

	private static String key(String s) {
		return "deadline.lore." + s;
	}

	private static void doc(String id, Page... pages) {
		DOCS.put(id, new Doc(id, List.of(pages)));
	}

	private static Page notebook(String n, int ink, boolean late) {
		return new Page(Kind.PAPER, "textures/gui/lore/cuaderno.png", 192, 256, key(CUADERNO + "." + n), ink, 32, 25, 148, 12, late);
	}

	private static Page letter(String k) {
		return new Page(Kind.PAPER, "textures/gui/lore/papel.png", 192, 256, key(k), INK, 20, 22, 152, 11, false);
	}

	private static Page photo(String tex, int w, int h) {
		return new Page(Kind.PHOTO, tex, w, h, null, 0, 0, 0, 0, 0, false);
	}

	/** The back of a photo: yellowed card, a few words in faded ink. */
	private static Page back(String k) {
		return new Page(Kind.PAPER, "textures/gui/lore/dorso.png", 192, 144, key(k), SEPIA, 18, 20, 156, 11, false);
	}

	public static Doc get(String id) {
		return DOCS.get(id);
	}

	public static boolean exists(String id) {
		return DOCS.containsKey(id);
	}

	/** Every lang key the documents use (tools check them). */
	public static List<String> keys() {
		List<String> out = new ArrayList<>();
		for (Doc d : DOCS.values()) {
			for (Page p : d.pages()) {
				if (p.text() != null) {
					out.add(p.text());
				}
			}
		}
		return out;
	}
}
