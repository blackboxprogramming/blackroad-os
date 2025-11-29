using UnityEngine;

namespace BlackRoad.Worldbuilder.Input
{
    [RequireComponent(typeof(Camera))]
    public class FlyCameraController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 10f;
        public float fastMultiplier = 2f;
        public float slowMultiplier = 0.5f;

        [Header("Look")]
        public float lookSensitivity = 3f;
        public float minPitch = -80f;
        public float maxPitch = 80f;

        private float _yaw;
        private float _pitch;

        private void Start()
        {
            var euler = transform.eulerAngles;
            _yaw = euler.y;
            _pitch = euler.x;

            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        private void Update()
        {
            HandleLook();
            HandleMove();

            // Toggle cursor lock for debugging
            if (UnityEngine.Input.GetKeyDown(KeyCode.Tab))
            {
                if (Cursor.lockState == CursorLockMode.Locked)
                {
                    Cursor.lockState = CursorLockMode.None;
                    Cursor.visible = true;
                }
                else
                {
                    Cursor.lockState = CursorLockMode.Locked;
                    Cursor.visible = false;
                }
            }
        }

        private void HandleLook()
        {
            if (Cursor.lockState != CursorLockMode.Locked) return;

            float mouseX = UnityEngine.Input.GetAxis("Mouse X") * lookSensitivity;
            float mouseY = UnityEngine.Input.GetAxis("Mouse Y") * lookSensitivity;

            _yaw += mouseX;
            _pitch -= mouseY;
            _pitch = Mathf.Clamp(_pitch, minPitch, maxPitch);

            transform.rotation = Quaternion.Euler(_pitch, _yaw, 0f);
        }

        private void HandleMove()
        {
            float speed = moveSpeed;

            if (UnityEngine.Input.GetKey(KeyCode.LeftShift))
                speed *= fastMultiplier;
            else if (UnityEngine.Input.GetKey(KeyCode.LeftControl))
                speed *= slowMultiplier;

            Vector3 input =
                new Vector3(
                    UnityEngine.Input.GetAxisRaw("Horizontal"),
                    0f,
                    UnityEngine.Input.GetAxisRaw("Vertical")
                );

            // Vertical up/down
            if (UnityEngine.Input.GetKey(KeyCode.E))
                input.y += 1f;
            if (UnityEngine.Input.GetKey(KeyCode.Q))
                input.y -= 1f;

            Vector3 worldMove =
                transform.TransformDirection(input.normalized) * (speed * Time.deltaTime);

            transform.position += worldMove;
        }
    }
}
