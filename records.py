# El 163 y el 143, por la estructura, no por fuerza bruta.
# python records.py
#
# 49 al 3 si 6 son 163 apuestas:
#   Se parten los 49 en 22 y 27. Ninguna apuesta mezcla los dos.
#   En el 22 va un Steiner S(3,6,22): 77 apuestas, una por cada trío.
#   Sale del código de Golay (el diseño de Witt). 77 es justo: 77*20 = 1540 tríos.
#   En el 27 van 86 apuestas de "3 si 4": cada cuarteto corta alguna en 3 o más.
#   Un sorteo de 6 cae de un lado o del otro:
#     4 o más en el 27 -> responden las 86;
#     si no, hay 3 o más en el 22 -> responden las 77.
#   77+86 = 163. El 22 ya no se puede acortar. El salto de 165 a 163
#   está en el bloque de 27.
#
# 24 al 4 si 6 son 143 apuestas:
#   No admite el mismo corte: un sorteo 3+3 deja los dos lados por debajo de 4.
#   La lista de abajo es la de ese récord. El programa la pasa por los 134596 sorteos.

from itertools import combinations

# Polinomio generador del código de Golay binario de longitud 23.
_GOLAY = (1 << 11) | (1 << 9) | (1 << 7) | (1 << 6) | (1 << 5) | (1 << 1) | 1


def steiner_22():
    """77 bloques de 6 sobre {1..22}. Cada trío está en uno solo."""
    mask23 = (1 << 23) - 1
    bloques = []
    for m in range(1 << 12):
        w = 0
        i = 0
        mm = m
        while mm:
            if mm & 1:
                w ^= _GOLAY << i
            mm >>= 1
            i += 1
        while w >> 23:
            w = (w & mask23) ^ (w >> 23)
        # El bit 23 es la paridad. Pedimos los dos puntos fijos (22 y 23)
        # y peso 8 en el código extendido, así el resto es un hexado.
        if (w.bit_count() & 1) == 0 or ((w >> 22) & 1) == 0 or w.bit_count() != 7:
            continue
        h = w & ((1 << 22) - 1)
        bloques.append(tuple(p + 1 for p in range(22) if (h >> p) & 1))
    return bloques


def record_49(steiner, lado27):
    """77 en el 1..22 y 86 en el 23..49."""
    a = [tuple(b) for b in steiner]
    b = [tuple(n + 22 for n in bloque) for bloque in lado27]
    return a + b


def _cuartetos_cubiertos(bloques):
    vistos = set()
    for bloque in bloques:
        s = set(bloque)
        for c in combinations(s, 4):
            vistos.add(c)
        for c in combinations(s, 3):
            for p in range(1, 28):
                if p not in s:
                    vistos.add(tuple(sorted(c + (p,))))
    return len(vistos)


def _trios_cubiertos(bloques):
    vistos = set()
    for bloque in bloques:
        for c in combinations(bloque, 3):
            vistos.add(c)
    return len(vistos)


def _fallos_24(bloques):
    tickets = []
    for bloque in bloques:
        m = 0
        for n in bloque:
            m |= 1 << (n - 1)
        tickets.append(m)
    mal = 0
    for comb in combinations(range(24), 6):
        d = 0
        for x in comb:
            d |= 1 << x
        if not any((d & t).bit_count() >= 4 for t in tickets):
            mal += 1
    return mal


