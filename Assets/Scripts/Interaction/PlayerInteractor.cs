using UnityEngine;

namespace BlackRoad.Worldbuilder.Interaction
{
    /// <summary>
    /// Raycasts from the center of the player's view to find Interactable objects.
    /// Shows a simple on-screen prompt and calls Interact() on key press.
    /// </summary>
    public class PlayerInteractor : MonoBehaviour
    {
        [Header("Refs")]
        [SerializeField] private Camera playerCamera;

        [Header("Settings")]
        [SerializeField] private float interactDistance = 4f;
        [SerializeField] private KeyCode interactKey = KeyCode.E;

        [Header("UI")]
        [SerializeField] private bool drawPrompt = true;

        private Interactable _current;

        private void Awake()
        {
            if (playerCamera == null)
                playerCamera = Camera.main;
        }

        private void Update()
        {
            UpdateCurrentTarget();

            if (_current != null && Input.GetKeyDown(interactKey))
            {
                _current.Interact(gameObject);
            }
        }

        private void UpdateCurrentTarget()
        {
            _current = null;
            if (playerCamera == null) return;

            Ray ray = playerCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (Physics.Raycast(ray, out RaycastHit hit, interactDistance))
            {
                _current = hit.collider.GetComponentInParent<Interactable>();
            }
        }

        private void OnGUI()
        {
            if (!drawPrompt || _current == null) return;

            string label = $"{_current.Verb} {_current.DisplayName}  [{interactKey}]";

            GUIStyle style = GUI.skin.label;
            style.alignment = TextAnchor.LowerCenter;
            style.fontSize = 16;

            Rect rect = new Rect(
                0,
                Screen.height - 40,
                Screen.width,
                30
            );

            GUI.Label(rect, label, style);
        }
    }
}
