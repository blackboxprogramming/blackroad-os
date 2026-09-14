from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from road_credentials.receipts import MAX_RECEIPT_BYTES, ReceiptError, read_receipt, write_receipt


class ReceiptTests(unittest.TestCase):
    def _receipt(self, rotation_id: str = "rotation-1") -> dict:
        return {
            "rotation_id": rotation_id,
            "started_at": "2026-09-14T00:00:00Z",
            "status": "test",
        }

    def test_receipt_name_stays_inside_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, receipt_hash = write_receipt(root, self._receipt(), previous_hash=None)
            self.assertEqual(root, path.parent)
            self.assertTrue(path.name.endswith("_rotation-1.json"))
            self.assertTrue(receipt_hash.startswith("sha256:"))
            self.assertEqual(receipt_hash, json.loads(path.read_text())["receipt_hash"])
            self.assertEqual(receipt_hash, read_receipt(path)["receipt_hash"])

    def test_unsafe_rotation_ids_are_rejected(self) -> None:
        for rotation_id in ("", "../outside", "a/b", "a b", ".", "a.json"):
            with self.subTest(rotation_id=rotation_id), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, "filename-safe"):
                    write_receipt(Path(directory), self._receipt(rotation_id), previous_hash=None)

    def test_missing_started_at_is_rejected(self) -> None:
        receipt = self._receipt()
        del receipt["started_at"]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "started_at"):
                write_receipt(Path(directory), receipt, previous_hash=None)

    def test_started_at_cannot_inject_a_path(self) -> None:
        receipt = self._receipt()
        receipt["started_at"] = "../../outside"
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "UTC ISO-8601"):
                write_receipt(Path(directory), receipt, previous_hash=None)

    def test_duplicate_receipt_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text('{"receipt_hash":"a","receipt_hash":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(ReceiptError, "duplicate receipt field"):
                read_receipt(path)

    def test_receipt_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "receipt.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(ReceiptError, "cannot be opened safely"):
                read_receipt(link)

    def test_oversized_receipt_is_rejected_before_parse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            with path.open("wb") as handle:
                handle.truncate(MAX_RECEIPT_BYTES + 1)
            with self.assertRaisesRegex(ReceiptError, "receipt exceeds"):
                read_receipt(path)

    def test_invalid_utf8_and_non_object_receipts_are_rejected(self) -> None:
        for payload in (b"\xff", b"[]"):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "receipt.json"
                path.write_bytes(payload)
                with self.assertRaises(ReceiptError):
                    read_receipt(path)


if __name__ == "__main__":
    unittest.main()
