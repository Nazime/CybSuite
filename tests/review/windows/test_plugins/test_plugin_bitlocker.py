from cybsuite.review import ReviewManager

from .utils import get_data_path


def test_plugin_bitlocker(new_cyberdb):
    plugin_name = "bitlocker_encryption"

    review_manager = ReviewManager(
        cyberdb=new_cyberdb,
        plugins_names=[plugin_name],
    )

    review_manager.review_files(
        {"bitlocker_volumes": get_data_path("bitlocker_volumes.json")}
    )

    controls = new_cyberdb.request(
        "control", control_definition__name="windows:bitlocker"
    )
    assert len(controls) == 1

    control = controls[0]
    assert control.details["mount_point"] == "C:"
    assert control.status == "ok"
