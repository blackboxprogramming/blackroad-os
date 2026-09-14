from __future__ import annotations

import unittest

from road_credentials.routes import rotation_route


class RouteTests(unittest.TestCase):
    def test_rotation_route_uses_canonical_ramps_namespace(self) -> None:
        self.assertEqual(
            "road://ramps/road-os/github/credentials/ci/rotations/rotation-1",
            rotation_route(
                runtime_id="road-os",
                connector_id="github",
                credential_id="ci",
                rotation_id="rotation-1",
            ),
        )

    def test_consumer_route_is_a_child_of_the_rotation(self) -> None:
        route = rotation_route(
            runtime_id="road-os",
            connector_id="github",
            credential_id="ci",
            rotation_id="rotation-1",
            consumer_id="deploy",
        )
        self.assertEqual(
            "road://ramps/road-os/github/credentials/ci/rotations/rotation-1/consumers/deploy",
            route,
        )

    def test_route_segments_cannot_inject_structure(self) -> None:
        route = rotation_route(
            runtime_id="road/os",
            connector_id="github?admin=true",
            credential_id="../root",
            rotation_id="rotate#all",
            consumer_id="a/b c",
        )
        self.assertEqual(
            "road://ramps/road%2Fos/github%3Fadmin%3Dtrue/credentials/%2E%2E%2Froot/"
            "rotations/rotate%23all/consumers/a%2Fb%20c",
            route,
        )

    def test_empty_route_segments_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "runtime_id"):
            rotation_route(runtime_id="", connector_id="github", credential_id="ci", rotation_id="r")

    def test_dot_segments_are_encoded(self) -> None:
        route = rotation_route(runtime_id=".", connector_id="..", credential_id="c", rotation_id="r")
        self.assertEqual("road://ramps/%2E/%2E%2E/credentials/c/rotations/r", route)


if __name__ == "__main__":
    unittest.main()
