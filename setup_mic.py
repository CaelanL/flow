import sounddevice as sd
import os


def list_input_devices():
    devices = sd.query_devices()
    input_devices = []
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            input_devices.append((i, d["name"]))
    return input_devices


def pick_device():
    devices = list_input_devices()
    if not devices:
        print("No input devices found!")
        return None

    print("\nAvailable microphones:")
    print("-" * 40)
    for idx, (device_id, name) in enumerate(devices):
        print(f"  [{device_id}] {name}")
    print()

    while True:
        choice = input("Enter device number: ").strip()
        try:
            choice = int(choice)
            if any(d[0] == choice for d in devices):
                return choice
            print("Invalid device number, try again.")
        except ValueError:
            print("Enter a number.")


def save_device_to_env(device_index):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("MIC_DEVICE_INDEX="):
                    lines.append(f"MIC_DEVICE_INDEX={device_index}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"MIC_DEVICE_INDEX={device_index}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    device = pick_device()
    if device is not None:
        save_device_to_env(device)
        print(f"\nSaved MIC_DEVICE_INDEX={device} to .env")
