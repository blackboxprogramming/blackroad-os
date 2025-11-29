using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    public class WorldGrid : MonoBehaviour
    {
        [Header("Grid Settings")]
        public float cellSize = 1f;

        private readonly Dictionary<Vector3Int, GameObject> _placedBlocks =
            new Dictionary<Vector3Int, GameObject>();

        public Vector3Int WorldToGrid(Vector3 worldPos)
        {
            return new Vector3Int(
                Mathf.RoundToInt(worldPos.x / cellSize),
                Mathf.RoundToInt(worldPos.y / cellSize),
                Mathf.RoundToInt(worldPos.z / cellSize)
            );
        }

        public Vector3 GridToWorld(Vector3Int gridPos)
        {
            return new Vector3(
                gridPos.x * cellSize,
                gridPos.y * cellSize,
                gridPos.z * cellSize
            );
        }

        public bool TryGetBlock(Vector3Int gridPos, out GameObject block)
        {
            return _placedBlocks.TryGetValue(gridPos, out block);
        }

        public GameObject PlaceBlock(Vector3Int gridPos, BlockType blockType)
        {
            if (blockType == null || blockType.prefab == null)
                return null;

            if (_placedBlocks.ContainsKey(gridPos))
                return _placedBlocks[gridPos];

            Vector3 worldPos = GridToWorld(gridPos);
            var instance = Instantiate(blockType.prefab, worldPos, Quaternion.identity, transform);
            _placedBlocks.Add(gridPos, instance);

            return instance;
        }

        public bool RemoveBlock(Vector3Int gridPos)
        {
            if (!_placedBlocks.TryGetValue(gridPos, out var instance))
                return false;

            _placedBlocks.Remove(gridPos);

            if (instance != null)
            {
                Destroy(instance);
            }

            return true;
        }
    }
}
