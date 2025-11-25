using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// A simple food source that critters can eat from.
    /// When quantity reaches zero, it can optionally destroy itself.
    /// </summary>
    public class FoodSource : MonoBehaviour
    {
        [SerializeField] private float maxQuantity = 100f;
        [SerializeField] private bool destroyWhenEmpty = true;

        [Tooltip("Units of food restored per second while eating.")]
        [SerializeField] private float nutritionPerSecond = 10f;

        public float Quantity { get; private set; }

        private void Awake()
        {
            Quantity = maxQuantity;
        }

        /// <summary>
        /// Consume some amount of food over deltaTime.
        /// Returns how much nutrition was actually provided.
        /// </summary>
        public float Consume(float deltaTime)
        {
            if (Quantity <= 0f) return 0f;

            float requested = nutritionPerSecond * deltaTime;
            float provided = Mathf.Min(requested, Quantity);
            Quantity -= provided;

            if (Quantity <= 0f && destroyWhenEmpty)
            {
                Destroy(gameObject);
            }

            return provided;
        }
    }
}
