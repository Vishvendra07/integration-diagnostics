"""Compare a customer mapping with a fixture schema and export a redacted support bundle."""

import argparse
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo

MAPPING = {"external_id": "contact_id", "stage": "sales_state", "display_name": "display_name"}
SCHEMA = {
    "contact_id": "string",
    "status": "string",
    "display_name": "string",
    "referrer": "string",
}
EXPECTED_TYPES = {"external_id": "string", "stage": "string", "display_name": "string"}


def diagnose(config, schema, errors):
    mapping = config["fields"]
    missing = sorted(
        key for key, name in mapping.items() if key in EXPECTED_TYPES and name not in schema
    )
    mismatch = sorted(
        key
        for key, name in mapping.items()
        if key in EXPECTED_TYPES and name in schema and EXPECTED_TYPES[key] != schema[name]
    )
    absent = sorted(EXPECTED_TYPES.keys() - mapping.keys())
    known_codes = {"rate_limit", "schema_drift", "unauthorized", "timeout"}
    counts = {}
    for event in errors:
        code = event.get("code")
        code = code if isinstance(code, str) and code in known_codes else "other"
        counts[code] = counts.get(code, 0) + 1
    return {
        "config_revision": int(config["version"]),
        "mapped_fields_missing": missing,
        "type_mismatch": mismatch,
        "unmapped_required_fields": absent,
        "error_counts": counts,
        "ready": not (missing or mismatch or absent),
    }


def export(path, report):
    with ZipFile(path, "w") as archive:
        files = {
            "manifest.json": {
                "format_version": 1,
                "files": ["report.json"],
                "scope": "Field categories and counts only",
            },
            "report.json": report,
        }
        for name, result in files.items():
            archive.writestr(ZipInfo(name), json.dumps(result, sort_keys=True, indent=2) + "\n")


def demo():
    return diagnose(
        {"version": 2, "fields": MAPPING},
        SCHEMA,
        [
            {"code": "schema_drift", "details": "sample payload"},
            {"code": "rate_limit", "url": "local"},
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, help="JSON object with config, schema, and error list"
    )
    parser.add_argument("--bundle", type=Path)
    args = parser.parse_args()
    result = (
        diagnose(**json.loads(args.input.read_text(encoding="utf-8"))) if args.input else demo()
    )
    if args.bundle:
        export(args.bundle, result)
    print(json.dumps(result, indent=2))
