"""
LOTTO OPTIMIZER V3.11 - Pantalla limpia y guardado exclusivo del MEJOR récord
===========================================================================
"""
import io
import math
import os
import random
import sys
import time
import urllib.request
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


def analizar_entrada_numeros(texto: str) -> List[int]:
    numeros = set()
    for parte in texto.replace(',', ' ').split():
        if '-' in parte:
            try:
                inicio, fin = map(int, parte.split('-'))
                numeros.update(range(inicio, fin + 1))
            except ValueError:
                pass
        elif parte.isdigit():
            numeros.add(int(parte))
    return sorted(list(numeros))


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def leer_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print(" Introduce un entero.")


def configurar_consola() -> None:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def escribir_apuestas(v: int, k: int, t: int, listas: List[List[int]], cob: Optional[float] = None, marca: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if marca:
        nombre = f"LOTTO_v{v}_k{k}_t{t}_{marca}_{timestamp}.txt"
    else:
        nombre = f"LOTTO_v{v}_k{k}_t{t}_{cob:.4f}pct_{timestamp}.txt"
    ordenadas = [sorted(nums) for nums in listas]
    ordenadas.sort(key=lambda fila: tuple(fila))
    with open(nombre, "w", encoding="utf-8") as f:
        for nums in ordenadas:
            f.write(" ".join(f"{n:02d}" for n in nums) + "\n")
    return nombre


@dataclass
class CondicionGrupo:
    numeros: List[int]
    min_aciertos: int
    max_aciertos: int
    mascara: int = 0

    def __post_init__(self):
        self.mascara = sum(1 << (n - 1) for n in self.numeros)


@dataclass
class Filtros:
    suma_min: Optional[int] = None
    suma_max: Optional[int] = None
    pares_min: Optional[int] = None
    pares_max: Optional[int] = None
    seguidos_max: Optional[int] = None
    bajos_min: Optional[int] = None
    bajos_max: Optional[int] = None
    por_decena_max: Optional[int] = None
    por_terminacion_max: Optional[int] = None
    distancia_min: Optional[int] = None
    distancia_max: Optional[int] = None
    incluir: List[int] = field(default_factory=list)


def apuesta_pasa_filtros(nums: List[int], filtros: Optional[Filtros], v: int) -> bool:
    if filtros is None:
        return True
    orden = sorted(nums)
    total = sum(orden)
    if filtros.suma_min is not None and total < filtros.suma_min:
        return False
    if filtros.suma_max is not None and total > filtros.suma_max:
        return False
    pares = sum(1 for n in orden if n % 2 == 0)
    if filtros.pares_min is not None and pares < filtros.pares_min:
        return False
    if filtros.pares_max is not None and pares > filtros.pares_max:
        return False
    seguidos = sum(1 for a, b in zip(orden, orden[1:]) if b == a + 1)
    if filtros.seguidos_max is not None and seguidos > filtros.seguidos_max:
        return False
    mitad = max(1, v // 2)
    bajos = sum(1 for n in orden if n <= mitad)
    if filtros.bajos_min is not None and bajos < filtros.bajos_min:
        return False
    if filtros.bajos_max is not None and bajos > filtros.bajos_max:
        return False
    if filtros.por_decena_max is not None:
        decenas: dict[int, int] = {}
        for n in orden:
            dec = (n - 1) // 10
            decenas[dec] = decenas.get(dec, 0) + 1
            if decenas[dec] > filtros.por_decena_max:
                return False
    if filtros.por_terminacion_max is not None:
        finales: dict[int, int] = {}
        for n in orden:
            finales[n % 10] = finales.get(n % 10, 0) + 1
            if finales[n % 10] > filtros.por_terminacion_max:
                return False
    if len(orden) >= 2:
        huecos = [b - a for a, b in zip(orden, orden[1:])]
        if filtros.distancia_min is not None and min(huecos) < filtros.distancia_min:
            return False
        if filtros.distancia_max is not None and max(huecos) > filtros.distancia_max:
            return False
    if filtros.incluir and any(n not in orden for n in filtros.incluir):
        return False
    return True


@dataclass
class Configuracion:
    v: int
    k: int
    t: int
    m: int
    universo_size: int = 50_000
    condiciones_grupos: List[CondicionGrupo] = field(default_factory=list)
    filtros: Optional[Filtros] = None
    mapa: Optional[List[int]] = None
    filtro_v: int = 0


class BitUtils:
    _cache_lista_a_bits = {}
    _cache_bits_a_lista = {}

    @staticmethod
    def lista_a_bits(nums: List[int]) -> int:
        key = tuple(sorted(nums))
        if key in BitUtils._cache_lista_a_bits:
            return BitUtils._cache_lista_a_bits[key]
        resultado = sum(1 << (n - 1) for n in nums)
        if len(BitUtils._cache_lista_a_bits) < 100000:
            BitUtils._cache_lista_a_bits[key] = resultado
        return resultado

    @staticmethod
    def bits_a_lista(bits: int, max_val: int) -> List[int]:
        key = (bits, max_val)
        if key in BitUtils._cache_bits_a_lista:
            return BitUtils._cache_bits_a_lista[key].copy()
        resultado = [i + 1 for i in range(max_val) if bits & (1 << i)]
        if len(BitUtils._cache_bits_a_lista) < 100000:
            BitUtils._cache_bits_a_lista[key] = resultado
        return resultado

    @staticmethod
    def contar_coincidencias(bits1: int, bits2: int) -> int:
        interseccion = bits1 & bits2
        try:
            return interseccion.bit_count()
        except AttributeError:
            return bin(interseccion).count('1')


class MotorMutaciones:
    def __init__(self, config: Configuracion):
        self.config = config

    def mutar(self, bits: int) -> int:
        nums = BitUtils.bits_a_lista(bits, self.config.v)
        disponibles = [n for n in range(1, self.config.v + 1) if n not in nums]
        if not nums or not disponibles:
            return bits
        nums = nums.copy()
        nums.remove(random.choice(nums))
        nums.append(random.choice(disponibles))
        return BitUtils.lista_a_bits(nums)


class LottoOptimizerV3:
    def __init__(self, config: Configuracion):
        self.config = config
        self.universo = [
            BitUtils.lista_a_bits(random.sample(range(1, config.v + 1), config.m))
            for _ in range(config.universo_size)
        ]
        self.total_sorteos = len(self.universo)
        self.por_numero: List[List[int]] = [[] for _ in range(config.v + 1)]
        for i, sorteo in enumerate(self.universo):
            for n in BitUtils.bits_a_lista(sorteo, config.v):
                self.por_numero[n].append(i)
        self.apuestas_bits: List[int] = []
        self.conteos = [0] * self.total_sorteos
        self.cubiertos = 0
        self.temperatura = 1.0
        self.ciclos = 0
        self.mejor_cobertura = 0.0
        self.mejor_apuestas_bits: List[int] = []
        self.mutador = MotorMutaciones(config)
        self._detener = False

    @property
    def cobertura(self) -> float:
        if self.total_sorteos == 0:
            return 0.0
        return (self.cubiertos / self.total_sorteos) * 100

    @property
    def num_apuestas(self) -> int:
        return len(self.apuestas_bits)

    def es_apuesta_valida_por_grupos(self, bits: int) -> bool:
        nums = BitUtils.bits_a_lista(bits, self.config.v)
        if self.config.mapa:
            nums = [self.config.mapa[n - 1] for n in nums]
        tope = self.config.filtro_v or self.config.v
        if not apuesta_pasa_filtros(nums, self.config.filtros, tope):
            return False
        if not self.config.condiciones_grupos:
            return True
        for cond in self.config.condiciones_grupos:
            aciertos = BitUtils.contar_coincidencias(bits, cond.mascara)
            if aciertos < cond.min_aciertos or aciertos > cond.max_aciertos:
                return False
        return True

    def _indices_afectados(self, bits: int):
        vistos = set()
        for n in BitUtils.bits_a_lista(bits, self.config.v):
            for i in self.por_numero[n]:
                if i not in vistos:
                    vistos.add(i)
                    yield i

    def _aplicar_cobertura(self, bits: int, signo: int) -> None:
        t = self.config.t
        for i in self._indices_afectados(bits):
            if BitUtils.contar_coincidencias(bits, self.universo[i]) < t:
                continue
            antes = self.conteos[i]
            self.conteos[i] = antes + signo
            if antes == 0 and self.conteos[i] == 1:
                self.cubiertos += 1
            elif antes == 1 and self.conteos[i] == 0:
                self.cubiertos -= 1

    def agregar_apuesta(self, nums: List[int]) -> None:
        bits = BitUtils.lista_a_bits(nums)
        self.apuestas_bits.append(bits)
        self._aplicar_cobertura(bits, 1)

    def generar_aleatorias(self, cantidad: int) -> None:
        print(f"\nGenerando {cantidad} apuestas... (PULSA Ctrl+C PARA PARAR)")
        generadas = 0
        intentos = 0
        max_intentos = cantidad * 2000

        try:
            while generadas < cantidad and intentos < max_intentos:
                if self._detener:
                    print(f"\n\nGeneración detenida. Apuestas conseguidas: {generadas}.")
                    break
                nums = random.sample(range(1, self.config.v + 1), self.config.k)
                bits = BitUtils.lista_a_bits(nums)
                if self.es_apuesta_valida_por_grupos(bits):
                    self.agregar_apuesta(nums)
                    generadas += 1
                    print(
                        f"\r Progreso: {generadas}/{cantidad} | 🎯 Cobertura actual: {self.cobertura:.4f}%          ",
                        end="",
                        flush=True,
                    )
                intentos += 1
            print()
        except KeyboardInterrupt:
            print(f"\n\n🛑 Generación detenida por ti. Apuestas conseguidas: {generadas}. Pasando a optimización...")
            time.sleep(1)

    def calcular_ganancia(self, idx: int, nueva_bits: int) -> int:
        antigua = self.apuestas_bits[idx]
        cambiados = antigua ^ nueva_bits
        if cambiados == 0:
            return 0
        ganancia = 0
        t = self.config.t
        for i in self._indices_afectados(cambiados):
            sorteo = self.universo[i]
            antes = BitUtils.contar_coincidencias(antigua, sorteo) >= t
            ahora = BitUtils.contar_coincidencias(nueva_bits, sorteo) >= t
            if antes and not ahora:
                if self.conteos[i] == 1:
                    ganancia -= 1
            elif not antes and ahora:
                if self.conteos[i] == 0:
                    ganancia += 1
        return ganancia

    def aplicar_mutacion(self, idx: int, nueva_bits: int) -> None:
        self._aplicar_cobertura(self.apuestas_bits[idx], -1)
        self._aplicar_cobertura(nueva_bits, 1)
        self.apuestas_bits[idx] = nueva_bits

    def _pintar_ciclo(self) -> None:
        print(
            f" 🔄 Ciclo: {self.ciclos:,} | 🎯 Récord Cobertura: {self.mejor_cobertura:.4f}% | 🌡️ Temp: {self.temperatura:.4f}   ",
            end="\r",
            flush=True,
        )

    def _paso(self) -> None:
        self.ciclos += 1
        recorde = False
        idx = random.randint(0, self.num_apuestas - 1)
        nueva_bits = self.mutador.mutar(self.apuestas_bits[idx])
        if nueva_bits != self.apuestas_bits[idx] and self.es_apuesta_valida_por_grupos(nueva_bits):
            ganancia = self.calcular_ganancia(idx, nueva_bits)
            if ganancia > 0 or (
                self.temperatura > 0.0001 and random.random() < math.exp(ganancia / self.temperatura)
            ):
                self.aplicar_mutacion(idx, nueva_bits)
                if self.cobertura > self.mejor_cobertura:
                    self.mejor_cobertura = self.cobertura
                    self.mejor_apuestas_bits = list(self.apuestas_bits)
                    recorde = True
        self.temperatura *= 0.9995
        if recorde or self.ciclos % 100 == 0:
            self._pintar_ciclo()

    def optimizar(self, en_pantalla: bool = True, objetivo: Optional[float] = None) -> None:
        if self.num_apuestas == 0:
            return
        self.mejor_cobertura = self.cobertura
        self.mejor_apuestas_bits = list(self.apuestas_bits)

        if en_pantalla:
            limpiar_pantalla()
            print("=" * 70)
            print(" OPTIMIZANDO - PULSA Ctrl+C EN CUALQUIER MOMENTO PARA SALIR Y GUARDAR")
            print("=" * 70)
        else:
            print("Optimizando. Pulsa Parar para guardar el mejor récord.")

        try:
            while not self._detener:
                self._paso()
                if objetivo is not None and self.mejor_cobertura >= objetivo:
                    print(f"\nCobertura {self.mejor_cobertura:.4f}% alcanza el objetivo {objetivo:.4f}%.")
                    break
            if self._detener:
                print("\nOptimización detenida. Guardando el MEJOR récord histórico...")
        except KeyboardInterrupt:
            print(f"\n\n🛑 ¡Optimización detenida por ti! Guardando el MEJOR récord histórico...")
            time.sleep(1)

    def guardar_mejor_record(self) -> str:
        """Guarda exclusivamente un único archivo con el mejor récord absoluto de la sesión"""
        if not self.mejor_apuestas_bits and self.num_apuestas > 0:
            self.mejor_apuestas_bits = list(self.apuestas_bits)

        cob = self.mejor_cobertura if self.mejor_cobertura > 0 else self.cobertura
        listas = [BitUtils.bits_a_lista(b, self.config.v) for b in self.mejor_apuestas_bits]
        return escribir_apuestas(self.config.v, self.config.k, self.config.t, listas, cob)

    def cargar_lista(self, listas: List[List[int]]) -> None:
        total = len(listas)
        for n, nums in enumerate(listas, 1):
            if self._detener:
                print(f"\nCarga detenida en {n - 1}/{total}.")
                break
            self.agregar_apuesta(nums)
            if n % 500 == 0 or n == total:
                print(
                    f"\r Incorporando récord: {n}/{total} | Cobertura muestra: {self.cobertura:.4f}%   ",
                    end="",
                    flush=True,
                )
        print()


def leer_parametros() -> tuple:
    while True:
        v = leer_entero(" Total números (v): ")
        k = leer_entero(" Números por apuesta (k): ")
        t = leer_entero(" Garantía (t): ")
        m = leer_entero(" Números por sorteo (m): ")
        if v < 1:
            print(" v tiene que ser al menos 1.")
            continue
        if not 1 <= k <= v:
            print(" k tiene que estar entre 1 y v.")
            continue
        if not 1 <= m <= v:
            print(" m tiene que estar entre 1 y v.")
            continue
        tope = min(k, m)
        if not 1 <= t <= tope:
            print(f" t tiene que estar entre 1 y {tope}.")
            continue
        return v, k, t, m


def leer_grupos(v: int, k: int) -> List[CondicionGrupo]:
    if input(" ¿Definir grupos? (s/n): ").lower() != 's':
        return []
    while True:
        num_grupos = leer_entero(" ¿Cuántos grupos?: ")
        if num_grupos >= 1:
            break
        print(" Hace falta al menos un grupo.")
    grupos = []
    for i in range(num_grupos):
        while True:
            nums = analizar_entrada_numeros(input(f" Números Grupo {i + 1} (ej. 1-12): "))
            if not nums or any(n < 1 or n > v for n in nums):
                print(f" El grupo necesita números entre 1 y {v}.")
                continue
            min_ac = leer_entero(f" Mínimo aciertos Grupo {i + 1}: ")
            max_ac = leer_entero(f" Máximo aciertos Grupo {i + 1}: ")
            if min_ac < 0 or min_ac > max_ac or min_ac > k:
                print(f" El mínimo tiene que estar entre 0 y {k}, y no puede superar al máximo.")
                continue
            grupos.append(CondicionGrupo(nums, min_ac, max_ac))
            break
    return grupos


# Reducidas récord públicas de Lotoideas. Clave (v, k, t, m) → zip.
# k es 6. «t si m» garantiza t aciertos cuando m números caen dentro de los v.
REDUCIDAS_LOTOIDEAS: dict[Tuple[int, int, int, int], str] = {
    (8, 6, 3, 3): "https://www.dropbox.com/s/2h18ls30vtcps0y/8-Numeros-al-3-por-4-apuestas-Garantia-3-si-3.zip?dl=1",
    (8, 6, 3, 4): "https://www.dropbox.com/s/n3dae2mkbwwv3f4/8-numeros-por-3-apuestas-Garantia-3-si-4.zip?dl=1",
    (8, 6, 4, 4): "https://www.dropbox.com/s/y6lutblfvpxch6x/8-Numeros-al-4-por-7-apuestas-Garantia-4-si-4.zip?dl=1",
    (8, 6, 4, 5): "https://www.dropbox.com/s/h195854suedsu37/8-numeros-por-3-apuestas-Garantia-4-si-5.zip?dl=1",
    (8, 6, 5, 5): "https://www.dropbox.com/s/c6mroo3dhph312t/8-numeros-al-5-por-12-apuestas-Garantia-5-si-5.zip?dl=1",
    (8, 6, 5, 6): "https://www.dropbox.com/s/kx9xlq20hj5eu07/8-numeros-al-5-por-4-apuestas-Garantia-5-si-6.zip?dl=1",
    (9, 6, 3, 3): "https://www.dropbox.com/s/qu58cygac646ab2/9-Numeros-al-3-por-7-apuestas-Garantia-3-si-3.zip?dl=1",
    (9, 6, 3, 4): "https://www.dropbox.com/s/zbrls7g7r6x843w/9-numeros-por-3-apuestas-Garantia-3-si-4.zip?dl=1",
    (9, 6, 3, 5): "https://www.dropbox.com/s/3x60as0efipuggr/9-numeros-por-2-apuestas-Garantia-3-si-5.zip?dl=1",
    (9, 6, 4, 4): "https://www.dropbox.com/s/jbdflqkordrais0/9-Numeros-al-4-por-12-apuestas-Garantia-4-si-4.zip?dl=1",
    (9, 6, 4, 5): "https://www.dropbox.com/s/80lnyg7x8jt2ljd/9-numeros-por-3-apuestas-Garantia-4-si-5.zip?dl=1",
    (9, 6, 5, 5): "https://www.dropbox.com/s/48o9cyd6chkl0v6/9-numeros-al-5-por-30-apuestas-Garantia-5-si-5.zip?dl=1",
    (9, 6, 5, 6): "https://www.dropbox.com/s/7bya83iur129p4i/9-numeros-al-5-por-7-apuestas-Garantia-5-si-6.zip?dl=1",
    (10, 6, 3, 3): "https://www.dropbox.com/s/c98umy8bkg1dxab/10-Numeros-al-3-por-10-apuestas-Garantia-3-si-3.zip?dl=1",
    (10, 6, 3, 4): "https://www.dropbox.com/s/gx6dakrqikw74rw/10-numeros-por-4-apuestas-Garantia-3-si-4.zip?dl=1",
    (10, 6, 3, 5): "https://www.dropbox.com/s/ickvq9p44x8xwrt/10-numeros-por-2-apuestas-Garantia-3-si-5.zip?dl=1",
    (10, 6, 3, 6): "https://www.dropbox.com/s/hfgxj8wx84vma79/10-Numeros-al-3-por-2-apuestas-Garantia-3-si-6.zip?dl=1",
    (10, 6, 4, 4): "https://www.dropbox.com/s/vsvyrxa1qiwpdpm/10-Numeros-al-4-por-20-apuestas-Garantia-4-si-4.zip?dl=1",
    (10, 6, 4, 5): "https://www.dropbox.com/s/nzcath64lzq7kaw/10-numeros-por-7-apuestas-Garantia-4-si-5.zip?dl=1",
    (10, 6, 4, 6): "https://www.dropbox.com/s/5lzzbjkr0zj2a31/10-Numeros-al-4-por-3-apuestas-Garantia-4-si-6.zip?dl=1",
    (10, 6, 5, 5): "https://www.dropbox.com/s/78n9dk72i3h6b9o/10-numeros-al-5-por-50-apuestas-Garantia-5-si-5.zip?dl=1",
    (10, 6, 5, 6): "https://www.dropbox.com/s/vq498uoipg65iwl/10-numeros-al-5-por-14-apuestas-Garantia-5-si-6.zip?dl=1",
    (11, 6, 3, 3): "https://www.dropbox.com/s/la54gwq9ewonmr3/11-Numeros-al-3-por-11-apuestas-Garantia-3-si-3.zip?dl=1",
    (11, 6, 3, 4): "https://www.dropbox.com/s/10cfkgfsgtxvusw/11-numeros-por-5-apuestas-Garantia-3-si-4.zip?dl=1",
    (11, 6, 3, 5): "https://www.dropbox.com/s/dc4nj07xaxdpqhh/11-numeros-por-2-apuestas-Garantia-3-si-5.zip?dl=1",
    (11, 6, 3, 6): "https://www.dropbox.com/s/dqdbpn10soezsox/11-Numeros-al-3-por-2-apuestas-Garantia-3-si-6.zip?dl=1",
    (11, 6, 4, 4): "https://www.dropbox.com/s/9j9whc59dd4wzf6/11-Numeros-al-4-por-32-apuestas-Garantia-4-si-4.zip?dl=1",
    (11, 6, 4, 5): "https://www.dropbox.com/s/hsr806311q5ie8h/11-numeros-por-10-apuestas-Garantia-4-si-5.zip?dl=1",
    (11, 6, 4, 6): "https://www.dropbox.com/s/mr6hgydra31wnw1/11-Numeros-al-4-por-5-apuestas-Garantia-4-si-6.zip?dl=1",
    (11, 6, 5, 5): "https://www.dropbox.com/s/m5sr85ia9bj4sud/11-numeros-al-5-por-100-apuestas-Garantia-5-si-5.zip?dl=1",
    (11, 6, 5, 6): "https://www.dropbox.com/s/6c61ea6g7nx3i01/11-numeros-al-5-por-22-apuestas-Garantia-5-si-6.zip?dl=1",
    (12, 6, 3, 3): "https://www.dropbox.com/s/mjsbo3txzkq6zl4/12-Numeros-al-3-por-15-apuestas-Garantia-3-si-3.zip?dl=1",
    (12, 6, 3, 4): "https://www.dropbox.com/s/gnrwo47e5hc2gnu/12-numeros-por-6-apuestas-Garantia-3-si-4.zip?dl=1",
    (12, 6, 3, 5): "https://www.dropbox.com/s/ayqvqkg68un4frh/12-numeros-por-2-apuestas-Garantia-3-si-5.zip?dl=1",
    (12, 6, 3, 6): "https://www.dropbox.com/s/wjwz29g9dnyf268/12-Numeros-al-3-por-2-apuestas-Garantia-3-si-6.zip?dl=1",
    (12, 6, 4, 4): "https://www.dropbox.com/s/1a6b67pmo5mmdtw/12-Numeros-al-4-por-41-apuestas-Garantia-4-si-4.zip?dl=1",
    (12, 6, 4, 5): "https://www.dropbox.com/s/itvl51fn1aoiv9q/12-numeros-por-14-apuestas-Garantia-4-si-5.zip?dl=1",
    (12, 6, 4, 6): "https://www.dropbox.com/s/tnyl35ufdfm2yem/12-Numeros-al-4-por-6-apuestas-Garantia-4-si-6.zip?dl=1",
    (12, 6, 5, 5): "https://www.dropbox.com/s/5unb56sttdjjc4y/12-numeros-al-5-por-132-apuestas-Garantia-5-si-5.zip?dl=1",
    (12, 6, 5, 6): "https://www.dropbox.com/s/62oxl2373vx4wp0/12-numeros-al-5-por-38-apuestas-Garantia-5-si-6.zip?dl=1",
    (13, 6, 3, 3): "https://www.dropbox.com/s/enjmsjqv4r1l6e4/13-Numeros-al-3-por-21-apuestas-Garantia-3-si-3.zip?dl=1",
    (13, 6, 3, 4): "https://www.dropbox.com/s/f9ai2tn2hmdhf0h/13-numeros-por-9-apuestas-Garantia-3-si-4.zip?dl=1",
    (13, 6, 3, 5): "https://www.dropbox.com/s/obeyii904l7z2u6/13-numeros-por-5-apuestas-Garantia-3-si-5.zip?dl=1",
    (13, 6, 3, 6): "https://www.dropbox.com/s/d159tr6b1zi18o0/13-Numeros-al-3-por-2-apuestas-Garantia-3-si-6.zip?dl=1",
    (13, 6, 4, 4): "https://www.dropbox.com/s/ai3q5e1nyeaovio/13-Numeros-al-4-por-66-apuestas-Garantia-4-si-4.zip?dl=1",
    (13, 6, 4, 5): "https://www.dropbox.com/s/600mvrqfw1ry9kp/13-numeros-por-21-apuestas-Garantia-4-si-5.zip?dl=1",
    (13, 6, 4, 6): "https://www.dropbox.com/s/fj9d0rmph16jn00/13-Numeros-al-4-por-10-apuestas-Garantia-4-si-6.zip?dl=1",
    (13, 6, 5, 5): "https://www.dropbox.com/s/qx2bkhwzeijaabr/13-numeros-al-5-por-245-apuestas-Garantia-5-si-5.zip?dl=1",
    (13, 6, 5, 6): "https://www.dropbox.com/s/0nm5eg9ffbbh250/13-numeros-al-5-por-61-apuestas-Garantia-5-si-6.zip?dl=1",
    (14, 6, 3, 3): "https://www.dropbox.com/s/vvbe6i20u1c9t7e/14-Numeros-al-3-por-25-apuestas-Garantia-3-si-3.zip?dl=1",
    (14, 6, 3, 4): "https://www.dropbox.com/s/z4ac4fjeygzf2ii/14-numeros-por-11-apuestas-Garantia-3-si-4.zip?dl=1",
    (14, 6, 3, 5): "https://www.dropbox.com/s/atm6243mol8kcq2/14-numeros-por-5-apuestas-Garantia-3-si-5.zip?dl=1",
    (14, 6, 3, 6): "https://www.dropbox.com/s/u5e2sbuily4qn3v/14-Numeros-al-3-por-4-apuestas-Garantia-3-si-6.zip?dl=1",
    (14, 6, 4, 4): "https://www.dropbox.com/s/xrpfhrwiqggvj07/14-Numeros-al-4-por-80-apuestas-Garantia-4-si-4.zip?dl=1",
    (14, 6, 4, 5): "https://www.dropbox.com/s/u7c24qzmf88m3bp/14-numeros-por-29-apuestas-Garantia-4-si-5.zip?dl=1",
    (14, 6, 4, 6): "https://www.dropbox.com/s/m9yzrf16owuflwe/14-Numeros-al-4-por-14-apuestas-Garantia-4-si-6.zip?dl=1",
    (14, 6, 5, 5): "https://www.dropbox.com/s/1erc7jl9dhys894/14-numeros-al-5-por-371-apuestas-Garantia-5-si-5.zip?dl=1",
    (14, 6, 5, 6): "https://www.dropbox.com/s/gccv5svh9jzz86k/14-numeros-al-5-por-98-apuestas-Garantia-5-si-6.zip?dl=1",
    (15, 6, 3, 3): "https://www.dropbox.com/s/rd1kocsna3ikvya/15-Numeros-al-3-por-31-apuestas-Garantia-3-si-3.zip?dl=1",
    (15, 6, 3, 4): "https://www.dropbox.com/s/tldkpqjtbsawx31/15-numeros-por-14-apuestas-Garantia-3-si-4.zip?dl=1",
    (15, 6, 3, 5): "https://www.dropbox.com/s/3wgkgzjurbnfjt8/15-numeros-por-7-apuestas-Garantia-3-si-5.zip?dl=1",
    (15, 6, 3, 6): "https://www.dropbox.com/s/lvr9zcbbh51llj9/15-Numeros-al-3-por-4-apuestas-Garantia-3-si-6.zip?dl=1",
    (15, 6, 4, 4): "https://www.dropbox.com/s/ihwhka7n45ivs6h/15-Numeros-al-4-por-117-apuestas-Garantia-4-si-4.zip?dl=1",
    (15, 6, 4, 5): "https://www.dropbox.com/s/7s2uhz86vj87ql8/15-numeros-por-40-apuestas-Garantia-4-si-5.zip?dl=1",
    (15, 6, 4, 6): "https://www.dropbox.com/s/7h340jo1ggkayoh/15-Numeros-al-4-por-19-apuestas-Garantia-4-si-6.zip?dl=1",
    (15, 6, 5, 5): "https://www.dropbox.com/s/r1nboqbpbuxbbgj/15-numeros-al-5-por-578-apuestas-Garantia-5-si-5.zip?dl=1",
    (15, 6, 5, 6): "https://www.dropbox.com/s/5gp67sc18u8969b/15-numeros-al-5-por-142-apuestas-Garantia-5-si-6.zip?dl=1",
    (16, 6, 3, 3): "https://www.dropbox.com/s/zns08mhsmokq82x/16-Numeros-al-3-por-38-apuestas-Garantia-3-si-3.zip?dl=1",
    (16, 6, 3, 4): "https://www.dropbox.com/s/4f5hrsysv80o1at/16-numeros-por-16-apuestas-Garantia-3-si-4.zip?dl=1",
    (16, 6, 3, 5): "https://www.dropbox.com/s/ua76xrookuat8c4/16-numeros-por-8-apuestas-Garantia-3-si-5.zip?dl=1",
    (16, 6, 3, 6): "https://www.dropbox.com/s/9bc8j5yghfc3rmw/16-Numeros-al-3-por-5-apuestas-Garantia-3-si-6.zip?dl=1",
    (16, 6, 4, 4): "https://www.dropbox.com/s/e60galmf2dtdvy5/16-Numeros-al-4-por-152-apuestas-Garantia-4-si-4.zip?dl=1",
    (16, 6, 4, 5): "https://www.dropbox.com/s/kfnbmbm0fv7fur5/16-numeros-por-52-apuestas-Garantia-4-si-5.zip?dl=1",
    (16, 6, 4, 6): "https://www.dropbox.com/s/7lea3kwlc8xwy9s/16-Numeros-al-4-por-25-apuestas-Garantia-4-si-6.zip?dl=1",
    (16, 6, 5, 5): "https://www.dropbox.com/s/v4rkzhbvnj684d6/16-numeros-al-5-por-808-apuestas-Garantia-5-si-5.zip?dl=1",
    (16, 6, 5, 6): "https://www.dropbox.com/s/8j6hieoo3vxyb21/16-numeros-al-5-por-223-apuestas-Garantia-5-si-6.zip?dl=1",
    (17, 6, 3, 3): "https://www.dropbox.com/s/hrl6cohe0jmqtmw/17-Numeros-al-3-por-44-apuestas-Garantia-3-si-3.zip?dl=1",
    (17, 6, 3, 4): "https://www.dropbox.com/s/g7qwy5jrn7sm9a3/17-numeros-por-20-apuestas-Garantia-3-si-4.zip?dl=1",
    (17, 6, 3, 5): "https://www.dropbox.com/s/hgl5ljbqtp4skyn/17-numeros-por-11-apuestas-Garantia-3-si-5.zip?dl=1",
    (17, 6, 3, 6): "https://www.dropbox.com/s/vc3d891qfd2xrjx/17-Numeros-al-3-por-6-apuestas-Garantia-3-si-6.zip?dl=1",
    (17, 6, 4, 4): "https://www.dropbox.com/s/ku4w79oitiglrj3/17-Numeros-al-4-por-188-apuestas-Garantia-4-si-4.zip?dl=1",
    (17, 6, 4, 5): "https://www.dropbox.com/s/gvgqmu9cwl151ww/17-numeros-por-66-apuestas-Garantia-4-si-5.zip?dl=1",
    (17, 6, 4, 6): "https://www.dropbox.com/s/623yepxdinm4cgm/17-Numeros-al-4-por-33-apuestas-Garantia-4-si-6.zip?dl=1",
    (17, 6, 5, 5): "https://www.dropbox.com/s/ne84f8ekzwd9uue/17-numeros-al-5-por-1.213-apuestas-Garantia-5-si-5.zip?dl=1",
    (17, 6, 5, 6): "https://www.dropbox.com/s/ryfmtc6x0atdo5s/17-numeros-al-5-por-332-apuestas-Garantia-5-si-6.zip?dl=1",
    (18, 6, 3, 3): "https://www.dropbox.com/s/jkosscwubzyqs6i/18-Numeros-al-3-por-48-apuestas-Garantia-3-si-3.zip?dl=1",
    (18, 6, 3, 4): "https://www.dropbox.com/s/rwcitks7n1mxygc/18-numeros-por-24-apuestas-Garantia-3-si-4.zip?dl=1",
    (18, 6, 3, 5): "https://www.dropbox.com/s/4iuj9sdsnbaa0xz/18-numeros-por-12-apuestas-Garantia-3-si-5.zip?dl=1",
    (18, 6, 3, 6): "https://www.dropbox.com/s/7hwstxu5rib9apr/18-Numeros-al-3-por-7-apuestas-Garantia-3-si-6.zip?dl=1",
    (18, 6, 4, 4): "https://www.dropbox.com/s/oei0jyapfvp34dq/18-Numeros-al-4-por-236-apuestas-Garantia-4-si-4.zip?dl=1",
    (18, 6, 4, 5): "https://www.dropbox.com/s/picitwby44l1dbd/18-numeros-por-81-apuestas-Garantia-4-si-5.zip?dl=1",
    (18, 6, 4, 6): "https://www.dropbox.com/s/ljk48v82de5mlyd/18-Numeros-al-4-por-42-apuestas-Garantia-4-si-6.zip?dl=1",
    (18, 6, 5, 5): "https://www.dropbox.com/s/xv84oum33x8od5u/18-numeros-al-5-por-1.546-apuestas-Garantia-5-si-5.zip?dl=1",
    (18, 6, 5, 6): "https://www.dropbox.com/s/69o8jqncvvm0okl/18-numeros-al-5-por-471-apuestas-Garantia-5-si-6.zip?dl=1",
    (19, 6, 3, 3): "https://www.dropbox.com/s/aii9z06h549oaq1/19-Numeros-al-3-por-60-apuestas-Garantia-3-si-3.zip?dl=1",
    (19, 6, 3, 4): "https://www.dropbox.com/s/hs5s3lqqg4yug5b/19-numeros-por-30-apuestas-Garantia-3-si-4.zip?dl=1",
    (19, 6, 3, 5): "https://www.dropbox.com/s/fe45ttkayygv5hm/19-numeros-por-15-apuestas-Garantia-3-si-5.zip?dl=1",
    (19, 6, 3, 6): "https://www.dropbox.com/s/1t9yjh6k7p0haoj/19-Numeros-al-3-por-9-apuestas-Garantia-3-si-6.zip?dl=1",
    (19, 6, 4, 4): "https://www.dropbox.com/s/1iksuu2uzqowxau/19-Numeros-al-4-por-325-apuestas-Garantia-4-si-4.zip?dl=1",
    (19, 6, 4, 5): "https://www.dropbox.com/s/46u1ryx95hg7ib2/19-numeros-por-111-apuestas-Garantia-4-si-5.zip?dl=1",
    (19, 6, 4, 6): "https://www.dropbox.com/s/mx6hfy50v8mit7y/19-Numeros-al-4-por-54-apuestas-Garantia-4-si-6.zip?dl=1",
    (19, 6, 5, 5): "https://www.dropbox.com/s/wnlyqz0pdxljvmo/19-numeros-al-5-por-2.175-apuestas-Garantia-5-si-5.zip?dl=1",
    (19, 6, 5, 6): "https://www.dropbox.com/s/mwlwr5flpky8du7/19-numeros-al-5-por-646-apuestas-Garantia-5-si-6.zip?dl=1",
    (20, 6, 3, 3): "https://www.dropbox.com/s/2hvaks4tiz39fbc/20-Numeros-al-3-por-71-apuestas-Garantia-3-si-3.zip?dl=1",
    (20, 6, 3, 4): "https://www.dropbox.com/s/1j0ruk00gy7f5eo/20-numeros-por-35-apuestas-Garantia-3-si-4.zip?dl=1",
    (20, 6, 3, 5): "https://www.dropbox.com/s/arg5ja5fkg6ajm2/20-numeros-por-18-apuestas-Garantia-3-si-5.zip?dl=1",
    (20, 6, 3, 6): "https://www.dropbox.com/s/4ay3kdghtro5xgb/20-Numeros-al-3-por-10-apuestas-Garantia-3-si-6.zip?dl=1",
    (20, 6, 4, 4): "https://www.dropbox.com/s/5xzbh07cwyqbp9b/20-Numeros-al-4-por-382-apuestas-Garantia-4-si-4.zip?dl=1",
    (20, 6, 4, 5): "https://www.dropbox.com/s/82kmm285ibmy7wg/20-numeros-por-139-apuestas-Garantia-4-si-5.zip?dl=1",
    (20, 6, 4, 6): "https://www.dropbox.com/s/8hqfdf78rhq5l29/20-Numeros-al-4-por-66-apuestas-Garantia-4-si-6.zip?dl=1",
    (20, 6, 5, 5): "https://www.dropbox.com/s/160wqr3wksb9ux1/20-numeros-al-5-por-2.850-apuestas-Garantia-5-si-5.zip?dl=1",
    (20, 6, 5, 6): "https://www.dropbox.com/s/er26nu3qzbn43ds/20-numeros-al-5-por-844-apuestas-Garantia-5-si-6.zip?dl=1",
    (21, 6, 3, 3): "https://www.dropbox.com/s/1ut9v6zb5x6r22l/21-Numeros-al-3-por-77-apuestas-Garantia-3-si-3.zip?dl=1",
    (21, 6, 3, 4): "https://www.dropbox.com/s/j4r38knh24m01va/21-numeros-por-40-apuestas-Garantia-3-si-4.zip?dl=1",
    (21, 6, 3, 5): "https://www.dropbox.com/s/ufz7nx8p3olg8si/21-numeros-por-21-apuestas-Garantia-3-si-5.zip?dl=1",
    (21, 6, 3, 6): "https://www.dropbox.com/s/p7alr3842fo5du6/21-Numeros-al-3-por-13-apuestas-Garantia-3-si-6.zip?dl=1",
    (21, 6, 4, 4): "https://www.dropbox.com/s/747xdokxcwquw6o/21-Numeros-al-4-por-484-apuestas-Garantia-4-si-4.zip?dl=1",
    (21, 6, 4, 5): "https://www.dropbox.com/s/zcjv11nc3t8gi71/21-numeros-por-169-apuestas-Garantia-4-si-5.zip?dl=1",
    (21, 6, 4, 6): "https://www.dropbox.com/s/s595cgxkvdehqyk/21-Numeros-al-4-por-80-apuestas-Garantia-4-si-6.zip?dl=1",
    (21, 6, 5, 5): "https://www.dropbox.com/s/t5a53243ewm0d8o/21-numeros-al-5-por-3.908-apuestas-Garantia-5-si-5.zip?dl=1",
    (21, 6, 5, 6): "https://www.dropbox.com/s/bxez1ifk4jbfng4/21-numeros-al-5-por-1.123-apuestas-Garantia-5-si-6.zip?dl=1",
    (22, 6, 3, 3): "https://www.dropbox.com/s/zo9fddgzveqqiv9/22-Numeros-al-3-por-77-apuestas-Garantia-3-si-3.zip?dl=1",
    (22, 6, 3, 4): "https://www.dropbox.com/s/gmd650oyzb44cr6/22-numeros-por-46-apuestas-Garantia-3-si-4.zip?dl=1",
    (22, 6, 3, 5): "https://www.dropbox.com/s/22stumzlqysx4p2/22-numeros-por-22-apuestas-Garantia-3-si-5.zip?dl=1",
    (22, 6, 3, 6): "https://www.dropbox.com/s/9qn5lknxg3iuhku/22-Numeros-al-3-por-15-apuestas-Garantia-3-si-6.zip?dl=1",
    (22, 6, 4, 4): "https://www.dropbox.com/s/t4eup3fgevgrjue/22-Numeros-al-4-por-580-apuestas-Garantia-4-si-4.zip?dl=1",
    (22, 6, 4, 5): "https://www.dropbox.com/s/q8w4hafzgi95tem/22-numeros-por-189-apuestas-Garantia-4-si-5.zip?dl=1",
    (22, 6, 4, 6): "https://www.dropbox.com/s/h3rwjnotuavwtnk/22-Numeros-al-4-por-101-apuestas-Garantia-4-si-6.zip?dl=1",
    (22, 6, 5, 5): "https://www.dropbox.com/s/li23z5pybgutoss/22-numeros-al-5-por-4.676-apuestas-Garantia-5-si-5.zip?dl=1",
    (22, 6, 5, 6): "https://www.dropbox.com/s/wklt5gakg5k6y2w/22-numeros-al-5-por-1.452-apuestas-Garantia-5-si-6.zip?dl=1",
    (23, 6, 3, 3): "https://www.dropbox.com/s/72yea84l1xopegk/23-Numeros-al-3-por-104-apuestas-Garantia-3-si-3.zip?dl=1",
    (23, 6, 3, 4): "https://www.dropbox.com/s/v0sb8xwn2m89ylv/23-numeros-por-54-apuestas-Garantia-3-si-4.zip?dl=1",
    (23, 6, 3, 5): "https://www.dropbox.com/s/gttlwl6yvbevn6q/23-numeros-por-26-apuestas-Garantia-3-si-5.zip?dl=1",
    (23, 6, 3, 6): "https://www.dropbox.com/s/cssu6auwnuvhag1/23-Numeros-al-3-por-17-apuestas-Garantia-3-si-6.zip?dl=1",
    (23, 6, 4, 4): "https://www.dropbox.com/s/721ec3t4o6oosi3/23-Numeros-al-4-por-716-apuestas-Garantia-4-si-4.zip?dl=1",
    (23, 6, 4, 5): "https://www.dropbox.com/s/yvc4j41817h4k25/23-numeros-por-229-apuestas-Garantia-4-si-5.zip?dl=1",
    (23, 6, 4, 6): "https://www.dropbox.com/s/wzjju4sit2ch3bl/23-Numeros-al-4-por-121-apuestas-Garantia-4-si-6.zip?dl=1",
    (23, 6, 5, 5): "https://www.dropbox.com/s/cxziow3gy1lsr2j/23-numeros-al-5-por-6.161-apuestas-Garantia-5-si-5.zip?dl=1",
    (23, 6, 5, 6): "https://www.dropbox.com/s/h0vrbed5e52ualt/23-numeros-al-5-por-1.902-apuestas-Garantia-5-si-6.zip?dl=1",
    (24, 6, 3, 3): "https://www.dropbox.com/s/jyhrgj7i2qie410/24-Numeros-al-3-por-116-apuestas-Garantia-3-si-3.zip?dl=1",
    (24, 6, 3, 4): "https://www.dropbox.com/s/yvlnijadxadfu6l/24-numeros-por-61-apuestas-Garantia-3-si-4.zip?dl=1",
    (24, 6, 3, 5): "https://www.dropbox.com/s/eyt5ke2beu1wepy/24-numeros-por-30-apuestas-Garantia-3-si-5.zip?dl=1",
    (24, 6, 3, 6): "https://www.dropbox.com/s/zzhd2ku67nz99wa/24-Numeros-al-3-por-20-apuestas-Garantia-3-si-6.zip?dl=1",
    (24, 6, 4, 4): "https://www.dropbox.com/s/1bx8w3sra02qg6l/24-Numeros-al-4-por-784-apuestas-Garantia-4-si-4.zip?dl=1",
    (24, 6, 4, 5): "https://www.dropbox.com/s/ss0avi68m5g6s1l/24-numeros-por-267-apuestas-Garantia-4-si-5.zip?dl=1",
    (24, 6, 4, 6): "https://www.dropbox.com/s/olx0gjyfvs22sm3/24-Numeros-al-4-por-143-apuestas-Garantia-4-si-6.zip?dl=1",
    (24, 6, 5, 5): "https://www.dropbox.com/s/kmwinaggdgd1zgp/24-numeros-al-5-por-7.084-apuestas-Garantia-5-si-5.zip?dl=1",
    (24, 6, 5, 6): "https://www.dropbox.com/s/oug1zx0suq5atop/24-numeros-al-5-por-2.437-apuestas-Garantia-5-si-6.zip?dl=1",
    (25, 6, 3, 3): "https://www.dropbox.com/s/maen1fex6514ei2/25-Numeros-al-3-por-130-apuestas-Garantia-3-si-3.zip?dl=1",
    (25, 6, 3, 4): "https://www.dropbox.com/s/s7e0q2x3p3krtix/25-numeros-por-68-apuestas-Garantia-3-si-4.zip?dl=1",
    (25, 6, 3, 5): "https://www.dropbox.com/s/ozk63t01g4zs84b/25-numeros-por-34-apuestas-Garantia-3-si-5.zip?dl=1",
    (25, 6, 3, 6): "https://www.dropbox.com/s/0hub8fr74q8vi5c/25-Numeros-al-3-por-22-apuestas-Garantia-3-si-6.zip?dl=1",
    (25, 6, 4, 4): "https://www.dropbox.com/s/r5np4oljabg3b45/25-Numeros-al-4-por-992-apuestas-Garantia-4-si-4.zip?dl=1",
    (25, 6, 4, 5): "https://www.dropbox.com/s/7317g27nbcxqpxc/25-numeros-por-334-apuestas-Garantia-4-si-5.zip?dl=1",
    (25, 6, 4, 6): "https://www.dropbox.com/s/co8vaug1aq9p9x7/25-Numeros-al-4-por-166-apuestas-Garantia-4-si-6.zip?dl=1",
    (25, 6, 5, 5): "https://www.dropbox.com/s/m4ac6l5q0opv6pt/25-numeros-al-5-por-9.321-apuestas-Garantia-5-si-5.zip?dl=1",
    (25, 6, 5, 6): "https://www.dropbox.com/s/ubxp5gfthz10e5n/25-numeros-al-5-por-3.134-apuestas-Garantia-5-si-6.zip?dl=1",
    (26, 6, 3, 3): "https://www.dropbox.com/s/xtts9fz0pp7zkb1/26-Numeros-al-3-por-130-apuestas-Garantia-3-si-3.zip?dl=1",
    (26, 6, 3, 4): "https://www.dropbox.com/s/cdg5p7d7oykydku/26-numeros-por-76-apuestas-Garantia-3-si-4.zip?dl=1",
    (26, 6, 3, 5): "https://www.dropbox.com/s/ygyeuw1xixqa38x/26-numeros-por-39-apuestas-Garantia-3-si-5.zip?dl=1",
    (26, 6, 3, 6): "https://www.dropbox.com/s/1mscywpigyopev6/26-Numeros-al-3-por-25-apuestas-Garantia-3-si-6.zip?dl=1",
    (26, 6, 4, 4): "https://www.dropbox.com/s/cudmecbxpjw9cj4/26-Numeros-al-4-por-1.152-apuestas-Garantia-4-si-4.zip?dl=1",
    (26, 6, 4, 6): "https://www.dropbox.com/s/8eohay2dh7edaod/26-Numeros-al-4-por-202-apuestas-Garantia-4-si-6.zip?dl=1",
    (27, 6, 3, 3): "https://www.dropbox.com/s/rfa67wsblo10hlo/27-Numeros-al-3-por-167-apuestas-Garantia-3-si-3.zip?dl=1",
    (27, 6, 3, 4): "https://www.dropbox.com/s/jwtipvwgeciy1fh/27-numeros-por-86-apuestas-Garantia-3-si-4.zip?dl=1",
    (27, 6, 3, 5): "https://www.dropbox.com/s/bz4aum27zi5ksga/27-numeros-por-45-apuestas-Garantia-3-si-5.zip?dl=1",
    (27, 6, 3, 6): "https://www.dropbox.com/s/c90qo6k26oq79as/27-Numeros-al-3-por-27-apuestas-Garantia-3-si-6.zip?dl=1",
    (27, 6, 4, 4): "https://www.dropbox.com/s/xdpa91wgxowzu1k/27-Numeros-al-4-por-1.170-apuestas-Garantia-4-si-4.zip?dl=1",
    (27, 6, 4, 5): "https://www.dropbox.com/s/ok9fdi20e3itdrd/27-numeros-por-484-apuestas-Garantia-4-si-5.zip?dl=1",
    (27, 6, 4, 6): "https://www.dropbox.com/s/z6ktpvvvhx85jby/27-Numeros-al-4-por-222-apuestas-Garantia-4-si-6.zip?dl=1",
    (28, 6, 3, 3): "https://www.dropbox.com/s/rs03ripf5zeox1k/28-Numeros-al-3-por-185-apuestas-Garantia-3-si-3.zip?dl=1",
    (28, 6, 3, 4): "https://www.dropbox.com/s/hvro1x96ctzaugl/28-numeros-por-97-apuestas-Garantia-3-si-4.zip?dl=1",
    (28, 6, 3, 5): "https://www.dropbox.com/s/vuis1lzmvew350m/28-numeros-por-49-apuestas-Garantia-3-si-5.zip?dl=1",
    (28, 6, 3, 6): "https://www.dropbox.com/s/qj29m1gdqs843sw/28-Numeros-al-3-por-31-apuestas-Garantia-3-si-6.zip?dl=1",
    (28, 6, 4, 4): "https://www.dropbox.com/s/fsbzkk9b2eokrja/28-Numeros-al-4-por-1.489-apuestas-Garantia-4-si-4.zip?dl=1",
    (28, 6, 4, 5): "https://www.dropbox.com/s/mmksnvy4njyt77o/28-numeros-por-585-apuestas-Garantia-4-si-5.zip?dl=1",
    (28, 6, 4, 6): "https://www.dropbox.com/s/y57t6giwo2xxj97/28-Numeros-al-4-por-278-apuestas-Garantia-4-si-6.zip?dl=1",
    (28, 6, 5, 5): "https://www.dropbox.com/s/4i2jevchnsw74uu/28-numeros-al-5-por-16.744-apuestas-Garantia-5-si-5.zip?dl=1",
    (29, 6, 3, 3): "https://www.dropbox.com/s/b9y87pjjjo19bdn/29-Numeros-al-3-por-217-apuestas-Garantia-3-si-3.zip?dl=1",
    (29, 6, 3, 4): "https://www.dropbox.com/s/abi2b0u5odt1xpc/29-numeros-por-109-apuestas-Garantia-3-si-4.zip?dl=1",
    (29, 6, 3, 5): "https://www.dropbox.com/s/d3dr0o1ayy37l1c/29-numeros-por-55-apuestas-Garantia-3-si-5.zip?dl=1",
    (29, 6, 3, 6): "https://www.dropbox.com/s/7m6g0nme1l8g2q0/29-Numeros-al-3-por-35-apuestas-Garantia-3-si-6.zip?dl=1",
    (29, 6, 4, 4): "https://www.dropbox.com/s/j1gxu62zgp8c3il/29-Numeros-al-4-por-1.802-apuestas-Garantia-4-si-4.zip?dl=1",
    (29, 6, 4, 6): "https://www.dropbox.com/s/j9vtvd07b393l46/29-numeros-al-4-por-328-apuestas-Garantia-4-si-6.zip?dl=1",
    (29, 6, 5, 6): "https://www.dropbox.com/s/a1rms700516bdln/29-numeros-al-5-por-7.811-apuestas-Garantia-5-si-6.zip?dl=1",
    (30, 6, 3, 3): "https://www.dropbox.com/s/7dpo84mko4mrnm6/30-Numeros-al-3-por-225-apuestas-Garantia-3-si-3.zip?dl=1",
    (30, 6, 3, 4): "https://www.dropbox.com/s/rf5qv1c4n7n3rjy/30-numeros-por-123-apuestas-Garantia-3-si-4.zip?dl=1",
    (30, 6, 3, 5): "https://www.dropbox.com/s/z29o9mgjwhs75m0/30-numeros-por-61-apuestas-Garantia-3-si-5.zip?dl=1",
    (30, 6, 3, 6): "https://www.dropbox.com/s/j7k2eqphzf8anba/30-Numeros-al-3-por-39-apuestas-Garantia-3-si-6.zip?dl=1",
    (30, 6, 4, 4): "https://www.dropbox.com/s/29cx5qxbzoa7evh/30-Numeros-al-4-por-2.171-apuestas-Garantia-4-si-4.zip?dl=1",
    (30, 6, 4, 5): "https://www.dropbox.com/s/o1cvwlv7tkwf2xe/30-numeros-por-866-apuestas-Garantia-4-si-5.zip?dl=1",
    (30, 6, 4, 6): "https://www.dropbox.com/s/ob09rwnq18451j0/30-numeros-al-4-por-391-apuestas-Garantia-4-si-6.zip?dl=1",
    (31, 6, 3, 3): "https://www.dropbox.com/s/ou6i4uxsh1yg0v5/31-Numeros-al-3-por-273-apuestas-Garantia-3-si-3.zip?dl=1",
    (31, 6, 3, 4): "https://www.dropbox.com/s/1eskft4bnmkbt28/31-numeros-por-139-apuestas-Garantia-3-si-4.zip?dl=1",
    (31, 6, 3, 5): "https://www.dropbox.com/s/acam8qz73f5ssvr/31-numeros-por-68-apuestas-Garantia-3-si-5.zip?dl=1",
    (31, 6, 3, 6): "https://www.dropbox.com/s/rr90g89sh1f9tk1/31-Numeros-al-3-por-45-apuestas-Garantia-3-si-6.zip?dl=1",
    (31, 6, 4, 5): "https://www.dropbox.com/s/vgvnbnfoaot2e7y/31-numeros-por-1.037-apuestas-Garantia-4-si-5.zip?dl=1",
    (31, 6, 4, 6): "https://www.dropbox.com/s/liv5nqzv6fqji9q/31-numeros-al-4-por-436-apuestas-Garantia-4-si-6.zip?dl=1",
    (32, 6, 3, 3): "https://www.dropbox.com/s/sf0wo79tu0d8yw6/32-Numeros-al-3-por-300-apuestas-Garantia-3-si-3.zip?dl=1",
    (32, 6, 3, 4): "https://www.dropbox.com/s/dvaw22cnnvt1ekf/32-numeros-por-153-apuestas-Garantia-3-si-4.zip?dl=1",
    (32, 6, 3, 5): "https://www.dropbox.com/s/h9ss8grm6lrx9u5/32-numeros-por-73-apuestas-Garantia-3-si-5.zip?dl=1",
    (32, 6, 3, 6): "https://www.dropbox.com/s/78g96ewahjjionn/32-Numeros-al-3-por-49-apuestas-Garantia-3-si-6.zip?dl=1",
    (32, 6, 4, 6): "https://www.dropbox.com/s/0sudy10h7oi2e66/32-numeros-al-4-por-519-apuestas-Garantia-4-si-6.zip?dl=1",
    (32, 6, 5, 5): "https://www.dropbox.com/s/7j61fllk4176jlh/32-numeros-al-5-por-35.216-apuestas-Garantia-5-si-5.zip?dl=1",
    (33, 6, 3, 3): "https://www.dropbox.com/s/mdhe2lagehxva5l/33-Numeros-al-3-por-333-apuestas-Garantia-3-si-3.zip?dl=1",
    (33, 6, 3, 4): "https://www.dropbox.com/s/0vbn8brmhu6x2cy/33-numeros-por-170-apuestas-Garantia-3-si-4.zip?dl=1",
    (33, 6, 3, 5): "https://www.dropbox.com/s/ceaky89uijxjcjn/33-numeros-por-79-apuestas-Garantia-3-si-5.zip?dl=1",
    (33, 6, 3, 6): "https://www.dropbox.com/s/mjfmiocb648i1q0/33-Numeros-al-3-por-55-apuestas-Garantia-3-si-6.zip?dl=1",
    (33, 6, 4, 4): "https://www.dropbox.com/s/b90h5mgtzaydy8u/33-Numeros-al-4-por-3.310-apuestas-Garantia-4-si-4.zip?dl=1",
    (33, 6, 4, 5): "https://www.dropbox.com/s/pbzpdkgcja4xpo8/33-numeros-por-1.327-apuestas-Garantia-4-si-5.zip?dl=1",
    (33, 6, 4, 6): "https://www.dropbox.com/s/e24pc9fhvvv1htj/33-numeros-al-4-por-614-apuestas-Garantia-4-si-6.zip?dl=1",
    (34, 6, 3, 3): "https://www.dropbox.com/s/mk9qtauztkkz15p/34-Numeros-al-3-por-364-apuestas-Garantia-3-si-3.zip?dl=1",
    (34, 6, 3, 4): "https://www.dropbox.com/s/sx70qmy7bkzg0p2/34-numeros-por-187-apuestas-Garantia-3-si-4.zip?dl=1",
    (34, 6, 3, 5): "https://www.dropbox.com/s/opgt0ihq6tf0zv1/34-numeros-por-86-apuestas-Garantia-3-si-5.zip?dl=1",
    (34, 6, 3, 6): "https://www.dropbox.com/s/18748owkl34sz7o/34-Numeros-al-3-por-59-apuestas-Garantia-3-si-6.zip?dl=1",
    (34, 6, 4, 6): "https://www.dropbox.com/s/stgjrlrhj9tyvr4/34-numeros-al-4-por-707-apuestas-Garantia-4-si-6.zip?dl=1",
    (35, 6, 3, 3): "https://www.dropbox.com/s/xia2cq8kkfvxup7/35-numeros-al-3-por-405-apuestas-Garantia-3-si-3.zip?dl=1",
    (35, 6, 3, 4): "https://www.dropbox.com/s/l1duq62b5zh1lgl/35-numeros-por-198-apuestas-Garantia-3-si-4.zip?dl=1",
    (35, 6, 3, 5): "https://www.dropbox.com/s/nujf0i3r24tbhfz/35-numeros-por-92-apuestas-Garantia-3-si-5.zip?dl=1",
    (35, 6, 3, 6): "https://www.dropbox.com/s/2xjw5d6xdje5hb3/35-Numeros-al-3-por-65-apuestas-Garantia-3-si-6.zip?dl=1",
    (35, 6, 4, 5): "https://www.dropbox.com/s/8u9kk5bpj0tpnns/35-numeros-por-1.716-apuestas-Garantia-4-si-5.zip?dl=1",
    (35, 6, 4, 6): "https://www.dropbox.com/s/6tpjdkev978b5sr/35-numeros-al-4-por-816-apuestas-Garantia-4-si-6.zip?dl=1",
    (36, 6, 3, 3): "https://www.dropbox.com/s/kqz6gd9nwppv9d6/36-Numeros-al-3-por-420-apuestas-Garantia-3-si-3.zip?dl=1",
    (36, 6, 3, 4): "https://www.dropbox.com/s/da5k4k5409zaobj/36-numeros-por-219-apuestas-Garantia-3-si-4.zip?dl=1",
    (36, 6, 3, 5): "https://www.dropbox.com/s/emqu1gl41asesqs/36-numeros-por-96-apuestas-Garantia-3-si-5.zip?dl=1",
    (36, 6, 3, 6): "https://www.dropbox.com/s/atrdcp47zt7ea0h/36-Numeros-al-3-por-70-apuestas-Garantia-3-si-6.zip?dl=1",
    (36, 6, 4, 4): "https://www.dropbox.com/s/jow8u30yzwgm9zf/36-Numeros-al-4-por-4.632-apuestas-Garantia-4-si-4.zip?dl=1",
    (36, 6, 4, 5): "https://www.dropbox.com/s/5vba0i7kglic9lj/36-numeros-por-1.879-apuestas-Garantia-4-si-5.zip?dl=1",
    (36, 6, 4, 6): "https://www.dropbox.com/s/8ir0k1kt5sug4ct/36-numeros-al-4-por-918-apuestas-Garantia-4-si-6.zip?dl=1",
    (36, 6, 5, 5): "https://www.dropbox.com/s/us77v8ty8rb9s0v/36-numeros-al-5-por-62.832-apuestas-Garantia-5-si-5.zip?dl=1",
    (37, 6, 3, 4): "https://www.dropbox.com/s/933p2y9clt6z11g/37-numeros-por-236-apuestas-Garantia-3-si-4.zip?dl=1",
    (37, 6, 3, 5): "https://www.dropbox.com/s/nxfwy1t0wufghr0/37-numeros-por-108-apuestas-Garantia-3-si-5.zip?dl=1",
    (37, 6, 3, 6): "https://www.dropbox.com/s/6ra1thqcftetuw4/37-Numeros-al-3-por-76-apuestas-Garantia-3-si-6.zip?dl=1",
    (37, 6, 4, 4): "https://www.dropbox.com/s/99vg49h3veuxuo1/37-Numeros-al-4-por-5.451-apuestas-Garantia-4-si-4.zip?dl=1",
    (37, 6, 4, 5): "https://www.dropbox.com/s/5ymhsq093k229am/37-numeros-por-2.025-apuestas-Garantia-4-si-5.zip?dl=1",
    (37, 6, 4, 6): "https://www.dropbox.com/s/f821uldo4fpt6ri/37-numeros-al-4-por-1.013-apuestas-Garantia-4-si-6.zip?dl=1",
    (37, 6, 5, 5): "https://www.dropbox.com/s/rb4hu1cvz4ud1tj/37-numeros-al-5-por-74.993-apuestas-Garantia-5-si-5.zip?dl=1",
    (38, 6, 3, 3): "https://www.dropbox.com/s/0pn9sfqdfxue3y1/38-Numeros-al-3-por-510-apuestas-Garantia-3-si-3.zip?dl=1",
    (38, 6, 3, 4): "https://www.dropbox.com/s/40hixqq4utdow5o/38-numeros-por-251-apuestas-Garantia-3-si-4.zip?dl=1",
    (38, 6, 3, 5): "https://www.dropbox.com/s/n3dw20w8yoet7oi/38-numeros-por-115-apuestas-Garantia-3-si-5.zip?dl=1",
    (38, 6, 3, 6): "https://www.dropbox.com/s/8patfb7qld47jn4/38-Numeros-al-3-por-83-apuestas-Garantia-3-si-6.zip?dl=1",
    (39, 6, 3, 4): "https://www.dropbox.com/s/gjq2ju53q062xxc/39-numeros-por-264-apuestas-Garantia-3-si-4.zip?dl=1",
    (39, 6, 3, 5): "https://www.dropbox.com/s/1tybccjmlc6zxnv/39-numeros-por-121-apuestas-Garantia-3-si-5.zip?dl=1",
    (39, 6, 3, 6): "https://www.dropbox.com/s/0gxpgmtzm5tdq9f/39-Numeros-al-3-por-88-apuestas-Garantia-3-si-6.zip?dl=1",
    (39, 6, 4, 5): "https://www.dropbox.com/s/2edrzx6uaydju9i/39-numeros-por-2.645-apuestas-Garantia-4-si-5.zip?dl=1",
    (39, 6, 4, 6): "https://www.dropbox.com/s/8zw3jrj6fslpjli/39-numeros-al-4-por-1.185-apuestas-Garantia-4-si-6.zip?dl=1",
    (40, 6, 3, 4): "https://www.dropbox.com/s/adq2dwh3c5fsjx9/40-numeros-por-298-apuestas-Garantia-3-si-4.zip?dl=1",
    (40, 6, 3, 5): "https://www.dropbox.com/s/7p3jlo5j9glp06l/40-numeros-por-125-apuestas-Garantia-3-si-5.zip?dl=1",
    (40, 6, 3, 6): "https://www.dropbox.com/s/pj5ykh606j7nqta/40-Numeros-al-3-por-94-apuestas-Garantia-3-si-6.zip?dl=1",
    (40, 6, 4, 5): "https://www.dropbox.com/s/k6ngpsw9i5ee5b6/40-numeros-por-2.715-apuestas-Garantia-4-si-5.zip?dl=1",
    (40, 6, 4, 6): "https://www.dropbox.com/s/yx198qxp5gflvhk/40-numeros-al-4-por-1.374-apuestas-Garantia-4-si-6.zip?dl=1",
    (41, 6, 3, 4): "https://www.dropbox.com/s/89w810xupumqf30/41-numeros-por-317-apuestas-Garantia-3-si-4.zip?dl=1",
    (41, 6, 3, 5): "https://www.dropbox.com/s/610usuv3nq4famz/41-numeros-por-137-apuestas-Garantia-3-si-5.zip?dl=1",
    (41, 6, 3, 6): "https://www.dropbox.com/s/4afz0kc9aizp9zm/41-Numeros-al-3-por-102-apuestas-Garantia-3-si-6.zip?dl=1",
    (41, 6, 4, 5): "https://www.dropbox.com/s/7bvxzjqeev4hjm8/41-numeros-por-3.135-apuestas-Garantia-4-si-5.zip?dl=1",
    (41, 6, 4, 6): "https://www.dropbox.com/s/ade2vk06dpgu395/41-numeros-al-4-por-1.602-apuestas-Garantia-4-si-6.zip?dl=1",
    (42, 6, 3, 4): "https://www.dropbox.com/s/cz57tis035evnlt/42-numeros-por-331-apuestas-Garantia-3-si-4.zip?dl=1",
    (42, 6, 3, 5): "https://www.dropbox.com/s/u61dtck3iol5bmo/42-numeros-por-148-apuestas-Garantia-3-si-5.zip?dl=1",
    (42, 6, 3, 6): "https://www.dropbox.com/s/fyl3gd67zu9f1lc/42-Numeros-al-3-por-109-apuestas-Garantia-3-si-6.zip?dl=1",
    (42, 6, 4, 5): "https://www.dropbox.com/s/qyht0ip8u2ixxi6/42-numeros-por-3.512-apuestas-Garantia-4-si-5.zip?dl=1",
    (42, 6, 4, 6): "https://www.dropbox.com/s/982cbgozvltdn3w/42-numeros-al-4-por-1.810-apuestas-Garantia-4-si-6.zip?dl=1",
    (43, 6, 3, 4): "https://www.dropbox.com/s/keuc2v9tco14mjn/43-numeros-por-357-apuestas-Garantia-3-si-4.zip?dl=1",
    (43, 6, 3, 5): "https://www.dropbox.com/s/lsnk3vtxorv8kh7/43-numeros-por-154-apuestas-Garantia-3-si-5.zip?dl=1",
    (43, 6, 3, 6): "https://www.dropbox.com/s/gmmgk30fqfwybq1/43-Numeros-al-3-por-116-apuestas-Garantia-3-si-6.zip?dl=1",
    (43, 6, 4, 6): "https://www.dropbox.com/s/uocd6m67kgnivqh/43-numeros-al-4-por-2.044-apuestas-Garantia-4-si-6.zip?dl=1",
    (44, 6, 3, 4): "https://www.dropbox.com/s/skcgb3waov4l6ls/44-numeros-por-393-apuestas-Garantia-3-si-4.zip?dl=1",
    (44, 6, 3, 5): "https://www.dropbox.com/s/ptbw85fw3mdoytn/44-numeros-por-154-apuestas-Garantia-3-si-5.zip?dl=1",
    (44, 6, 3, 6): "https://www.dropbox.com/s/4e5hhz5cbq4xfbb/44-Numeros-al-3-por-123-apuestas-Garantia-3-si-6.zip?dl=1",
    (44, 6, 4, 5): "https://www.dropbox.com/s/smxreai0uh9uk6s/44-numeros-por-4.435-apuestas-Garantia-4-si-5.zip?dl=1",
    (44, 6, 4, 6): "https://www.dropbox.com/s/fppt4sahljjr8lw/44-numeros-al-4-por-2.329-apuestas-Garantia-4-si-6.zip?dl=1",
    (45, 6, 3, 4): "https://www.dropbox.com/s/7k774ehei1si546/45-numeros-por-403-apuestas-Garantia-3-si-4.zip?dl=1",
    (45, 6, 3, 5): "https://www.dropbox.com/s/sp5zauf92gt60dg/45-numeros-por-181-apuestas-Garantia-3-si-5.zip?dl=1",
    (45, 6, 3, 6): "https://www.dropbox.com/s/1mg79ksgai1kx2u/45-Numeros-al-3-por-131-apuestas-Garantia-3-si-6.zip?dl=1",
    (45, 6, 4, 5): "https://www.dropbox.com/s/w139mcieln02bwx/45-numeros-por-4.650-apuestas-Garantia-4-si-5.zip?dl=1",
    (46, 6, 3, 4): "https://www.dropbox.com/s/rwyjhdozqq958x3/46-numeros-por-436-apuestas-Garantia-3-si-4.zip?dl=1",
    (46, 6, 3, 5): "https://www.dropbox.com/s/np8u30d256ilfzf/46-numeros-por-193-apuestas-Garantia-3-si-5.zip?dl=1",
    (46, 6, 3, 6): "https://www.dropbox.com/s/ckhktqqzn60sccn/46-Numeros-al-3-por-138-apuestas-Garantia-3-si-6.zip?dl=1",
    (46, 6, 4, 6): "https://www.dropbox.com/s/k0qcr7tqpn9kj10/46-numeros-al-4-por-2.974-apuestas-Garantia-4-si-6.zip?dl=1",
    (47, 6, 3, 4): "https://www.dropbox.com/s/liy67ynrha29ejg/47-numeros-por-469-apuestas-Garantia-3-si-4.zip?dl=1",
    (47, 6, 3, 5): "https://www.dropbox.com/s/tsifheb4mbt9b33/47-numeros-por-207-apuestas-Garantia-3-si-5.zip?dl=1",
    (47, 6, 3, 6): "https://www.dropbox.com/s/olmzxkfr0a7fsrk/47-Numeros-al-3-por-145-apuestas-Garantia-3-si-6.zip?dl=1",
    (47, 6, 4, 5): "https://www.dropbox.com/s/h1jpt9e4vrf5ybm/47-numeros-por-5.650-apuestas-Garantia-4-si-5.zip?dl=1",
    (47, 6, 4, 6): "https://www.dropbox.com/s/alu0kjs45e3c0tf/47-numeros-al-4-por-3.259-apuestas-Garantia-4-si-6.zip?dl=1",
    (48, 6, 3, 3): "https://www.dropbox.com/s/u9ouw3835zbqh2u/48-numeros-al-3-por-987-apuestas-Garantia-3-si-3.zip?dl=1",
    (48, 6, 3, 4): "https://www.dropbox.com/s/1eom1qdwoddyw5v/48-numeros-por-480-apuestas-Garantia-3-si-4.zip?dl=1",
    (48, 6, 3, 5): "https://www.dropbox.com/s/j9wjbxqpd6n65lf/48-numeros-por-207-apuestas-Garantia-3-si-5.zip?dl=1",
    (48, 6, 3, 6): "https://www.dropbox.com/s/r7opwprulcltwq6/48-Numeros-al-3-por-153-apuestas-Garantia-3-si-6.zip?dl=1",
    (48, 6, 4, 6): "https://www.dropbox.com/s/eto2zp985l6oqjg/48-numeros-al-4-por-3.528-apuestas-Garantia-4-si-6.zip?dl=1",
    (49, 6, 3, 4): "https://www.dropbox.com/s/n1q2rw7e3obx095/49-numeros-por-530-apuestas-Garantia-3-si-4.zip?dl=1",
    (49, 6, 3, 5): "https://www.dropbox.com/s/ipcrd4wd6oid0zv/49-numeros-por-234-apuestas-Garantia-3-si-5.zip?dl=1",
    (49, 6, 3, 6): "https://www.dropbox.com/s/lfdy11ahh718tto/49-Numeros-al-3-por-163-apuestas-Garantia-3-si-6.zip?dl=1",
    (49, 6, 4, 5): "https://www.dropbox.com/s/l2ezyhwgo438n4z/49-numeros-por-6.825-apuestas-Garantia-4-si-5.zip?dl=1",
    (49, 6, 4, 6): "https://www.dropbox.com/s/b1k1c16ar6wps2d/49-numeros-al-4-por-3.771-apuestas-Garantia-4-si-6.zip?dl=1",
}


def descargar_reducida_lotoideas(url: str, v: int, k: int) -> List[List[int]]:
    print(" Descargando la reducida récord de Lotoideas...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        datos = resp.read()
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        nombres = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if not nombres:
            raise ValueError("el zip no trae un txt")
        texto = z.read(nombres[0]).decode("latin-1")
    apuestas = []
    for linea in texto.splitlines():
        nums = [int(parte) for parte in linea.replace(",", " ").split() if parte.isdigit()]
        if not nums:
            continue
        if len(nums) != k or len(set(nums)) != k or any(n < 1 or n > v for n in nums):
            raise ValueError("una apuesta del zip no encaja con v y k")
        apuestas.append(nums)
    if not apuestas:
        raise ValueError("el zip no trae apuestas")
    print(f" Reducida leída: {len(apuestas)} apuestas.")
    return apuestas


def preguntar_reducida() -> str:
    while True:
        eleccion = input(" ¿Usar la récord de Lotoideas (u) o intentar mejorarla (m)? ").strip().lower()
        if eleccion in ("u", "m"):
            return eleccion
        print(" Responde u o m.")


def personalizar_archivo(arch: str, v: int) -> None:
    if input("\n ¿Sustituir por números reales? (s/n): ").lower() != "s":
        return
    nums_reales = analizar_entrada_numeros(input(f" Introduce tus {v} números: "))
    if len(nums_reales) != v:
        print(f" ⚠️ Has introducido {len(nums_reales)} números en lugar de {v}. Mapeo cancelado.")
        return
    arch_pers = arch.replace(".txt", "_PERSONALIZADO.txt")
    with open(arch, "r", encoding="utf-8") as fi, open(arch_pers, "w", encoding="utf-8") as fo:
        for lin in fi:
            if lin.strip():
                fo.write(" ".join(f"{nums_reales[int(x) - 1]:02d}" for x in lin.split()) + "\n")
    print(" ✓ Mapeo completado. Archivo PERSONALIZADO guardado.")


def main():
    configurar_consola()
    limpiar_pantalla()
    print(" 🎰 LOTTO OPTIMIZER V3.11 - Guardado Exclusivo del Mejor Récord")
    try:
        v, k, t, m = leer_parametros()
        grupos = leer_grupos(v, k)
        config = Configuracion(v=v, k=k, t=t, m=m, condiciones_grupos=grupos)
        url = None if grupos else REDUCIDAS_LOTOIDEAS.get((v, k, t, m))
        arch = None

        if grupos and (v, k, t, m) in REDUCIDAS_LOTOIDEAS:
            print(" Hay récord de Lotoideas para estos datos. Con grupos se busca una lista nueva.")

        if url:
            print("\n Hay una reducida récord pública de Lotoideas para estos datos.")
            print(f" {url}")
            eleccion = preguntar_reducida()
            try:
                apuestas = descargar_reducida_lotoideas(url, v, k)
            except Exception as e:
                print(f" No se ha podido descargar la reducida ({e}). Se sigue con la búsqueda.")
                apuestas = None
            if apuestas and eleccion == "u":
                arch = escribir_apuestas(v, k, t, apuestas, marca="lotoideas")
                print(f"\n ✓ Archivo guardado con la reducida récord de Lotoideas: {arch}")
            elif apuestas:
                opt = LottoOptimizerV3(config)
                opt.cargar_lista(apuestas)
                print(" Si el recocido no la supera, se guarda esta lista de Lotoideas.")
                opt.optimizar()
                arch = opt.guardar_mejor_record()
                print(f"\n ✓ Archivo guardado con el MEJOR récord absoluto: {arch}")

        if arch is None:
            opt = LottoOptimizerV3(config)
            while True:
                cantidad = leer_entero("\n Cantidad de apuestas a generar: ")
                if cantidad >= 1:
                    break
                print(" La cantidad tiene que ser al menos 1.")
            opt.generar_aleatorias(cantidad)
            if opt.num_apuestas > 0:
                opt.optimizar()
                arch = opt.guardar_mejor_record()
                print(f"\n ✓ Archivo guardado con el MEJOR récord absoluto: {arch}")

        if arch:
            personalizar_archivo(arch, v)
    except Exception as e:
        print(f" Error: {e}")

    input("\n Presiona ENTER para salir...")


def _grupos_desde_texto(texto: str, v: int, k: int) -> List[CondicionGrupo]:
    grupos = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        partes = [p.strip() for p in linea.replace("|", ";").split(";")]
        if len(partes) != 3:
            raise ValueError("Cada grupo va en una línea: numeros ; minimo ; maximo")
        nums = analizar_entrada_numeros(partes[0])
        if not nums or any(n < 1 or n > v for n in nums):
            raise ValueError(f"El grupo necesita números entre 1 y {v}.")
        min_ac = int(partes[1])
        max_ac = int(partes[2])
        if min_ac < 0 or min_ac > max_ac or min_ac > k:
            raise ValueError(f"El mínimo tiene que estar entre 0 y {k}, y no puede superar al máximo.")
        grupos.append(CondicionGrupo(nums, min_ac, max_ac))
    return grupos


def grupos_traducidos(texto: str, base: List[int], k: int) -> List[CondicionGrupo]:
    indice = {n: i + 1 for i, n in enumerate(base)}
    lineas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        partes = [p.strip() for p in linea.replace("|", ";").split(";")]
        if len(partes) != 3:
            raise ValueError("Cada grupo va en una línea: numeros ; minimo ; maximo")
        nums = analizar_entrada_numeros(partes[0])
        if not nums or any(n not in indice for n in nums):
            raise ValueError("El grupo tiene que usar números de la base marcada.")
        abstractos = " ".join(str(indice[n]) for n in nums)
        lineas.append(f"{abstractos} ; {partes[1]} ; {partes[2]}")
    return _grupos_desde_texto("\n".join(lineas), len(base), k)


def escrutar_apuestas(apuestas: List[List[int]], premiados: List[int]) -> dict:
    prem = set(premiados)
    conteo: dict[int, int] = {}
    for fila in apuestas:
        aciertos = len(set(fila) & prem)
        conteo[aciertos] = conteo.get(aciertos, 0) + 1
    return conteo


def texto_escrutinio(conteo: dict, total: int, k: int) -> str:
    lineas = [f"Escrutinio de {total} apuestas."]
    for aciertos in range(k, -1, -1):
        lineas.append(f"  {aciertos} aciertos: {conteo.get(aciertos, 0)}")
    return "\n".join(lineas)


def texto_analisis(apuestas: List[List[int]]) -> str:
    if not apuestas:
        return "No hay apuestas."
    sumas = [sum(fila) for fila in apuestas]
    pares = [sum(1 for n in fila if n % 2 == 0) for fila in apuestas]
    freq: dict[int, int] = {}
    for fila in apuestas:
        for n in fila:
            freq[n] = freq.get(n, 0) + 1
    mas = sorted(freq, key=lambda n: (-freq[n], n))[:10]
    menos = sorted(freq, key=lambda n: (freq[n], n))[:10]
    return "\n".join([
        f"Apuestas: {len(apuestas)}",
        f"Suma mínima {min(sumas)}, máxima {max(sumas)}, media {sum(sumas) / len(sumas):.2f}",
        f"Pares por apuesta: mínimo {min(pares)}, máximo {max(pares)}",
        "Números más repetidos: " + ", ".join(f"{n} ({freq[n]})" for n in mas),
        "Números menos repetidos: " + ", ".join(f"{n} ({freq[n]})" for n in menos),
    ])


def texto_estadisticas(apuestas: List[List[int]]) -> str:
    if not apuestas:
        return "No hay apuestas."
    freq: dict[int, int] = {}
    decenas: dict[int, int] = {}
    finales: dict[int, int] = {}
    pares = impares = 0
    for fila in apuestas:
        for n in fila:
            freq[n] = freq.get(n, 0) + 1
            decenas[(n - 1) // 10] = decenas.get((n - 1) // 10, 0) + 1
            finales[n % 10] = finales.get(n % 10, 0) + 1
            if n % 2 == 0:
                pares += 1
            else:
                impares += 1
    lineas = [f"Pares {pares}, impares {impares}"]
    lineas.append("Por decena: " + ", ".join(f"{d * 10 + 1}-{d * 10 + 10}:{decenas[d]}" for d in sorted(decenas)))
    lineas.append("Por terminación: " + ", ".join(f"{d}:{finales[d]}" for d in sorted(finales)))
    lineas.append("Frecuencia:")
    for n in sorted(freq):
        lineas.append(f"  {n:02d}  {freq[n]}")
    return "\n".join(lineas)


def texto_validacion(apuestas: List[List[int]], k: int, permitidos: Optional[List[int]], filtros: Optional[Filtros], v_filtro: int) -> str:
    if not apuestas:
        return "No hay apuestas que validar."
    problemas = []
    vistas = set()
    techo = set(permitidos) if permitidos else None
    for i, fila in enumerate(apuestas, 1):
        if len(fila) != k or len(set(fila)) != k:
            problemas.append(f"Apuesta {i}: no tiene {k} números distintos.")
        if techo is not None and any(n not in techo for n in fila):
            problemas.append(f"Apuesta {i}: usa un número fuera de la base.")
        elif techo is None and any(n < 1 or n > v_filtro for n in fila):
            problemas.append(f"Apuesta {i}: fuera de 1..{v_filtro}.")
        if not apuesta_pasa_filtros(fila, filtros, v_filtro):
            problemas.append(f"Apuesta {i}: no cumple un filtro.")
        clave = tuple(sorted(fila))
        if clave in vistas:
            problemas.append(f"Apuesta {i}: está repetida.")
        vistas.add(clave)
    if not problemas:
        return f"Válidas: {len(apuestas)} apuestas de {k} números."
    return "Problemas:\n" + "\n".join(problemas[:40])


def main_gui() -> None:
    import queue
    import threading
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))

    fondo = "#F3F6F4"
    tarjeta = "#FFFFFF"
    tinta = "#14241C"
    suave = "#5C6B63"
    linea = "#D5E0D8"
    acento = "#18E667"
    tinta_acento = "#032612"
    primario = "#0A3D22"
    claro = "#F4F7F5"
    fuente = ("Segoe UI", 10)
    fuente_sm = ("Segoe UI", 9)

    mensajes: queue.Queue = queue.Queue()
    sesion = {"opt": None, "arch": None, "apuestas": [], "base": None, "k": 6, "v": 8, "ocupado": False}
    pista_win = {"w": None}

    class _Salida:
        def write(self, texto: str) -> int:
            if texto:
                mensajes.put(texto)
            return len(texto)

        def flush(self) -> None:
            pass

    sys.stdout = _Salida()
    sys.stderr = _Salida()

    guia = """Calcular
Genera las apuestas. Con los ciclos activos, después las mejora. Si eliges un % de cobertura, para cuando la muestra llega a ese porcentaje.

Parar
Corta lo que esté en marcha y guarda el mejor récord de la sesión.

Usar récord
Si Lotoideas publica un zip para esta base y esta garantía, lo descarga y lo guarda sin cambiar ni una apuesta.

Mejorar récord
Empieza por esa lista. Solo la sustituye si la cobertura de la muestra sube. Si no, se queda la de Lotoideas.

Escrutar
Compara las apuestas cargadas con la combinación ganadora y cuenta cuántas tienen 0, 1, 2… aciertos.

Garantías
Resume la garantía pedida (por ejemplo 5 si 6) y dice si hay reducida récord pública.

Análisis
Mira las apuestas: sumas, pares y los números que más y menos se repiten.

Validar
Avisa de apuestas repetidas, con números de más o de menos, fuera de la base o que no cumplen un filtro.

Estadísticas
Frecuencia de cada número, por decenas, por terminación, y el total de pares e impares.

Cargar
Abre un sistema propio. Un archivo de texto, una apuesta por línea.

Guardar
Escribe las apuestas que hay ahora en un archivo de texto.

Rejilla
Si marcas números, esa selección es la base y las apuestas salen con esos números. Si no marcas ninguno, se usan los números del 1 al tamaño de Base.

Al azar
Marca en la rejilla tantos números como indique Base.

Vaciar
Quita las marcas. Vuelves al modo de tamaño de Base.

G
Rellena la combinación a escrutar con k números al azar, de la base si hay una marcada.

Tipo
La garantía. «5 si 6» quiere decir: si los 6 números del sorteo caen dentro de la base, alguna apuesta acierta al menos 5.

Al 5 (n-1)
La garantía pasa a ser k−1 si k. Con k = 6 es un 5 si 6.

Ciclos
Encendidos, el programa intenta mejorar la cobertura después de generar. Apagados, solo genera y guarda.

Nº de apuestas
Cuántas combinaciones crear.

% de cobertura
Tope de los ciclos. La cobertura se mide sobre una muestra de 50.000 sorteos, no sobre todos los sorteos posibles.

Filtros
Una casilla apagada no se aplica. Sumas: mínimo y máximo de la suma. Pares: cuántos pares puede llevar la apuesta. Bajos: números hasta la mitad del universo. Distancias: hueco mínimo y máximo entre números seguidos. Seguidos: máximo de parejas consecutivas. Decenas y terminaciones: máximo de números con la misma decena o la misma última cifra.

Grupos
Una línea por grupo: números ; mínimo ; máximo. Cada apuesta tiene que incluir entre el mínimo y el máximo de esos números.

Apuestas condicionadas
Números que tienen que salir en todas las apuestas. Sirven rangos, por ejemplo 1-3 7.
"""

    tipos = [
        ("5 si 6", 5, 6),
        ("4 si 6", 4, 6),
        ("3 si 6", 3, 6),
        ("5 si 5", 5, 5),
        ("4 si 5", 4, 5),
        ("3 si 5", 3, 5),
        ("4 si 4", 4, 4),
        ("3 si 4", 3, 4),
        ("3 si 3", 3, 3),
        ("Al 5 (n-1)", 0, 0),
    ]

    raiz = tk.Tk()
    raiz.title("Loto 3.11")
    raiz.configure(bg=fondo)
    raiz.minsize(1040, 720)
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(".", background=fondo, foreground=tinta, font=fuente)
    estilo.configure("TCombobox", padding=4)
    estilo.configure("TEntry", padding=4)
    estilo.configure("TCheckbutton", background=tarjeta, foreground=tinta, font=fuente)
    estilo.configure("TRadiobutton", background=tarjeta, foreground=tinta, font=fuente)
    estilo.map("TCheckbutton", background=[("active", tarjeta)])
    estilo.map("TRadiobutton", background=[("active", tarjeta)])

    def cerrar_pista(_evento=None) -> None:
        if pista_win["w"] is not None:
            pista_win["w"].destroy()
            pista_win["w"] = None

    def pista(widget, texto: str) -> None:
        def entrar(_evento, widget=widget, texto=texto) -> None:
            cerrar_pista()
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 6
            ventana = tk.Toplevel(raiz)
            ventana.wm_overrideredirect(True)
            ventana.configure(bg=tinta)
            ventana.geometry(f"+{x}+{y}")
            tk.Label(
                ventana, text=texto, bg=tinta, fg=claro, font=fuente_sm,
                wraplength=320, justify="left", padx=10, pady=8,
            ).pack()
            pista_win["w"] = ventana

        widget.bind("<Enter>", entrar)
        widget.bind("<Leave>", cerrar_pista)

    def tarjeta_frame(padre, **kwargs):
        marco = tk.Frame(padre, bg=tarjeta, highlightthickness=1, highlightbackground=linea, **kwargs)
        return marco

    def etiqueta(padre, texto, fondo=tarjeta, color=tinta, fnt=fuente):
        return tk.Label(padre, text=texto, bg=fondo, fg=color, font=fnt)

    barra = tk.Frame(raiz, bg=fondo)
    barra.pack(side="top", fill="x", padx=20, pady=(16, 4))
    etiqueta(barra, "Loto 3.11", fondo, tinta, ("Segoe UI", 22, "bold")).pack(side="left")
    etiqueta(barra, "Reducidas y escrutinio", fondo, suave, fuente_sm).pack(side="left", padx=(12, 0), pady=(10, 0))

    numeros_var = tk.StringVar(value="0")
    apuestas_var = tk.StringVar(value="0")
    estado_var = tk.StringVar(value="Listo")

    def cajon(variable, leyenda):
        caja = tk.Frame(barra, bg=acento)
        caja.pack(side="right", padx=(8, 0))
        tk.Label(caja, textvariable=variable, bg=acento, fg=tinta_acento, font=("Segoe UI", 18, "bold"), padx=10).pack(side="left")
        tk.Label(caja, text=leyenda, bg=acento, fg=tinta_acento, font=fuente_sm, padx=8).pack(side="left")
        return caja

    cajon(apuestas_var, "apuestas")
    cajon(numeros_var, "en la base")

    acciones = tk.Frame(raiz, bg=fondo)
    acciones.pack(side="top", fill="x", padx=20, pady=(8, 4))

    estado = tk.Frame(raiz, bg=fondo)
    estado.pack(side="bottom", fill="x", padx=20, pady=(0, 12))
    tk.Label(estado, textvariable=estado_var, bg=fondo, fg=suave, font=fuente_sm, anchor="w").pack(fill="x")

    cuerpo = tk.Frame(raiz, bg=fondo)
    cuerpo.pack(side="top", fill="both", expand=True, padx=20, pady=8)

    izquierda = tarjeta_frame(cuerpo)
    izquierda.pack(side="left", fill="y", padx=(0, 12))
    etiqueta(izquierda, "Números", fnt=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(12, 0))
    etiqueta(izquierda, "Si marcas, esa es la base. Si no, vale el tamaño.", color=suave, fnt=fuente_sm).pack(anchor="w", padx=12)

    rejilla = tk.Frame(izquierda, bg=tarjeta)
    rejilla.pack(padx=12, pady=10)
    sel = {}
    teclas = {}

    def pintar_numero(n: int) -> None:
        activo = sel[n].get()
        teclas[n].configure(bg=acento if activo else tarjeta, fg=tinta_acento if activo else tinta)

    mando = tk.Frame(izquierda, bg=tarjeta)
    base_var = tk.StringVar(value="8")
    k_var = tk.StringVar(value="6")

    def marcados() -> List[int]:
        return sorted(n for n, var in sel.items() if var.get())

    def actualizar_resumen(*_args) -> None:
        numeros_var.set(str(len(marcados())))
        apuestas_var.set(str(len(sesion["apuestas"])))

    def alternar(n: int) -> None:
        sel[n].set(not sel[n].get())
        pintar_numero(n)
        actualizar_resumen()

    for n in range(1, 50):
        sel[n] = tk.BooleanVar(value=False)
        if n % 10 == 0:
            fila, col = 0, (n // 10) - 1
        else:
            fila, col = n % 10, n // 10
        tecla = tk.Button(
            rejilla, text=f"{n:02d}", width=3, relief="flat", bd=0,
            bg=tarjeta, fg=tinta, font=("Segoe UI", 10), cursor="hand2",
            highlightthickness=1, highlightbackground=linea, highlightcolor=acento,
            command=lambda n=n: alternar(n),
        )
        tecla.grid(row=fila, column=col, padx=2, pady=2)
        teclas[n] = tecla
        pista(tecla, "Púlsalo para meterlo o sacarlo de la base.")

    def al_azar() -> None:
        try:
            cuantos = int(base_var.get())
        except ValueError:
            messagebox.showerror("Base", "La base tiene que ser un entero.")
            return
        if not 1 <= cuantos <= 49:
            messagebox.showerror("Base", "La base al azar va de 1 a 49.")
            return
        elegidos = set(random.sample(range(1, 50), cuantos))
        for n, var in sel.items():
            var.set(n in elegidos)
            pintar_numero(n)
        actualizar_resumen()

    def vaciar() -> None:
        for n, var in sel.items():
            var.set(False)
            pintar_numero(n)
        actualizar_resumen()

    premio = tk.StringVar()

    def combinacion_azar() -> None:
        try:
            k = int(k_var.get())
        except ValueError:
            return
        origen = marcados() or list(range(1, 50))
        if k > len(origen):
            messagebox.showerror("Combinación", "k es mayor que los números disponibles.")
            return
        premio.set(" ".join(f"{n:02d}" for n in sorted(random.sample(origen, k))))

    mando.pack(fill="x", padx=12, pady=(0, 12))
    etiqueta(mando, "Base").pack(side="left")
    base_entry = tk.Entry(mando, textvariable=base_var, width=4, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea)
    base_entry.pack(side="left", padx=(6, 10))
    etiqueta(mando, "k").pack(side="left")
    k_spin = tk.Spinbox(mando, from_=1, to=15, textvariable=k_var, width=3, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea, buttonbackground=tarjeta)
    k_spin.pack(side="left", padx=(6, 10))

    derecha = tk.Frame(cuerpo, bg=fondo)
    derecha.pack(side="left", fill="both", expand=True)

    escrutinio = tarjeta_frame(derecha)
    escrutinio.pack(fill="x", pady=(0, 10))
    etiqueta(escrutinio, "Combinación a escrutar", fnt=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
    fila_premio = tk.Frame(escrutinio, bg=tarjeta)
    fila_premio.pack(fill="x", padx=12, pady=(4, 12))
    premio_entry = tk.Entry(fila_premio, textvariable=premio, relief="flat", font=("Segoe UI", 14), highlightthickness=1, highlightbackground=linea)
    premio_entry.pack(side="left", fill="x", expand=True, ipady=4)

    opciones = tarjeta_frame(derecha)
    opciones.pack(fill="x", pady=(0, 10))
    etiqueta(opciones, "Reducción", fnt=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
    tipo_var = tk.StringVar(value="5 si 6")
    tipo_box = ttk.Combobox(opciones, textvariable=tipo_var, values=[nombre for nombre, _, _ in tipos], width=16, state="readonly")
    tipo_box.grid(row=0, column=1, sticky="w", pady=(10, 4))
    ciclos_var = tk.BooleanVar(value=True)
    ciclos_chk = ttk.Checkbutton(opciones, text="Activar ciclos", variable=ciclos_var)
    ciclos_chk.grid(row=0, column=2, sticky="w", padx=12, pady=(10, 4))
    modo_var = tk.StringVar(value="n")
    modo_n = ttk.Radiobutton(opciones, text="Nº de apuestas", variable=modo_var, value="n")
    modo_n.grid(row=1, column=0, sticky="w", padx=12)
    cantidad_var = tk.StringVar(value="20")
    cantidad_entry = tk.Entry(opciones, textvariable=cantidad_var, width=8, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea)
    cantidad_entry.grid(row=1, column=1, sticky="w", pady=4)
    modo_p = ttk.Radiobutton(opciones, text="% de cobertura", variable=modo_var, value="p")
    modo_p.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))
    porc_var = tk.StringVar(value="100")
    porc_entry = tk.Entry(opciones, textvariable=porc_var, width=8, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea)
    porc_entry.grid(row=2, column=1, sticky="w", pady=(0, 10))

    filtros_ui = tarjeta_frame(derecha)
    filtros_ui.pack(fill="x", pady=(0, 10))
    etiqueta(filtros_ui, "Filtros", fnt=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", padx=12, pady=(10, 4))
    checks = {}
    entradas = {}

    def fila_filtro(fila: int, columna: int, clave: str, texto: str, campos: int, explicacion: str) -> None:
        var = tk.BooleanVar(value=False)
        checks[clave] = var
        casilla = ttk.Checkbutton(filtros_ui, text=texto, variable=var)
        casilla.grid(row=fila, column=columna, sticky="w", padx=(12, 4), pady=2)
        pista(casilla, explicacion)
        for i in range(campos):
            ent = tk.StringVar()
            entradas[f"{clave}{i}"] = ent
            caja = tk.Entry(filtros_ui, textvariable=ent, width=6, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea)
            caja.grid(row=fila, column=columna + 1 + i, padx=2, pady=2, sticky="w")
            pista(caja, explicacion)

    fila_filtro(1, 0, "suma", "Sumas", 2, "Mínimo y máximo de la suma de la apuesta.")
    fila_filtro(2, 0, "pares", "Pares", 2, "Mínimo y máximo de números pares en la apuesta.")
    fila_filtro(3, 0, "bajos", "Bajos", 2, "Mínimo y máximo de números bajos, los que van de 1 hasta la mitad.")
    fila_filtro(4, 0, "dist", "Distancias", 2, "Hueco mínimo y máximo entre dos números seguidos de la apuesta.")
    fila_filtro(1, 3, "seguidos", "Seguidos", 1, "Máximo de parejas consecutivas, como 7 y 8.")
    fila_filtro(2, 3, "decenas", "Decenas", 1, "Máximo de números en la misma decena.")
    fila_filtro(3, 3, "term", "Terminaciones", 1, "Máximo de números con la misma última cifra. También son los homólogos.")
    etiqueta(filtros_ui, "Grupos   números ; mínimo ; máximo", color=suave, fnt=fuente_sm).grid(row=5, column=0, columnspan=6, sticky="w", padx=12, pady=(8, 0))
    grupos_texto = tk.Text(filtros_ui, height=2, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=linea)
    grupos_texto.grid(row=6, column=0, columnspan=6, sticky="we", padx=12, pady=4)
    etiqueta(filtros_ui, "Apuestas condicionadas", color=suave, fnt=fuente_sm).grid(row=7, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))
    incluir_var = tk.StringVar()
    incluir_entry = tk.Entry(filtros_ui, textvariable=incluir_var, relief="flat", font=fuente, highlightthickness=1, highlightbackground=linea)
    incluir_entry.grid(row=7, column=2, columnspan=4, sticky="we", padx=12, pady=(0, 10))
    filtros_ui.grid_columnconfigure(5, weight=1)

    actividad = tarjeta_frame(raiz, height=128)
    actividad.pack_propagate(False)
    actividad.pack(side="bottom", fill="x", padx=20, pady=(0, 4))
    etiqueta(actividad, "Actividad", fnt=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
    marco_log = tk.Frame(actividad, bg=tarjeta)
    marco_log.pack(fill="both", expand=True, padx=12, pady=(4, 12))
    barra_log = tk.Scrollbar(marco_log)
    registro = tk.Text(
        marco_log, height=5, font=("Consolas", 10), bg="#E7EEE9", fg=tinta, relief="flat",
        wrap="word", padx=8, pady=8, yscrollcommand=barra_log.set,
    )
    barra_log.configure(command=registro.yview)
    barra_log.pack(side="right", fill="y")
    registro.pack(side="left", fill="both", expand=True)

    def entero_opcional(clave: str) -> Optional[int]:
        texto = entradas[clave].get().strip()
        if texto == "":
            return None
        return int(texto)

    def construir_filtros() -> Optional[Filtros]:
        if not any(var.get() for var in checks.values()) and not incluir_var.get().strip():
            return None
        return Filtros(
            suma_min=entero_opcional("suma0") if checks["suma"].get() else None,
            suma_max=entero_opcional("suma1") if checks["suma"].get() else None,
            pares_min=entero_opcional("pares0") if checks["pares"].get() else None,
            pares_max=entero_opcional("pares1") if checks["pares"].get() else None,
            bajos_min=entero_opcional("bajos0") if checks["bajos"].get() else None,
            bajos_max=entero_opcional("bajos1") if checks["bajos"].get() else None,
            distancia_min=entero_opcional("dist0") if checks["dist"].get() else None,
            distancia_max=entero_opcional("dist1") if checks["dist"].get() else None,
            seguidos_max=entero_opcional("seguidos0") if checks["seguidos"].get() else None,
            por_decena_max=entero_opcional("decenas0") if checks["decenas"].get() else None,
            por_terminacion_max=entero_opcional("term0") if checks["term"].get() else None,
            incluir=analizar_entrada_numeros(incluir_var.get()),
        )

    def parametros():
        k = int(k_var.get())
        nombre = tipo_var.get()
        t = m = None
        for etiqueta_tipo, tt, mm in tipos:
            if etiqueta_tipo == nombre:
                t, m = tt, mm
                break
        if t == 0:
            t, m = k - 1, k
        if t < 1:
            raise ValueError("Con Al 5 (n-1), k tiene que ser al menos 2.")
        base = marcados()
        if base:
            v = len(base)
        else:
            v = int(base_var.get())
        if not 1 <= k <= v:
            raise ValueError("k tiene que estar entre 1 y el tamaño de la base.")
        if not 1 <= m <= v or not 1 <= t <= min(k, m):
            raise ValueError(f"La garantía {t} si {m} no cabe en v={v} y k={k}.")
        texto_grupos = grupos_texto.get("1.0", "end")
        grupos = grupos_traducidos(texto_grupos, base, k) if base else _grupos_desde_texto(texto_grupos, v, k)
        filtros = construir_filtros()
        cantidad = int(cantidad_var.get() or "0")
        porc = float(porc_var.get() or "0")
        return {
            "v": v, "k": k, "t": t, "m": m, "base": base, "grupos": grupos,
            "filtros": filtros, "cantidad": cantidad, "porc": porc,
            "ciclos": ciclos_var.get(), "modo": modo_var.get(),
        }

    progreso = {"activo": False}

    def escribir_log() -> None:
        while True:
            try:
                texto = mensajes.get_nowait()
            except queue.Empty:
                break
            for simbolo in ("🎯", "🌡️", "🔄", "🎰", "🛑", "✓"):
                texto = texto.replace(simbolo, "")
            es_progreso = "\r" in texto and "\n" not in texto.strip("\r")
            if es_progreso:
                limpio = " ".join(texto.replace("\r", " ").split())
                if progreso["activo"]:
                    registro.delete("progreso", "end")
                else:
                    if registro.index("end-1c") != "1.0":
                        registro.insert("end", "\n")
                    registro.mark_set("progreso", "end-1c")
                    registro.mark_gravity("progreso", "left")
                    progreso["activo"] = True
                registro.insert("end", limpio)
            else:
                progreso["activo"] = False
                trozo = texto.replace("\r", "\n")
                if trozo and not trozo.endswith("\n"):
                    trozo += "\n"
                registro.insert("end", trozo)
            registro.see("end")
        raiz.after(200, escribir_log)

    def anotar(texto: str) -> None:
        mensajes.put(texto if texto.endswith("\n") else texto + "\n")
        primera = texto.strip().splitlines()
        if primera:
            raiz.after(0, lambda linea_estado=primera[0][:140]: estado_var.set(linea_estado))

    def ocupado(si: bool) -> None:
        sesion["ocupado"] = si
        estado = "disabled" if si else "normal"
        for boton in accion:
            boton.configure(state=estado)
        parar_btn.configure(state="normal" if si else "disabled")
        estado_var.set("Trabajando. Parar guarda el mejor récord." if si else "Listo")

    def guardar_lista(datos, listas, marca: str = "v11") -> str:
        arch = escribir_apuestas(datos["v"], datos["k"], datos["t"], listas, marca=marca)
        sesion["arch"] = arch
        sesion["apuestas"] = listas
        sesion["base"] = datos["base"]
        sesion["k"] = datos["k"]
        sesion["v"] = datos["v"]
        raiz.after(0, actualizar_resumen)
        anotar(f"Archivo: {arch}")
        return arch

    def lanzar(modo: str) -> None:
        if sesion["ocupado"]:
            return
        try:
            datos = parametros()
        except Exception as e:
            messagebox.showerror("Datos", str(e))
            return
        url = None if datos["grupos"] else REDUCIDAS_LOTOIDEAS.get((datos["v"], datos["k"], datos["t"], datos["m"]))
        if modo in ("usar", "mejorar") and not url:
            messagebox.showinfo("Récord", "No hay zip público de Lotoideas para esta base y esta garantía, o hay grupos.")
            return
        if modo == "calcular" and datos["modo"] == "n" and datos["cantidad"] < 1:
            messagebox.showerror("Datos", "El número de apuestas tiene que ser al menos 1.")
            return

        def a_reales(filas):
            base = datos["base"]
            if not base:
                return filas
            return [[base[n - 1] for n in fila] for fila in filas]

        def trabajo() -> None:
            try:
                if modo == "usar":
                    anotar(url)
                    apuestas = a_reales(descargar_reducida_lotoideas(url, datos["v"], datos["k"]))
                    guardar_lista(datos, apuestas, "lotoideas")
                    anotar("Guardada la reducida récord de Lotoideas, sin cambiarla.")
                    return
                config = Configuracion(
                    v=datos["v"], k=datos["k"], t=datos["t"], m=datos["m"],
                    condiciones_grupos=datos["grupos"], filtros=datos["filtros"],
                    mapa=datos["base"] or None, filtro_v=49 if datos["base"] else datos["v"],
                )
                opt = LottoOptimizerV3(config)
                opt._detener = False
                sesion["opt"] = opt
                if modo == "mejorar":
                    anotar(url)
                    anotar("Si el recocido no la supera, se guarda la lista de Lotoideas.")
                    opt.cargar_lista(descargar_reducida_lotoideas(url, datos["v"], datos["k"]))
                    if opt.num_apuestas and not opt._detener:
                        opt.optimizar(en_pantalla=False)
                else:
                    cantidad = datos["cantidad"] if datos["cantidad"] >= 1 else 20
                    opt.generar_aleatorias(cantidad)
                    if datos["ciclos"] and opt.num_apuestas and not opt._detener:
                        objetivo = datos["porc"] if datos["modo"] == "p" else None
                        opt.optimizar(en_pantalla=False, objetivo=objetivo)
                if opt.num_apuestas:
                    fuente = opt.mejor_apuestas_bits or opt.apuestas_bits
                    listas = a_reales([BitUtils.bits_a_lista(b, datos["v"]) for b in fuente])
                    cob = opt.mejor_cobertura if opt.mejor_cobertura > 0 else opt.cobertura
                    arch = escribir_apuestas(datos["v"], datos["k"], datos["t"], listas, cob)
                    sesion["arch"] = arch
                    sesion["apuestas"] = listas
                    sesion["base"] = datos["base"]
                    sesion["k"] = datos["k"]
                    sesion["v"] = datos["v"]
                    raiz.after(0, actualizar_resumen)
                    anotar(f"Archivo: {arch}")
                else:
                    anotar("No hay apuestas que guardar.")
            except Exception as e:
                anotar(f"Error: {e}")
            finally:
                raiz.after(0, lambda: ocupado(False))

        ocupado(True)
        threading.Thread(target=trabajo, daemon=True).start()

    def parar() -> None:
        opt = sesion.get("opt")
        if opt is not None:
            opt._detener = True

    def exigir_apuestas():
        if not sesion["apuestas"]:
            messagebox.showinfo("Apuestas", "Primero calcula, carga o usa una reducida.")
            return False
        return True

    def escrutar() -> None:
        if not exigir_apuestas():
            return
        premiados = analizar_entrada_numeros(premio.get())
        if len(premiados) < 1:
            messagebox.showerror("Escrutar", "Escribe la combinación ganadora.")
            return
        conteo = escrutar_apuestas(sesion["apuestas"], premiados)
        k_real = max(len(fila) for fila in sesion["apuestas"])
        anotar(texto_escrutinio(conteo, len(sesion["apuestas"]), k_real))

    def garantias() -> None:
        try:
            datos = parametros()
        except Exception as e:
            messagebox.showerror("Garantías", str(e))
            return
        url = None if datos["grupos"] else REDUCIDAS_LOTOIDEAS.get((datos["v"], datos["k"], datos["t"], datos["m"]))
        lineas = [
            f"Base de {datos['v']} números, apuestas de {datos['k']}.",
            f"Garantía pedida: {datos['t']} si {datos['m']}.",
            f"Apuestas cargadas: {len(sesion['apuestas'])}.",
        ]
        if url:
            lineas.append("Hay reducida récord pública de Lotoideas:")
            lineas.append(url)
        else:
            lineas.append("No hay zip de Lotoideas para estos datos.")
        opt = sesion.get("opt")
        if opt is not None and opt.total_sorteos:
            lineas.append(f"Cobertura de la muestra: {opt.mejor_cobertura or opt.cobertura:.4f}%.")
        anotar("\n".join(lineas))

    def analizar() -> None:
        if exigir_apuestas():
            anotar(texto_analisis(sesion["apuestas"]))

    def estadisticas() -> None:
        if exigir_apuestas():
            anotar(texto_estadisticas(sesion["apuestas"]))

    def validar() -> None:
        if not exigir_apuestas():
            return
        try:
            datos = parametros()
        except Exception as e:
            messagebox.showerror("Validar", str(e))
            return
        permitidos = datos["base"] or None
        if permitidos:
            universo = 49
        else:
            mayor = max(n for fila in sesion["apuestas"] for n in fila)
            universo = max(datos["v"], mayor)
        anotar(texto_validacion(sesion["apuestas"], datos["k"], permitidos, datos["filtros"], universo))

    def cargar() -> None:
        ruta = filedialog.askopenfilename(filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        apuestas = []
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                nums = analizar_entrada_numeros(linea)
                if nums:
                    apuestas.append(nums)
        sesion["apuestas"] = apuestas
        sesion["arch"] = ruta
        if apuestas:
            sesion["k"] = len(apuestas[0])
        actualizar_resumen()
        anotar(f"Cargadas {len(apuestas)} apuestas desde {ruta}")

    def guardar() -> None:
        if not exigir_apuestas():
            return
        try:
            datos = parametros()
        except Exception:
            datos = {"v": sesion["v"], "k": sesion["k"], "t": 1}
        arch = escribir_apuestas(datos["v"], datos["k"], datos.get("t", 1), sesion["apuestas"], marca="propio")
        sesion["arch"] = arch
        anotar(f"Sistema propio guardado: {arch}")

    def ayuda() -> None:
        ventana = tk.Toplevel(raiz)
        ventana.title("Qué hace cada cosa")
        ventana.geometry("560x640")
        ventana.configure(bg=fondo)
        caja = tk.Text(ventana, wrap="word", font=("Segoe UI", 11), bg=tarjeta, fg=tinta, relief="flat", padx=18, pady=14)
        caja.pack(fill="both", expand=True, padx=16, pady=16)
        caja.tag_configure("titulo", font=("Segoe UI", 12, "bold"), spacing1=12)
        for bloque in guia.strip().split("\n\n"):
            lineas = bloque.split("\n", 1)
            caja.insert("end", lineas[0] + "\n", "titulo")
            if len(lineas) > 1:
                caja.insert("end", lineas[1] + "\n")
        caja.configure(state="disabled")

    def hacer_boton(padre, texto, orden, ayuda_txt, primario_btn=False):
        bg = primario if primario_btn else tarjeta
        fg = claro if primario_btn else tinta
        boton = tk.Button(
            padre, text=texto, command=orden, bg=bg, fg=fg, font=("Segoe UI", 10, "bold" if primario_btn else "normal"),
            relief="flat", bd=0, padx=12, pady=7, cursor="hand2",
            activebackground=acento, activeforeground=tinta_acento,
            highlightthickness=1, highlightbackground=linea, highlightcolor=acento,
        )
        pista(boton, ayuda_txt)
        return boton

    hacer = tk.Frame(acciones, bg=fondo)
    hacer.pack(fill="x", pady=(0, 6))
    revisar = tk.Frame(acciones, bg=fondo)
    revisar.pack(fill="x")
    etiqueta(hacer, "Hacer", fondo, suave, fuente_sm).pack(side="left", padx=(0, 8))
    etiqueta(revisar, "Revisar", fondo, suave, fuente_sm).pack(side="left", padx=(0, 8))

    accion = []
    especificacion = [
        (hacer, "Calcular", lambda: lanzar("calcular"), "Genera las apuestas y, si los ciclos están activos, las mejora.", True),
        (hacer, "Usar récord", lambda: lanzar("usar"), "Descarga la reducida pública de Lotoideas y la guarda igual.", False),
        (hacer, "Mejorar récord", lambda: lanzar("mejorar"), "Intenta superar la lista de Lotoideas. Si no puede, la deja igual.", False),
        (revisar, "Escrutar", escrutar, "Cuenta los aciertos de tus apuestas contra la combinación ganadora.", False),
        (revisar, "Garantías", garantias, "Muestra la garantía pedida y si hay zip público.", False),
        (revisar, "Análisis", analizar, "Resume sumas, pares y números más repetidos.", False),
        (revisar, "Validar", validar, "Busca apuestas repetidas, incompletas o fuera de los filtros.", False),
        (revisar, "Estadísticas", estadisticas, "Frecuencias, decenas, terminaciones, pares e impares.", False),
        (revisar, "Cargar", cargar, "Abre un sistema propio, una apuesta por línea.", False),
        (revisar, "Guardar", guardar, "Guarda las apuestas actuales en un texto.", False),
    ]
    for padre, texto, orden, ayuda_txt, es_primario in especificacion:
        boton = hacer_boton(padre, texto, orden, ayuda_txt, es_primario)
        boton.pack(side="left", padx=(0, 6))
        accion.append(boton)
    parar_btn = hacer_boton(hacer, "Parar", parar, "Corta el cálculo y guarda el mejor récord.")
    parar_btn.configure(state="disabled", bg=tinta, fg=claro)
    parar_btn.pack(side="left", padx=(0, 6))
    guia_btn = hacer_boton(revisar, "Qué hace cada cosa", ayuda, "Abre la explicación de cada botón y de cada campo.")
    guia_btn.pack(side="right")

    azar_btn = hacer_boton(mando, "Al azar", al_azar, "Marca al azar tantos números como ponga Base.")
    azar_btn.pack(side="left", padx=(0, 6))
    vaciar_btn = hacer_boton(mando, "Vaciar", vaciar, "Quita todas las marcas de la rejilla.")
    vaciar_btn.pack(side="left")
    g_btn = hacer_boton(fila_premio, "G", combinacion_azar, "Rellena la combinación ganadora con k números al azar.")
    g_btn.pack(side="left", padx=(8, 0))
    accion.extend([azar_btn, vaciar_btn, g_btn])

    pista(base_entry, "Tamaño de la base cuando la rejilla está vacía. Con 8, k 6 y 5 si 6 hay zip de Lotoideas.")
    pista(k_spin, "Números de cada apuesta.")
    pista(premio_entry, "La combinación ganadora. Números separados por espacios, comas o rangos.")
    pista(tipo_box, "Garantía que pides. 5 si 6: si salen 6 de la base, alguna apuesta acierta 5 o más.")
    pista(ciclos_chk, "Con los ciclos, el programa intenta mejorar la cobertura. Sin ellos, solo genera.")
    pista(modo_n, "Crear exactamente este número de apuestas.")
    pista(cantidad_entry, "Cuántas apuestas generar.")
    pista(modo_p, "Parar los ciclos al llegar a este porcentaje de la muestra.")
    pista(porc_entry, "Porcentaje de cobertura de la muestra. 100 es el tope.")
    pista(grupos_texto, "Una línea por grupo: 1-12 ; 1 ; 3")
    pista(incluir_entry, "Números obligatorios en todas las apuestas. Ejemplo: 7 14 o 1-3.")
    pista(cajon_numeros := barra.winfo_children()[-1], "Cuántos números hay marcados en la rejilla.")

    escribir_log()
    raiz.update_idletasks()
    ancho = min(1120, raiz.winfo_screenwidth() - 40)
    alto = min(920, raiz.winfo_screenheight() - 80)
    raiz.geometry(f"{ancho}x{alto}+{(raiz.winfo_screenwidth() - ancho) // 2}+{(raiz.winfo_screenheight() - alto) // 2}")
    raiz.mainloop()


if __name__ == "__main__":
    if "--consola" in sys.argv:
        main()
    else:
        main_gui()
