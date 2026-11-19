"""Gera modelos JSON do Jupiter a partir das configurações E1–E4."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARAMETERS = {"LAMBDA": "DOUBLE", "C": "INTEGER", "B": "INTEGER", "MU": "DOUBLE"}
POSITIONS = {
    "Fonte": (90, 240), "Entrada": (360, 240), "Fila": (630, 240),
    "Ocupados": (900, 240), "Livres": (765, 400), "Vagas": (510, 80),
    "Chegar": (225, 240), "Admitir": (495, 240), "Descartar": (360, 390),
    "Iniciar": (765, 240), "Concluir": (1035, 240),
}
INITIAL = {"Fonte": "1", "Entrada": "0", "Fila": "0", "Ocupados": "0", "Livres": "C", "Vagas": "K"}
METRICS = {
    "TP": "E{#Ocupados} * MU",
    "MRT_ms": "1000 * (E{#Fila} + E{#Ocupados}) / (E{#Ocupados} * MU)",
    "MQT_ms": "1000 * E{#Fila} / (E{#Ocupados} * MU)",
    "U_pct": "100 * E{#Ocupados} / C",
    "DP_pct": "100 * P{#Vagas = 0}",
    "MPT_ms": "1000 / MU",
}


def make_model(case):
    values = {k: int(case[col]) for k, col in zip(PARAMETERS, ("lambda", "c", "B", "mu"))}
    values["K"] = values["C"] + values["B"]
    definitions = [
        {"id": f"def{i}", "name": key, "type": dtype, "value": str(values[key])}
        for i, (key, dtype) in enumerate({**PARAMETERS, "K": "INTEGER"}.items())
    ]
    # O parâmetro explícito K evita dependência da ordem de avaliação de definições.
    ids = {name: f"p{i}" for i, name in enumerate(INITIAL, 1)}
    places = []
    for name, mark in INITIAL.items():
        x, y = POSITIONS[name]
        initial = values[mark] if mark in values else int(mark)
        places.append(dict(id=ids[name], name=name, x=x, y=y, initialMarking=initial,
                           stringMarking=mark, initialStringMarking=mark))

    def links(names, kind):
        return [dict(type=kind, place=name, multiplicity=1, weight=1) for name in names]

    transitions = []
    arcs = []
    rules = (
        ("Chegar", ("Fonte",), ("Fonte", "Entrada"), (), "1 / LAMBDA", "SINGLE_SERVER"),
        ("Admitir", ("Entrada", "Vagas"), ("Fila",), (), None, "SINGLE_SERVER"),
        ("Descartar", ("Entrada",), (), ("Vagas",), None, "SINGLE_SERVER"),
        ("Iniciar", ("Fila", "Livres"), ("Ocupados",), (), None, "SINGLE_SERVER"),
        ("Concluir", ("Ocupados",), ("Livres", "Vagas"), (), "1 / MU", "INFINITY_SERVER"),
    )
    for i, (name, inputs, outputs, inhibitors, delay, policy) in enumerate(rules, 1):
        tid = f"t{i}"
        ids[name] = tid
        x, y = POSITIONS[name]
        tr = dict(id=tid, name=name, x=x, y=y, labelX=x, labelY=y+45,
                  type="TIMED" if delay else "IMMEDIATE", firingPolicy=policy,
                  raceType="RACE_WITH_ENABLING_MEMORY", priority=1,
                  inputArcs=links(inputs, "INPUT"), outputArcs=links(outputs, "OUTPUT"),
                  inhibitorArcs=links(inhibitors, "INHIBITOR"))
        if delay:
            tr["distribution"] = {"type": "exponential", "parameters": {"Mean delay": delay}}
        else:
            tr["weight"] = 1
        transitions.append(tr)

        for source, target, kind in (
            [(p, name, "normal") for p in inputs]
            + [(name, p, "normal") for p in outputs]
            + [(p, name, "inhibitor") for p in inhibitors]
        ):
            sx, sy = POSITIONS[source]
            tx, ty = POSITIONS[target]
            dx, dy = tx-sx, ty-sy
            if source == "Chegar" and target == "Fonte":
                anchor, angle, line = "top", 90, "right-angle"
            elif abs(dx) >= abs(dy):
                anchor, angle, line = ("right", 180, "straight") if dx > 0 else ("left", 0, "right-angle")
            else:
                anchor, angle, line = ("bottom", 90, "straight") if dy > 0 else ("top", 270, "straight")
            arcs.append(dict(id=f"a{len(arcs)+1}", source=ids[source], target=ids[target],
                             type=kind, sourceAnchor=anchor, targetAnchorAngle=angle,
                             weight="1", lineType=line))

    return dict(modelName=f"Servidor web {case['id']}", definitions=definitions, places=places,
                transitions=transitions, arcs=arcs, executions=[], visualElements=[], chartSquare=False, timeUnit="s",
                rewardMeasures=[dict(id=f"rm{i}", name=name, expression=expr)
                                for i, (name, expr) in enumerate(METRICS.items())])


def main():
    model_dir = ROOT / "modelos"
    model_dir.mkdir(exist_ok=True)
    with (ROOT / "cenarios.csv").open(encoding="utf-8", newline="") as file:
        for case in csv.DictReader(file):
            model = make_model(case)
            (model_dir / f"{case['id']}.json").write_text(
                json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )


if __name__ == "__main__":
    main()


