from monitoring.expiry_checker import refresh_expiry_status
# Integration test is intentionally run against the local SQLite database.
def test_expiry_function_returns_integer():
    assert isinstance(refresh_expiry_status(), int)
