
def test_list_operations():
    numbers = [1, 2, 3]
    assert len(numbers) == 3
    assert numbers[0] == 1


def test_dictionary_lookup():
    user = {"username": "tester", "active": True}
    assert user["username"] == "tester"
    assert user["active"] is True


def test_string_validation():
    email = "tester@example.com"
    assert "@" in email
    assert "." in email
