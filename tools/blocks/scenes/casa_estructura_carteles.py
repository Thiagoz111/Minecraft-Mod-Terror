# Casa Morales - close-up check of every piece of story signage, as a player standing on the sidewalk sees them:
# the dog sign wired to the railing (the Nona's marker scribble, chapter 1 gag), the same sign screwed to a wall,
# the house number azulejo 1961 (THE clue: the sealed room) and the doorbell 'Morales' on a pier, and the street
# plate 'Pje Las Glicinas' with its numbering strip on the concrete post.
B = []
for x in range(-3, 10):
    for z in range(-4, 3):
        B.append((x, -1, z, 'casa_vereda', 'north'))
# fence: pier, low wall + railing with the Nona sign, pier
B += [(-1, 0, 0, 'casa_pilar', 'north'), (-1, 1, 0, 'casa_pilar_remate', 'north'),
      (0, 0, 0, 'casa_murito', 'north'), (0, 1, 0, 'casa_reja_cartel_perro_nona', 'north'),
      (1, 0, 0, 'casa_murito', 'north'), (1, 1, 0, 'casa_reja', 'north'),
      (2, 0, 0, 'casa_pilar', 'north'), (2, 1, 0, 'casa_pilar_remate', 'north')]
# a rendered wall with the wall sign, the number tile and the doorbell
for x in range(3, 8):
    for y in range(0, 3):
        B.append((x, y, 1, 'casa_revoque_blanco', 'north'))
B += [(4, 1, 0, 'casa_cartel_perro_nona', 'north'), (6, 1, 0, 'casa_numero_1961', 'north'), (6, 0, 0, 'casa_timbre', 'north')]
# the street post with its name plate
B += [(8, 0, -2, 'casa_poste_pie', 'north'), (8, 1, -2, 'casa_poste_cartel_calle', 'north'), (8, 2, -2, 'casa_poste', 'north')]
SCENE = dict(blocks=B, camera=(3.5, 1.5, -3.6), target=(4.0, 1.1, 0.5), fov=72)
