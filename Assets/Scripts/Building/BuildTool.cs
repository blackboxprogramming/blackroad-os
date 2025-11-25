using System.Collections.Generic;
using UnityEngine;
using BlackRoad.Worldbuilder.Environment;
using BlackRoad.Worldbuilder.Player;

namespace BlackRoad.Worldbuilder.Building
{
    /// <summary>
    /// Lets the player place and remove prefabs on terrain using raycasts.
    /// Left click: place selected prefab (snapped to grid).
    /// Right click: remove hit buildable object.
    /// Number keys 1..N: select prefab.
    /// </summary>
    public class BuildTool : MonoBehaviour
    {
        [Header("Refs")]
        [SerializeField] private Camera playerCamera;
        [SerializeField] private PlayerController playerController;
        [SerializeField] private float maxPlaceDistance = 80f;
        [SerializeField] private LayerMask placementMask = ~0;

        [Header("Building")]
        [SerializeField] private float gridSize = 2f;
        [SerializeField] private List<GameObject> buildPrefabs = new List<GameObject>();

        [Header("Debug")]
        [SerializeField] private Color previewColor = new Color(0f, 1f, 0f, 0.4f);

        public int CurrentIndex { get; private set; } = 0;
        public GameObject CurrentPrefab =>
            buildPrefabs != null && buildPrefabs.Count > 0 && CurrentIndex >= 0 && CurrentIndex < buildPrefabs.Count
                ? buildPrefabs[CurrentIndex]
                : null;

        private Vector3 _lastPreviewPos;
        private bool _hasPreview;

        private void Awake()
        {
            if (playerCamera == null)
                playerCamera = Camera.main;
            if (playerController == null)
                playerController = FindObjectOfType<PlayerController>();
        }

        private void Update()
        {
            HandleSelection();
            HandlePlacement();
        }

        private void HandleSelection()
        {
            // 1..9 selects prefabs
            for (int i = 0; i < buildPrefabs.Count && i < 9; i++)
            {
                if (Input.GetKeyDown(KeyCode.Alpha1 + i))
                {
                    CurrentIndex = i;
                }
            }
        }

        private void HandlePlacement()
        {
            if (playerCamera == null || CurrentPrefab == null)
                return;

            Ray ray = playerCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (Physics.Raycast(ray, out RaycastHit hit, maxPlaceDistance, placementMask))
            {
                Vector3 pos = hit.point;

                // Snap to grid horizontally, keep terrain height
                pos.x = Mathf.Round(pos.x / gridSize) * gridSize;
                pos.z = Mathf.Round(pos.z / gridSize) * gridSize;

                _lastPreviewPos = pos;
                _hasPreview = true;

                // Place
                if (Input.GetMouseButtonDown(0))
                {
                    Instantiate(CurrentPrefab, pos, Quaternion.identity);
                }

                // Remove
                if (Input.GetMouseButtonDown(1))
                {
                    if (hit.collider != null)
                    {
                        // Simple rule: destroy hit object if it has tag "Buildable" or no Rigidbody.
                        var go = hit.collider.gameObject;
                        if (go.CompareTag("Buildable") || go.GetComponent<Rigidbody>() == null)
                        {
                            Destroy(go);
                        }
                    }
                }
            }
            else
            {
                _hasPreview = false;
            }
        }

        private void OnDrawGizmos()
        {
            if (!_hasPreview || CurrentPrefab == null) return;

            Gizmos.color = previewColor;
            Vector3 size = Vector3.one * gridSize;
            Gizmos.DrawCube(_lastPreviewPos, size);
        }
    }
}
