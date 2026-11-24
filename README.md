# Integration Diagnostics

Detect field mapping drift and export a support bundle that contains field categories and error counts.

[Source](project.py) · [Demo evidence](evidence/demo.json) · [Verification](evidence/checks.json)

## Run locally

Requires Python 3.11+.

```sh
python project.py --bundle support.zip
python -m unittest discover -v
```

## Engineering decision

Use an allowlist for export fields and recognized error codes. Keep source field values, URLs, and free-text failure details outside the archive.

Fixture schemas and a local deterministic bundle. The utility does not send logs to a third party.



[Technology or project reference](https://docs.python.org/3/library/zipfile.html)