# Tabla de Lotoideas (Primitiva, Bonoloto, Lototurf, Eurodreams), boletos de 6.
# Columnas: 5 si 6, 4 si 6, 3 si 6, 5 si 5, 4 si 5, 3 si 5, 4 si 4, 3 si 4, 3 si 3.
_COLUMNAS = ((5, 6), (4, 6), (3, 6), (5, 5), (4, 5), (3, 5), (4, 4), (3, 4), (3, 3))
_FILAS = {
    8: (4, None, None, 12, 3, None, 7, 3, 4),
    9: (7, None, None, 30, 3, 2, 12, 3, 7),
    10: (14, 3, 2, 50, 7, 2, 20, 4, 10),
    11: (22, 5, 2, 100, 10, 2, 32, 5, 11),
    12: (38, 6, 2, 132, 14, 2, 41, 6, 15),
    13: (61, 10, 2, 245, 21, 5, 66, 9, 21),
    14: (98, 14, 4, 371, 29, 5, 80, 11, 25),
    15: (142, 19, 4, 578, 40, 7, 117, 14, 31),
    16: (223, 25, 5, 808, 52, 8, 152, 16, 38),
    17: (332, 33, 6, 1546, 66, 11, 188, 20, 44),
    18: (471, 42, 7, 1716, 81, 12, 236, 24, 48),
    19: (646, 54, 9, 2175, 111, 15, 325, 30, 60),
    20: (844, 66, 10, 2850, 139, 18, 382, 35, 71),
    21: (1123, 80, 13, 3908, 169, 21, 484, 40, 77),
    22: (1452, 101, 15, 4676, 189, 22, 580, 46, 77),
    23: (1902, 121, 17, 6161, 229, 26, 716, 54, 104),
    24: (2437, 143, 20, 7084, 267, 30, 784, 61, 116),
    25: (3134, 166, 22, 9321, 334, 34, 992, 68, 130),
    26: (4009, 202, 25, 11544, 390, 39, 1152, 76, 130),
    27: (5076, 222, 27, 14673, 484, 45, 1170, 86, 167),
    28: (6354, 278, 31, 16744, 585, 49, 1489, 97, 185),
    29: (7811, 328, 35, 21046, 714, 55, 1802, 109, 217),
    30: (9468, 391, 39, 24911, 866, 61, 2171, 123, 225),
    31: (11445, 436, 45, 30629, 1037, 68, 2554, 139, 273),
    32: (13744, 519, 49, 35216, 1204, 73, 2791, 153, 300),
    33: (16403, 614, 55, 42785, 1327, 79, 3310, 170, 333),
    34: (19526, 707, 59, 48547, 1560, 86, 3852, 187, 364),
    35: (23033, 816, 65, 57844, 1716, 92, 4418, 198, 405),
    36: (27038, 918, 70, 62832, 1879, 96, 4632, 219, 420),
    37: (31536, 1013, 76, 74993, 2025, 108, 5451, 236, 471),
    38: (36680, 1105, 83, 87135, 2338, 115, 6078, 251, 510),
    39: (42128, 1185, 88, 102651, 2645, 121, 6779, 264, 532),
    40: (48210, 1374, 94, 113900, 2715, 125, 7468, 298, 563),
    41: (54988, 1602, 102, 133259, 3135, 137, 7939, 317, 574),
    42: (62421, 1810, 109, 146031, 3512, 148, 8824, 331, 574),
    43: (70974, 2044, 116, None, 3966, 154, 10101, 357, 667),
    44: (80162, 2329, 123, None, 4435, 154, 11373, 393, 721),
    45: (90437, 2667, 131, None, 4650, 181, 12634, 403, 813),
    46: (101636, 2974, 138, None, 5233, 193, 13691, 436, 869),
    47: (114030, 3259, 145, None, 5650, 207, 15049, 469, 944),
    48: (127522, 3528, 153, None, 6367, 207, 15826, 480, 987),
    49: (142361, 3771, 163, None, 6825, 234, 17615, 530, 1035),
}

_MEMO = {}
_OK = {}
_K = 6


def _bits(nums):
    m = 0
    for n in nums:
        m |= 1 << (n - 1)
    return m


def _comb(n, r):
    if r < 0 or r > n:
        return 0
    c = 1
    for i in range(r):
        c = c * (n - i) // (i + 1)
    return c


def _floja(queda, huecos, tope, g, s, r, t, bins):
    if huecos == 0:
        if queda:
            return False
        return sum(bins[:r]) < t
    c = min(tope, queda, s)
    for v in range(c, -1, -1):
        bins[g - huecos] = v
        if _floja(queda - v, huecos - 1, v, g, s, r, t, bins):
            return True
    return False


