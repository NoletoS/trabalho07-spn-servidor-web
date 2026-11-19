"""Executa a rede no motor oficial do Jupiter Analytics do localhost."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:3001/api/engine/execute"

def run(case, time=1500, warmup=75):
    model = json.loads((ROOT / "modelos" / f"{case}.json").read_text(encoding="utf-8"))
    request = dict(
        request_id=f"spn_{case}_{uuid4().hex[:12]}",
        model_type="spn",
        execution_type="spn_stationary_simulation",
        model={key: model[key] for key in ("modelName", "places", "definitions", "rewardMeasures", "transitions")},
        options=dict(
            simulation_time=time, warmup_time=warmup, confidence_level=0.95,
            max_relative_error=0.05, sampling_points=100, seed=7107,
            max_events=10_000_000, parallelism=2, repetitions=32,
            timeout_ms=70_000,
        ),
    )
    http = Request(URL, data=json.dumps(request).encode("utf-8"),
                   headers={"Content-Type": "application/json"})
    try:
        with urlopen(http, timeout=90) as response:
            result = json.load(response)
    except HTTPError as error:
        raise RuntimeError(error.read().decode("utf-8")) from error
    if result.get("status") == "error":
        raise RuntimeError(json.dumps(result.get("errors", result), ensure_ascii=False))
    folder = ROOT / "simulacoes"
    folder.mkdir(exist_ok=True)
    (folder / f"{case}.json").write_text(
        json.dumps({"request": request, "response": result}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(case, result.get("status"), json.dumps((result.get("result") or {}).get("metrics")), flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="*", help="Exemplo: E2b E2c. Sem casos, executa todos.")
    parser.add_argument("--tempo", type=int, default=1500)
    parser.add_argument("--aquecimento", type=int, default=75)
    args = parser.parse_args()
    for case in args.cases or sorted(path.stem for path in (ROOT / "modelos").glob("E*.json")):
        run(case, args.tempo, args.aquecimento)

if __name__ == "__main__":
    main()


