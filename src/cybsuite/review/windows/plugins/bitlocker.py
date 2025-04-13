from cybsuite.review.windows import Metadata, WindowsReviewer


class BitlockerReviewer(WindowsReviewer):
    name = "bitlocker_encryption"
    metadata = Metadata(category="windows", description="Review Bitlocker")
    files = {"bitlocker_volumes": "commands/bitlocker_volumes.json"}
    controls = ["windows:bitlocker"]

    def do_run(self, files):
        bitlocker_volumes_file = files["bitlocker_volumes"]
        bitlocker_volumes = self.load_json(bitlocker_volumes_file)
        for bitlocker_volume in bitlocker_volumes:
            # Check for each volume if Bitlocker is enabled
            mount_point = bitlocker_volume["MountPoint"]
            control = self.control(
                "windows:bitlocker",
                details={"mount_point": mount_point},
            )

            control.ok(
                bitlocker_volume["EncryptionMethod"] is not None,
                confidence="certain",
                justification="Check if 'Get-BitLockerVolume' returned EncryptionMethod that is not null.",
            )

        # TODO: Check Encryption Method?
