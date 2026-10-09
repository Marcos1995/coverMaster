"""
LOTTO OPTIMIZER V3.9 - Pantalla limpia y guardado exclusivo del MEJOR récord
===========================================================================
"""
import random
import os
import math
import copy
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum

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

class Velocidad(Enum):
    RAPIDA = ("RAPIDA", 0.990, 500, 0.8)
    MEDIA = ("MEDIA", 0.995, 800, 0.85)
    LENTA = ("LENTA", 0.998, 1200, 0.9)
    ULTRA = ("ULTRA", 0.999, 1500, 0.92)
    TURBO = ("TURBO", 0.985, 300, 0.75)
    USUARIO = ("USUARIO", 0.995, 800, 0.85)

    def __init__(self, nombre: str, factor: float, umbral: int, ratio_1num: float):
        self._nombre = nombre
        self._factor = factor
        self._umbral = umbral
        self._ratio_1num = ratio_1num

    @property
    def nombre(self) -> str: return self._nombre
    @property
    def factor_enfriamiento(self) -> float: return self._factor
    @property
    def umbral_estancamiento(self) -> int: return self._umbral
    @property
    def ratio_mutacion_1num(self) -> float: return self._ratio_1num

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
    max_snapshots: int = 10 
    max_caida_permitida: float = 0.3 
    snapshot_intervalo: int = 500 
    cache_size: int = 50_000
    condiciones_grupos: List[CondicionGrupo] = field(default_factory=list)

@dataclass
class Snapshot:
    apuestas_bits: List[int]
    conteos: List[int]
    cobertura: float
    ciclo: int
    temperatura: float
    timestamp: datetime = field(default_factory=datetime.now)

class BitUtils:
    _cache_lista_a_bits = {}
    _cache_bits_a_lista = {}

    @staticmethod
    def lista_a_bits(nums: List[int]) -> int:
        key = tuple(sorted(nums))
        if key in BitUtils._cache_lista_a_bits: return BitUtils._cache_lista_a_bits[key]
        resultado = sum(1 << (n - 1) for n in nums)
        if len(BitUtils._cache_lista_a_bits) < 100000: BitUtils._cache_lista_a_bits[key] = resultado
        return resultado

    @staticmethod
    def bits_a_lista(bits: int, max_val: int) -> List[int]:
        key = (bits, max_val)
        if key in BitUtils._cache_bits_a_lista: return BitUtils._cache_bits_a_lista[key].copy()
        resultado = [i + 1 for i in range(max_val) if bits & (1 << i)]
        if len(BitUtils._cache_bits_a_lista) < 100000: BitUtils._cache_bits_a_lista[key] = resultado
        return resultado

    @staticmethod
    def contar_coincidencias(bits1: int, bits2: int) -> int:
        interseccion = bits1 & bits2
        try: return interseccion.bit_count()
        except AttributeError: return bin(interseccion).count('1')

class SistemaSnapshots:
    def __init__(self, max_snapshots: int = 10):
        self.snapshots: List[Snapshot] = []
        self.max_snapshots = max_snapshots
        self.mejor_snapshot: Optional[Snapshot] = None

    def guardar(self, apuestas, conteos, cobertura, ciclo, temperatura):
        snapshot = Snapshot(copy.deepcopy(apuestas), copy.deepcopy(conteos), cobertura, ciclo, temperatura)
        self.snapshots.append(snapshot)
        if self.mejor_snapshot is None or cobertura > self.mejor_snapshot.cobertura: self.mejor_snapshot = snapshot
        if len(self.snapshots) > self.max_snapshots:
            peor = sorted(self.snapshots, key=lambda s: s.cobertura)[0]
            if peor != self.mejor_snapshot: self.snapshots.remove(peor)

    def obtener_mejor(self): return self.mejor_snapshot

class MotorMutaciones:
    def __init__(self, config: Configuracion):
        self.config = config

    def mutar(self, bits: int) -> int:
        nums = BitUtils.bits_a_lista(bits, self.config.v)
        disponibles = [n for n in range(1, self.config.v + 1) if n not in nums]
        if not nums or not disponibles: return bits
        nums = nums.copy()
        nums.remove(random.choice(nums))
        nums.append(random.choice(disponibles))
        return BitUtils.lista_a_bits(nums)

