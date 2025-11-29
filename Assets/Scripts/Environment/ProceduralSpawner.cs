using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Environment
{
    /// <summary>
    /// Spawns environment prefabs (trees, rocks, houses) on a Terrain
    /// using simple rules for height, slope, and density.
    /// Run once in editor or at runtime.
    /// </summary>
    public class ProceduralSpawner : MonoBehaviour
    {
        [System.Serializable]
        public class SpawnRule
        {
            public string id = "trees";
            public GameObject prefab;
            [Tooltip("How many instances to try to place.")]
            public int attempts = 500;
            [Tooltip("Minimum normalized height [0..1] on terrain.")]
            [Range(0f, 1f)] public float minHeight = 0f;
            [Range(0f, 1f)] public float maxHeight = 1f;
            [Tooltip("Maximum terrain slope allowed in degrees.")]
            [Range(0f, 90f)] public float maxSlope = 30f;
            [Tooltip("Min distance from other instances of this rule.")]
            public float minSpacing = 3f;
        }

        [Header("Terrain")]
        public Terrain targetTerrain;

        [Header("Spawning Rules")]
        public List<SpawnRule> rules = new List<SpawnRule>();

        [Header("Randomness")]
        public int randomSeed = 12345;

        private TerrainData _terrainData;
        private Vector3 _terrainPos;

        private void OnValidate()
        {
            if (targetTerrain == null)
                targetTerrain = GetComponent<Terrain>();
        }

        [ContextMenu("Spawn All")]
        public void SpawnAll()
        {
            if (targetTerrain == null)
            {
                Debug.LogError("[ProceduralSpawner] No Terrain assigned.");
                return;
            }

            _terrainData = targetTerrain.terrainData;
            _terrainPos = targetTerrain.transform.position;
            Random.InitState(randomSeed);

            foreach (var rule in rules)
            {
                SpawnForRule(rule);
            }
        }

        private void SpawnForRule(SpawnRule rule)
        {
            if (rule.prefab == null)
            {
                Debug.LogWarning($"[ProceduralSpawner] Rule {rule.id} has no prefab.");
                return;
            }

            var placedPositions = new List<Vector3>();

            for (int i = 0; i < rule.attempts; i++)
            {
                // Random point in terrain space (0..1)
                float rx = Random.value;
                float rz = Random.value;

                float height = _terrainData.GetInterpolatedHeight(rx, rz);
                float normHeight = Mathf.InverseLerp(
                    _terrainData.bounds.min.y,
                    _terrainData.bounds.max.y,
                    height + _terrainPos.y
                );

                if (normHeight < rule.minHeight || normHeight > rule.maxHeight)
                    continue;

                // World position
                float worldX = _terrainPos.x + rx * _terrainData.size.x;
                float worldZ = _terrainPos.z + rz * _terrainData.size.z;
                Vector3 worldPos = new Vector3(worldX, height + _terrainPos.y, worldZ);

                // Check slope (avoid steep areas)
                Vector3 normal = _terrainData.GetInterpolatedNormal(rx, rz);
                float slope = Vector3.Angle(normal, Vector3.up);
                if (slope > rule.maxSlope)
                    continue;

                // Respect min spacing
                bool tooClose = false;
                foreach (var p in placedPositions)
                {
                    if (Vector3.SqrMagnitude(p - worldPos) < rule.minSpacing * rule.minSpacing)
                    {
                        tooClose = true;
                        break;
                    }
                }
                if (tooClose) continue;

                // Random rotation around Y
                Quaternion rot = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);

                // Slight random scale
                float scaleFactor = Random.Range(0.85f, 1.15f);
                var instance = Instantiate(rule.prefab, worldPos, rot, transform);
                instance.transform.localScale *= scaleFactor;

                placedPositions.Add(worldPos);
            }

            Debug.Log($"[ProceduralSpawner] Rule {rule.id}: placed {placedPositions.Count} instances.");
        }
    }
}
