
import requests
from configs import AUTH_SERVER

def authenticate(email, password):
    r = requests.post(AUTH_SERVER, data={'email': email, 'password': password})
    return r.json()
