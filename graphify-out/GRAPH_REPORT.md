# Graph Report - coverMaster  (2026-10-10)

## Corpus Check
- 18 files · ~19,095 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: .mdc 2, .spec 2)

## Summary
- 216 nodes · 344 edges · 26 communities (15 shown, 11 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c00479a7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_gui
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
- LottoOptimizerV3_11.py
- DECISIONES.md
- LottoOptimizerV3
- BitUtils
- BitUtils
- main
- Configuracion
- Configuracion
- DESIGN.md

## God Nodes (most connected - your core abstractions)
1. `main_gui()` - 23 edges
2. `LottoOptimizerV3` - 18 edges
3. `LottoOptimizerV3` - 18 edges
4. `Lotto Optimizer V3.10` - 16 edges
5. `main()` - 12 edges
6. `main()` - 12 edges
7. `_anotar()` - 10 edges
8. `main_gui()` - 9 edges
9. `datos_desde_ui()` - 9 edges
10. `_trabajo()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `main_gui()` --indirect_call--> `mapear()`  [INFERRED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 0 → community 17_
- `main()` --calls--> `limpiar_pantalla()`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 17_
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 23 → community 17_
- `trabajo()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 23 → community 0_
- `trabajo()` --calls--> `LottoOptimizerV3`  [EXTRACTED]
  LottoOptimizerV3_10.py → LottoOptimizerV3_10.py  _Bridges community 1 → community 0_

## Import Cycles
- None detected.

## Communities (26 total, 11 thin omitted)

### Community 0 - "main_gui"
Cohesion: 0.17
Nodes (10): descargar_reducida_lotoideas(), escribir_apuestas(), _grupos_desde_texto(), _leer_enteros_gui(), main_gui(), aviso_record(), lanzar(), trabajo() (+2 more)

### Community 2 - "Lotto Optimizer V3.10"
Cohesion: 0.12
Nodes (16): Cobertura, Ganancia, Generación, Grupos, Lotto Optimizer V3.10, Muestra de sorteos, Números reales, Optimización (+8 more)

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 4 - "main_gui"
Cohesion: 0.11
Nodes (30): datos_desde_ui(), descargar_reducida_lotoideas(), escribir_apuestas(), escrutar_apuestas(), main_gui(), analizar(), _anotar(), calcular() (+22 more)

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

### Community 17 - "LottoOptimizerV3_11.py"
Cohesion: 0.11
Nodes (28): dataclasses, datetime, io, analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), leer_entero(), leer_grupos() (+20 more)

### Community 22 - "main"
Cohesion: 0.23
Nodes (12): analizar_entrada_numeros(), CondicionGrupo, configurar_consola(), _grupos_desde_texto(), grupos_traducidos(), leer_entero(), leer_grupos(), leer_parametros() (+4 more)

## Knowledge Gaps
- **48 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 90 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main_gui()` connect `main_gui` to `LottoOptimizerV3_11.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `main_gui`, `LottoOptimizerV3_11.py`, `Configuracion`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `Configuracion`, `LottoOptimizerV3_11.py`, `main_gui`, `main`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Lotto Optimizer V3.10` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `main_gui` be split into smaller, more focused modules?**
  _Cohesion score 0.10695187165775401 - nodes in this community are weakly interconnected._
- **Should `LottoOptimizerV3_11.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._