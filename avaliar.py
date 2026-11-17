"""Avaliação estacionária da rede de Petri do servidor web."""
from collections import deque
from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parent
PLACES = ("entrada", "fila", "ocupados", "livres", "vagas")


def stabilize(marking):
    """Dispara transições imediatas até chegar a uma marcação tangível."""
    entrada, fila, ocupados, livres, vagas = marking
    if entrada and vagas:
        entrada, fila, vagas = entrada - 1, fila + 1, vagas - 1
        event = "admissao"
    elif entrada:
        entrada -= 1
        event = "descarte"
    else:
        event = None
    while fila and livres:
        fila, ocupados, livres = fila - 1, ocupados + 1, livres - 1
    return (entrada, fila, ocupados, livres, vagas), event


def fire(marking, arrival, service):
    entrada, fila, occupied, free, slots = marking
    after_arrival, branch = stabilize((entrada + 1, fila, occupied, free, slots))
    yield after_arrival, arrival, branch
    if occupied:
        after_departure, _ = stabilize((0, fila, occupied - 1, free + 1, slots + 1))
        yield after_departure, occupied * service, "conclusao"


def evaluate(case):
    demand, workers, buffer, service = (case[k] for k in ("lambda", "c", "B", "mu"))
    capacity = workers + buffer
    initial = (0, 0, 0, workers, capacity)
    outgoing = {}
    pending = deque([initial])
    while pending:
        marking = pending.popleft()
        if marking in outgoing:
            continue
        edges = list(fire(marking, demand, service))
        outgoing[marking] = edges
        pending.extend(target for target, _, _ in edges if target not in outgoing)
    states = sorted(outgoing, key=lambda m: m[1] + m[2])
    assert len(states) == capacity + 1
    weights = [1.0]
    for low, high in zip(states, states[1:]):
        up = sum(rate for target, rate, _ in outgoing[low] if target == high)
        down = sum(rate for target, rate, _ in outgoing[high] if target == low)
        weights.append(weights[-1] * up / down)
    norm = math.fsum(weights)
    stationary = dict(zip(states, (w / norm for w in weights)))
    rewards = {}
    for marking, probability in stationary.items():
        assert marking[0] == 0 and marking[2] + marking[3] == workers
        assert marking[1] + marking[2] + marking[4] == capacity
        assert marking[1] == 0 or marking[3] == 0
        for target, rate, event in outgoing[marking]:
            rewards[event] = rewards.get(event, 0) + probability * rate
            if target != marking:
                reverse = sum(r for next_state, r, _ in outgoing[target] if next_state == marking)
                assert math.isclose(probability * rate, stationary[target] * reverse, rel_tol=1e-10)
    queue = math.fsum(p * m[1] for m, p in stationary.items())
    busy = math.fsum(p * m[2] for m, p in stationary.items())
    tp = rewards["conclusao"]
    dp = rewards["descarte"] / demand
    assert math.isclose(tp, rewards["admissao"], rel_tol=1e-10)
    assert math.isclose(tp, demand * (1 - dp), rel_tol=1e-10)
    assert math.isclose(tp, service * busy, rel_tol=1e-10)
    return dict(case, K=capacity, TP=tp, MRT_ms=1000 * (queue+busy)/tp,
                MQT_ms=1000 * queue/tp, U_pct=100*busy/workers,
                DP_pct=100*dp, MPT_ms=1000*busy/tp), stationary


def run(folder=ROOT, output=None):
    folder = Path(folder)
    output = Path(output) if output is not None else folder
    with (folder / "cenarios.csv").open(encoding="utf-8", newline="") as file:
        cases = [dict(id=row["id"], **{key: int(row[key]) for key in ("lambda", "c", "B", "mu")})
                 for row in csv.DictReader(file)]
    results = []
    state_rows = []
    for case in cases:
        result, stationary = evaluate(case)
        results.append(result)
        for state, probability in stationary.items():
            state_rows.append(dict(id=case["id"], **dict(zip(PLACES, state)), pi=probability))
    for filename, rows in (("resultados.csv", results), ("estacionario.csv", state_rows)):
        with (output / filename).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return results


if __name__ == "__main__":
    for row in run():
        print(row["id"], *(f'{row[key]:8.3f}' for key in ("TP", "MRT_ms", "MQT_ms", "U_pct", "DP_pct")))
