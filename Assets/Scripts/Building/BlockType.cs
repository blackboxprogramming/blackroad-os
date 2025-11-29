using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    [CreateAssetMenu(
        fileName = "BlockType",
        menuName = "BlackRoad/Worldbuilder/BlockType",
        order = 0
    )]
    public class BlockType : ScriptableObject
    {
        public string blockId = "block.dirt";
        public string displayName = "Dirt";
        public GameObject prefab;
        public Color gizmoColor = Color.gray;
    }
}
