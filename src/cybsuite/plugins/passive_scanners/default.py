from cybsuite.cyberdb import BasePassiveScanner, Metadata, pm_passive_scanners


class DefaultScanner(BasePassiveScanner):
    name = "default"
    metadata = Metadata(
        description="Default scanner",
    )

    def do_run(self):
        for scaner in pm_passive_scanners.iter(tags=["default"]):
            self.logger.info(f"Running {scaner.name} scanner")
            scanner = scaner(self.cyberdb)
            try:
                scanner.do_run()
            except Exception as e:
                self.logger.error(f"Error running {scaner.name} scanner: {e}")
