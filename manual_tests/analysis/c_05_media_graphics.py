"""Critical round -- media, images, graphics, scrolling/zoom and live-site web compat.

Suites: 1731 (Media playback / PiP), 88 (Image formats), 102 (Scrolling and zoom),
1977 (Graphics and hardware acceleration), 69048 (WebRender), 1694 (Top sites).

Two whole suites reduce to a single verdict:

* 1694 is 55 rows of "verify that everything works as expected on <live third-party site>".
  There is no in-tree equivalent and there cannot be -- the tree deliberately does not test
  against the live web.
* 1977 and 69048 are "no rendering artifacts / no visual issues" sweeps over real sites and
  third-party WebGL demos. The tree has a very large reftest corpus, but it compares
  synthetic references, which is a different question from "does twitter.com look right on
  this driver".

Picture-in-Picture is the opposite case: toolkit/components/pictureinpicture/tests has 81
browser-chrome tests and covers the feature mechanics thoroughly. What it does not cover is
the per-streaming-site rows (YouTube / Netflix / Prime / Max / Hulu), which need real
accounts and live players.
"""

from _ledger import C
from c_util import CREST

PIP = "toolkit/components/pictureinpicture/tests/"
ZOOM = "browser/base/content/test/zoom/"
AUTOPLAY = "dom/media/autoplay/test/browser/"

# ================================================================ media formats
C(
    1731,
    "STRONG",
    "dom/media/test/test_can_play_type.html; test_can_play_type_mpeg.html; "
    "test_can_play_type_ogg.html; test_can_play_type_wave.html; test_can_play_type_webm.html; "
    "test_playback.html; test_audio1.html; test_mp3_broadcast.html; test_mp3_with_multiple_ID3v2.html",
    "dom/media/test drives real decode-and-play for each container/codec pair and asserts "
    "playback reaches completion, with canPlayType coverage per format on top.",
    [95233, 95239, 95240, 95241, 95244],
)

# ================================================================ autoplay
C(
    1731,
    "STRONG",
    AUTOPLAY + "browser_autoplay_policy_detection_click_to_play.js; "
    "browser_autoplay_policy_user_gestures.js; browser_autoplay_policy_play_twice.js; "
    "browser_autoplay_userinteraction.js; "
    "toolkit/content/tests/browser/browser_delay_autoplay_media.js; "
    "browser_delay_autoplay_playMediaInMuteTab.js",
    "The autoplay policy tests cover muted media being allowed to start in the current tab "
    "while audible media is gated on a user gesture -- the exact rule this case states.",
    [330154],
)
C(
    1731,
    "STRONG",
    "browser/base/content/test/permissions/browser_autoplay_blocked.js; "
    + AUTOPLAY
    + "browser_autoplay_policy_request_permission.js; "
    "browser_autoplay_policy_detection_global_and_site_sticky.js; "
    "browser_autoplay_policy_detection_global_sticky.js",
    "browser_autoplay_blocked.js drives the blocked-autoplay doorhanger and the Allow / Block "
    "choices for audio and video, and the sticky-permission tests assert the resulting "
    "per-site permission.",
    [4108464, 4108465],
)

