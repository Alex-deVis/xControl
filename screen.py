from enum import Enum
from logging import getLogger

import cv2

from .display import Display
from .geometry import Frame, Point
from .utils import wait_for, wait_to_be_set

log = getLogger()


class Click(Enum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class Screen:
    def __init__(self, display: Display) -> None:
        self.display = display
        assert isinstance(self.display, Display)

    def get_mouse_position(self) -> Point:
        cmd = "xdotool getmouselocation"
        out = self.display.run_command(cmd, waitFor=True)
        x = int(out.split(" ")[0].split(":")[1])
        y = int(out.split(" ")[1].split(":")[1])
        return Point(x, y)

    def mouse_move(self, point: Point, click: Click = None):
        assert isinstance(point, Point)

        cmd = f"xdotool mousemove {point.X} {point.Y} "
        if click:
            assert isinstance(click, Click)
            cmd += f"click --delay 50 {click.value} "

        self.display.activate_window()
        self.display.run_command(cmd, waitFor=True)

        if not wait_for(lambda: self.get_mouse_position() == point, 1):
            raise TimeoutError(f"Mouse did not move to {point} in 1 second")

    def mouse_drag(self, start: Point, end: Point, click: Click):
        assert isinstance(start, Point) and isinstance(end, Point)

        cmd = f"xdotool mousedown {start.X} {start.Y} {click.value} "
        self.display.activate_window()
        self.display.run_command(cmd, waitFor=True)
        if not wait_for(lambda: self.get_mouse_position() == start, 1):
            raise TimeoutError(f"Mouse did not move to {start} in 1 second")

        cmd = f"xdotool mouseup {end.X} {end.Y} {click.value} "
        self.display.activate_window()
        self.display.run_command(cmd, waitFor=True)
        if not wait_for(lambda: self.get_mouse_position() == end, 1):
            raise TimeoutError(f"Mouse did not move to {end} in 1 second")

    def key(self, key: str):
        self.display.activate_window()
        self.display.run_command(f"xdotool key --delay 50 {key}", waitFor=True)

    def type(self, text: str, clear: bool):
        assert isinstance(text, str) and isinstance(clear, bool)

        if clear:
            self.__clear()

        cmd = f'xdotool type --delay 50 --clearmodifiers "{text}"'
        self.display.activate_window()
        self.display.run_command(cmd, waitFor=True)

    def wait_for_image(
        self, imagePath: str, frame: Frame, confidence: float, timeout: float
    ) -> Point:
        point = wait_to_be_set(
            lambda: self.__locate_on_screen(imagePath, frame, confidence), 1
        )
        if point:
            return point
        raise TimeoutError(f"Image {imagePath} not found in {timeout} seconds")

    def wait_for_image_to_disappear(
        self, imagePath: str, frame: Frame, confidence: float, timeout: float
    ) -> None:
        if not wait_for(
            lambda: not self.__locate_on_screen(imagePath, frame, confidence), 1
        ):
            raise TimeoutError(
                f"Image {imagePath} did not disappear in {timeout} seconds"
            )

    def __locate_on_screen(
        self, imagePath: str, frame: Frame, confidence: float
    ) -> Point:
        assert isinstance(imagePath, str)
        assert isinstance(frame, Frame) or frame is None
        assert isinstance(confidence, float) and 0 <= confidence <= 1

        screenshot = self.display.screenshot(frame)
        template = cv2.imread(imagePath)
        if template is None:
            raise FileNotFoundError(imagePath)

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > confidence:
            h, w = template.shape[:-1]
            return Point(max_loc[0] + w // 2, max_loc[1] + h // 2)

        return None

    def __clear(self) -> None:
        cmd = "xdotool key Home keydown Shift key End key Delete keyup Shift "
        self.display.activate_window()
        self.display.run_command(cmd, waitFor=True)
