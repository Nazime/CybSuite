import pytest
from cybsuite.cyberdb import CyberDBScanManager
from koalak.plugin_manager import Plugin, PluginManager


class BasePlugin(Plugin):
    def run(self):
        pass


pm = PluginManager("test", base_plugin=BasePlugin)


class APlugin(BasePlugin):
    name = "a"

    def run(self):
        pass


class BPlugin(BasePlugin):
    name = "b"

    def run(self):
        raise ZeroDivisionError


def test_context_manager(new_cyberdb):
    sm = CyberDBScanManager(cyberdb=new_cyberdb, quiet=True)

    with pytest.raises(ValueError):
        # Not allowed to use 'with' outside of iteration
        with sm:
            pass

    for plugin in sm.iter_plugins(plugin_manager=pm, plugins=pm.instances()):
        # Allowed to use 'with' inside itering
        with sm:
            # Also, error is correctly handled! for plugin b
            plugin.run()

    with pytest.raises(ValueError):
        # Not allowed to use 'with' outside of iteration
        with sm:
            pass
