import logging
import os
import shlex
import time
from datetime import datetime
from subprocess import DEVNULL, PIPE, Popen

import cv2
import numpy as np
import Xlib.display
from PIL import Image

from .geometry import Frame, Point

log = logging.getLogger()


class Display:
    def __init__(self, displayId: str, width: int, height: int) -> None:
        assert isinstance(displayId, str) and displayId.startswith(":")
        assert isinstance(width, int) and width > 0
        assert isinstance(height, int) and height > 0

        self.displayId = displayId
        self.main_display = os.environ.get("DISPLAY", ":0")
        self.width = width
        self.height = height
        self.title = f"Xephyr-Window-{displayId}"

        # Setup environment variables
        self.env = os.environ.copy()
        self.env["DISPLAY"] = self.displayId

    def launch(self, startCmd: str, env: dict = None, waitFor: bool = False):
        assert isinstance(startCmd, str)
        assert isinstance(env, dict) or env is None
        assert isinstance(waitFor, bool)

        self.__close_xephyr()
        self.__start_xephyr()

        # Update environment variables
        if env is not None:
            if "DISPLAY" in env:
                del env["DISPLAY"]
            self.env.update(env)

        proc = Popen(
            shlex.split(f"vglrun +wm -d {self.main_display} {startCmd}"),
            env=self.env,
            stdout=DEVNULL,
            stderr=DEVNULL,
        )

        # This is useful for commands that act as a launcher for the actual application
        if waitFor:
            proc.wait()

    def screenshot(
        self,
        frame: Frame = None,
        path: str = None,
    ) -> np.ndarray:
        assert isinstance(frame, Frame) or frame is None
        assert isinstance(path, str) or path is None

        # Screenshot the entire screen if frame is not specified
        if frame is None:
            frame = Frame(Point(0, 0), self.width, self.height)

        display = Xlib.display.Display(self.displayId).screen()
        root = display.root
        raw = root.get_image(
            frame.get_top_left().X,
            frame.get_top_left().Y,
            frame.width,
            frame.height,
            Xlib.X.ZPixmap,
            0xFFFFFFFF,
        )
        pil_image = Image.frombytes(
            "RGB", (frame.width, frame.height), raw.data, "raw", "BGRX"
        )
        np_image = np.array(pil_image)
        screenshot = np_image[:, :, ::-1]

        # Save the screenshot if path is specified
        if path is not None:
            timestamp = datetime.now().strftime("%H-%M-%S-%f")
            filename = os.path.join(path, f"screenshot_{timestamp}.png")
            log.debug(f"Saving {frame} to {filename}")
            status = cv2.imwrite(filename, screenshot)
            if not status:
                log.error(f"Failed to save {filename}")

        return screenshot

    def activate_window(self):
        self.run_command(
            f"xdotool search --name {self.title} windowactivate", waitFor=True
        )

    def run_command(self, cmd: str, waitFor: bool = False) -> str:
        log.debug(f"Run command: {cmd}")
        proc = Popen(
            shlex.split(cmd),
            env=self.env,
            stdout=PIPE,
            stderr=PIPE,
        )

        if waitFor:
            try:
                rc = proc.wait(timeout=5)
            except:
                log.debug(f"Failed to wait for {cmd}; continuing")
                return ""
            assert proc.stdout is not None, "Failed to get stdout"
            assert proc.stderr is not None, "Failed to get stderr"

            if rc != 0:
                err = proc.stderr.read().decode("utf-8")
                # If there is no stderr, use stdout
                if len(err) == 0:
                    err = proc.stdout.read().decode("utf-8")
                log.debug(f"{cmd} exited with {rc}, err: {err}")

            return proc.stdout.read().decode("utf-8")

        return ""

    def close(self):
        self.__close_xephyr()

    def __start_xephyr(self) -> None:
        Popen(
            shlex.split(
                f"Xephyr -ac -br -noreset -softCursor -zaphod -no-host-grab -title {self.title} -screen {self.width}x{self.height} {self.displayId}"
            ),
            close_fds=True,
        )

        # Wait for Xephyr to start
        time.sleep(1)
        self.run_command("spectrwm")

    def __close_xephyr(self) -> None:
        self.run_command(f"pkill -f ^Xephyr.*{self.displayId}$", waitFor=True)
