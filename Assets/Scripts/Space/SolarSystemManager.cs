using System;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Space
{
    /// <summary>
    /// Simulates circular orbits for a small solar system.
    /// Uses "simulated days" as the time unit and updates planet positions
    /// relative to a central star.
    ///
    /// This is not a full N-body physics system; it uses constant angular
    /// velocity per orbit, but the orbital periods are mathematically correct.
    /// </summary>
    public class SolarSystemManager : MonoBehaviour
    {
        [Serializable]
        public class OrbitingBody
        {
            [Tooltip("The transform representing this planet/moon.")]
            public Transform bodyTransform;

            [Tooltip("Orbit center (usually the star or a parent planet).")]
            public Transform orbitCenter;

            [Header("Orbit Parameters")]
            [Tooltip("Orbital radius in Unity units.")]
            public float orbitalRadius = 10f;

            [Tooltip("Orbital period in simulated days (e.g., 365 for Earth).")]
            public float orbitalPeriodDays = 365f;

            [Tooltip("Tilt of orbital plane in degrees.")]
            public float inclinationDegrees = 0f;

            [Tooltip("Starting position along orbit in degrees (0 = x+ axis).")]
            public float initialPhaseDegrees = 0f;

            [Header("Spin")]
            [Tooltip("How long it takes the body to rotate once around its own axis, in simulated hours.")]
            public float rotationPeriodHours = 24f;
        }

        [Header("Time")]
        [Tooltip("How many simulated days pass per real-time second.")]
        public float daysPerRealSecond = 1f / 60f; // 1 day per minute by default

        [Tooltip("Current simulated time in days. Can be set at runtime or in editor.")]
        public double simulatedDays = 0.0;

        [Header("Bodies")]
        public OrbitingBody[] bodies;

        private const float DegreesPerCircle = 360f;

        private void Update()
        {
            // Advance simulation time
            simulatedDays += daysPerRealSecond * Time.deltaTime;

            UpdateBodies();
        }

        private void UpdateBodies()
        {
            if (bodies == null) return;

            foreach (var b in bodies)
            {
                if (b == null || b.bodyTransform == null || b.orbitCenter == null)
                    continue;

                // Guard against invalid period
                if (b.orbitalPeriodDays <= 0.0001f)
                    continue;

                // Compute fraction of orbit completed
                double orbitFraction = simulatedDays / b.orbitalPeriodDays;
                // Convert to angle, add initial phase
                float angleDeg = (float)(orbitFraction * DegreesPerCircle) + b.initialPhaseDegrees;
                float angleRad = angleDeg * Mathf.Deg2Rad;

                // Base position in orbit plane before inclination
                Vector3 localPos = new Vector3(
                    Mathf.Cos(angleRad) * b.orbitalRadius,
                    0f,
                    Mathf.Sin(angleRad) * b.orbitalRadius
                );

                // Apply orbital plane inclination (rotation around X axis)
                Quaternion inclinationRot = Quaternion.Euler(b.inclinationDegrees, 0f, 0f);
                localPos = inclinationRot * localPos;

                // World position is center + localPos
                b.bodyTransform.position = b.orbitCenter.position + localPos;

                // Self-rotation (day/night on the planet)
                if (b.rotationPeriodHours > 0.0001f)
                {
                    // 24 hours per simulated day
                    double totalHours = simulatedDays * 24.0;
                    double spins = totalHours / b.rotationPeriodHours;
                    float spinAngleDeg = (float)(spins * DegreesPerCircle);

                    // Y-axis spin
                    b.bodyTransform.rotation = Quaternion.Euler(0f, spinAngleDeg, 0f);
                }
            }
        }
    }
}
