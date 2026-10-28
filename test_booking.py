import requests, json, sys

def run_booking_tests():
    BASE = 'http://localhost:8080/api'

    # Register (ignore if exists)
    reg = {
        'username': 'testuser',
        'password': 'testpassword123',
        'email': 'test@example.com'
    }
    try:
        r = requests.post(f'{BASE}/auth/register/', json=reg)
        print('Register:', r.status_code, r.text)
    except Exception as e:
        print('Register error:', e)

    # Login
    login_resp = requests.post(f'{BASE}/auth/login/', json={'username': 'testuser', 'password': 'testpassword123'})
    print('Login:', login_resp.status_code, login_resp.text)
    if login_resp.status_code != 200:
        sys.exit('Login failed')
    TOKEN = login_resp.json()['token']
    headers = {'Authorization': f'Token {TOKEN}'}

    # Get a doctor (first one)
    doctors = requests.get(f'{BASE}/healthcare/doctors/', headers=headers).json()
    if not doctors:
        sys.exit('No doctors found')
    doctor = doctors[0]
    print('Selected doctor:', doctor['name'], 'id', doctor['id'])

    # Get availability for that doctor
    avail = requests.get(f"{BASE}/healthcare/doctors/{doctor['id']}/availability/", headers=headers).json()
    if not avail:
        sys.exit('No availability slots')
    slot = avail[0]
    print('Selected slot id:', slot['id'], 'date', slot['date'], 'time', slot['start_time'])

    # Book appointment
    payload = {
        'availability': slot['id'],
        'patient_name': 'Test User',
        'patient_email': 'test@example.com',
        'reason': 'Routine check'
    }
    book = requests.post(f'{BASE}/healthcare/appointments/', json=payload, headers=headers)
    print('Booking response:', book.status_code, book.text)

    # Fetch appointments list
    appts = requests.get(f'{BASE}/healthcare/appointments/list/', headers=headers).json()
    print('Appointments after booking (count):', len(appts))
    print(json.dumps(appts, indent=2))

if __name__ == '__main__':
    run_booking_tests()

