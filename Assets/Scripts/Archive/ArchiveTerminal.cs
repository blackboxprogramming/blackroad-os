using UnityEngine;
using BlackRoad.Worldbuilder.Interaction;

namespace BlackRoad.Worldbuilder.Archive
{
    /// <summary>
    /// In-world terminal that toggles the archive UI panel when interacted with.
    /// Attach to a console/monolith object with a collider.
    /// </summary>
    public class ArchiveTerminal : Interactable
    {
        [SerializeField] private ArchivePanelUI archivePanel;

        private void Awake()
        {
            // Default labels for Interactable UI
#if UNITY_EDITOR
            var so = new UnityEditor.SerializedObject(this);
            so.FindProperty("displayName").stringValue = "Archive Terminal";
            so.FindProperty("verb").stringValue = "Access";
            so.ApplyModifiedPropertiesWithoutUndo();
#endif
        }

        public override void Interact(GameObject interactor)
        {
            if (archivePanel == null)
                archivePanel = Object.FindObjectOfType<ArchivePanelUI>();

            if (archivePanel != null)
            {
                archivePanel.Toggle();
            }
        }
    }
}
