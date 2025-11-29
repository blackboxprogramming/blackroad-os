using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using BlackRoad.Worldbuilder.Building;

namespace BlackRoad.Worldbuilder.Core
{
    /// <summary>
    /// Saves and loads all Buildable objects in the scene
    /// to a JSON file in Application.persistentDataPath.
    /// F5 = save, F9 = load (default slot "slot1").
    /// </summary>
    public class WorldSerializer : MonoBehaviour
    {
        [Header("Registry")]
        [SerializeField] private BuildableRegistry registry;

        [Header("Slot")]
        [SerializeField] private string slotName = "slot1";

        [Header("Keys")]
        [SerializeField] private KeyCode saveKey = KeyCode.F5;
        [SerializeField] private KeyCode loadKey = KeyCode.F9;

        [Header("Options")]
        [SerializeField] private bool autoCreateFolder = true;
        [SerializeField] private string folderName = "WorldSaves";

        [Serializable]
        private class PlacedObjectData
        {
            public string id;
            public float px, py, pz;
            public float rx, ry, rz;
            public float sx, sy, sz;
        }

        [Serializable]
        private class WorldSave
        {
            public PlacedObjectData[] objects;
        }

        private string SaveDirectory =>
            autoCreateFolder
                ? Path.Combine(Application.persistentDataPath, folderName)
                : Application.persistentDataPath;

        private string SavePath =>
            Path.Combine(SaveDirectory, $"{slotName}.json");

        private void Update()
        {
            if (Input.GetKeyDown(saveKey))
            {
                Save();
            }

            if (Input.GetKeyDown(loadKey))
            {
                Load();
            }
        }

        [ContextMenu("Save Now")]
        public void Save()
        {
            if (registry == null)
            {
                Debug.LogError("[WorldSerializer] No BuildableRegistry assigned.");
                return;
            }

            var buildables = FindObjectsOfType<Buildable>();
            var list = new List<PlacedObjectData>();

            foreach (var b in buildables)
            {
                if (b == null) continue;

                var t = b.transform;
                var id = b.Id;
                if (string.IsNullOrWhiteSpace(id))
                    continue;

                var data = new PlacedObjectData
                {
                    id = id,
                    px = t.position.x,
                    py = t.position.y,
                    pz = t.position.z,
                    rx = t.rotation.eulerAngles.x,
                    ry = t.rotation.eulerAngles.y,
                    rz = t.rotation.eulerAngles.z,
                    sx = t.localScale.x,
                    sy = t.localScale.y,
                    sz = t.localScale.z
                };

                list.Add(data);
            }

            var save = new WorldSave { objects = list.ToArray() };
            string json = JsonUtility.ToJson(save, true);

            if (!Directory.Exists(SaveDirectory))
            {
                Directory.CreateDirectory(SaveDirectory);
            }

            File.WriteAllText(SavePath, json);
            Debug.Log($"[WorldSerializer] Saved {list.Count} objects to {SavePath}");
        }

        [ContextMenu("Load Now")]
        public void Load()
        {
            if (registry == null)
            {
                Debug.LogError("[WorldSerializer] No BuildableRegistry assigned.");
                return;
            }

            if (!File.Exists(SavePath))
            {
                Debug.LogWarning($"[WorldSerializer] No save file at {SavePath}");
                return;
            }

            string json = File.ReadAllText(SavePath);
            var save = JsonUtility.FromJson<WorldSave>(json);
            if (save == null || save.objects == null)
            {
                Debug.LogError("[WorldSerializer] Failed to parse save file.");
                return;
            }

            // Remove existing buildables first
            var existing = FindObjectsOfType<Buildable>();
            foreach (var b in existing)
            {
                if (b != null)
                {
                    Destroy(b.gameObject);
                }
            }

            int spawned = 0;
            foreach (var obj in save.objects)
            {
                var prefab = registry.GetPrefab(obj.id);
                if (prefab == null)
                {
                    Debug.LogWarning($"[WorldSerializer] No prefab for id '{obj.id}'");
                    continue;
                }

                Vector3 pos = new Vector3(obj.px, obj.py, obj.pz);
                Quaternion rot = Quaternion.Euler(obj.rx, obj.ry, obj.rz);
                Vector3 scale = new Vector3(obj.sx, obj.sy, obj.sz);

                var instance = Instantiate(prefab, pos, rot);
                instance.transform.localScale = scale;

                spawned++;
            }

            Debug.Log($"[WorldSerializer] Loaded {spawned} objects from {SavePath}");
        }
    }
}
