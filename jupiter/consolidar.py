"""Consolida os JSONs retornados pelo Jupiter sem recalcular suas métricas."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEYS = ("TP", "MRT_ms", "MQT_ms", "U_pct", "DP_pct", "MPT_ms")


def write_csv(name, rows):
    with (ROOT / name).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    with (ROOT / "cenarios.csv").open(encoding="utf-8", newline="") as file:
        cases = list(csv.DictReader(file))
    results = []
    intervals = []
    for case in cases:
        name = case["id"]
        execution = json.loads((ROOT / "simulacoes" / f"{name}.json").read_text(encoding="utf-8"))
        response = execution["response"]
        request = execution["request"]
        assert request["execution_type"] == response["execution_type"] == "spn_stationary_simulation"
        assert response["status"] == "ok" and response["engine"] == "newengine-rust"
        definitions = {d["name"]: int(d["value"]) for d in request["model"]["definitions"]}
        assert all(definitions[key] == int(case[column])
                   for key, column in zip(("LAMBDA", "C", "B", "MU"), ("lambda", "c", "B", "mu")))
        raw = response["result"]
        metrics = {metric: raw["metrics"][metric] for metric in KEYS}
        assert all(math.isfinite(value) for value in metrics.values())
        assert math.isclose(metrics["MRT_ms"], metrics["MQT_ms"] + metrics["MPT_ms"], rel_tol=1e-8)
        assert math.isclose(metrics["TP"], float(case["mu"]) * int(case["c"]) * metrics["U_pct"] / 100,
                            rel_tol=1e-8)
        assert abs(metrics["TP"] - float(case["lambda"]) * (1 - metrics["DP_pct"] / 100)) < 1
        results.append(dict(case, K=definitions["K"], **metrics))
        for key in KEYS:
            stat = raw["statistics"][key]
            assert math.isclose(metrics[key], stat["mean"], rel_tol=1e-8, abs_tol=1e-14)
            intervals.append(dict(id=name, metrica=key, **stat))
    write_csv("resultados.csv", results)
    write_csv("intervalos.csv", intervals)
    print(f"{len(results)} execuções e {len(intervals)} estimativas consolidadas.")


if __name__ == "__main__":
    main()

