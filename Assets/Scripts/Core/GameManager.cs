using UnityEngine;

namespace BlackRoad.Worldbuilder.Core
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Building")]
        public Building.BlockDatabase blockDatabase;
        public Building.BlockPlacer blockPlacer;

        [Header("Input")]
        public Input.FlyCameraController flyCamera;

        [Header("Settings")]
        public bool showGridGizmos = true;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Update()
        {
            // Simple escape to quit / future menus
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                Application.Quit();
            }
        }
    }
}
