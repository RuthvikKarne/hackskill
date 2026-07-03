"""Users Module — User profiles, roles, permissions.

Responsibilities:
  - User CRUD (create, read, update, deactivate)
  - Role assignment (Hospital Admin, Doctor, Nurse, etc.)
  - Permission management
  - Hospital and department assignment
  - User activity status

Publishes Events:
  - users.user.created
  - users.user.updated
  - users.user.deactivated
  - users.user.role_changed
"""
