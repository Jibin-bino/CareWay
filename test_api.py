import requests, json, sys

def run_tests():
    base = 'http://localhost:8080/api'
    # Register user (ignore if already exists)
    reg_data = {"username": "testuser", "password": "testpassword123", "email": "test@example.com"}
    try:
        r = requests.post(f'{base}/auth/register/', json=reg_data)
        print('Register status:', r.status_code, r.text)
    except Exception as e:
        print('Register error:', e)
    # Login
    login_data = {"username": "testuser", "password": "testpassword123"}
    login_resp = requests.post(f'{base}/auth/login/', json=login_data)
    print('Login status:', login_resp.status_code, login_resp.text)
    if login_resp.status_code == 200:
        token = login_resp.json().get('token')
        print('Token:', token)
        # Fetch appointments
        headers = {'Authorization': f'Token {token}'}
        appt_resp = requests.get(f'{base}/healthcare/appointments/list/', headers=headers)
        print('Appointments status:', appt_resp.status_code)
        if appt_resp.ok:
            print('Appointments:', json.dumps(appt_resp.json(), indent=2))
        else:
            print('Error fetching appointments:', appt_resp.text)
    else:
        sys.exit('Login failed')

if __name__ == '__main__':
    run_tests()

