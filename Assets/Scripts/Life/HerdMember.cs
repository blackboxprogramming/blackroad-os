using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// Attached to critters that belong to a herd.
    /// Provides a steering offset (cohesion + separation) that
    /// can be used by movement logic (e.g. CritterAgent).
    /// </summary>
    [RequireComponent(typeof(CritterAgent))]
    public class HerdMember : MonoBehaviour
    {
        [SerializeField] private CritterHerd herd;
        [SerializeField] private float steerWeight = 0.6f;

        public Vector3 SteerOffset { get; private set; }

        private void OnEnable()
        {
            if (herd != null)
                herd.Register(this);
        }

        private void OnDisable()
        {
            if (herd != null)
                herd.Unregister(this);
        }

        private void LateUpdate()
        {
            if (herd == null)
            {
                SteerOffset = Vector3.zero;
                return;
            }

            var members = herd.Members;
            if (members == null || members.Count == 0)
            {
                SteerOffset = Vector3.zero;
                return;
            }

            Vector3 cohesion = Vector3.zero;
            Vector3 separation = Vector3.zero;
            int neighborCount = 0;

            foreach (var m in members)
            {
                if (m == null || m == this) continue;

                Vector3 toNeighbor = m.transform.position - transform.position;
                float dist = toNeighbor.magnitude;

                // Cohesion: move toward herd center
                cohesion += m.transform.position;
                neighborCount++;

                // Separation: avoid crowding
                if (dist < herd.SeparationDistance && dist > 0.001f)
                {
                    separation -= toNeighbor / dist; // push away
                }
            }

            if (neighborCount > 0)
            {
                cohesion /= neighborCount;
                cohesion = (cohesion - transform.position).normalized * herd.CohesionWeight;
            }

            separation *= herd.SeparationWeight;

            Vector3 combined = cohesion + separation;
            combined.y = 0f; // stay horizontal

            SteerOffset = combined.normalized * steerWeight;
        }
    }
}
