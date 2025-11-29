using System.Collections;
using UnityEngine;
using BlackRoad.Worldbuilder.Environment; // for DayNightCycle
using UnityEngine;

namespace BlackRoad.Worldbuilder.Life
{
    /// <summary>
    /// Simple wandering creature that walks around a home area,
    /// occasionally idles, and goes to sleep during night hours
    /// according to the DayNightCycle.
    /// Simple movement agent for critters. Handles forward walking and
    /// blends in optional steering from a HerdMember component when present.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class CritterAgent : MonoBehaviour
    {
        public enum CritterState
        {
            Sleeping,
            Idle,
            Walking
        }

        [Header("Movement")]
        [SerializeField] private float walkSpeed = 2f;
        [SerializeField] private float turnSpeed = 5f;
        [SerializeField] private float gravity = 9.81f;

        [Header("Home Range")]
        [SerializeField] private float homeRadius = 25f;
        [SerializeField] private float minWanderDistance = 5f;
        [SerializeField] private float maxWanderDistance = 20f;

        [Header("Idle Behaviour")]
        [SerializeField] private Vector2 idleTimeRange = new Vector2(1.5f, 4f);

        [Header("Sleep Schedule")]
        [Tooltip("Normalized time-of-day range where the critter sleeps (0–1).")]
        [SerializeField] private float sleepStart = 0.80f; // 19:12
        [SerializeField] private float sleepEnd = 0.20f;   // 04:48

        [Header("Environment")]
        [SerializeField] private DayNightCycle dayNight;
        [SerializeField] private LayerMask groundMask = ~0;

        public CritterState State { get; private set; }

        private CharacterController _controller;
        private Vector3 _homePos;
        private Vector3 _targetPos;
        private Vector3 _velocity;

        private Coroutine _stateRoutine;
        [Header("Movement")]
        [SerializeField] private float walkSpeed = 2f;
        [SerializeField] private float turnSpeed = 120f;

        private Vector3 _velocity;
        private CharacterController _controller;
        private HerdMember _herdMember;

        public Vector3 Velocity => _velocity;

        private void Awake()
        {
            _controller = GetComponent<CharacterController>();
            _homePos = transform.position;
        }

        private void Start()
        {
            if (dayNight == null)
                dayNight = FindObjectOfType<DayNightCycle>();

            // Start behaviour loop
            _stateRoutine = StartCoroutine(StateLoop());
        }

        private IEnumerator StateLoop()
        {
            while (true)
            {
                if (IsSleepTime())
                {
                    State = CritterState.Sleeping;
                    yield return SleepRoutine();
                }
                else
                {
                    // pick either walk or idle randomly
                    if (Random.value < 0.5f)
                    {
                        State = CritterState.Idle;
                        yield return IdleRoutine();
                    }
                    else
                    {
                        State = CritterState.Walking;
                        yield return WalkRoutine();
                    }
                }

                yield return null;
            }
        }

        private bool IsSleepTime()
        {
            if (dayNight == null) return false;

            float t = dayNight.timeOfDay;

            // sleep window may wrap around 0
            if (sleepStart < sleepEnd)
                return t >= sleepStart && t <= sleepEnd;

            return t >= sleepStart || t <= sleepEnd;
        }

        private IEnumerator SleepRoutine()
        {
            // stand mostly still; tiny sway so they don't look frozen
            float timer = 0f;
            while (IsSleepTime())
            {
                timer += Time.deltaTime;
                float bob = Mathf.Sin(timer * 0.5f) * 0.01f;
                var p = transform.position;
                p.y += bob;
                transform.position = p;

                // zero velocity / gravity handled in Update
                _velocity = Vector3.zero;

                yield return null;
            }
        }

        private IEnumerator IdleRoutine()
        {
            float idleDuration = Random.Range(idleTimeRange.x, idleTimeRange.y);
            float timer = 0f;

            while (timer < idleDuration && !IsSleepTime())
            {
                timer += Time.deltaTime;
                _velocity = new Vector3(0f, _velocity.y, 0f); // keep gravity only
                yield return null;
            }
        }

        private IEnumerator WalkRoutine()
        {
            if (!TryGetWanderTarget(out _targetPos))
            {
                // If we fail to find a target, just idle instead.
                yield break;
            }

            while (!IsSleepTime())
            {
                // Flatten movement on XZ, we'll handle vertical via gravity
                Vector3 flatPos = new Vector3(transform.position.x, 0f, transform.position.z);
                Vector3 flatTarget = new Vector3(_targetPos.x, 0f, _targetPos.z);
                Vector3 toTarget = flatTarget - flatPos;
                float dist = toTarget.magnitude;

                if (dist < 0.5f)
                    yield break; // reached target

                Vector3 dir = toTarget.normalized;

                // Rotate toward target
                if (dir.sqrMagnitude > 0.0001f)
                {
                    Quaternion targetRot = Quaternion.LookRotation(dir, Vector3.up);
                    transform.rotation = Quaternion.Slerp(
                        transform.rotation,
                        targetRot,
                        turnSpeed * Time.deltaTime
                    );
                }

                // Move forward
                Vector3 move = transform.forward * walkSpeed;
                _velocity.x = move.x;
                _velocity.z = move.z;

                yield return null;
            }
        }

        private bool TryGetWanderTarget(out Vector3 result)
        {
            // Pick a random direction + distance around home
            for (int i = 0; i < 10; i++)
            {
                float angle = Random.Range(0f, Mathf.PI * 2f);
                float dist = Random.Range(minWanderDistance, maxWanderDistance);
                Vector3 offset = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * dist;

                Vector3 candidate = _homePos + offset;

                // Sample ground height via raycast
                if (Physics.Raycast(
                        candidate + Vector3.up * 50f,
                        Vector3.down,
                        out RaycastHit hit,
                        100f,
                        groundMask))
                {
                    candidate = hit.point;
                    result = candidate;
                    return true;
                }
            }

            result = Vector3.zero;
            return false;
        }

        private void Update()
        {
            // Apply gravity (except very lightly while sleeping)
            if (State == CritterState.Sleeping)
            {
                _velocity.y = Mathf.MoveTowards(_velocity.y, 0f, gravity * Time.deltaTime);
            }
            else
            {
                if (_controller.isGrounded)
                    _velocity.y = -1f;
                else
                    _velocity.y -= gravity * Time.deltaTime;
            }

            _controller.Move(_velocity * Time.deltaTime);
            _herdMember = GetComponent<HerdMember>();
        }

        private void Update()
        {
            WalkRoutine();
        }

        /// <summary>
        /// Sets the heading the critter should look toward.
        /// </summary>
        /// <param name="direction">Desired facing direction.</param>
        public void SetHeading(Vector3 direction)
        {
            if (direction.sqrMagnitude < 0.0001f) return;

            direction.y = 0f;
            Quaternion target = Quaternion.LookRotation(direction.normalized, Vector3.up);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, target, turnSpeed * Time.deltaTime);
        }

        /// <summary>
        /// Walk forward while optionally blending in herd steering.
        /// </summary>
        private void WalkRoutine()
        {
            Vector3 moveDir = transform.forward;

            // Optional herd steering
            if (_herdMember != null && _herdMember.SteerOffset.sqrMagnitude > 0.0001f)
            {
                // Blend forward direction with herd steering
                moveDir = (moveDir + _herdMember.SteerOffset).normalized;
            }

            // Apply move
            Vector3 move = moveDir * walkSpeed;
            _velocity.x = move.x;
            _velocity.z = move.z;

            if (_controller != null)
            {
                _controller.SimpleMove(_velocity);
            }
            else
            {
                transform.position += _velocity * Time.deltaTime;
            }
        }
    }
}
