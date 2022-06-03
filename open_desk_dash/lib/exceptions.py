class DeletionFailed(Exception):
    def __init__(self, msg="Plugin Deletion Failed", msg_type="error", *args, **kwargs):
        self.msg_type = msg_type
        super().__init__(msg, *args, **kwargs)


class InstallFailed(Exception):
    def __init__(self, msg="Plugin Install Failed", msg_type="error", *args, **kwargs):
        self.msg_type = msg_type
        super().__init__(msg, *args, **kwargs)
