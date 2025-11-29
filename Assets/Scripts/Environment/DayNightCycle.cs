using UnityEngine;

namespace BlackRoad.Worldbuilder.Environment
{
    /// <summary>
    /// Simple day/night cycle: rotates the directional light and
    /// adjusts intensity + fog color over a 24h-style loop.
    /// </summary>
    public class DayNightCycle : MonoBehaviour
    {
        [Header("References")]
        [Tooltip("Main directional light used as the sun.")]
        public Light sunLight;

        [Header("Time")]
        [Tooltip("Length of a full day/night cycle in real seconds.")]
        public float dayLengthSeconds = 600f; // 10 minutes

        [Range(0f, 1f)]
        [Tooltip("Current normalized time of day (0 = sunrise, 0.5 = sunset).")]
        public float timeOfDay = 0.25f;

        [Header("Lighting")]
        public Gradient sunColorOverDay;
        public AnimationCurve sunIntensityOverDay = AnimationCurve.Linear(0, 0, 1, 1);

        [Header("Fog")]
        public bool controlFog = true;
        public Gradient fogColorOverDay;
        public AnimationCurve fogDensityOverDay = AnimationCurve.Linear(0, 0.002f, 1, 0.01f);

        private float _timeSpeed;

        private void Reset()
        {
            // Reasonable defaults if you drop it into scene
            dayLengthSeconds = 600f;
            timeOfDay = 0.25f;
            sunIntensityOverDay = AnimationCurve.EaseInOut(0, 0, 0.25f, 1f);
        }

        private void Start()
        {
            if (sunLight == null)
            {
                sunLight = RenderSettings.sun;
            }

            if (dayLengthSeconds <= 0f)
                dayLengthSeconds = 600f;

            _timeSpeed = 1f / dayLengthSeconds;
        }

        private void Update()
        {
            // Advance normalized time [0–1]
            timeOfDay += _timeSpeed * Time.deltaTime;
            if (timeOfDay > 1f)
                timeOfDay -= 1f;

            UpdateSun();
            UpdateFog();
        }

        private void UpdateSun()
        {
            if (sunLight == null) return;

            // Rotate sun: 0..1 -> 0..360 degrees
            float sunAngle = timeOfDay * 360f - 90f; // -90 makes 0 = sunrise on horizon
            sunLight.transform.rotation = Quaternion.Euler(sunAngle, 170f, 0f);

            if (sunColorOverDay != null)
                sunLight.color = sunColorOverDay.Evaluate(timeOfDay);

            if (sunIntensityOverDay != null)
                sunLight.intensity = sunIntensityOverDay.Evaluate(timeOfDay);
        }

        private void UpdateFog()
        {
            if (!controlFog) return;

            if (fogColorOverDay != null)
                RenderSettings.fogColor = fogColorOverDay.Evaluate(timeOfDay);

            if (fogDensityOverDay != null)
                RenderSettings.fogDensity = fogDensityOverDay.Evaluate(timeOfDay);
        }
    }
}
