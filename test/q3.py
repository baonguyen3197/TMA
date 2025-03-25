from flask import Flask, request, jsonify, url_for, redirect, render_template, abort, session
import secrets

app = Flask(__name__)

secret_key = secrets.token_hex(32)
print(f"Secret key: {secret_key}")
app.secret_key = secret_key

users = {
    "aaa": {
        "password": "admin123",
        "roles": ["admin", "manager", "staff"],
        "failed_attempts": 0,
        "email": "aaa@example.com",
        "notifications": []
    },
    "bbb": {
        "password": "manager123",
        "roles": ["manager", "staff"],
        "failed_attempts": 0,
        "email": "bbb@example.com",
        "notifications": []
    },
    "ccc": {
        "password": "staff123",
        "roles": ["staff"],
        "failed_attempts": 0,
        "email": "ccc@example.com",
        "notifications": []
    },
}

ROLE_PRIORITY = {"admin": 1, "manager": 2, "staff": 3}
admin_notifications = []
day_off_requests = []
day_off_approvals = []

def send_email(user, new_password, role):
    if role != "admin":
        raise Exception("Only admin can send email.")
    print(f"Email sent to {user}: Your new password is {new_password}")

@app.route('/')
def index():
    return render_template('home.html')

def notify_admin(username):
    message = f"User {username}'s account is locked due to too many failed login attempts."
    admin_notifications.append(message) 

@app.route('/email/<email>', methods=['GET'])
def email_notifications(email):
    user = next((u for u in users.values() if u.get("email") == email), None)
    if not user:
        return "User not found", 404
    
    return render_template('email.html', notifications=user["notifications"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username not in users:
            error = "User not found"
        else:
            user = users[username]

            if user["failed_attempts"] >= 5:
                error = "Account locked. Contact admin."
            elif user["password"] == password:
                user["failed_attempts"] = 0
                session['username'] = username
                session['roles'] = user["roles"]

                highest_role = min(user["roles"], key=lambda role: ROLE_PRIORITY[role])
                return redirect(url_for('role_page', role=highest_role, username=username))
            else:
                user["failed_attempts"] += 1
                if user["failed_attempts"] == 5:
                    notify_admin(username)
                error = "Invalid credentials"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/<role>/<username>', methods=['GET'])
def role_page(role, username):
    if username not in users:
        return "User not found", 404
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['username'] != username:
        return render_template('error_user.html', message="You cannot access another user's page.", role=session['roles'][0], username=session['username']), 403

    user = users[username]
    
    if role not in user["roles"]:
        return "Invalid role", 404
    
    if role == "admin":
        return render_template('admin.html', username=username, notifications=admin_notifications)
    elif role == "manager":
        return render_template('manager.html', username=username, day_off_requests=day_off_requests)
    elif role == "staff":
        return render_template('staff.html', username=username, notifications=users[username]['notifications'])
    
@app.route('/admin', methods=['GET', 'POST'])
def manage_accounts():
    global users
    if 'username' not in session or 'admin' not in session['roles']:
        return render_template('error_user_permission.html', message="You do not have permission to access this page."), 403

    # if request.method == 'GET':
    #     return render_template('admin.html', username=session['username'], notifications=admin_notifications)

    action = request.form.get('action')
    username = request.form.get('username')

    if not action or not username:
        return render_template('admin.html', username=session['username'], error="Action and username are required.", notifications=admin_notifications), 400

    if action == 'create':
        password = request.form.get('password')
        roles = request.form.getlist('roles')

        if username in users:
            return render_template('admin.html', username=session['username'], error="User already exists.", notifications=admin_notifications)
        users[username] = {"password": password, "roles": roles, "failed_attempts": 0, "notifications": []}
        return render_template('admin.html', username=session['username'], message=f"User {username} created successfully.", notifications=admin_notifications)
    
    elif action == 'modify':
        if username not in users:
            return render_template('admin.html', username=session['username'], error="User not found.", notifications=admin_notifications), 404

        roles = request.form.getlist('roles')
        users[username]['roles'] = roles
        return render_template('admin.html', username=session['username'], message=f"User {username} roles modified successfully.", notifications=admin_notifications)

    elif action == 'delete':
        if username not in users:
            return render_template('admin.html', username=session['username'], error="User not found.", notifications=admin_notifications), 404
        del users[username]
        return render_template('admin.html', username=session['username'], message=f"User {username} deleted successfully.", notifications=admin_notifications)

    elif action == 'reset_password':
        if username not in users:
            return render_template('admin.html', error="User not found.")
        new_password = request.form.get('password')
        if not new_password:
            return render_template('admin.html', error="Password is required.")
        
        users[username]["password"] = new_password
        users[username]["failed_attempts"] = 0
        users[username]["notifications"].append(f"Your password has been reset to: {new_password}")
        return render_template('admin.html', username=session['username'], message=f"Password for {username} reset successfully.")

    else:
        return render_template('admin.html', username=session['username'], error="Invalid action.", notifications=admin_notifications), 400

@app.route('/manager', methods=['GET', 'POST'])
def manage_day_off():
    if 'username' not in session or 'manager' not in session['roles']:
        return render_template('error.html', message="You do not have permission to perform this action."), 403

    # if request.method == 'GET':
    #     return render_template('manager.html', username=session['username'], requests=day_off_requests)

    for request_index, request_status in request.form.items():
        if request_index.isdigit():
            request_index = int(request_index)
            if request_index < 0 or request_index >= len(day_off_requests):
                continue

            staff_username = day_off_requests[request_index]['username']
            request_date = day_off_requests[request_index]['date']

            if request_status == 'approve':
                day_off_requests[request_index]['status'] = "Approved"
                users[staff_username]['notifications'].append(
                    f"Your day-off request for {request_date} has been approved."
                )
            elif request_status == 'reject':
                day_off_requests[request_index]['status'] = "Rejected"
                users[staff_username]['notifications'].append(
                    f"Your day-off request for {request_date} has been rejected."
                )

    return render_template('manager.html', username=session['username'], requests=day_off_requests)

@app.route('/staff', methods=['POST'])
def submit_day_off():
    if 'username' not in session or 'staff' not in session['roles']:
        return render_template('error.html', message="You do not have permission to perform this action."), 403

    date = request.form.get('date')
    reason = request.form.get('reason')

    if not date or not reason:
        return jsonify({"error": "Date and reason are required."}), 400

    day_off_requests.append({
        "username": session['username'],
        "date": date,
        "reason": reason,
        "status": "Pending"
    })

    return jsonify({"message": "Day-off request submitted successfully."}), 200

with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('role_page', role='admin', username='admin'))
    print(url_for('role_page', role='manager', username='manager'))
    print(url_for('role_page', role='staff', username='staff'))

if __name__ == '__main__':
    app.run(debug=True)