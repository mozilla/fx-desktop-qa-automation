from ..environment import Environment, parse_firefox_sites
from .helpers import by_id, write_files

PLUGIN = """
import pytest

def pytest_addoption(parser):
    parser.addoption("--plug-flag")

def pytest_configure(config):
    config.addinivalue_line("markers", "plugmark: from the plugin")

@pytest.fixture()
def plugfix():
    return 1
"""


def fake_site(root):
    """A site-packages dir with a pytest plugin 'fakeplug' that requires 'dep'."""
    return write_files(
        root,
        {
            "fakeplug_mod.py": PLUGIN,
            "fakeplug-1.0.dist-info/METADATA": (
                "Metadata-Version: 2.1\nName: fakeplug\nVersion: 1.0\nRequires-Dist: dep\n"
                'Requires-Dist: only-for-docs ; extra == "docs"\n'
            ),
            "fakeplug-1.0.dist-info/RECORD": "fakeplug_mod.py,,\nfakeplug-1.0.dist-info/METADATA,,\n",
            "fakeplug-1.0.dist-info/entry_points.txt": "[pytest11]\nfakeplug = fakeplug_mod\n",
            "dep.py": "",
            "dep-2.0.dist-info/METADATA": "Metadata-Version: 2.1\nName: dep\nVersion: 2.0\n",
            "dep-2.0.dist-info/RECORD": "dep.py,,\ndep-2.0.dist-info/METADATA,,\n",
        },
    )


def test_environment_reads_metadata_and_plugins(tmp_path):
    env = Environment([fake_site(tmp_path / "site")])
    assert set(env.dists) == {"fakeplug", "dep"}
    assert env.module_to_dist == {"fakeplug_mod": "fakeplug", "dep": "dep"}
    assert [m for m, _ in env.dists["fakeplug"].plugin_files] == ["fakeplug_mod"]
    assert env.closure({"fakeplug"}) == ({"fakeplug", "dep"}, set())
    assert env.closure({"absent"}) == (set(), {"absent"})


def test_site_files_with_pth_and_includes(tmp_path):
    root = write_files(
        tmp_path / "ff",
        {
            "python/sites/ui.txt": "requires-python:>=3.11\npypi:Fake_Plug==1.0\npackages.txt:python/sites/more.txt\n",
            "python/sites/more.txt": "pth:testing/mozbase/mozinfo\n",
            "testing/mozbase/mozinfo/mozinfo/__init__.py": "",
            "testing/mozbase/mozinfo/setup.py": "",
        },
    )
    site = parse_firefox_sites([root / "python/sites/ui.txt"], None)
    assert [f.value for f in site.pypi] == ["fake-plug"]
    assert site.modules == {"mozinfo"}
    assert len(site.files) == 2


def test_plugin_fixture_available_only_when_firefox_installs_it(
    tmp_path, make_repo, run_inventory
):
    site = fake_site(tmp_path / "site")
    repo = make_repo(
        {
            "tests/a/test_a.py": """
                import pytest

                @pytest.mark.plugmark
                def test_a(plugfix):
                    pass
            """,
        }
    )
    with_plugin = run_inventory(
        repo,
        firefox={"python/sites/ui.txt": "pypi:fakeplug==1.0\n"},
        site_packages=site,
    )
    assert with_plugin["missing_after_migration"] == []
    assert with_plugin["config"]["markers"][0]["registered_in_firefox"]

    repo2 = make_repo(
        {"tests/a/test_a.py": "def test_a(plugfix):\n    pass\n"}, name="repo2"
    )
    (tmp_path / "firefox" / "python" / "sites" / "ui.txt").write_text(
        "pypi:other==1.0\n"
    )
    without = run_inventory(repo2, site_packages=site)
    (missing,) = without["missing_after_migration"]
    assert missing["name"] == "plugfix"
    assert missing["starfox_provider_origins"] == ["plugin:fakeplug"]
    assert by_id(without) == {}
