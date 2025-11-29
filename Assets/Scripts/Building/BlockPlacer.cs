using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    [RequireComponent(typeof(Camera))]
    public class BlockPlacer : MonoBehaviour
    {
        [Header("Refs")]
        public WorldGrid worldGrid;
        public BlockDatabase blockDatabase;

        [Header("Placement")]
        public float maxDistance = 50f;
        public LayerMask placementMask = ~0;

        private Camera _camera;
        private BlockType _currentBlock;

        private void Awake()
        {
            _camera = GetComponent<Camera>();
        }

        private void Start()
        {
            if (blockDatabase != null)
            {
                _currentBlock = blockDatabase.GetDefault();
            }

            if (worldGrid == null)
            {
                // Try to find one in the scene
                worldGrid = FindObjectOfType<WorldGrid>();
            }
        }

        private void Update()
        {
            if (_camera == null || worldGrid == null || _currentBlock == null)
                return;

            Ray ray = _camera.ScreenPointToRay(UnityEngine.Input.mousePosition);

            if (Physics.Raycast(ray, out RaycastHit hit, maxDistance, placementMask))
            {
                // Place with left click
                if (UnityEngine.Input.GetMouseButtonDown(0))
                {
                    Vector3Int gridPos = worldGrid.WorldToGrid(hit.point + hit.normal * 0.5f);
                    worldGrid.PlaceBlock(gridPos, _currentBlock);
                }

                // Remove with right click
                if (UnityEngine.Input.GetMouseButtonDown(1))
                {
                    Vector3Int gridPos = worldGrid.WorldToGrid(hit.point - hit.normal * 0.5f);
                    worldGrid.RemoveBlock(gridPos);
                }
            }
        }
    }
}
