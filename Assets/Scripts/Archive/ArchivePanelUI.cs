using UnityEngine;
using UnityEngine.UI;

namespace BlackRoad.Worldbuilder.Archive
{
    /// <summary>
    /// Simple on-screen panel that displays world stats from WorldStatsTracker.
    /// Can be toggled on/off by ArchiveTerminal or key.
    /// </summary>
    public class ArchivePanelUI : MonoBehaviour
    {
        [Header("Text Elements")]
        [SerializeField] private Text timeText;
        [SerializeField] private Text populationText;
        [SerializeField] private Text cosmosText;

        [Header("Toggle")]
        [SerializeField] private KeyCode toggleKey = KeyCode.Tab;
        [SerializeField] private bool startVisible = false;

        private CanvasGroup _canvasGroup;

        private void Awake()
        {
            _canvasGroup = GetComponent<CanvasGroup>();
            SetVisible(startVisible);
        }

        private void Update()
        {
            if (Input.GetKeyDown(toggleKey))
            {
                Toggle();
            }

            Refresh();
        }

        public void Refresh()
        {
            var stats = WorldStatsTracker.Instance;
            if (stats == null) return;

            if (timeText != null)
                timeText.text = stats.GetTimeSummary();

            if (populationText != null)
                populationText.text = stats.GetPopulationSummary();

            if (cosmosText != null)
                cosmosText.text = stats.GetCosmosSummary();
        }

        public void Toggle()
        {
            SetVisible(!IsVisible());
        }

        public void SetVisible(bool visible)
        {
            if (_canvasGroup == null) return;

            _canvasGroup.alpha = visible ? 1f : 0f;
            _canvasGroup.interactable = visible;
            _canvasGroup.blocksRaycasts = visible;
        }

        public bool IsVisible()
        {
            return _canvasGroup != null && _canvasGroup.alpha > 0.9f;
        }
    }
}
