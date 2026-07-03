"""Auth Module — Authentication, JWT, session management.

Responsibilities:
  - User login (email + password)
  - JWT access token issuance (RS256, 15 min)
  - Refresh token management (Redis-backed, 7 days)
  - Logout (token blocklist)
  - Password reset flow
  - GET /auth/me

Publishes Events:
  - auth.user.logged_in
  - auth.user.logged_out
  - auth.user.password_changed
  - auth.user.failed_login

Note: Auth is independent of the Users module.
Auth handles identity; Users handles profile management.
"""
