import os
from PIL import ImageGrab


class Screenshot:
    @staticmethod
    def capture(
        name: str,
        path="~/Desktop/screenshots",
    ):
        screenshot = ImageGrab.grab()
        # Save the screenshot with the timestamp as the filename
        desktop_path = os.path.expanduser(path)
        os.makedirs(desktop_path, exist_ok=True)
        file_path = os.path.join(desktop_path, f"{name}.png")
        screenshot.save(file_path)
        print(f"Screenshot saved as screenshot_{name}.png")
