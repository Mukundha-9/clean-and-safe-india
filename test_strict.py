import urllib.request, urllib.error, json

def post_json(url, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
        return res.status, json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

base_url = 'https://seemed-exploration-mambo-italia.trycloudflare.com'

print('=== 1. SEND OTP ===')
code, res = post_json(f'{base_url}/api/auth/send-otp', {'email': 'mukundha.real@gmail.com'})
otp = res['otp']
print(f'OTP Response: {code} | OTP: {otp}')

print('\n=== 2. REGISTER WITH 20 CREDITS ===')
code, res = post_json(f'{base_url}/api/auth/register', {
    'name': 'K. Mukundha',
    'email': 'mukundha.real@gmail.com',
    'otp': otp,
    'password': 'RealSecret@2026'
})
print(f'Registration Response: {code} | User: {res["user"]["name"]} | Civic Credits: {res["user"]["civicCredits"]}')

print('\n=== 3. TEST RANDOM / WRONG PASSWORDS (MUST BE REJECTED WITH 401) ===')
for fake_pass in ['random123', 'wrongpassword', '123456', 'xyz']:
    code, res = post_json(f'{base_url}/api/auth/login', {
        'email': 'mukundha.real@gmail.com',
        'password': fake_pass,
        'department': 'citizen'
    })
    print(f'Password "{fake_pass}": Code {code} | Error: {res.get("error")}')

print('\n=== 4. TEST CORRECT PASSWORD (MUST SUCCEED WITH 200) ===')
code, res = post_json(f'{base_url}/api/auth/login', {
    'email': 'mukundha.real@gmail.com',
    'password': 'RealSecret@2026',
    'department': 'citizen'
})
print(f'Correct Password: Code {code} | Success: {res.get("success")} | User: {res["user"]["name"]} | Credits: {res["user"]["civicCredits"]}')
