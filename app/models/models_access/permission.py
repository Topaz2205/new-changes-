class Permission:
    def __init__(self, permission_id, name):
        self.permission_id = permission_id
        self.name = name

    def to_dict(self):
        return {
            "id": self.permission_id,
            "name": self.name
        }