# ================================================================ Picture-in-Picture
C(
    1731,
    "STRONG",
    PIP + "browser_autotoggle.js; browser_backgroundTab.js; browser_closeTab.js",
    "browser_autotoggle.js is dedicated to the auto-trigger feature: that it is off by default "
    "and enabled by pref, that backgrounding a tab with a playing video opens PiP, that it "
    "auto-closes again, that it is suppressed on videos carrying the disable-PiP attribute, and "
    "that other media types do not trigger it. browser_closeTab.js covers closing the source "
    "tab tearing down the PiP window.",
    [2725451, 2725455, 2725458, 2742301, 2742305, 2742308],
)
C(
    1731,
    "STRONG",
    PIP + "browser_aaa_run_first_firstTimePiPToggleEvents.js; browser_showMessage.js; "
    "browser_nimbusMessageFirstTimePip.js; browser_nimbusFirstTimeStyleVariant.js",
    "A test that must run first specifically to observe the first-time in-video toggle, plus "
    "the message and style-variant tests for that toggle.",
    [1746413],
)
C(
    1731,
    "STRONG",
    PIP
    + "browser_keyboardToggle.js; browser_mouseButtonVariation.js; browser_controlsHover.js; "
    "browser_noPlayerControlsOnMiddleRightClick.js",
    "Opening PiP from the normal (non-first-time) in-video toggle, by mouse and by keyboard, "
    "including which mouse buttons do and do not activate it.",
    [1746414],
)
C(
    1731,
    "STRONG",
    PIP
    + "browser_resizeVideo.js; browser_smallVideoLayout.js; browser_cornerSnapping.js; "
    "browser_saveLastPiPLoc.js",
    "Resizing the PiP window, including the small-video layout thresholds and the mini player, "
    "with the resulting geometry asserted.",
    [1746425, 2081830],
)
C(
    1731,
    "STRONG",
    PIP
    + "browser_autotoggle.js; browser_cannotTriggerFromContent.js; browser_noToggleOnAudio.js",
    "The disable-PiP attribute suppressing the in-video toggle is asserted directly.",
    [2190041],
)
C(
    1731,
    "STRONG",
    PIP
    + "browser_controlsHover.js; browser_improved_controls.js; browser_playerControls.js; "
    "browser_playbackRate.js",
    "The PiP player's viewing and hover control modes, and the controls that appear in each.",
    [2081806],
)

# ================================================================ image formats
C(
    88,
    "STRONG",
    "image/test/reftest/jpeg/reftest.list; image/test/reftest/png/reftest.list; "
    "image/test/reftest/gif/reftest.list; image/test/reftest/bmp/reftest.list; "
    "image/test/reftest/webp/reftest.list; image/test/reftest/apng/reftest.list; "
    "image/test/mochitest/test_animated_gif.html; image/test/mochitest/test_animSVGImage.html; "
    "image/test/browser/browser_image.js; image/test/browser/browser_remote_image_svg.js",
    "image/test/reftest carries a per-format directory -- jpeg, png, gif, bmp, webp, apng, ico, "
    "avif, jxl -- each decoding real files of that format and comparing against a reference, "
    "which is precisely 'verify that .<ext> files are working properly'. SVG rendering is "
    "covered by the animSVGImage mochitests and browser_remote_image_svg.js.",
    [111468, 111469, 111470, 111542, 111543, 111545, 181159],
)

# ================================================================ zoom
C(
    102,
    "STRONG",
    "browser/components/customizableui/test/browser_934951_zoom_in_toolbar.js; "
    "browser_947914_button_zoomIn.js; browser_947914_button_zoomOut.js; "
    "browser_947914_button_zoomReset.js; " + ZOOM + "browser_zoom_commands.js",
    "The zoom in / out / reset toolbar buttons each have a dedicated test, plus the zoom "
    "commands themselves.",
    [165052],
)
C(
    102,
    "STRONG",
    "browser/modules/test/browser/browser_urlBar_zoom.js; "
    + ZOOM
    + "browser_subframe_textzoom.js; "
    "browser_zoom_commands.js; browser_keyboard_mousewheel_zoom_consistency.js",
    "browser_urlBar_zoom.js asserts the urlbar zoom indicator appears, updates and resets; "
    "browser_subframe_textzoom.js covers text-only zoom.",
    [165063],
)
C(
    102,
    "STRONG",
    ZOOM + "browser_default_zoom_multitab.js; browser_image_zoom_tabswitch.js; "
    "browser_default_zoom_sitespecific.js; browser_background_zoom.js; "
    "browser_tabswitch_zoom_flicker.js",
    "Zoom level being tracked per site across several tabs, and surviving tab switches, are "
    "each covered by a dedicated test.",
    [165075, 1120109],
)
C(
    102,
    "STRONG",
    ZOOM + "browser_default_zoom_sitespecific.js; browser_sitespecific_image_zoom.js; "
    "browser_sitespecific_video_zoom.js; browser_background_link_zoom_reset.js",
    "Site-specific zoom levels, including the image- and video-document variants.",
    [545732],
)
C(
    102,
    "STRONG",
    "browser/components/privatebrowsing/test/browser/browser_privatebrowsing_zoom.js; "
    "browser_privatebrowsing_zoomrestore.js",
    "Whether the global zoom level carries into a private window, and what happens to it when "
    "that window closes.",
    [545734],
)
C(
    102,
    "STRONG",
    ZOOM + "browser_default_zoom.js; browser_default_zoom_fission.js; "
    "browser/modules/test/browser/browser_urlBar_zoom.js; "
    "browser/components/preferences/tests/browser_accessibility_zoom.js",
    "The default zoom level, the badge that appears when the current site deviates from it, and "
    "the preferences surface that sets it.",
    [545729],
)

