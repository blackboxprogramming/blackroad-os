using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// Tracks basic physiological needs for a critter (currently hunger only).
    /// Hunger rises over time, and can be reduced by eating FoodSource objects.
    /// </summary>
    public class CritterNeeds : MonoBehaviour
    {
        [Header("Hunger")]
        [SerializeField] private float hunger = 0f; // 0 = full, 1 = starving
        [SerializeField] private float hungerIncreasePerSecond = 0.01f;
        [SerializeField] private float hungerDecreasePerSecond = 0.3f;
        [SerializeField] private float hungryThreshold = 0.4f;
        [SerializeField] private float starvingThreshold = 0.8f;

        public float Hunger => hunger;
        public bool IsHungry => hunger >= hungryThreshold;
        public bool IsStarving => hunger >= starvingThreshold;

        private void Update()
        {
            // hunger goes up by default
            hunger += hungerIncreasePerSecond * Time.deltaTime;
            hunger = Mathf.Clamp01(hunger);
        }

        /// <summary>
        /// Called while eating; amount is 0..1 fraction of "fullness", we convert to hunger reduction.
        /// </summary>
        public void ApplyNutrition(float deltaTime)
        {
            hunger -= hungerDecreasePerSecond * deltaTime;
            hunger = Mathf.Clamp01(hunger);
        }

        /// <summary>
        /// For debug / testing: instantly reset hunger.
        /// </summary>
        public void SetHunger(float value)
        {
            hunger = Mathf.Clamp01(value);
        }
    }
}
