using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Building
{
    [CreateAssetMenu(
        fileName = "BlockDatabase",
        menuName = "BlackRoad/Worldbuilder/BlockDatabase",
        order = 1
    )]
    public class BlockDatabase : ScriptableObject
    {
        public BlockType[] blocks;

        private Dictionary<string, BlockType> _byId;

        private void OnEnable()
        {
            BuildIndex();
        }

        private void BuildIndex()
        {
            _byId = new Dictionary<string, BlockType>();

            if (blocks == null) return;

            foreach (var block in blocks)
            {
                if (block == null || string.IsNullOrEmpty(block.blockId)) continue;

                if (!_byId.ContainsKey(block.blockId))
                {
                    _byId.Add(block.blockId, block);
                }
            }
        }

        public BlockType Get(string id)
        {
            if (_byId == null || _byId.Count == 0)
                BuildIndex();

            return _byId != null && _byId.TryGetValue(id, out var block) ? block : null;
        }

        public BlockType GetDefault()
        {
            if (blocks != null && blocks.Length > 0)
                return blocks[0];

            return null;
        }
    }
}
