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
import time

import numpy as np
from PIL import Image
from selenium.webdriver.remote.webelement import WebElement


def _repo_root() -> pathlib.Path:
    """
    Walk up to the directory holding manifests/key.yaml.

    Baselines must resolve to the same files wherever pytest was started from;
    a relative path would quietly create a second tree and pass against it.
    """
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "manifests" / "key.yaml").exists():
            return parent
    raise RuntimeError("could not locate the repository root from visual_baseline.py")


BASELINE_ROOT = _repo_root() / "data" / "visual_baselines"

# Screenshots come back in device pixels, so a Retina laptop captures a 2x
# image of the element a 1x CI runner captures. Pinning the ratio makes a
# baseline mean the same thing everywhere; every visual test must set it.
PIXEL_RATIO_PREF = ("layout.css.devPixelsPerPx", "1.0")

# Platform folder names, matching the manifest's win/mac/linux vocabulary.
PLATFORMS = {"Darwin": "mac", "Windows": "win", "Linux": "linux"}


class VisualBaseline:
    """Capture chrome elements and compare them against committed references."""

    # Gap between the captures used to decide an element has stopped painting.
    SETTLE_INTERVAL = 0.3

    def __init__(
        self,
        driver,
        sys_platform: str,
        update: bool = False,
        artifacts_dir: str | None = None,
    ):
        self.driver = driver
        self.platform = PLATFORMS.get(sys_platform, sys_platform.lower())
        self.update = update
        # Where CI collects files to upload. Without this the failed capture
        # only ever exists on the runner, so a CI-only mismatch cannot be
        # looked at -- which is how the 2x device-pixel-ratio bug stayed
        # guesswork until the numbers happened to give it away.
        self.artifacts_dir = artifacts_dir

    def path_for(self, name: str) -> pathlib.Path:
        return BASELINE_ROOT / self.platform / f"{name}.png"

    @staticmethod
    def _as_array(png: bytes) -> np.ndarray:
        """Decode a PNG to an HxWx3 array, dropping alpha so the compare is RGB."""
        return np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.int16)

    def capture(self, element: WebElement) -> np.ndarray:
        return self._as_array(element.screenshot_as_png)

    def capture_settled(
        self, element: WebElement, max_delta: int = 8, tries: int = 10
    ) -> np.ndarray:
        """Capture `element` once two consecutive frames agree, since chrome
        keeps painting after it becomes visible."""
        previous = self.capture(element)
        for _ in range(tries - 1):
            time.sleep(self.SETTLE_INTERVAL)
            current = self.capture(element)
            if previous.shape == current.shape:
                if int(np.abs(previous - current).max()) <= max_delta:
                    return current
            previous = current
        raise AssertionError(
            f"element never stopped changing: {tries} captures "
            f"{self.SETTLE_INTERVAL}s apart never produced two frames alike "
            f"within {max_delta}"
        )

    @staticmethod
    def _scale_hint(baseline: np.ndarray, current: np.ndarray) -> str:
        """
        Name the likely cause when the two differ by a whole-number scale: the
        baseline was captured at a different device pixel ratio, which is a
        wrong machine rather than a changed UI.
        """
        h, w = (
            baseline.shape[0] / current.shape[0],
            baseline.shape[1] / current.shape[1],
        )
        if h == w and h != 1 and (h == int(h) or 1 / h == int(1 / h)):
            return (
                f"That is exactly {h:g}x in both axes, so the baseline was "
                f"captured at a different device pixel ratio -- check the test "
                f"sets {PIXEL_RATIO_PREF[0]}. "
            )
        return ""

    def expect_matches(
        self,
        element: WebElement,
        name: str,
        max_delta: int = 8,
        max_pixels_over: int = 0,
    ):
        """Assert `element` matches baseline `name` (no file extension)."""
        current = self.capture_settled(element, max_delta)
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
                f"{current.shape[1]}x{current.shape[0]}. "
                + self._scale_hint(baseline, current)
                + "If the change is intended, refresh with "
                "--update-visual-baselines."
            )

        # Count against max_delta itself, not a fixed threshold: a caller
        # passing max_delta=4 must not have pixels at 5-8 quietly forgiven.
        per_pixel = np.abs(baseline - current).max(axis=2)
        over = int((per_pixel > max_delta).sum())
        if over > max_pixels_over:
            failed = self._save_failed(name, current, baseline)
            raise AssertionError(
                f"{name} no longer matches its baseline: {over} pixel(s) of "
                f"{per_pixel.size} differ by more than {max_delta} "
                f"(allowed {max_pixels_over}); largest difference "
                f"{int(per_pixel.max())}. What was captured is at {failed}; if "
                "the change is intended, refresh with --update-visual-baselines."
            )
        logging.info(f"{name} matches baseline (max delta {int(per_pixel.max())})")
        return self

    def _save_failed(
        self, name: str, current: np.ndarray, baseline: np.ndarray
    ) -> pathlib.Path:
        """
        Write the capture that failed, and copy it plus the baseline into the
        artifacts directory when there is one, so CI uploads both.
        """
        failed = self.path_for(f"{name}.failed")
        Image.fromarray(current.astype(np.uint8)).save(failed)
        if self.artifacts_dir:
            out = pathlib.Path(self.artifacts_dir)
            out.mkdir(parents=True, exist_ok=True)
            Image.fromarray(current.astype(np.uint8)).save(out / f"{name}.failed.png")
            Image.fromarray(baseline.astype(np.uint8)).save(
                out / f"{name}.baseline.png"
            )
        return failed

    @staticmethod
    def _colour_histogram(image: np.ndarray, bins: int = 32) -> np.ndarray:
        """Normalised RGB histogram: which colours an image uses, and in what proportion."""
        counts, _ = np.histogramdd(
            image.reshape(-1, 3), bins=(bins,) * 3, range=((0, 256),) * 3
        )
        return counts / counts.sum()

    def expect_palette_matches(
        self, element: WebElement, name: str, max_distance: float = 0.001
    ):
        """
        Assert `element` uses the same colours, in the same proportions, as
        baseline `name` -- ignoring where on screen they are.

        CI installs the latest beta rather than a pinned build, so chrome
        geometry shifts under us: between 160.0b2 and the build CI ran on
        2026-11-03 the tab narrowed by 6px, moving 2111 pixels and failing a
        pixel-exact compare. Both images still held the same 698 colours with
        the counts moving 0.002%, so comparing the distribution survives a
        build roll while a palette change still shows: shifting the accent
        channel by only 4 scores 0.007, against 0.000 for the build
        difference.

        Use this where the case is about colour. Where it is about shape, use
        expect_matches, which will not tolerate a layout change.
        """
        path = self.path_for(name)
        current = self.capture_settled(element)

        if self.update or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(current.astype(np.uint8)).save(path)
            if not self.update:
                raise AssertionError(
                    f"No baseline existed at {path}, so one was written from this "
                    "run. Review it, commit it, and re-run to assert against it."
                )
            return self

        baseline = self._as_array(path.read_bytes())
        distance = float(
            np.abs(
                self._colour_histogram(baseline) - self._colour_histogram(current)
            ).sum()
            / 2
        )
        if distance > max_distance:
            self._save_failed(name, current, baseline)
            raise AssertionError(
                f"{name}: colour palette changed, distribution distance "
                f"{distance:.4f} exceeds {max_distance}. The capture is in the "
                "artifacts; if the change is intended, refresh with "
                "--update-visual-baselines."
            )
        logging.info(f"{name} palette matches (distance {distance:.4f})")
        return self

    def expect_palette_differs(
        self, element: WebElement, name: str, min_distance: float = 0.05
    ):
        """Assert `element` does NOT use the same colours as baseline `name`."""
        path = self.path_for(name)
        if not path.exists():
            raise AssertionError(f"No baseline at {path} to differ from.")
        distance = float(
            np.abs(
                self._colour_histogram(self._as_array(path.read_bytes()))
                - self._colour_histogram(self.capture_settled(element))
            ).sum()
            / 2
        )
        if distance < min_distance:
            raise AssertionError(
                f"{name}: expected a different palette but the distribution "
                f"distance was only {distance:.4f} (wanted at least "
                f"{min_distance})."
            )
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
        # Settled here too: a half-painted frame differs for the wrong
        # reason, which would pass this assertion without a state change.
        # Settled at the default tolerance, not min_delta: a caller who
        # loosens the differ threshold must not also loosen what counts as
        # "stopped painting", or a still-animating element reads as settled.
        current = self.capture_settled(element)
        baseline = self._as_array(path.read_bytes())
        if baseline.shape != current.shape:
            raise AssertionError(
                f"{baseline_name}: size changed, baseline is "
                f"{baseline.shape[1]}x{baseline.shape[0]} but the element is "
                f"{current.shape[1]}x{current.shape[0]}. "
                + self._scale_hint(baseline, current)
                + "A different element cannot be compared against it."
            )
        max_delta = int(np.abs(baseline - current).max())
        if max_delta < min_delta:
            raise AssertionError(
                f"{baseline_name}: expected a visible difference but the largest "
                f"per-channel delta was only {max_delta} (wanted at least "
                f"{min_delta}), so the state does not appear to have changed."
            )
        logging.info(f"{baseline_name} differs as expected (max delta {max_delta})")
        return self
