from cybsuite.review.windows import Metadata, WindowsReviewer


# TODO: work in progress, not working yet
class RegistriesReviewer(WindowsReviewer):
    name = "registries"
    metadata = Metadata(category="windows", description="Review registries")
    controls = ["windows:cached_logons_count"]

    def do_run(self, files):
        registry_value = self.get_windows_registry(
            "HKLM\\SOFTWARE\\Microsoft/Windows NT/CurrentVersion/Winlogon"
        )

        cached_logons_count = int(registry_value["CachedLogonsCount"])

        control = self.control(
            "windows:cached_logons_count",
            details={"cached_logons_count": cached_logons_count},
        )

        control.ko(
            cached_logons_count >= 1,
            confidence="certain",
            justification="Checked registry for cached logons count.",
        )


# TODO fix JucyRegistryReviewer later
class JucyRegistryReviewer:
    name = "jucy_registry"
    metadata = Metadata(
        category="windows",
        description="Review jucy registries for passwords and sensitive information",
    )
    controls = ["windows:jucy_registry"]

    def do_run(self, files):
        keywords = [
            "password",
        ]

        for registry_path, registry_value in self.get_windows_registries().items():
            for reg_key, reg_value in registry_value.items():
                if isinstance(reg_value, int):
                    continue
                reg_value = str(reg_value)
                if len(reg_value) > 300:
                    continue
                reg_value_lower = reg_value.lower()
                reg_key_lower = reg_key.lower()

                for keyword in keywords:
                    if keyword in reg_key_lower or keyword in reg_value_lower:
                        self.alert(
                            "windows:jucy_registry",
                            details={
                                "registry_path": registry_path,
                                "registry_key": reg_key,
                                "registry_value": reg_value,
                                "keyword": keyword,
                            },
                            confidence="manual",
                        )
