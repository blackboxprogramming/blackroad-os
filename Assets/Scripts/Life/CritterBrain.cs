using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// High-level decision-maker for a critter:
    /// - If not hungry: let CritterAgent handle wandering/idle/sleep.
    /// - If hungry: look for nearby FoodSource and move toward it to eat.
    /// </summary>
    [RequireComponent(typeof(CritterAgent))]
    [RequireComponent(typeof(CritterNeeds))]
    public class CritterBrain : MonoBehaviour
    {
        [Header("Sensing")]
        [SerializeField] private float senseRadius = 20f;
        [SerializeField] private LayerMask foodMask = ~0;

        [Header("Eating")]
        [SerializeField] private float eatDistance = 1.5f;
        [SerializeField] private float checkFoodInterval = 2f;

        private CritterAgent _agent;
        private CritterNeeds _needs;
        private Coroutine _brainRoutine;
        private FoodSource _currentTarget;

        private void Awake()
        {
            _agent = GetComponent<CritterAgent>();
            _needs = GetComponent<CritterNeeds>();
        }

        private void OnEnable()
        {
            _brainRoutine = StartCoroutine(BrainLoop());
        }

        private void OnDisable()
        {
            if (_brainRoutine != null)
            {
                StopCoroutine(_brainRoutine);
            }
        }

        private IEnumerator BrainLoop()
        {
            while (true)
            {
                if (_needs.IsHungry && !IsSleeping())
                {
                    yield return HungryRoutine();
                }
                else
                {
                    // Let CritterAgent's own state machine do its thing.
                    yield return null;
                }

                yield return null;
            }
        }

        private bool IsSleeping()
        {
            return _agent.State == CritterAgent.CritterState.Sleeping;
        }

        private IEnumerator HungryRoutine()
        {
            float timeSinceCheck = 0f;

            while (_needs.IsHungry && !IsSleeping())
            {
                timeSinceCheck += Time.deltaTime;

                if (timeSinceCheck >= checkFoodInterval || _currentTarget == null)
                {
                    timeSinceCheck = 0f;
                    _currentTarget = FindNearestFood();
                }

                if (_currentTarget == null)
                {
                    // No food nearby, just let normal wandering continue
                    yield return null;
                }
                else
                {
                    yield return MoveTowardsAndEat(_currentTarget);
                }
            }
        }

        private FoodSource FindNearestFood()
        {
            Collider[] hits = Physics.OverlapSphere(transform.position, senseRadius, foodMask);
            FoodSource nearest = null;
            float bestSqr = float.MaxValue;

            foreach (var hit in hits)
            {
                if (hit == null) continue;

                var food = hit.GetComponent<FoodSource>();
                if (food == null || food.Quantity <= 0f) continue;

                float sqr = (food.transform.position - transform.position).sqrMagnitude;
                if (sqr < bestSqr)
                {
                    bestSqr = sqr;
                    nearest = food;
                }
            }

            return nearest;
        }

        private IEnumerator MoveTowardsAndEat(FoodSource food)
        {
            if (food == null) yield break;

            Transform t = transform;
            var controller = GetComponent<CharacterController>();

            while (food != null && food.Quantity > 0f && _needs.IsHungry && !IsSleeping())
            {
                Vector3 toFood = food.transform.position - t.position;
                float dist = toFood.magnitude;

                if (dist > eatDistance)
                {
                    // Approach food manually: simple steering toward it
                    Vector3 dir = toFood.normalized;
                    dir.y = 0f;
                    if (dir.sqrMagnitude > 0.0001f)
                    {
                        Quaternion targetRot = Quaternion.LookRotation(dir, Vector3.up);
                        t.rotation = Quaternion.Slerp(
                            t.rotation,
                            targetRot,
                            5f * Time.deltaTime
                        );
                    }

                    Vector3 move = dir * 1.5f; // approach speed
                    Vector3 velocity = move;
                    velocity.y = controller.isGrounded ? -1f : velocity.y - 9.81f * Time.deltaTime;
                    controller.Move(velocity * Time.deltaTime);
                }
                else
                {
                    // Eat
                    float nutrition = food.Consume(Time.deltaTime);
                    if (nutrition > 0f)
                    {
                        _needs.ApplyNutrition(Time.deltaTime);
                    }
                }

                yield return null;
            }
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 0.8f, 0.2f, 0.3f);
            Gizmos.DrawWireSphere(transform.position, senseRadius);
        }
    }
}
