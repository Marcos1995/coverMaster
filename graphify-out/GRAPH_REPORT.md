# Graph Report - coverMaster  (2026-10-09)

## Corpus Check
- 14 files · ~5,274 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .mdc 2)

## Summary
- 102 nodes · 114 edges · 17 communities (13 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ef793bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LottoOptimizerV3_9.py
- LottoOptimizerV3
- .__init__
- Debug
- Velocidad
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

## God Nodes (most connected - your core abstractions)
1. `LottoOptimizerV3` - 12 edges
2. `Velocidad` - 7 edges
3. `main()` - 6 edges
4. `Debug` - 6 edges
5. `Contexto del proyecto` - 6 edges
6. `SistemaSnapshots` - 5 edges
7. `Dashboard brief (for the Stitch prompt)` - 5 edges
8. `Configuracion` - 4 edges
9. `BitUtils` - 4 edges
10. `MotorMutaciones` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `Configuracion`  [EXTRACTED]
  LottoOptimizerV3_9.py → LottoOptimizerV3_9.py  _Bridges community 2 → community 0_
- `main()` --calls--> `LottoOptimizerV3`  [EXTRACTED]
  LottoOptimizerV3_9.py → LottoOptimizerV3_9.py  _Bridges community 1 → community 0_

## Import Cycles
- None detected.

## Communities (17 total, 4 thin omitted)

### Community 0 - "LottoOptimizerV3_9.py"
Cohesion: 0.15
Nodes (14): collections, copy, dataclasses, datetime, analizar_entrada_numeros(), CondicionGrupo, limpiar_pantalla(), main() (+6 more)

### Community 1 - "LottoOptimizerV3"
Cohesion: 0.22
Nodes (3): BitUtils, LottoOptimizerV3, Guarda exclusivamente un único archivo con el mejor récord absoluto de la sesión

### Community 2 - ".__init__"
Cohesion: 0.25
Nodes (4): Configuracion, MotorMutaciones, SistemaSnapshots, Snapshot

### Community 3 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

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

## Knowledge Gaps
- **31 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 65 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LottoOptimizerV3` connect `LottoOptimizerV3` to `LottoOptimizerV3_9.py`, `.__init__`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Velocidad` connect `Velocidad` to `LottoOptimizerV3_9.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `SistemaSnapshots` connect `.__init__` to `LottoOptimizerV3_9.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._