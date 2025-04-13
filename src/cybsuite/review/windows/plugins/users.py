from cybsuite.review.windows import Metadata, WindowsReviewer


class UsersReviewer(WindowsReviewer):
    name = "users"
    metadata = Metadata(category="windows", description="Review users")
    files = {"local_users": "commands/local_users.json"}
    controls = ["windows:users:built_in_admin_not_renamed"]

    def do_run(self, files):
        hostname = self.context.hostname
        filepath = files["local_users"]
        data = self.load_json(filepath)

        for user in data:
            sid = user["SID"]["Value"]
            rid = sid.split("-")[-1]
            self.feed(
                "windows_user", host=hostname, user=user["Name"], rid=rid, sid=sid
            )
            # Controls for Built-in Administrator (RID 500)
            if rid == "500":
                self.control(
                    "windows:users:built_in_admin_not_renamed",
                    details={"user": user["Name"]},
                ).ok(
                    user["Name"] != "Administrator",
                    confidence="certain",
                    justification="Checked RID 500 (built-in Administrator) name with command Get-LocalUser",
                )
