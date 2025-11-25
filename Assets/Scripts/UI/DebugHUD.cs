using UnityEngine;
using BlackRoad.Worldbuilder.Environment;
using BlackRoad.Worldbuilder.Building;
using BlackRoad.Worldbuilder.Player;

namespace BlackRoad.Worldbuilder.UI
{
    /// <summary>
    /// Very simple on-screen HUD for development:
    /// shows time of day, current build prefab, and fly/walk mode.
    /// </summary>
    public class DebugHUD : MonoBehaviour
    {
        [SerializeField] private DayNightCycle dayNight;
        [SerializeField] private BuildTool buildTool;
        [SerializeField] private PlayerController playerController;

        [Header("Style")]
        [SerializeField] private int fontSize = 14;
        [SerializeField] private Color textColor = Color.white;
        [SerializeField] private Vector2 margin = new Vector2(10f, 10f);

        private GUIStyle _style;

        private void Awake()
        {
            if (dayNight == null)
                dayNight = FindObjectOfType<DayNightCycle>();
            if (buildTool == null)
                buildTool = FindObjectOfType<BuildTool>();
            if (playerController == null)
                playerController = FindObjectOfType<PlayerController>();
        }

        private void OnGUI()
        {
            if (_style == null)
            {
                _style = new GUIStyle(GUI.skin.label)
                {
                    fontSize = fontSize,
                    normal = { textColor = textColor }
                };
            }

            float x = margin.x;
            float y = margin.y;

            string mode = playerController != null && playerController.IsFlying ? "FLY" : "WALK";
            string blockName = buildTool != null && buildTool.CurrentPrefab != null
                ? buildTool.CurrentPrefab.name
                : "(none)";

            string timeStr = dayNight != null
                ? $"{(dayNight.timeOfDay * 24f):0.0}h"
                : "n/a";

            GUI.Label(new Rect(x, y, 400f, 24f),
                $"Time: {timeStr}   Mode: {mode}   Block: {blockName}",
                _style);

            y += 22f;
            GUI.Label(new Rect(x, y, 400f, 24f),
                "LMB: place   RMB: remove   1–9: select prefab   F: toggle fly",
                _style);
        }
    }
}