def _por_grupos(v, t, m):
    """La estrategia vieja: grupos enteros, si el reparto ya garantiza."""
    mejor = None
    for s in range(2, _K + 1):
        if _K % s or v % s:
            continue
        r = _K // s
        g = v // s
        if g < r:
            continue
        ncomb = _comb(g, r)
        if ncomb < 1 or ncomb > 8000:
            continue
        if _floja(m, g, s, g, s, r, t, [0] * g):
            continue
        tickets = []
        for elegidos in combinations(range(g), r):
            bits = 0
            for e in elegidos:
                bits |= ((1 << s) - 1) << (e * s)
            tickets.append(bits)
        if mejor is None or len(tickets) < len(mejor):
            mejor = tickets
    return mejor


def _avaro(v, t, m):
    nd, nc = _comb(v, m), _comb(v, _K)
    if nd * nc > 600000:
        return None
    draws = [_bits(c) for c in combinations(range(1, v + 1), m)]
    cands = [_bits(c) for c in combinations(range(1, v + 1), _K)]
    cov = [[] for _ in cands]
    quien = [[] for _ in draws]
    for di, d in enumerate(draws):
        for ci, c in enumerate(cands):
            if (d & c).bit_count() >= t:
                cov[ci].append(di)
                quien[di].append(ci)
    score = [len(x) for x in cov]
    vivo = [True] * nd
    quedan = nd
    elegidos = []
    while quedan:
        ci = max(range(nc), key=score.__getitem__)
        if score[ci] <= 0:
            return None
        elegidos.append(cands[ci])
        for di in cov[ci]:
            if not vivo[di]:
                continue
            vivo[di] = False
            quedan -= 1
            for cj in quien[di]:
                score[cj] -= 1
        score[ci] = 0
    return elegidos


def construir(v, t, m):
    """Apuestas de 6 que garantizan t si salen m. None si esta vía no llega."""
    clave = (v, t, m)
    if clave in _MEMO:
        return _MEMO[clave]
    if t > m or t > _K or v < _K or m > v:
        _MEMO[clave] = None
        _OK[clave] = False
        return None
    if (v, t, m) == (22, 3, 3):
        hecho = [_bits(b) for b in steiner_22()]
        _MEMO[clave] = hecho
        _OK[clave] = True
        return hecho
    if (v, t, m) == (27, 3, 4):
        hecho = [_bits(b) for b in BLOQUES_27]
        _MEMO[clave] = hecho
        _OK[clave] = True
        return hecho
    if (v, t, m) == (24, 4, 6):
        hecho = [_bits(b) for b in APUESTAS_24]
        _MEMO[clave] = hecho
        _OK[clave] = True
        return hecho
    mejor = _por_grupos(v, t, m)
    mejor_ok = mejor is not None
    for a in range(_K, v - _K + 1):
        b = v - a
        for j in range(t, m - t + 2):
            mb = m - j + 1
            if mb > b or j > a:
                continue
            wa = construir(a, t, j)
            wb = construir(b, t, mb)
            if not wa or not wb or not _OK.get((a, t, j)) or not _OK.get((b, t, mb)):
                continue
            tickets = list(wa) + [blk << a for blk in wb]
            if mejor is None or len(tickets) < len(mejor):
                mejor = tickets
                mejor_ok = True
    av = _avaro(v, t, m)
    if av and (mejor is None or len(av) < len(mejor)):
        mejor = av
        mejor_ok = True
    _MEMO[clave] = mejor
    _OK[clave] = bool(mejor) and mejor_ok
    return mejor


def _cubre_todo(v, t, m, tickets):
    n = _comb(v, m)
    if n > 8000 or n * len(tickets) > 1500000:
        return None
    for comb in combinations(range(v), m):
        d = 0
        for x in comb:
            d |= 1 << x
        if not any((d & tck).bit_count() >= t for tck in tickets):
            return False
    return True


