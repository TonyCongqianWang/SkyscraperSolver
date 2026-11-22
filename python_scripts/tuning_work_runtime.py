"""Strict loader and parser for the instrumented solver's pooled work model."""
import hashlib
import json
import math
from pathlib import Path

from calibrate_work import COUNTER_NAMES, SCHEMA
from work_model_export import FORMAT, FORMAT_VERSION, predict_seconds

DEFAULT_MODEL = (Path(__file__).resolve().parent / "models"
                 / "work_calibration.model.json")


def load_model(path=DEFAULT_MODEL):
    source = Path(path)
    payload = source.read_bytes()
    model = json.loads(payload)
    if (model.get("format") != FORMAT
            or model.get("format_version") != FORMAT_VERSION
            or model.get("fit") != "pooled"
            or model.get("counter_schema") != SCHEMA):
        raise ValueError("Unsupported pooled work calibration format or counter schema")
    coeffs = model.get("seconds_per_count", {})
    if set(coeffs) != set(COUNTER_NAMES):
        raise ValueError("Work counter names do not match instrumented solver")
    for value in [model.get("intercept_seconds"), *coeffs.values()]:
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid work model coefficient")
    return model, hashlib.sha256(payload).hexdigest()


def parse_record(lines, model):
    """Require exactly one complete WORK_COUNTERS record, or fail closed."""
    records = [line.strip() for line in lines
               if line.strip().startswith("WORK_COUNTERS ")]
    if len(records) != 1:
        raise ValueError("Expected exactly one WORK_COUNTERS record; check instrumented build")
    parts = records[0].split()
    if len(parts) < 5 or parts[:2] != ["WORK_COUNTERS", model["counter_schema"]]:
        raise ValueError("Work output counter schema mismatch")
    parsed = {}
    for field in parts[2:]:
        if field.count("=") != 1:
            raise ValueError("Malformed work counter field")
        name, raw = field.split("=", 1)
        if name in parsed or not raw.isdecimal():
            raise ValueError("Duplicated or non-integer work counter")
        parsed[name] = int(raw)
    if set(parsed) != set(model["seconds_per_count"]) | {"nodes", "solutions"}:
        raise ValueError("Incomplete work counter record")
    counters = {name: parsed[name] for name in model["seconds_per_count"]}
    seconds = predict_seconds(model, counters)
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Invalid predicted work")
    return seconds, parsed["nodes"], parsed["solutions"]
