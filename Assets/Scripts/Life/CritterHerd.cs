using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// Defines a herd center and radius. Herd members will try
    /// to stay roughly within this zone.
    /// </summary>
    public class CritterHerd : MonoBehaviour
    {
        [Header("Herd Settings")]
        [SerializeField] private float herdRadius = 30f;
        [SerializeField] private float cohesionWeight = 1f;
        [SerializeField] private float separationDistance = 2f;
        [SerializeField] private float separationWeight = 1.5f;

        private readonly List<HerdMember> _members = new List<HerdMember>();

        public float HerdRadius => herdRadius;
        public float CohesionWeight => cohesionWeight;
        public float SeparationDistance => separationDistance;
        public float SeparationWeight => separationWeight;

        public Vector3 Center
        {
            get
            {
                if (_members.Count == 0) return transform.position;

                Vector3 sum = Vector3.zero;
                foreach (var m in _members)
                {
                    if (m != null)
                        sum += m.transform.position;
                }
                return sum / _members.Count;
            }
        }

        public IReadOnlyList<HerdMember> Members => _members;

        public void Register(HerdMember member)
        {
            if (member != null && !_members.Contains(member))
                _members.Add(member);
        }

        public void Unregister(HerdMember member)
        {
            if (member != null)
                _members.Remove(member);
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 1f, 0.5f, 0.3f);
            Gizmos.DrawWireSphere(transform.position, herdRadius);
        }
    }
}
