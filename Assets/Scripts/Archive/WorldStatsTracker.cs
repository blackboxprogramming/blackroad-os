using UnityEngine;
using BlackRoad.Worldbuilder.Environment;
using BlackRoad.Worldbuilder.Life;
using BlackRoad.Worldbuilder.Villagers;
using BlackRoad.Worldbuilder.Space;

namespace BlackRoad.Worldbuilder.Archive
{
    /// <summary>
    /// Central registry for world statistics: population, critters, time, solar system.
    /// Other systems can query this for UI/Archive purposes.
    /// </summary>
    public class WorldStatsTracker : MonoBehaviour
    {
        public static WorldStatsTracker Instance { get; private set; }

        [Header("References")]
        [SerializeField] private DayNightCycle dayNight;
        [SerializeField] private SolarSystemManager solarSystem;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Start()
        {
            if (dayNight == null)
                dayNight = FindObjectOfType<DayNightCycle>();
            if (solarSystem == null)
                solarSystem = FindObjectOfType<SolarSystemManager>();
        }

        // --- Population stats ---

        public int GetCritterCount()
        {
            return FindObjectsOfType<CritterAgent>().Length;
        }

        public int GetVillagerCount()
        {
            return FindObjectsOfType<VillagerAgent>().Length;
        }

        // --- Time / Day stats ---

        public float GetTimeOfDayNormalized()
        {
            return dayNight != null ? dayNight.timeOfDay : 0.5f;
        }

        public float GetTimeOfDayHours()
        {
            return GetTimeOfDayNormalized() * 24f;
        }

        // --- Solar stats (very simple) ---

        public int GetOrbitingBodyCount()
        {
            if (solarSystem == null || solarSystem.bodies == null)
                return 0;

            return solarSystem.bodies.Length;
        }

        // --- High-level summary strings used by UI ---

        public string GetTimeSummary()
        {
            float hours = GetTimeOfDayHours();
            int h = Mathf.FloorToInt(hours);
            int m = Mathf.FloorToInt((hours - h) * 60f);
            return $"Day time: {h:00}:{m:00}";
        }

        public string GetPopulationSummary()
        {
            int critters = GetCritterCount();
            int villagers = GetVillagerCount();
            return $"Critters: {critters}   Villagers: {villagers}";
        }

        public string GetCosmosSummary()
        {
            int bodies = GetOrbitingBodyCount();
            return $"Orbiting bodies tracked: {bodies}";
        }
    }
}
