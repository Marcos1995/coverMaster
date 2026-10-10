# Graph Report - coverMaster  (2026-10-10)

## Corpus Check
- 21 files · ~42,635 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .mdc 2, .spec 2, .exe 2)

## Summary
- 389 nodes · 826 edges · 29 communities (18 shown, 11 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f1c91909`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LottoOptimizerV3_11.py
- LottoOptimizerV3
- Lotto Optimizer V3.10
- Debug
- main_gui
- Contexto del proyecto
- Dashboard brief (for the Stitch prompt)
- Verify (UI)
- Web design
- Agent rules
- Build judgments with Laya
- Laya
- Review
- Project
- tablas/SKILL.md
- LottoOptimizerV3_13.c
- DECISIONES.md
- LottoOptimizerV3
- main_gui
- LottoOptimizerV3_12.c
- main
- Configuracion
- DESIGN.md
- BitUtils
- BitUtils
- escribir_apuestas

## God Nodes (most connected - your core abstractions)
1. `main_gui()` - 23 edges
2. `api_dispatch()` - 23 edges
3. `api_dispatch()` - 21 edges
4. `LottoOptimizerV3` - 18 edges
5. `LottoOptimizerV3` - 18 edges
6. `Lotto Optimizer V3.10` - 16 edges
7. `parse_datos()` - 15 edges
8. `parse_datos()` - 15 edges
9. `hilo()` - 14 edges
10. `hilo()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `main_gui()` --indirect_call--> `mapear()`  [INFERRED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 20 → community 22_
- `main()` --calls--> `escribir_apuestas()`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 28 → community 22_
- `trabajo()` --calls--> `escribir_apuestas()`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 28 → community 20_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 24 → community 22_
- `trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 24 → community 20_

## Import Cycles
- None detected.

## Communities (29 total, 11 thin omitted)

### Community 0 - "LottoOptimizerV3_11.py"
Cohesion: 0.17
Nodes (18): dataclasses, datetime, io, LOTTO OPTIMIZER V3.10 - Pantalla limpia y guardado exclusivo del MEJOR récord…, apuesta_pasa_filtros(), _entero_ui(), Filtros, _filtros_desde_ui() (+10 more)

### Community 2 - "Lotto Optimizer V3.10"
Cohesion: 0.12
Nodes (16): Cobertura, Ganancia, Generación, Grupos, Lotto Optimizer V3.10, Muestra de sorteos, Números reales, Optimización (+8 more)

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 4 - "main_gui"
Cohesion: 0.08
Nodes (41): analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), datos_desde_ui(), descargar_reducida_lotoideas(), escribir_apuestas(), escrutar_apuestas(), _grupos_desde_texto() (+33 more)

### Community 5 - "Contexto del proyecto"
Cohesion: 0.29
Nodes (6): Comandos utiles, Contexto del proyecto, Estado, Notas para el agente, Produccion, Stack

### Community 6 - "Dashboard brief (for the Stitch prompt)"
Cohesion: 0.33
Nodes (5): Anatomy (always), Charts without libraries (inline SVG, no CDN), CSS, Dashboard brief (for the Stitch prompt), Data honesty (non-negotiable)

### Community 7 - "Verify (UI)"
Cohesion: 0.40
Nodes (4): 1. Screenshots, 2. Look, 3. Fix and repeat, Verify (UI)

### Community 8 - "Web design"
Cohesion: 0.40
Nodes (4): Before HECHO, Steps, Style = `DESIGN.md`, Web design

### Community 9 - "Agent rules"
Cohesion: 0.50
Nodes (3): Agent rules, Flujo, Think → Simple → Surgical → Verify (Karpathy)

### Community 10 - "Build judgments with Laya"
Cohesion: 0.50
Nodes (3): Build judgments with Laya, Call, Design

### Community 11 - "Laya"
Cohesion: 0.50
Nodes (3): Laya, Reply (decision-only requests), Steps

### Community 12 - "Review"
Cohesion: 0.50
Nodes (3): Check, Do, Review

### Community 13 - "Project"
Cohesion: 0.50
Nodes (3): Docs, Project, Setup

### Community 17 - "LottoOptimizerV3_13.c"
Cohesion: 0.07
Nodes (78): abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar(), api_dispatch(), aplicar(), atender() (+70 more)

### Community 19 - "LottoOptimizerV3"
Cohesion: 0.17
Nodes (4): Configuracion, limpiar_pantalla(), LottoOptimizerV3, MotorMutaciones

### Community 20 - "main_gui"
Cohesion: 0.19
Nodes (9): CondicionGrupo, descargar_reducida_lotoideas(), _grupos_desde_texto(), _leer_enteros_gui(), main_gui(), aviso_record(), lanzar(), trabajo() (+1 more)

### Community 21 - "LottoOptimizerV3_12.c"
Cohesion: 0.06
Nodes (88): commdlg, ctype, limits, abrir_ventana(), acaba_txt(), agregar(), analizar_numeros(), anotar() (+80 more)

### Community 22 - "main"
Cohesion: 0.27
Nodes (10): analizar_entrada_numeros(), configurar_consola(), leer_entero(), leer_grupos(), leer_parametros(), limpiar_pantalla(), main(), mapear() (+2 more)

## Knowledge Gaps
- **48 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 105 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main_gui()` connect `main_gui` to `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `main_gui`, `main`, `Configuracion`, `escribir_apuestas`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_11.py`, `main_gui`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.08019323671497584 - nodes in this community are weakly interconnected._
- **Should `LottoOptimizerV3_13.c` be split into smaller, more focused modules?**
  _Cohesion score 0.07067901234567901 - nodes in this community are weakly interconnected._