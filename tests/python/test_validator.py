import json
import tempfile
import unittest
from pathlib import Path

from validator.validator import point_from_json, terminals_connected, validate


class ValidatorTests(unittest.TestCase):
    """Примеры unit- и интеграционного тестов валидатора."""

    def test_point_from_json_returns_coordinates(self):
        point, error = point_from_json({"x": 3, "y": 5}, "net-1")

        self.assertEqual((3, 5), point)
        self.assertIsNone(error)

    def test_terminals_connected_rejects_disconnected_terminal(self):
        is_connected, error = terminals_connected(
            {(0, 0), (1, 0), (3, 0)},
            [{"from": {"x": 0, "y": 0}, "to": {"x": 1, "y": 0}}],
            "net-1",
        )

        self.assertFalse(is_connected)
        self.assertIn("отсутствуют в рёбрах", error)

    def test_validate_accepts_connected_output(self):
        input_data = {"nets": [{"net_id": "net-1", "terminals": [{"x": 0, "y": 0}, {"x": 2, "y": 0}]}]}
        output_data = {"nets": [{"net_id": "net-1", "edges": [{"from": {"x": 0, "y": 0}, "to": {"x": 2, "y": 0}}]}]}

        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "output.json"
            input_path.write_text(json.dumps(input_data), encoding="utf-8")
            output_path.write_text(json.dumps(output_data), encoding="utf-8")

            is_valid, message = validate(input_path, output_path)

        self.assertTrue(is_valid)
        self.assertIn("терминалы соединены", message)


if __name__ == "__main__":
    unittest.main()
