import re
from enum import Enum

import cv2
import numpy as np
import pytesseract


class PSM(Enum):
    """Page segmentation mode"""

    BLOCK_OF_TEXT = "--psm 6"
    SINGLE_LINE = "--psm 7"
    SINGLE_WORD = "--psm 8"
    NUMBER = "--psm 7 -c tessedit_char_whitelist=0123456789"

    @classmethod
    def from_string(cls, type: str) -> "PSM":
        if type in PSM._member_names_:
            return PSM[type]
        raise ValueError(f"Unknown type {type}")


class OCR_SPEC:
    """
    OCR specification for image processing and text extraction.

    Args:
        - type (PSM): The page segmentation mode to be used for text extraction.
        - lowerBound (list): The lower bound of the content color in BGR format.
        - upperBound (list): The upper bound of the content color in BGR format.
    """

    def __init__(self, type: PSM, lowerBound: list, upperBound: list) -> None:
        assert isinstance(type, PSM)
        assert isinstance(lowerBound, list) and len(lowerBound) == 3
        assert isinstance(upperBound, list) and len(upperBound) == 3

        self.type: PSM = type
        self.lowerBound = lowerBound
        self.upperBound = upperBound

    def from_dict(d: dict) -> "OCR_SPEC":
        assert isinstance(d, dict)
        assert sorted(["psm", "lowerBound", "upperBound"]) == sorted(list(d.keys()))
        return OCR_SPEC(PSM.from_string(d["psm"]), d["lowerBound"], d["upperBound"])


class OCR:
    def extract_text(
        self,
        img: np.ndarray,
        spec: OCR_SPEC,
        preview: bool = False,
        prepare_image: callable = None,
    ) -> str:
        assert (
            isinstance(img, np.ndarray)
            and isinstance(spec, OCR_SPEC)
            and isinstance(preview, bool)
            and (callable(prepare_image) or prepare_image is None)
        )
        assert img.ndim == 3, "Image must be BGR"

        # Use custom image processing function if specified
        if prepare_image:
            img = prepare_image(img)
        else:
            img = self.__convert_to_bw(img, spec)
            img = self.__improve_resolution(img)
            img = self.__enhance(img)

        txt = pytesseract.image_to_string(img, config=f"-l eng {spec.type.value}")
        txt = self.__format(txt)

        if preview:
            self.__show_image(img)
            print(f"OCR result is {txt}")

        return txt

    def __convert_to_bw(self, img: np.ndarray, spec: OCR_SPEC) -> np.ndarray:
        assert isinstance(img, np.ndarray) and isinstance(spec, OCR_SPEC)
        assert img.ndim == 3, "Image must be BGR"

        # Create background mask
        lowerColor = np.array(spec.lowerBound, dtype=np.uint8)
        upperColor = np.array(spec.upperBound, dtype=np.uint8)
        bgMask = cv2.inRange(img, lowerColor, upperColor) == 0

        # Convert to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img[bgMask] = 255
        img[~bgMask] = 0

        return img

    def __improve_resolution(self, img: np.ndarray) -> np.ndarray:
        assert isinstance(img, np.ndarray)
        assert img.ndim == 2, "Image must be grayscale"

        # Remove empty rows and columns from background (white pixels)
        empty_rows = np.where(np.all(img == 255, axis=1) == False)[0]
        empty_cols = np.where(np.all(img == 255, axis=0) == False)[0]
        if empty_rows.size:
            img = img[empty_rows[0] : empty_rows[-1] + 1, :]
        if empty_cols.size:
            img = img[:, empty_cols[0] : empty_cols[-1] + 1]

        # Pad and resize image
        padding = 15
        img = np.pad(img, padding, mode="constant", constant_values=255)
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LINEAR)

        return img

    def __enhance(self, img: np.ndarray) -> np.ndarray:
        assert isinstance(img, np.ndarray)

        img = cv2.erode(img, np.ones((3, 3), np.uint8), iterations=1)
        img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=1)
        img = cv2.GaussianBlur(img, (3, 3), 0)

        return img

    def __format(self, text: str) -> str:
        text = re.sub(r"\t+", " ", text)
        return text.strip()

    def __show_image(self, img: np.ndarray):
        assert isinstance(img, np.ndarray)
        cv2.imshow("img", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