class LottoOptimizerV3:
    def __init__(self, config: Configuracion):
        self.config = config
        self.universo = [BitUtils.lista_a_bits(random.sample(range(1, config.v + 1), config.m)) for _ in range(config.universo_size)]
        self.total_sorteos = len(self.universo)
        self.apuestas_bits = []
        self.conteos = [0] * self.total_sorteos
        self.velocidad = Velocidad.MEDIA
        self.temperatura = 1.0
        self.ciclos = 0
        self.mejor_cobertura = 0.0
        
        # Almacenamos únicamente las apuestas correspondientes al récord absoluto
        self.mejor_apuestas_bits = []
        
        self.snapshots = SistemaSnapshots(config.max_snapshots)
        self.mutador = MotorMutaciones(config)
        self._cache_ganancias = {}

    @property
    def cobertura(self) -> float:
        return (sum(1 for c in self.conteos if c > 0) / self.total_sorteos) * 100
    @property
    def num_apuestas(self) -> int: return len(self.apuestas_bits)

    def es_apuesta_valida_por_grupos(self, bits: int) -> bool:
        if not self.config.condiciones_grupos: return True
        for cond in self.config.condiciones_grupos:
            aciertos = BitUtils.contar_coincidencias(bits, cond.mascara)
            if aciertos > cond.max_aciertos + 2: 
                return False
        return True

    def agregar_apuesta(self, nums: List[int]) -> None:
        bits = BitUtils.lista_a_bits(nums)
        self.apuestas_bits.append(bits)
        for i, sorteo in enumerate(self.universo):
            if BitUtils.contar_coincidencias(bits, sorteo) >= self.config.t: self.conteos[i] += 1

    def generar_aleatorias(self, cantidad: int) -> None:
        print(f"\nGenerando {cantidad} apuestas... (PULSA Ctrl+C PARA PARAR)")
        generadas = 0
        intentos = 0
        max_intentos = cantidad * 2000

        try:
            while generadas < cantidad and intentos < max_intentos:
                nums = random.sample(range(1, self.config.v + 1), self.config.k)
                bits = BitUtils.lista_a_bits(nums)
                if self.es_apuesta_valida_por_grupos(bits):
                    self.agregar_apuesta(nums)
                    generadas += 1
                    print(f"\r Progreso: {generadas}/{cantidad} | 🎯 Cobertura actual: {self.cobertura:.4f}%          ", end="", flush=True)
                
                intentos += 1
                if intentos % 5000 == 0 and generadas < cantidad and intentos > 20000:
                    self.agregar_apuesta(nums)
                    generadas += 1

            print()
        except KeyboardInterrupt:
            print(f"\n\n🛑 Generación detenida por ti. Apuestas conseguidas: {generadas}. Pasando a optimización...")
            time.sleep(1)

    def calcular_ganancia(self, idx: int, nueva_bits: int) -> int:
        antigua = self.apuestas_bits[idx]
        cache_key = (antigua, nueva_bits)
        if cache_key in self._cache_ganancias: return self._cache_ganancias[cache_key]
        ganancia = 0
        t = self.config.t
        for i, sorteo in enumerate(self.universo):
            antes = BitUtils.contar_coincidencias(antigua, sorteo) >= t
            ahora = BitUtils.contar_coincidencias(nueva_bits, sorteo) >= t
            if antes and not ahora:
                if self.conteos[i] == 1: ganancia -= 1
            elif not antes and ahora:
                if self.conteos[i] == 0: ganancia += 1
        self._cache_ganancias[cache_key] = ganancia
        return ganancia

    def aplicar_mutacion(self, idx: int, nueva_bits: int) -> None:
        antigua = self.apuestas_bits[idx]
        t = self.config.t
        for i, sorteo in enumerate(self.universo):
            if BitUtils.contar_coincidencias(antigua, sorteo) >= t: self.conteos[i] -= 1
            if BitUtils.contar_coincidencias(nueva_bits, sorteo) >= t: self.conteos[i] += 1
        self.apuestas_bits[idx] = nueva_bits

    def optimizar(self) -> None:
        if self.num_apuestas == 0: return
        self.mejor_cobertura = self.cobertura
        self.mejor_apuestas_bits = copy.deepcopy(self.apuestas_bits)
        
        limpiar_pantalla()
        print("=" * 70)
        print(" OPTIMIZANDO - PULSA Ctrl+C EN CUALQUIER MOMENTO PARA SALIR Y GUARDAR")
        print("=" * 70)
        
        try:
            while True:
                self.ciclos += 1
                idx = random.randint(0, self.num_apuestas - 1)
                nueva_bits = self.mutador.mutar(self.apuestas_bits[idx])

                ganancia = self.calcular_ganancia(idx, nueva_bits)
                if ganancia > 0 or (self.temperatura > 0.0001 and random.random() < math.exp(ganancia / self.temperatura)):
                    self.aplicar_mutacion(idx, nueva_bits)
                    if self.cobertura > self.mejor_cobertura:
                        self.mejor_cobertura = self.cobertura
                        # Guardamos copia exacta únicamente de este nuevo récord absoluto
                        self.mejor_apuestas_bits = copy.deepcopy(self.apuestas_bits)
                
                self.temperatura *= 0.9995
                print(f" 🔄 Ciclo: {self.ciclos:,} | 🎯 Récord Cobertura: {self.mejor_cobertura:.4f}% | 🌡️ Temp: {self.temperatura:.4f}   ", end="\r", flush=True)

        except KeyboardInterrupt:
            print(f"\n\n🛑 ¡Optimización detenida por ti! Guardando el MEJOR récord histórico...")
            time.sleep(1)

    def guardar_mejor_record(self) -> str:
        """Guarda exclusivamente un único archivo con el mejor récord absoluto de la sesión"""
        if not self.mejor_apuestas_bits and self.num_apuestas > 0:
            self.mejor_apuestas_bits = copy.deepcopy(self.apuestas_bits)

        cob = self.mejor_cobertura if self.mejor_cobertura > 0 else self.cobertura
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"LOTTO_v{self.config.v}_k{self.config.k}_t{self.config.t}_{cob:.4f}pct_{timestamp}.txt"
        
        apuestas_ordenadas = [sorted(BitUtils.bits_a_lista(b, self.config.v)) for b in self.mejor_apuestas_bits]
        apuestas_ordenadas.sort(key=lambda x: tuple(x))
        
        with open(nombre, 'w', encoding='utf-8') as f:
            for nums in apuestas_ordenadas: 
                f.write(" ".join(f"{n:02d}" for n in nums) + "\n")
        return nombre

