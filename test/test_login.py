import pytest
from flask import session
from q3 import app, send_email, users, day_off_requests, admin_notifications
import io
from contextlib import redirect_stdout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # global users, admin_notifications, day_off_requests
        users.clear()
        users.update({
            "aaa": {"password": "admin123", "roles": ["admin", "manager", "staff"], "failed_attempts": 0, "email": "aaa@example.com", "notifications": []},
            "bbb": {"password": "manager123", "roles": ["manager", "staff"], "failed_attempts": 0, "email": "bbb@example.com", "notifications": []},
            "ccc": {"password": "staff123", "roles": ["staff"], "failed_attempts": 0, "email": "ccc@example.com", "notifications": []},
        })
        admin_notifications.clear()
        day_off_requests.clear()
        yield client

# Functional test for login function

def test_valid_login(client):
    response = client.post('/login', data={'username': 'aaa', 'password': 'admin123'})
    assert response.status_code == 302 
    assert response.headers['Location'] == '/admin/aaa'

def test_login_invalid_input(client):
    response = client.post('/login', data={'username': '', 'password': ''})
    assert response.status_code == 200
    assert b"User not found" in response.data

def test_invalid_password(client):
    response = client.post('/login', data={'username': 'aaa', 'password': 'user123'})
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

def test_invalid_username(client):
    response = client.post('/login', data={'username': 'invalid_user', 'password': 'password123'})
    assert response.status_code == 200
    assert b"User not found" in response.data

def test_valid_login_redirection(client):
    response = client.post('/login', data={'username': 'aaa', 'password': 'admin123'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/aaa'

# Pesticide Paradox
@pytest.mark.parametrize("username, password, expected_error", [
    ('ccc', 'wrong', b"Invalid credentials"),
    ('xxx', 'pass', b"User not found"),
    ('ccc', '', b"Invalid credentials"),
])
def test_login_variations(client, username, password, expected_error):
    response = client.post('/login', data={'username': username, 'password': password})
    assert response.status_code == 200
    assert expected_error in response.data

def test_account_lockout(client):
    for _ in range(5):
        response = client.post('/login', data={'username': 'ccc', 'password': 'wrongpassword'})
        assert response.status_code == 200
        assert b"Invalid credentials" in response.data

    response = client.post('/login', data={'username': 'ccc', 'password': 'password123'})
    assert response.status_code == 200
    assert b"Account locked. Contact admin." in response.data


# Non-functional test for login function
def test_login_compatibility():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:5000/login")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys("aaa")
        password_field.send_keys("admin123")
        password_field.send_keys(Keys.RETURN)

        driver.implicitly_wait(5)

        assert 'Welcome aaa! This is admin page' in driver.page_source

    finally:
        driver.quit()