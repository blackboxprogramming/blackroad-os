using UnityEngine;

namespace BlackRoad.Worldbuilder.Player
{
    /// <summary>
    /// First-person controller with walk/run/jump and a fly-mode toggle.
    /// Attach to a GameObject with CharacterController and a child Camera.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        [Header("View")]
        [SerializeField] private Camera playerCamera;
        [SerializeField] private float mouseSensitivity = 2f;
        [SerializeField] private float minPitch = -80f;
        [SerializeField] private float maxPitch = 80f;

        [Header("Movement")]
        [SerializeField] private float walkSpeed = 5f;
        [SerializeField] private float runMultiplier = 1.8f;
        [SerializeField] private float jumpForce = 5f;
        [SerializeField] private float gravity = 9.81f;

        [Header("Fly Mode")]
        [SerializeField] private bool startInFlyMode = false;
        [SerializeField] private float flySpeedMultiplier = 2f;
        [SerializeField] private KeyCode flyToggleKey = KeyCode.F;

        public bool IsFlying { get; private set; }

        private CharacterController _controller;
        private float _yaw;
        private float _pitch;
        private Vector3 _velocity;

        private void Awake()
        {
            _controller = GetComponent<CharacterController>();
            if (playerCamera == null)
                playerCamera = GetComponentInChildren<Camera>();

            Vector3 euler = transform.localEulerAngles;
            _yaw = euler.y;
            _pitch = euler.x;

            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;

            IsFlying = startInFlyMode;
        }

        private void Update()
        {
            HandleLook();
            HandleModeToggle();
            HandleMove();
        }

        private void HandleLook()
        {
            if (Cursor.lockState != CursorLockMode.Locked || playerCamera == null)
                return;

            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            _yaw += mouseX;
            _pitch -= mouseY;
            _pitch = Mathf.Clamp(_pitch, minPitch, maxPitch);

            transform.rotation = Quaternion.Euler(0f, _yaw, 0f);
            playerCamera.transform.localRotation = Quaternion.Euler(_pitch, 0f, 0f);
        }

        private void HandleModeToggle()
        {
            if (Input.GetKeyDown(flyToggleKey))
            {
                IsFlying = !IsFlying;
                // Reset vertical velocity when switching modes
                _velocity.y = 0f;
            }
        }

        private void HandleMove()
        {
            Vector3 input = new Vector3(
                Input.GetAxisRaw("Horizontal"),
                0f,
                Input.GetAxisRaw("Vertical")
            ).normalized;

            float speed = walkSpeed;
            if (Input.GetKey(KeyCode.LeftShift))
                speed *= runMultiplier;

            if (IsFlying)
                speed *= flySpeedMultiplier;

            Vector3 move = transform.TransformDirection(input) * speed;

            if (IsFlying)
            {
                // Vertical fly
                if (Input.GetKey(KeyCode.Space))
                    move.y += speed;
                if (Input.GetKey(KeyCode.LeftControl))
                    move.y -= speed;

                // No gravity
                _controller.Move(move * Time.deltaTime);
            }
            else
            {
                // Grounded mode with gravity / jump
                if (_controller.isGrounded)
                {
                    _velocity.y = -1f; // small downward force

                    if (Input.GetKeyDown(KeyCode.Space))
                    {
                        _velocity.y = jumpForce;
                    }
                }
                else
                {
                    _velocity.y -= gravity * Time.deltaTime;
                }

                Vector3 finalMove = new Vector3(move.x, _velocity.y, move.z);
                _controller.Move(finalMove * Time.deltaTime);
            }
        }
    }
}