def probar_tabla():
    print("La ventana: fuerza bruta es el recocido; estrategia son los grupos y, si no cubren, el sorteo suelto; ambas hace las dos.", flush=True)
    print("Esta estrategia es el corte: dos bloques, y en cada uno una reducida más chica. Si no hay corte, grupos.", flush=True)
    print("El 163 y el 143 cubren siempre. El 5 si 6 no admite corte: un 3+3 deja los dos lados por debajo de 5.", flush=True)
    iguales = 0
    cubre = 0
    no = 0
    for v in range(8, 50):
        fila = _FILAS[v]
        for col, (t, m) in enumerate(_COLUMNAS):
            rec = fila[col]
            if rec is None:
                continue
            tickets = construir(v, t, m)
            if not tickets or not _OK.get((v, t, m)):
                no += 1
                continue
            if v <= 12:
                ok = _cubre_todo(v, t, m, tickets)
                if ok is False:
                    print(f"FALLO {v} al {t} si {m}: {len(tickets)} apuestas no cubren.", flush=True)
                    raise SystemExit(1)
            cubre += 1
            if len(tickets) <= rec:
                iguales += 1
                if len(tickets) == rec:
                    print(f"{v} al {t} si {m}: {len(tickets)} apuestas, igual que el récord.", flush=True)
    print(f"Tabla Primitiva (boletos de 6, también al 5): {cubre} casos cubiertos por la estrategia, {iguales} al récord, {no} sin esta vía.", flush=True)


def main():
    steiner = steiner_22()
    trios = _trios_cubiertos(steiner)
    cuartetos = _cuartetos_cubiertos(BLOQUES_27)
    r49 = record_49(steiner, BLOQUES_27)
    mal24 = _fallos_24(APUESTAS_24)
    print(f"22 números, 3 si 3: {len(steiner)} apuestas, tríos cubiertos {trios} de 1540.")
    print(f"27 números, 3 si 4: {len(BLOQUES_27)} apuestas, cuartetos cubiertos {cuartetos} de 17550.")
    print(f"49 al 3 si 6: {len(r49)} apuestas. Un sorteo con menos de 4 en el 27 tiene al menos 3 en el 22.")
    print(f"24 al 4 si 6: {len(APUESTAS_24)} apuestas, sorteos sin 4: {mal24} de 134596.")
    if len(steiner) != 77 or trios != 1540:
        raise SystemExit(1)
    if len(BLOQUES_27) != 86 or cuartetos != 17550:
        raise SystemExit(1)
    if len(r49) != 163 or mal24:
        raise SystemExit(1)
    probar_tabla()


# Patrón 3 si 4 en 27 puntos: cada cuarteto corta un bloque en 3 o más.
BLOQUES_27 = [(1, 2, 3, 6, 9, 25), (1, 2, 3, 9, 15, 16), (1, 2, 5, 9, 10, 21), (1, 2, 9, 13, 14, 18), (1, 3, 5, 6, 18, 25), (1, 4, 8, 19, 26, 27), (1, 4, 17, 20, 23, 24), (1, 6, 10, 13, 15, 25), (1, 6, 14, 16, 21, 25), (1, 7, 8, 11, 17, 19), (1, 7, 12, 20, 24, 26), (1, 8, 12, 19, 22, 23), (1, 8, 19, 20, 24, 25), (1, 11, 20, 22, 24, 27), (2, 3, 8, 13, 21, 24), (2, 3, 10, 14, 20, 24), (2, 4, 6, 20, 26, 27), (2, 4, 7, 9, 19, 22), (2, 4, 11, 12, 19, 25), (2, 5, 8, 14, 15, 24), (2, 5, 13, 16, 19, 20), (2, 6, 7, 11, 17, 20), (2, 6, 12, 20, 22, 23), (2, 7, 19, 23, 25, 27), (2, 8, 9, 11, 23, 26), (2, 8, 10, 16, 18, 24), (2, 8, 12, 17, 25, 27), (2, 8, 15, 18, 19, 21), (2, 17, 19, 22, 25, 26), (3, 4, 5, 10, 26, 27), (3, 4, 5, 14, 17, 22), (3, 4, 7, 12, 18, 21), (3, 4, 10, 11, 13, 23), (3, 5, 7, 14, 23, 26), (3, 5, 11, 12, 14, 27), (3, 5, 12, 21, 22, 23), (3, 6, 15, 16, 19, 24), (3, 7, 10, 13, 22, 27), (3, 7, 11, 15, 16, 18), (3, 8, 9, 10, 14, 19), (3, 8, 15, 16, 20, 25), (3, 9, 13, 19, 20, 21), (3, 10, 12, 13, 17, 26), (3, 11, 18, 21, 22, 26), (3, 17, 18, 21, 23, 27), (4, 5, 7, 12, 13, 15), (4, 5, 11, 16, 18, 23), (4, 6, 7, 8, 22, 25), (4, 6, 8, 9, 11, 12), (4, 7, 10, 12, 14, 16), (4, 9, 24, 25, 26, 27), (4, 10, 15, 17, 18, 22), (4, 11, 13, 14, 17, 26), (4, 11, 14, 15, 21, 23), (4, 12, 15, 16, 23, 26), (4, 13, 16, 17, 21, 22), (5, 6, 10, 19, 21, 24), (5, 7, 10, 17, 18, 21), (5, 7, 16, 18, 22, 27), (5, 8, 9, 13, 16, 24), (5, 8, 10, 20, 21, 25), (5, 9, 14, 15, 19, 20), (5, 11, 13, 15, 22, 26), (5, 12, 16, 17, 18, 26), (5, 13, 15, 17, 23, 27), (6, 7, 8, 9, 23, 27), (6, 8, 9, 17, 22, 26), (6, 9, 12, 17, 19, 27), (6, 11, 19, 23, 25, 26), (6, 13, 14, 18, 19, 24), (7, 9, 11, 17, 24, 25), (7, 10, 15, 18, 23, 26), (7, 11, 12, 17, 22, 27), (7, 13, 16, 21, 23, 26), (7, 14, 15, 21, 22, 27), (8, 13, 14, 18, 20, 25), (9, 10, 16, 18, 19, 20), (9, 12, 22, 23, 24, 25), (9, 15, 18, 20, 21, 24), (10, 11, 12, 15, 18, 27), (10, 11, 14, 16, 22, 26), (10, 13, 14, 15, 16, 21), (10, 14, 16, 17, 23, 27), (11, 12, 13, 16, 21, 27), (12, 14, 15, 17, 21, 26), (13, 14, 18, 22, 23, 27)]

