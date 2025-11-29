using UnityEngine;
using BlackRoad.Worldbuilder.Interaction;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// Allows the player to feed and "pet" critters.
    /// Feeding reduces hunger via CritterNeeds.
    /// Petting increases a simple trust value.
    /// </summary>
    public class CritterInteraction : Interactable
    {
        [Header("Needs & Behaviour")]
        [SerializeField] private CritterNeeds needs;
        [SerializeField] private CritterAgent agent;

        [Header("Interaction Effects")]
        [Tooltip("How much hunger to reduce per feeding (0..1).")]
        [SerializeField] private float feedAmount = 0.25f;
        [Tooltip("How much trust is gained per pet.")]
        [SerializeField] private float trustIncrease = 0.1f;

        [Header("Trust")]
        [Range(0f, 1f)]
        [SerializeField] private float trust = 0f;

        public float Trust => trust;

        private void Awake()
        {
            if (needs == null)
                needs = GetComponent<CritterNeeds>();
            if (agent == null)
                agent = GetComponent<CritterAgent>();
        }

        public override void Interact(GameObject interactor)
        {
            // Simple rule:
            // - If critter is hungry -> feeding action
            // - Else -> pet action
            if (needs != null && needs.IsHungry)
            {
                Feed();
            }
            else
            {
                Pet();
            }
        }

        private void Feed()
        {
            if (needs == null) return;

            // Feed: lower hunger instantly by some amount.
            needs.SetHunger(Mathf.Clamp01(needs.Hunger - feedAmount));
            trust = Mathf.Clamp01(trust + trustIncrease * 0.5f);

            // Small "happy" animation cue (bob up slightly).
            StartCoroutine(BobAnimation(Color.green));
        }

        private void Pet()
        {
            trust = Mathf.Clamp01(trust + trustIncrease);

            // Slight bob to show reaction.
            StartCoroutine(BobAnimation(Color.cyan));
        }

        private System.Collections.IEnumerator BobAnimation(Color color)
        {
            Renderer rend = GetComponentInChildren<Renderer>();
            Color original = rend != null ? rend.material.color : Color.white;

            float t = 0f;
            Vector3 basePos = transform.position;

            while (t < 0.4f)
            {
                t += Time.deltaTime;
                float bob = Mathf.Sin(t * Mathf.PI * 4f) * 0.05f;
                transform.position = basePos + Vector3.up * bob;

                if (rend != null)
                {
                    rend.material.color = Color.Lerp(original, color, t / 0.4f);
                }

                yield return null;
            }

            transform.position = basePos;
            if (rend != null)
                rend.material.color = original;
        }
    }
}
