"""
LOTTO OPTIMIZER V3.10 - Pantalla limpia y guardado exclusivo del MEJOR récord
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
class Configuracion:
    v: int
    k: int
    t: int
    m: int
    universo_size: int = 50_000
    condiciones_grupos: List[CondicionGrupo] = field(default_factory=list)


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

    def optimizar(self, en_pantalla: bool = True) -> None:
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
    print(" 🎰 LOTTO OPTIMIZER V3.10 - Guardado Exclusivo del Mejor Récord")
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


def _leer_enteros_gui(campos) -> Tuple[int, int, int, int, int]:
    v = int(campos["v"].get().strip())
    k = int(campos["k"].get().strip())
    t = int(campos["t"].get().strip())
    m = int(campos["m"].get().strip())
    cantidad = int(campos["cantidad"].get().strip() or "0")
    if v < 1:
        raise ValueError("v tiene que ser al menos 1.")
    if not 1 <= k <= v:
        raise ValueError("k tiene que estar entre 1 y v.")
    if not 1 <= m <= v:
        raise ValueError("m tiene que estar entre 1 y v.")
    tope = min(k, m)
    if not 1 <= t <= tope:
        raise ValueError(f"t tiene que estar entre 1 y {tope}.")
    return v, k, t, m, cantidad


def main_gui() -> None:
    import queue
    import threading
    import tkinter as tk
    from tkinter import messagebox

    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))

    mensajes: queue.Queue = queue.Queue()
    sesion = {"opt": None, "arch": None, "ocupado": False}

    class _Salida:
        def write(self, texto: str) -> int:
            if texto:
                mensajes.put(texto)
            return len(texto)

        def flush(self) -> None:
            pass

    sys.stdout = _Salida()
    sys.stderr = _Salida()

    raiz = tk.Tk()
    raiz.title("Lotto Optimizer V3.10")
    raiz.geometry("760x680")
    raiz.configure(bg="#f4f7f5")

    marco = tk.Frame(raiz, bg="#f4f7f5", padx=16, pady=12)
    marco.pack(fill="both", expand=True)

    tk.Label(marco, text="Lotto Optimizer", font=("Segoe UI", 22, "bold"), bg="#18E667", fg="#032612", padx=12, pady=8).pack(fill="x")
    tk.Label(
        marco,
        text="Misma lógica que la consola. Parar guarda el mejor récord, no el último ciclo.",
        bg="#f4f7f5",
        fg="#032612",
        anchor="w",
    ).pack(fill="x", pady=(8, 10))

    fila = tk.Frame(marco, bg="#f4f7f5")
    fila.pack(fill="x")
    campos = {}
    for clave, etiqueta, valor in (
        ("v", "Total números (v)", "8"),
        ("k", "Por apuesta (k)", "6"),
        ("t", "Garantía (t)", "5"),
        ("m", "Por sorteo (m)", "6"),
        ("cantidad", "Cantidad", "20"),
    ):
        caja = tk.Frame(fila, bg="#f4f7f5")
        caja.pack(side="left", padx=(0, 8))
        tk.Label(caja, text=etiqueta, bg="#f4f7f5").pack(anchor="w")
        var = tk.StringVar(value=valor)
        tk.Entry(caja, textvariable=var, width=12).pack()
        campos[clave] = var

    tk.Label(marco, text="Grupos, uno por línea: 1-12 ; 1 ; 3. Vacío = sin grupos.", bg="#f4f7f5", anchor="w").pack(fill="x", pady=(10, 2))
    grupos_texto = tk.Text(marco, height=4, font=("Consolas", 10))
    grupos_texto.pack(fill="x")

    aviso = tk.StringVar(value="")
    tk.Label(marco, textvariable=aviso, bg="#f4f7f5", fg="#032612", anchor="w", justify="left", wraplength=720).pack(fill="x", pady=8)

    botones = tk.Frame(marco, bg="#f4f7f5")
    botones.pack(fill="x")

    def aviso_record(*_args) -> None:
        try:
            v, k, t, m, _cant = _leer_enteros_gui(campos)
            grupos = _grupos_desde_texto(grupos_texto.get("1.0", "end"), v, k)
        except Exception:
            aviso.set("")
            return
        url = None if grupos else REDUCIDAS_LOTOIDEAS.get((v, k, t, m))
        if url:
            aviso.set(f"Hay reducida récord de Lotoideas.\n{url}")
        elif grupos and (v, k, t, m) in REDUCIDAS_LOTOIDEAS:
            aviso.set("Hay récord de Lotoideas. Con grupos se busca una lista nueva.")
        else:
            aviso.set("No hay zip público de Lotoideas para estos datos.")

    for var in campos.values():
        var.trace_add("write", aviso_record)
    grupos_texto.bind("<KeyRelease>", aviso_record)

    registro = tk.Text(marco, height=16, font=("Consolas", 10), bg="#032612", fg="#f4f7f5")
    registro.pack(fill="both", expand=True, pady=(8, 8))

    reales = tk.StringVar()
    fila_real = tk.Frame(marco, bg="#f4f7f5")
    fila_real.pack(fill="x")
    tk.Label(fila_real, text="Números reales", bg="#f4f7f5").pack(side="left")
    tk.Entry(fila_real, textvariable=reales).pack(side="left", fill="x", expand=True, padx=8)

    def escribir_log() -> None:
        while True:
            try:
                texto = mensajes.get_nowait()
            except queue.Empty:
                break
            registro.insert("end", texto.replace("\r", "\n"))
            registro.see("end")
        raiz.after(200, escribir_log)

    def ocupado(si: bool) -> None:
        sesion["ocupado"] = si
        estado = "disabled" if si else "normal"
        for boton in (usar_btn, mejorar_btn, generar_btn, mapear_btn):
            boton.configure(state=estado)
        parar_btn.configure(state="normal" if si else "disabled")

    def lanzar(modo: str) -> None:
        if sesion["ocupado"]:
            return
        try:
            v, k, t, m, cantidad = _leer_enteros_gui(campos)
            grupos = _grupos_desde_texto(grupos_texto.get("1.0", "end"), v, k)
        except Exception as e:
            messagebox.showerror("Datos", str(e))
            return
        if modo == "generar" and cantidad < 1:
            messagebox.showerror("Datos", "La cantidad tiene que ser al menos 1.")
            return
        url = None if grupos else REDUCIDAS_LOTOIDEAS.get((v, k, t, m))
        if modo in ("usar", "mejorar") and not url:
            messagebox.showinfo("Récord", "No hay zip público de Lotoideas para estos datos sin grupos.")
            return

        def trabajo() -> None:
            try:
                config = Configuracion(v=v, k=k, t=t, m=m, condiciones_grupos=grupos)
                if modo == "usar":
                    apuestas = descargar_reducida_lotoideas(url, v, k)
                    sesion["arch"] = escribir_apuestas(v, k, t, apuestas, marca="lotoideas")
                    print(f"\nArchivo guardado con la reducida récord de Lotoideas: {sesion['arch']}")
                    return
                opt = LottoOptimizerV3(config)
                opt._detener = False
                sesion["opt"] = opt
                if modo == "mejorar":
                    apuestas = descargar_reducida_lotoideas(url, v, k)
                    print("Si el recocido no la supera, se guarda esta lista de Lotoideas.")
                    opt.cargar_lista(apuestas)
                else:
                    opt.generar_aleatorias(cantidad)
                if opt.num_apuestas > 0 and not opt._detener:
                    opt.optimizar(en_pantalla=False)
                    sesion["arch"] = opt.guardar_mejor_record()
                    print(f"\nArchivo guardado con el MEJOR récord absoluto: {sesion['arch']}")
                elif opt.num_apuestas > 0:
                    sesion["arch"] = opt.guardar_mejor_record()
                    print(f"\nArchivo guardado con el MEJOR récord absoluto: {sesion['arch']}")
                else:
                    print("\nNo hay apuestas que guardar.")
            except Exception as e:
                print(f"\nError: {e}")
            finally:
                raiz.after(0, lambda: ocupado(False))

        ocupado(True)
        threading.Thread(target=trabajo, daemon=True).start()

    def parar() -> None:
        opt = sesion.get("opt")
        if opt is not None:
            opt._detener = True

    def mapear() -> None:
        arch = sesion.get("arch")
        if not arch:
            messagebox.showinfo("Números reales", "Todavía no hay un archivo guardado.")
            return
        try:
            v = int(campos["v"].get().strip())
            nums_reales = analizar_entrada_numeros(reales.get())
        except Exception as e:
            messagebox.showerror("Números reales", str(e))
            return
        if len(nums_reales) != v:
            messagebox.showerror("Números reales", f"Has introducido {len(nums_reales)} números en lugar de {v}.")
            return
        arch_pers = arch.replace(".txt", "_PERSONALIZADO.txt")
        with open(arch, "r", encoding="utf-8") as fi, open(arch_pers, "w", encoding="utf-8") as fo:
            for lin in fi:
                if lin.strip():
                    fo.write(" ".join(f"{nums_reales[int(x) - 1]:02d}" for x in lin.split()) + "\n")
        sesion["arch"] = arch_pers
        print(f"\nMapeo completado: {arch_pers}")

    usar_btn = tk.Button(botones, text="Usar récord", command=lambda: lanzar("usar"), bg="#18E667", fg="#032612")
    mejorar_btn = tk.Button(botones, text="Intentar mejorarla", command=lambda: lanzar("mejorar"), bg="#18E667", fg="#032612")
    generar_btn = tk.Button(botones, text="Generar y optimizar", command=lambda: lanzar("generar"), bg="#0A3D22", fg="#f4f7f5")
    parar_btn = tk.Button(botones, text="Parar", command=parar, state="disabled", bg="#032612", fg="#f4f7f5")
    for boton in (usar_btn, mejorar_btn, generar_btn, parar_btn):
        boton.pack(side="left", padx=(0, 8), ipadx=6, ipady=4)
    mapear_btn = tk.Button(fila_real, text="Aplicar al archivo", command=mapear, bg="#18E667", fg="#032612")
    mapear_btn.pack(side="left")

    aviso_record()
    escribir_log()
    raiz.mainloop()


if __name__ == "__main__":
    if getattr(sys, "frozen", False) or "--gui" in sys.argv:
        main_gui()
    else:
        main()
