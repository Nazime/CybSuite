from cybsuite.cyberdb import BasePassiveScanner, Metadata


# TODO: This class is deactivated not working for now
class TagDC(BasePassiveScanner):
    name = "tag_dc"
    metadata = Metadata(
        description="All hosts that have port 389 445 and 88 will have 'dc' tag"
    )

    def do_run(self):
        for host in self.db.request("host", services__port=88).filter(
            services__port=389
        ):
            pass
            # add tag
