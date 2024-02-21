import numpy as np

from .display import Display
from .geometry import Frame, Offset, Point, RelativeFrame
from .ocr import OCR, OCR_SPEC, PSM
from .screen import Click, Screen


class XControl:
    __instances = {}
    uniqueDisplay = False

    def __init__(self, displayId: str, width: int, height: int) -> None:
        self.display: Display = Display(displayId, width, height)
        self.screen: Screen = Screen(self.display)
        self.ocr: OCR = OCR()

    @classmethod
    def config(cls, uniqueDisplay: bool = False):
        assert isinstance(uniqueDisplay, bool)

        if uniqueDisplay:
            assert (
                len(cls.__instances) <= 1
            ), "There are already multiple displays created."

        cls.uniqueDisplay = uniqueDisplay

    @classmethod
    def get_instance(
        cls, displayId: str = None, width: int = None, height: int = None
    ) -> "XControl":
        """
        Returns the instance of the XControl class for the specified display ID if it exists, otherwise creates a new instance.

        Args:
            - displayId (str): The display ID of the nested X server.
            - width (int): The width of the screen.
            - height (int): The height of the screen.

        Returns:
            - XControl: The instance of the XControl class.

        Note:
            - If the instance already exists, the width and height arguments are ignored.
        """
        if displayId is None:
            assert (
                cls.uniqueDisplay and len(cls.__instances) == 1
            ), "Display ID is required when multiple displays are allowed."
            return list(cls.__instances.values())[0]

        if displayId not in cls.__instances:
            assert (
                len(cls.__instances) == 0 or not cls.uniqueDisplay
            ), "There is already a display created."
            cls.__instances[displayId] = XControl(displayId, width, height)

        return cls.__instances[displayId]

    def launch(self, startCmd: str, env: dict = None, waitFor: bool = False) -> None:
        """
        Launches the specified application in the nested X server.

        Args:
            - startCmd (str): The command to start the application.
            - env (dict, optional): Environment variables to be set for the application.
            - waitFor (bool, optional): Whether to wait for the application to start before returning.
                                      This is useful for commands that act as a launcher for the actual application.
        """
        self.display.launch(startCmd, env, waitFor)

    def close(self) -> None:
        """
        Closes the nested X server and terminates the nested application.
        """
        self.display.close()

    def get_mouse_position(self) -> Point:
        """
        Returns the current position of the mouse pointer on the screen.

        Note:
            - Point(0, 0) represent the top-left corner of the screen.
        """
        return self.screen.get_mouse_position()

    def mouse_move(self, point: Point, click: Click = None) -> None:
        """
        Moves the mouse pointer to the specified point on the screen and performs a click action if specified.
        It waits for the mouse to reach the destination before returning.

        Args:
            - point (Point): A Point object representing the coordinates (x, y).
            - click (Click, optional): Specifies whether to perform a click action after.

        Raises:
            - TimeoutError: If the mouse pointer does not reach the destination within 1 second.

        Note:
            - Point(0, 0) represent the top-left corner of the screen.
        """
        self.screen.mouse_move(point, click)

    def mouse_drag(self, start: Point, end: Point, click: Click = Click.LEFT) -> None:
        """
        Drags the mouse pointer from the start point to the end point on the screen and performs a click action if specified.
        It waits for the mouse to reach the destination before returning.

        Args:
            - start (Point): A Point object representing the start coordinates (x, y).
            - end (Point): A Point object representing the end coordinates (x, y).
            - click (Click, optional): Specifies which mouse button to use for the drag action.

        Raises:
            - TimeoutError: If the mouse pointer does not reach either the start or end point within 1 second.

        Note:
            - Point(0, 0) represent the top-left corner of the screen.
        """
        self.screen.mouse_drag(start, end, click)

    def key(self, key: str) -> None:
        """
        Sends a single key press to the nested application.

        Args:
            - key (str): The key to be pressed.
        """
        self.screen.key(key)

    def type(self, text: str, clear: bool = False):
        """
        Inputs the specified text into the nested application.

        Args:
            - text (str): The text to be input.
            - clear (bool, optional): Whether to clear the current input field before typing the text.
        """
        self.screen.type(text, clear)

    def screenshot(self, frame: Frame = None, path: str = None) -> np.ndarray:
        """
        Captures a screenshot of the specified frame on the screen.

        Args:
            - frame (Frame, optional): The frame to be captured. If not specified, the entire screen is captured.
            - path (str, optional): The path to save the screenshot to.

        Returns:
            - np.ndarray: The screenshot as a NumPy array.

        Note:
            - The returned image is in BGR (Blue, Green, Red) format.
        """
        return self.display.screenshot(frame, path)

    def wait_for_image(
        self,
        imagePath: str,
        frame: Frame = None,
        confidence: float = 0.7,
        timeout: float = 1,
    ) -> Point:
        """
        Waits for the specified image to appear on the screen within the specified frame.

        Args:
            - imagePath (str): The path to the image to be found.
            - frame (Frame, optional): The frame to search for the image. If not specified, the entire screen is searched.
            - confidence (float, optional): The minimum confidence level required for the image to be found.
            - timeout (float, optional): The maximum time to wait for the image to appear.

        Returns:
            - Point: The coordinates of the top-left corner of the found image.

        Raises:
            - TimeoutError: If the image does not appear within the specified timeout.

        Note:
            - The confidence level must be between 0 and 1.
        """
        return self.screen.wait_for_image(imagePath, frame, confidence, timeout)

    def wait_for_image_to_disappear(
        self,
        imagePath: str,
        frame: Frame = None,
        confidence: float = 0.7,
        timeout: float = 1,
    ) -> None:
        """
        Waits for the specified image to disappear from the screen within the specified frame.

        Args:
            - imagePath (str): The path to the image to be found.
            - frame (Frame, optional): The frame to search for the image. If not specified, the entire screen is searched.
            - confidence (float, optional): The minimum confidence level required for the image to be found.
            - timeout (float, optional): The maximum time to wait for the image to disappear.

        Raises:
            - TimeoutError: If the image does not disappear within the specified timeout.

        Note:
            - The confidence level must be between 0 and 1.
        """
        self.screen.wait_for_image_to_disappear(imagePath, frame, confidence, timeout)

    def extract_text(
        self,
        frame: Frame,
        spec: OCR_SPEC,
        preview: bool = False,
        prepare_image: callable = None,
    ) -> str:
        """
        Extracts text from the specified frame using a given OCR specification.

        Args:
            - frame (Frame): The frame to extract text from.
            - spec (OCR_SPEC): The OCR specification to be used for text extraction.
            - preview (bool, optional): Whether to preview the processed image before text extraction.
            - prepare_image (callable, optional): A custom image processing function to be used before text extraction.
                This function should accept a single argument, which is the input image as a NumPy array, and return a
                black and white image. If no custom function is provided, the default image processing function will be used.

        Returns:
            - str: The extracted text.
        """
        img = self.screenshot(frame)
        return self.ocr.extract_text(img, spec, preview, prepare_image)

    def extract_text_from_image(
        self,
        img: np.ndarray,
        spec: OCR_SPEC,
        preview: bool = False,
        prepare_image: callable = None,
    ) -> str:
        """
        Extracts text from the specified frame using a given OCR specification.
        Same as `extract_text()` but takes an image as input instead of a frame.

        Args:
            - frame (Frame): The frame to extract text from.
            - spec (OCR_SPEC): The OCR specification to be used for text extraction.
            - preview (bool, optional): Whether to preview the processed image before text extraction.
            - prepare_image (callable, optional): A custom image processing function to be used before text extraction.
                This function should accept a single argument, which is the input image as a NumPy array, and return a
                black and white image. If no custom function is provided, the default image processing function will be used.

        Returns:
            - str: The extracted text.
        """
        return self.ocr.extract_text(img, spec, preview, prepare_image)

    def run_command(self, cmd: str, waitFor: bool = False) -> str:
        """
        Runs the specified command in the nested application.

        Args:
            - cmd (str): The command to be run.
            - waitFor (bool, optional): Whether to wait for the command to complete before returning.

        Returns:
            - str: The output of the command.
        """
        self.display.run_command(cmd, waitFor)