# ================================================================ reviewed but kept
CREST(
    1694,
    "MEDIUM",
    "n/a",
    "All 55 rows are 'verify that everything works as expected on <live third-party site>' "
    "spot checks against the real web (globo.com, mail.google.com, paypal.com, netflix.com, "
    "facebook.com and so on). The tree does not test against live sites, by design, so there is "
    "nothing to compare against.",
)
CREST(
    1731,
    "MEDIUM",
    PIP + "browser_text_tracks_webvtt_1.js; browser_subtitles_settings_panel.js; "
    "browser_audioScrubber.js; browser_privateWindow.js",
    "What is left is site-specific and platform-specific: subtitles, volume slider, controls and "
    "the urlbar entry point exercised against the YouTube / Netflix / Prime / Max / Hulu players, "
    "HDR playback on macOS, DRM/GMP installation from an offline state, and two YouTube "
    "buffering regressions. The underlying mechanics (WebVTT tracks, the subtitles panel, the "
    "audio scrubber) are covered against synthetic video, but the live players and accounts are "
    "the thing under test here.",
)
CREST(
    88,
    "MEDIUM",
    "image/test/browser/browser_image.js",
    "Two rows left over: image-heavy real websites rendering correctly, and .gifv -- which is an "
    "MP4 container behind a GIF-like URL rather than an image format the decoders handle.",
)
CREST(
    102,
    "MEDIUM",
    ZOOM + "browser_tooltip_zoom.js; browser_mousewheel_zoom.js; "
    "gfx/layers/apz/test/mochitest/",
    "The remainder splits three ways: zoom interacting with transient chrome surfaces "
    "(doorhangers, menus, context menus, dropdowns, dialogs, text selection) which the tree only "
    "touches via browser_tooltip_zoom.js; the double-tap-to-zoom gesture matrix, which needs a "
    "real touchscreen or touchpad and OS gesture settings; and the async-scrolling smoothness "
    "sweeps over image-heavy, video and PDF pages, which APZ tests approach only as synthetic "
    "unit tests.",
)
CREST(
    1977,
    "MEDIUM",
    "image/test/reftest/; dom/canvas/test/webgl-conf/",
    "'No rendering artifacts or crashes while browsing popular sites', WebGL 2.0 demos hosted on "
    "toji.github.io, custom fonts, animated banners and hardware-acceleration on/off comparisons. "
    "The tree's reftest and WebGL conformance corpora compare synthetic references; these rows "
    "are human visual inspection against live content on real GPU drivers.",
)
CREST(
    69048,
    "MEDIUM",
    "image/test/reftest/; dom/canvas/test/webgl-conf/",
    "Suite 69048 restates the same WebRender visual sweep as 1977 (WebGL demos, CSS3 and HTML5 "
    "animations, custom fonts, draggable images, animated text). Same reasoning applies.",
)
