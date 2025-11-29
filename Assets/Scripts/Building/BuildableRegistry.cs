using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    /// <summary>
    /// ScriptableObject registry that maps buildable IDs to prefabs.
    /// The world serializer uses this to respawn objects when loading.
    /// </summary>
    [CreateAssetMenu(
        fileName = "BuildableRegistry",
        menuName = "BlackRoad/Worldbuilder/BuildableRegistry",
        order = 10)]
    public class BuildableRegistry : ScriptableObject
    {
        [System.Serializable]
        public class Entry
        {
            public string id;
            public GameObject prefab;
        }

        [SerializeField] private Entry[] entries;

        private Dictionary<string, GameObject> _map;

        private void OnEnable()
        {
            BuildIndex();
        }

        private void BuildIndex()
        {
            _map = new Dictionary<string, GameObject>();

            if (entries == null) return;

            foreach (var e in entries)
            {
                if (e == null || string.IsNullOrWhiteSpace(e.id) || e.prefab == null)
                    continue;

                if (!_map.ContainsKey(e.id))
                {
                    _map.Add(e.id, e.prefab);
                }
            }
        }

        public GameObject GetPrefab(string id)
        {
            if (_map == null || _map.Count == 0)
                BuildIndex();

            return _map != null && _map.TryGetValue(id, out var prefab)
                ? prefab
                : null;
        }
    }
}
