using UnityEngine;

namespace BlackRoad.Worldbuilder.Interaction
{
    /// <summary>
    /// Base component for objects that can be interacted with by the player.
    /// </summary>
    public abstract class Interactable : MonoBehaviour
    {
        [Tooltip("Display name shown in UI when player looks at this.")]
        [SerializeField] private string displayName = "Object";

        [Tooltip("Optional interaction verb (e.g., 'Feed', 'Open', 'Talk').")]
        [SerializeField] private string verb = "Use";

        public string DisplayName => displayName;
        public string Verb => verb;

        /// <summary>
        /// Called when the player attempts to interact with this object.
        /// </summary>
        public abstract void Interact(GameObject interactor);
    }
}
