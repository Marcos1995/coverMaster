# Cuatro grupos y el récord de 163.
# 49 al 3 si 6 no son cuatro grupos de 12: son dos bloques, 27 y 22, 86+77=163.
# 24 al 4 si 6 sí cabe en cuatro grupos de 6, juntando cada pareja.
# python cuatro_grupos.py

from itertools import combinations

GARANTIA = 4


def partes(n, g, tope):
    """Repartos de n bolas en g grupos, cada uno con como mucho `tope`, de mayor a menor."""
    out = []

    def walk(queda, huecos, anterior, pref):
        if huecos == 1:
            if 0 <= queda <= anterior:
                out.append(pref + (queda,))
            return
        for c in range(min(anterior, queda), -1, -1):
            walk(queda - c, huecos - 1, c, pref + (c,))

    walk(n, g, tope, ())
    return out


def mejor_pareja(bins):
    m = 0
    for i, j in combinations(range(len(bins)), 2):
        m = max(m, bins[i] + bins[j])
    return m


def demostrar_repartos():
    print("49 al 3 si 6: el récord 163 es 27+22, no cuatro de 12.")
    print("  Si en el 27 hay 4 o más, bastan 86 apuestas (3 si 4).")
    print("  Si no, en el 22 hay 3 o más, y bastan 77 (cada trío dentro de un 6).")
    for a in range(7):
        b = 6 - a
        via = "27" if a >= 4 else "22"
        print(f"  {a} en el 27 y {b} en el 22 -> cubre el bloque {via}")
    print("  86+77=163. Ninguna apuesta mezcla los dos bloques.")
    print("Cuatro grupos de 12 (48 números; uno queda fuera):")
    for extra in (0, 1):
        dentro = 6 - extra
        peor = min(mejor_pareja(b) for b in partes(dentro, 4, 12))
        print(f"  con {extra} acierto fuera, el peor par de grupos junta {peor}")
    print("  El peor par junta 3, no 4: haría falta cubrir tríos en cada pareja, y eso pasa de 163.")
    peor24 = min(mejor_pareja(b) for b in partes(6, 4, 6))
    print(f"24 en cuatro grupos de 6: el peor par de grupos junta {peor24} de los 6.")
    print("  Por eso cada pareja se cubre al 4, y los cuatro sextetos enteros cubren el 4+0.")


def particiones(n=6):
    """Las 10 formas de partir n puntos en dos tríos complementarios."""
    visto = set()
    out = []
    for t in combinations(range(n), 3):
        if t in visto:
            continue
        c = tuple(x for x in range(n) if x not in set(t))
        visto.add(t)
        visto.add(c)
        out.append((t, c))
    return out


def diseno_3_y_3():
    """40 apuestas 3+3: cada trío va con los dos tríos de una partición del otro grupo.

    Cada trío de un lado y cada número del otro coinciden en alguna apuesta.
    """
    pa = particiones()
    pb = particiones()
    tickets = []
    for (a, ac), (b, bc) in zip(pa, pb):
        for ta in (a, ac):
            for tb in (b, bc):
                tickets.append((ta, tb))
    return tickets


def cubrir_pares():
    """Tríos que juntos contienen cada pareja de un grupo de 6."""
    triples = list(combinations(range(6), 3))
    falta = set(combinations(range(6), 2))
    elegidos = []
    while falta:
        mejor = max(triples, key=lambda t: len(falta & set(combinations(t, 2))))
        elegidos.append(mejor)
        falta -= set(combinations(mejor, 2))
    return elegidos


def diseno_2_y_2(cubre):
    """Producto: cada pareja de un grupo y cada pareja del otro caben en un 3+3."""
    return [(ta, tb) for ta in cubre for tb in cubre]


def mascara(grupos, locales):
    bits = 0
    for g, nums in zip(grupos, locales):
        for x in nums:
            bits |= 1 << (6 * g + x)
    return bits


def construir():
    """Cuatro grupos de 6. Cada pareja lleva un 3+3. Cada grupo, su sexteto."""
    pares = list(combinations(range(4), 2))
    cruce = diseno_3_y_3()
    extra = diseno_2_y_2(cubrir_pares())
    apuestas = []
    for g in range(4):
        apuestas.append(((1 << 6) - 1) << (6 * g))
    for g, h in pares:
        vistos = set()
        for ta, tb in cruce + extra:
            m = mascara((g, h), (ta, tb))
            if m not in vistos:
                vistos.add(m)
                apuestas.append(m)
    return apuestas


def sorteos():
    out = []
    for comb in combinations(range(24), 6):
        d = 0
        for x in comb:
            d |= 1 << x
        out.append(d)
    return out


def cubre(draw, ticket):
    return (draw & ticket).bit_count() >= GARANTIA


def quitar_las_que_sobran(apuestas, draws):
    n = len(apuestas)
    cov = [[] for _ in range(n)]
    cuenta = [0] * len(draws)
    for di, d in enumerate(draws):
        for ti, t in enumerate(apuestas):
            if cubre(d, t):
                cov[ti].append(di)
                cuenta[di] += 1
    viva = [True] * n
    cambio = True
    while cambio:
        cambio = False
        for ti in range(n):
            if not viva[ti]:
                continue
            if any(cuenta[di] < 2 for di in cov[ti]):
                continue
            viva[ti] = False
            for di in cov[ti]:
                cuenta[di] -= 1
            cambio = True
    return [t for t, ok in zip(apuestas, viva) if ok]


def fallos(apuestas, draws):
    mal = 0
    for d in draws:
        if not any(cubre(d, t) for t in apuestas):
            mal += 1
    return mal


def main():
    demostrar_repartos()
    cruce = diseno_3_y_3()
    assert len(cruce) == 40
    assert len(particiones()) == 10
    draws = sorteos()
    assert len(draws) == 134596
    brutas = construir()
    mal = fallos(brutas, draws)
    print(f"Construcción por parejas: {len(brutas)} apuestas, sorteos sin 4: {mal}.")
    if mal:
        raise SystemExit(1)
    finas = quitar_las_que_sobran(brutas, draws)
    mal2 = fallos(finas, draws)
    print(f"Tras quitar las que no hacían falta: {len(finas)} apuestas, sorteos sin 4: {mal2}.")
    print("Cada pareja tiene 225 repartos 2+2 y un 3+3 tapa 9: 25 por pareja.")
    print("Las seis parejas no comparten apuestas: 150 como mínimo, por encima de 143.")
    if mal2:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
