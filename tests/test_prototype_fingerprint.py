"""Cross-platform source fingerprint guarantees for the offline projection."""
import tempfile
import unittest
from pathlib import Path

from next_season.knowledge.prototype import fingerprint
from next_season.knowledge.repository import load_dataset


class PrototypeFingerprintTests(unittest.TestCase):
    def test_lf_crlf_and_lone_cr_have_the_same_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.csv"
            fingerprints = set()
            for content in (b"crop,value\namaize,1\n", b"crop,value\r\namaize,1\r\n", b"crop,value\ramaize,1\r"):
                path.write_bytes(content)
                fingerprints.add(fingerprint(path))
        self.assertEqual(len(fingerprints), 1)

    def test_real_content_change_still_changes_the_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.csv"
            path.write_bytes(b"crop,value\namaize,1\n")
            original = fingerprint(path)
            path.write_bytes(b"crop,value\namaize,2\n")
            changed = fingerprint(path)
        self.assertNotEqual(original, changed)

    def test_rebuilt_prototype_projection_matches_all_approved_inputs(self):
        projection = load_dataset("prototype_recommendation")
        self.assertEqual(set(projection["release_inputs"]), {
            "slice.json", "crop_calendar_verified.csv",
            "crop_rotation_rules_verified.csv", "rainfall_references_verified.json",
        })


if __name__ == "__main__":
    unittest.main()
