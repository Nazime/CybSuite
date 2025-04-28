from cybsuite.review import pm_reviewer, ReviewManager

from .utils import get_data_path

def test_plugin_bitlocker(new_cyberdb):
    plugin_name = "bitlocker_encryption"

    review_manager = ReviewManager(
        cyberdb=new_cyberdb,
        name=plugin_name,
        category="windows",
    )

    review_manager.review_files({"bitlocker_volumes": get_data_path("bitlocker_volumes.json")})
    
    controls = new_cyberdb.request("control", control_definition="windows:bitlocker")
    assert len(controls) == 1

    pass
