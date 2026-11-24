from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from project import diagnose, export


class DiagnosticTests(unittest.TestCase):
    def test_allowlisted_output_omits_values_and_unknown_codes(self):
        sentinel = "this-value-exists-only-in-the-input"
        report = diagnose(
            {
                "version": 2,
                "token": sentinel,
                "fields": {"external_id": "contact_id", "stage": sentinel},
            },
            {"contact_id": "integer"},
            [{"code": sentinel, "detail": sentinel}],
        )
        self.assertEqual(report["mapped_fields_missing"], ["stage"])
        self.assertEqual(report["type_mismatch"], ["external_id"])
        self.assertEqual(report["error_counts"], {"other": 1})
        with TemporaryDirectory() as directory:
            path = Path(directory) / "support.zip"
            export(path, report)
            with ZipFile(path) as bundle:
                self.assertEqual(set(bundle.namelist()), {"manifest.json", "report.json"})
                self.assertNotIn(sentinel, bundle.read("report.json").decode())