APUESTAS_24 = [(1, 2, 3, 9, 11, 20), (1, 2, 4, 8, 10, 19), (1, 2, 5, 18, 21, 23), (1, 2, 6, 14, 17, 22), (1, 2, 7, 15, 16, 24), (1, 2, 10, 12, 14, 15), (1, 2, 11, 13, 22, 24), (1, 3, 4, 5, 15, 17), (1, 3, 4, 6, 12, 22), (1, 3, 6, 8, 16, 23), (1, 3, 7, 14, 19, 21), (1, 3, 8, 12, 13, 16), (1, 3, 9, 13, 14, 23), (1, 3, 10, 18, 22, 24), (1, 4, 6, 7, 9, 18), (1, 4, 7, 13, 15, 21), (1, 4, 10, 12, 13, 16), (1, 4, 11, 16, 17, 18), (1, 4, 14, 20, 23, 24), (1, 5, 6, 8, 10, 13), (1, 5, 6, 11, 19, 24), (1, 5, 7, 8, 20, 22), (1, 5, 7, 9, 12, 24), (1, 5, 12, 13, 16, 22), (1, 5, 14, 16, 19, 20), (1, 6, 10, 15, 20, 21), (1, 6, 12, 13, 16, 23), (1, 7, 10, 11, 17, 23), (1, 8, 9, 17, 21, 24), (1, 8, 11, 12, 21, 23), (1, 8, 11, 14, 15, 18), (1, 9, 10, 16, 19, 20), (1, 9, 15, 19, 22, 23), (1, 12, 16, 17, 19, 20), (1, 12, 16, 18, 19, 20), (1, 13, 16, 17, 19, 20), (1, 13, 16, 18, 19, 20), (1, 16, 17, 18, 21, 22), (2, 3, 4, 13, 14, 18), (2, 3, 5, 7, 8, 14), (2, 3, 5, 16, 19, 22), (2, 3, 6, 7, 15, 24), (2, 3, 7, 8, 9, 10), (2, 3, 7, 15, 23, 24), (2, 3, 10, 12, 17, 21), (2, 4, 5, 6, 12, 20), (2, 4, 6, 7, 11, 23), (2, 4, 9, 16, 17, 23), (2, 4, 12, 16, 21, 24), (2, 4, 15, 17, 20, 22), (2, 5, 8, 11, 13, 17), (2, 5, 9, 13, 15, 16), (2, 5, 10, 17, 19, 24), (2, 6, 7, 8, 15, 24), (2, 6, 7, 21, 22, 23), (2, 6, 9, 13, 19, 21), (2, 6, 10, 11, 16, 18), (2, 7, 8, 15, 23, 24), (2, 7, 12, 13, 15, 24), (2, 7, 15, 17, 18, 24), (2, 7, 15, 19, 20, 24), (2, 7, 17, 18, 19, 20), (2, 8, 9, 12, 18, 22), (2, 8, 14, 16, 20, 21), (2, 9, 14, 18, 20, 24), (2, 10, 13, 20, 22, 23), (2, 11, 12, 14, 19, 23), (2, 11, 15, 18, 19, 21), (3, 4, 7, 10, 16, 20), (3, 4, 8, 11, 15, 24), (3, 4, 9, 12, 19, 24), (3, 4, 18, 20, 21, 23), (3, 5, 6, 9, 18, 19), (3, 5, 7, 11, 12, 18), (3, 5, 10, 12, 16, 23), (3, 5, 13, 20, 21, 24), (3, 6, 8, 12, 13, 23), (3, 6, 8, 17, 18, 23), (3, 6, 8, 19, 20, 23), (3, 6, 10, 14, 17, 20), (3, 6, 11, 13, 16, 21), (3, 7, 9, 13, 17, 22), (3, 8, 15, 21, 22, 24), (3, 8, 17, 18, 19, 20), (3, 9, 15, 16, 18, 21), (3, 10, 11, 13, 15, 19), (3, 11, 14, 16, 17, 24), (3, 11, 17, 19, 22, 23), (3, 12, 14, 15, 20, 22), (4, 5, 7, 13, 19, 23), (4, 5, 8, 16, 18, 24), (4, 5, 9, 10, 21, 22), (4, 5, 9, 11, 14, 22), (4, 5, 10, 11, 14, 21), (4, 6, 8, 17, 19, 21), (4, 6, 10, 13, 17, 24), (4, 6, 14, 15, 16, 19), (4, 7, 8, 12, 14, 17), (4, 7, 18, 19, 22, 24), (4, 8, 9, 13, 15, 20), (4, 8, 13, 16, 22, 23), (4, 9, 10, 11, 14, 22), (4, 9, 11, 14, 21, 22), (4, 10, 12, 15, 18, 23), (4, 11, 12, 13, 19, 20), (5, 6, 7, 16, 17, 21), (5, 6, 13, 15, 18, 22), (5, 6, 14, 15, 23, 24), (5, 7, 10, 15, 18, 20), (5, 8, 9, 17, 20, 23), (5, 8, 12, 15, 19, 21), (5, 9, 10, 11, 14, 21), (5, 10, 11, 14, 21, 22), (5, 11, 15, 16, 20, 23), (5, 12, 13, 14, 17, 18), (5, 12, 17, 22, 23, 24), (6, 7, 10, 12, 19, 22), (6, 7, 11, 13, 14, 20), (6, 8, 9, 12, 14, 16), (6, 8, 11, 18, 20, 22), (6, 9, 10, 15, 23, 24), (6, 9, 11, 12, 15, 17), (6, 9, 16, 20, 22, 24), (6, 12, 14, 18, 21, 24), (6, 17, 18, 19, 20, 23), (7, 8, 9, 11, 16, 19), (7, 8, 10, 13, 18, 21), (7, 9, 12, 20, 21, 23), (7, 9, 14, 15, 17, 19), (7, 10, 13, 14, 16, 24), (7, 11, 12, 15, 16, 22), (7, 11, 17, 20, 21, 24), (7, 14, 16, 18, 22, 23), (8, 10, 11, 12, 20, 24), (8, 10, 14, 18, 19, 23), (8, 10, 15, 16, 17, 22), (8, 13, 14, 19, 22, 24), (9, 10, 12, 13, 17, 18), (9, 11, 13, 18, 23, 24), (10, 16, 19, 21, 23, 24), (12, 13, 19, 20, 21, 22), (13, 14, 15, 17, 21, 23), (15, 17, 18, 19, 20, 24)]

if __name__ == "__main__":
    main()
