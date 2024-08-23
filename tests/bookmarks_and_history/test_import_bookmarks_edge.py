import os
from shutil import copyfile

import pytest


@pytest.fixture()
def edge_bookmarks(sys_platform, home_folder):
    if sys_platform == "Win":
        target = os.path.join(
            home_folder, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default"
        )
