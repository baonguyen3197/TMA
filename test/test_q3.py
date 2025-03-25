import pytest
from flask import session
from q3 import app, send_email, users, day_off_requests, admin_notifications
import io
from contextlib import redirect_stdout

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
        # users = {
        #     "aaa": {"password": "admin123", "roles": ["admin", "manager", "staff"], "failed_attempts": 0, "email": "aaa@example.com", "notifications": []},
        #     "bbb": {"password": "manager123", "roles": ["manager", "staff"], "failed_attempts": 0, "email": "bbb@example.com", "notifications": []},
        #     "ccc": {"password": "staff123", "roles": ["staff"], "failed_attempts": 0, "email": "ccc@example.com", "notifications": []},
        # }
        # admin_notifications = []
        # day_off_requests = []
        admin_notifications.clear()
        day_off_requests.clear()
        yield client

# Principle 1: Show Presence of Defects
def test_login_invalid_input(client):
    response = client.post('/login', data={'username': '', 'password': ''})
    assert response.status_code == 200
    assert b"User not found" in response.data

# Principle 2: Exhaustive Testing Impossible
def test_admin_modify_user_not_found(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']
    response = client.post('/admin', data={'action': 'modify', 'username': 'xxx', 'roles': ['staff']})
    assert response.status_code == 404
    assert b"User not found" in response.data

# Principle 3: Early Testing
def test_send_email_success(client):
    f = io.StringIO()
    with redirect_stdout(f):
        send_email('ccc', 'newpass', 'admin')
    assert "Email sent to ccc: Your new password is newpass" in f.getvalue()

# Principle 4: Defects Cluster
def test_manager_invalid_index(client):
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager']
    response = client.post('/manager', data={'-1': 'approve'})
    assert response.status_code == 200
    assert len(day_off_requests) == 0

# Principle 5: Pesticide Paradox
@pytest.mark.parametrize("username, password, expected_error", [
    ('ccc', 'wrong', b"Invalid credentials"),
    ('xxx', 'pass', b"User not found"),
    ('ccc', '', b"Invalid credentials"),
])
def test_login_variations(client, username, password, expected_error):
    response = client.post('/login', data={'username': username, 'password': password})
    assert response.status_code == 200
    assert expected_error in response.data

# Principle 6: Context-Dependent
def test_session_integrity(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']
    with client.session_transaction() as sess:
        sess['roles'] = ['admin']
    response = client.get('/admin/ccc')
    assert response.status_code == 404

# Principle 7: Absence-of-Errors Fallacy
def test_day_off_workflow(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']
    client.post('/staff', data={'date': '2025-03-27', 'reason': 'vacation'})
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager']
    client.post('/manager', data={'0': 'approve'})
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']
    response = client.get('/staff/ccc')
    assert b"Your day-off request for 2025-03-27 has been approved" in response.data

# Other tests for reference
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_role_page_admin(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin', 'manager', 'staff']
    response = client.get('/admin/aaa')
    assert response.status_code == 200
    assert b"Welcome aaa! This is admin page" in response.data

def test_role_page_manager(client):
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager', 'staff']
    response = client.get('/manager/bbb')
    assert response.status_code == 200
    assert b"Welcome bbb! This is manager page" in response.data

def test_role_page_staff(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']
    response = client.get('/staff/ccc')
    assert response.status_code == 200
    assert b"Welcome ccc! This is staff page" in response.data

def test_role_page_user_not_found(client):
    # Simulate a logged-in session
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    # Access the role page with a non-existent username
    response = client.get('/admin/nonexistent_user')
    
    # Verify the response status code and message
    assert response.status_code == 404
    assert b"User not found" in response.data

def test_role_page_redirect_to_login(client):
    # Access the role page without a session
    response = client.get('/admin/aaa')

    # Verify that the response is a redirect to the login page
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_role_page_unauthorized_access(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']

    # Access another user's role page
    response = client.get('/admin/aaa')

    # Verify that the response is a 403 Forbidden error
    assert response.status_code == 403
    assert b"You cannot access another user's page." in response.data

    response = client.post('/manager')
    assert response.status_code == 403
    assert b"You do not have permission to perform this action." in response.data

    # Case 2: User logged in but does not have the 'manager' role
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']

    response = client.post('/manager')
    assert response.status_code == 403
    assert b"You do not have permission to perform this action." in response.data

def test_role_page_invalid_role(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']

    response = client.get('/test/ccc')
    
    assert response.status_code == 404
    assert b"Invalid role" in response.data

def test_manage_accounts_unauthorized(client):
    # Case 1: User not logged in
    response = client.post('/admin')
    assert response.status_code == 403
    assert b"You do not have permission to access this page." in response.data

    # Case 2: User logged in but does not have the 'admin' role
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager', 'staff']

    response = client.post('/admin')
    assert response.status_code == 403
    assert b"You do not have permission to access this page." in response.data

# Test send_email exception
def test_send_email_exception(client):
    from q3 import send_email
    with pytest.raises(Exception, match="Only admin can send email"):
        send_email('ccc', 'newpass', 'staff')

def test_admin_invalid_action(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    response = client.post('/admin', data={
        'action': 'invalid_action', 
        'username': 'bbb'
    })

    # Verify the response
    assert response.status_code == 400
    assert b"Invalid action." in response.data

def test_admin_missing_action_or_username(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    # Missing action
    response = client.post('/admin', data={'username': 'ddd'})
    assert response.status_code == 400
    assert b"Action and username are required." in response.data

    # Missing username
    response = client.post('/admin', data={'action': 'create'})
    assert response.status_code == 400
    assert b"Action and username are required." in response.data

# Test /admin create user
def test_admin_create_user(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']
    response = client.post('/admin', data={
        'action': 'create',
        'username': 'ddd',
        'password': 'pass123',
        'roles': ['staff']
    })
    assert response.status_code == 200
    assert b"User ddd created successfully" in response.data

    response = client.post('/admin', data={
        'action': 'create',
        'username': 'ccc',
        'password': 'pass123',
        'roles': ['staff']
    })
    assert response.status_code == 200
    assert b"User already exists." in response.data

def test_admin_modify_roles(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    # Modify roles for user 'bbb'
    response = client.post('/admin', data={
        'action': 'modify',
        'username': 'bbb',
        'roles': ['staff']
    })
    assert response.status_code == 200
    assert b"User bbb roles modified successfully." in response.data

    from q3 import users
    assert users['bbb']['roles'] == ['staff']

def test_admin_delete_user(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    # Delete user 'bbb'
    response = client.post('/admin', data={
        'action': 'delete',
        'username': 'bbb'
    })
    assert response.status_code == 200
    assert b"User bbb deleted successfully." in response.data

    from q3 import users
    assert 'bbb' not in users

    response = client.post('/admin', data={
        'action': 'delete',
        'username': 'nonexistent_user'
    })
    assert response.status_code == 404
    assert b"User not found." in response.data
   
def test_admin_reset_password(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    users['ccc'] = {'password': 'staff123', 'roles': ['staff'], 'failed_attempts': 0, 'notifications': []}
    print("Before reset:", users['ccc'])

    response = client.post('/admin', data={
        'action': 'reset_password',
        'username': 'ccc',
        'password': ''
    })

    assert response.status_code == 200
    assert b"Password is required." in response.data

    # Ensure the user's password was not changed
    assert users['ccc']['password'] == 'staff123'

    # Reset the password
    response = client.post('/admin', data={
        'action': 'reset_password',
        'username': 'ccc',
        'password': 'newpassword123'
    })
    print("After reset:", users['ccc'])
    assert response.status_code == 200
    assert b"Password for ccc reset successfully." in response.data
    assert users['ccc']['password'] == 'newpassword123'
    assert "Your password has been reset to: newpassword123" in users['ccc']['notifications']

    response = client.post('/admin', data={
        'action': 'reset_password',
        'username': 'nonexistent_user',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
    assert b"User not found." in response.data


# Test notify_admin
def test_notify_admin(client):
    from q3 import notify_admin, admin_notifications
    notify_admin("ccc")
    assert "User ccc's account is locked due to too many failed login attempts." in admin_notifications

# Test /email/<email>
def test_email_notifications(client):
    users['ccc']['notifications'].append("Your password has been reset to: newpassword123")
    
    # Test the email notifications route
    response = client.get('/email/ccc@example.com')
    assert response.status_code == 200
    assert b"Your password has been reset to: newpassword123" in response.data

    # Test for a non-existent user
    response = client.get('/email/unknown@example.com')
    assert response.status_code == 404
    assert b"User not found" in response.data

# Test login lockout
def test_login_lockout(client):
    for _ in range(5):
        client.post('/login', data={'username': 'ccc', 'password': 'wrong'})
    response = client.post('/login', data={'username': 'ccc', 'password': 'staff123'})
    assert response.status_code == 200
    assert b"Account locked" in response.data

# Test manager approve/reject request
def test_manager_approve_request(client):
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager']
    day_off_requests.append({
        'username': 'ccc',
        'date': '2025-03-25',
        'reason': 'Vacation',
        'status': 'Pending'
    })
    response = client.post('/manager', data={'0': 'approve'})
    assert response.status_code == 200
    assert b"Approved" in response.data

def test_manager_reject_request(client):
    from q3 import day_off_requests, users
    day_off_requests.append({
        'username': 'ccc',
        'date': '2025-03-27',
        'reason': 'Vacation',
        'status': 'Pending'
    })

    with client.session_transaction() as sess:
        sess['username'] = 'bbb'
        sess['roles'] = ['manager']

    # Reject the request
    response = client.post('/manager', data={'0': 'reject'})
    assert response.status_code == 200

    # Verify that the request was rejected
    assert day_off_requests[0]['status'] == 'Rejected'
    assert "Your day-off request for 2025-03-27 has been rejected." in users['ccc']['notifications']

def test_manage_day_off_no_requests(client):
    # Ensure there are no day-off requests
    from q3 import day_off_requests
    day_off_requests.clear()

    # Simulate a manager session
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'  # User 'bbb' has the 'manager' role
        sess['roles'] = ['manager']

    # Send a request
    response = client.post('/manager', data={"0": "approve"})
    assert response.status_code == 200  # The request should be ignored
    assert len(day_off_requests) == 0

def test_manage_day_off_invalid_request_index(client):
    # Add a pending day-off request
    from q3 import day_off_requests
    day_off_requests.append({
        "username": "ccc",
        "date": "2025-03-27",
        "reason": "Vacation",
        "status": "Pending"
    })

    # Simulate a manager session
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'  # User 'bbb' has the 'manager' role
        sess['roles'] = ['manager']

    # Send a request with an invalid index (not a digit)
    response = client.post('/manager', data={"invalid_index": "approve"})
    assert response.status_code == 200  # The request should be ignored
    assert day_off_requests[0]["status"] == "Pending"  # No changes should be made

    # Send a request with an out-of-range index
    response = client.post('/manager', data={"999": "approve"})
    assert response.status_code == 200  # The request should be ignored
    assert day_off_requests[0]["status"] == "Pending"  # No changes should be made

def test_manage_day_off_valid_request(client):
    # Add a pending day-off request
    from q3 import day_off_requests, users
    day_off_requests.append({
        "username": "ccc",
        "date": "2025-03-27",
        "reason": "Vacation",
        "status": "Pending"
    })

    # Simulate a manager session
    with client.session_transaction() as sess:
        sess['username'] = 'bbb'  # User 'bbb' has the 'manager' role
        sess['roles'] = ['manager']

    # Approve the day-off request
    response = client.post('/manager', data={"0": "approve"})
    assert response.status_code == 200
    assert day_off_requests[0]["status"] == "Approved"
    assert "Your day-off request for 2025-03-27 has been approved." in users["ccc"]["notifications"]

    # Reject the day-off request
    response = client.post('/manager', data={"0": "reject"})
    assert response.status_code == 200
    assert day_off_requests[0]["status"] == "Rejected"
    assert "Your day-off request for 2025-03-27 has been rejected." in users["ccc"]["notifications"]

def test_manage_day_off_unauthorized(client):
    # Case 1: User not logged in
    response = client.post('/manager')
    assert response.status_code == 403
    assert b"You do not have permission to perform this action." in response.data

    # Case 2: User logged in but does not have the 'manager' role
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'  # User 'ccc' only has the 'staff' role
        sess['roles'] = ['staff']

    response = client.post('/manager')
    assert response.status_code == 403
    assert b"You do not have permission to perform this action." in response.data

# Test staff submit day off
def test_staff_submit_day_off(client):
    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']
    response = client.post('/staff', data={'date': '2025-03-27', 'reason': 'vacation'})
    assert response.status_code == 200
    assert b"Day-off request submitted successfully" in response.data

def test_login_success(client):
    # Simulate a successful login for user 'aaa'
    response = client.post('/login', data={
        'username': 'aaa',
        'password': 'admin123'
    })

    # Verify that the response is a redirect (302)
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/aaa'  # Redirect to the admin role page

    # Follow the redirect to the role page
    response = client.get('/admin/aaa', follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome aaa! This is admin page" in response.data  # Adjust based on your admin.html content

    # Verify that the session is correctly set up
    with client.session_transaction() as sess:
        assert sess['username'] == 'aaa'
        assert sess['roles'] == ['admin', 'manager', 'staff']

# Test login failed 5 times
def test_login_failed_5_times(client):
    for _ in range(5):
        response = client.post('/login', data={'username': 'aaa', 'password': 'wrongpassword'})
        assert response.status_code == 200
        assert b"Invalid credentials" in response.data

    # On the 6th attempt, the account should be locked
    response = client.post('/login', data={'username': 'aaa', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert b"Account locked. Contact admin." in response.data

    # Verify that the user's failed_attempts count is 5
    from q3 import users
    assert users['aaa']['failed_attempts'] == 5

def test_logout(client):
    with client.session_transaction() as sess:
        sess['username'] = 'aaa'
        sess['roles'] = ['admin']

    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

    # Verify that the session is cleared
    with client.session_transaction() as sess:
        assert 'username' not in sess
        assert 'roles' not in sess

def test_submit_day_off(client):
    response = client.post('/staff', data={
            'date': '2025-03-27',
            'reason': 'Vacation'
        })
    assert response.status_code == 403
    assert b"You do not have permission to perform this action." in response.data

    with client.session_transaction() as sess:
        sess['username'] = 'ccc'
        sess['roles'] = ['staff']

    # Submit a day-off request without providing the 'date'
    response = client.post('/staff', data={
        'date': '',
        'reason': 'Vacation'
    })
    assert response.status_code == 400
    assert b"Date and reason are required." in response.data

    # Submit a day-off request without providing the 'reason'
    response = client.post('/staff', data={
        'date': '2025-03-27',
        'reason': ''
    })
    assert response.status_code == 400
    assert b"Date and reason are required." in response.data

    # Submit a day-off request without providing both 'date' and 'reason'
    response = client.post('/staff', data={
        'date': '',
        'reason': ''
    })
    assert response.status_code == 400
    assert b"Date and reason are required." in response.data
