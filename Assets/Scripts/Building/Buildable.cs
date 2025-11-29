using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    /// <summary>
    /// Attach to any prefab you want the world serializer
    /// to be able to save and reload.
    /// </summary>
    public class Buildable : MonoBehaviour
    {
        [Tooltip("Unique ID used to look up this prefab in the BuildableRegistry.")]
        [SerializeField] private string buildableId = "house.small";

        public string Id => buildableId;

#if UNITY_EDITOR
        private void OnValidate()
        {
            if (string.IsNullOrWhiteSpace(buildableId))
            {
                buildableId = gameObject.name.ToLower().Replace(' ', '_');
            }
        }
#endif
    }
}