def main():
    limpiar_pantalla()
    print(" 🎰 LOTTO OPTIMIZER V3.9 - Guardado Exclusivo del Mejor Récord")
    try:
        v = int(input(" Total números (v): "))
        k = int(input(" Números por apuesta (k): "))
        t = int(input(" Garantía (t): "))
        m = int(input(" Números por sorteo (m): "))
        config = Configuracion(v=v, k=k, t=t, m=m)
        
        if input(" ¿Definir grupos? (s/n): ").lower() == 's':
            num_grupos = int(input(" ¿Cuántos grupos?: "))
            for i in range(num_grupos):
                nums = analizar_entrada_numeros(input(f" Números Grupo {i+1} (ej. 1-12): "))
                min_ac = int(input(f" Mínimo aciertos Grupo {i+1}: "))
                max_ac = int(input(f" Máximo aciertos Grupo {i+1}: "))
                config.condiciones_grupos.append(CondicionGrupo(nums, min_ac, max_ac))
                
        opt = LottoOptimizerV3(config)
        opt.generar_aleatorias(int(input("\n Cantidad de apuestas a generar: ")))
        
        if opt.num_apuestas > 0:
            opt.optimizar()
            arch = opt.guardar_mejor_record()
            print(f"\n ✓ Archivo guardado con el MEJOR récord absoluto: {arch}")
            
            if input("\n ¿Sustituir por números reales? (s/n): ").lower() == 's':
                nums_reales = analizar_entrada_numeros(input(f" Introduce tus {v} números: "))
                if len(nums_reales) == v:
                    arch_pers = arch.replace(".txt", "_PERSONALIZADO.txt")
                    with open(arch, 'r') as fi, open(arch_pers, 'w') as fo:
                        for lin in fi:
                            if lin.strip():
                                fo.write(" ".join(f"{nums_reales[int(x)-1]:02d}" for x in lin.split()) + "\n")
                    print(f" ✓ Mapeo completado. Archivo PERSONALIZADO guardado.")
                else:
                    print(f" ⚠️ Has introducido {len(nums_reales)} números en lugar de {v}. Mapeo cancelado.")
    except Exception as e: 
        print(f" Error: {e}")
        
    input("\n Presiona ENTER para salir...")

if __name__ == "__main__": 
    main()