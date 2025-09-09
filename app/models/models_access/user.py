class User:
    def __init__(self, id, username, email, password, role_id, created_at=None):
        self.user_id = id
        self.username = username
        self.email = email
        self.password = password
        self.role_id = role_id
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role_id": self.role_id,
            "created_at": self.created_at 
        }
