"""Compare a chrome element against a stored reference image.

The reference ("baseline") is a PNG committed under
``data/visual_baselines/<platform>/``. A test captures the same element and
asserts the two match within a tolerance.

Tolerance borrows reftest's vocabulary (``layout/tools/reftest``): a comparison
passes when no pixel differs by more than ``max_delta`` on any channel, and at
most ``max_pixels_over`` pixels exceed it. Measured on macOS across three
Firefox launches, cropped chrome elements differ by **0-1** per channel, while
a real state change (opening the window switcher) differs by **25** -- so the
default of 8 sits well clear of the noise and well under the signal.

Capture crops to one element rather than the whole window on purpose. Firefox's
own mozscreenshots has to re-enable font antialiasing in CI because full-window
text is the main source of false positives; a small chrome element avoids that
entirely. Note that very large elements cannot be captured at all -- Marionette
raises ScreenshotException -- so keep targets modest.

Refresh baselines with ``--update-visual-baselines``, which writes whatever is
on screen and skips the assertion. Review the image diff before committing it,
the same way a mock-server recording is reviewed after ``--mock-mode=record``.
"""

import io
import logging
import pathlib

import numpy as np
from PIL import Image
from selenium.webdriver.remote.webelement import WebElement

BASELINE_ROOT = pathlib.Path("data", "visual_baselines")

# Platform folder names, matching the manifest's win/mac/linux vocabulary.
PLATFORMS = {"Darwin": "mac", "Windows": "win", "Linux": "linux"}


class VisualBaseline:
    """Capture chrome elements and compare them against committed references."""

    def __init__(self, driver, sys_platform: str, update: bool = False):
        self.driver = driver
        self.platform = PLATFORMS.get(sys_platform, sys_platform.lower())
        self.update = update

    def path_for(self, name: str) -> pathlib.Path:
        return BASELINE_ROOT / self.platform / f"{name}.png"

    @staticmethod
    def _as_array(png: bytes) -> np.ndarray:
        """Decode a PNG to an HxWx3 array, dropping alpha so the compare is RGB."""
        return np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.int16)

    def capture(self, element: WebElement) -> np.ndarray:
        return self._as_array(element.screenshot_as_png)

    def difference(self, before: np.ndarray, after: np.ndarray) -> dict:
        """
        Summarise how two captures differ.

        Returns the largest per-channel delta and how many pixels exceed a few
        thresholds, so a failure message can say how far off it was.
        """
        per_pixel = np.abs(before - after).max(axis=2)
        return {
            "max_delta": int(per_pixel.max()),
            "pixels": int(per_pixel.size),
            "differing": int((per_pixel > 0).sum()),
            "over_8": int((per_pixel > 8).sum()),
            "over_16": int((per_pixel > 16).sum()),
        }

    def expect_matches(
        self,
        element: WebElement,
        name: str,
        max_delta: int = 8,
        max_pixels_over: int = 0,
    ):
        """
        Assert `element` still looks like its stored baseline.

        Arguments:
            element: the chrome element to capture.
            name: baseline file name, without extension.
            max_delta: the largest per-channel difference any pixel may have.
            max_pixels_over: how many pixels may exceed max_delta.
        """
        current = self.capture(element)
        path = self.path_for(name)

        if self.update or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(current.astype(np.uint8)).save(path)
            action = "Updated" if self.update else "Created"
            logging.info(f"{action} visual baseline {path}")
            if not self.update:
                raise AssertionError(
                    f"No baseline existed at {path}, so one was written from this "
                    "run. Review it, commit it, and re-run to assert against it."
                )
            return self

        baseline = self._as_array(path.read_bytes())
        if baseline.shape != current.shape:
            raise AssertionError(
                f"{name}: size changed, baseline is "
                f"{baseline.shape[1]}x{baseline.shape[0]} but the element is "
                f"{current.shape[1]}x{current.shape[0]}. If the change is "
                "intended, refresh with --update-visual-baselines."
            )

        # Count against max_delta itself, not a fixed threshold: a caller
        # passing max_delta=4 must not have pixels at 5-8 quietly forgiven.
        per_pixel = np.abs(baseline - current).max(axis=2)
        over = int((per_pixel > max_delta).sum())
        if over > max_pixels_over:
            failed = self.path_for(f"{name}.failed")
            Image.fromarray(current.astype(np.uint8)).save(failed)
            raise AssertionError(
                f"{name} no longer matches its baseline: {over} pixel(s) of "
                f"{per_pixel.size} differ by more than {max_delta} "
                f"(allowed {max_pixels_over}); largest difference "
                f"{int(per_pixel.max())}. What was captured is at {failed}; if "
                "the change is intended, refresh with --update-visual-baselines."
            )
        logging.info(f"{name} matches baseline (max delta {int(per_pixel.max())})")
        return self

    def expect_differs(
        self, element: WebElement, baseline_name: str, min_delta: int = 8
    ):
        """
        Assert `element` does NOT look like a stored baseline.

        The counterpart to expect_matches: used where a case is about a state
        *changing* -- a hovered button, an active tab -- so that a test cannot
        pass by comparing a state against itself.
        """
        path = self.path_for(baseline_name)
        if not path.exists():
            raise AssertionError(
                f"No baseline at {path} to differ from; capture it first with "
                "--update-visual-baselines."
            )
        diff = self.difference(self._as_array(path.read_bytes()), self.capture(element))
        if diff["max_delta"] < min_delta:
            raise AssertionError(
                f"{baseline_name}: expected a visible difference but the largest "
                f"per-channel delta was only {diff['max_delta']} (wanted at least "
                f"{min_delta}), so the state does not appear to have changed."
            )
        logging.info(
            f"{baseline_name} differs as expected (max delta {diff['max_delta']})"
        )
        return self
