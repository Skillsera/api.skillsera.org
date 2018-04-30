
import requests
from api import graph
from configs import AUTH_SERVER


def authenticate(email, password):
    r = requests.post('%s/authorize' % AUTH_SERVER, data={'email': email, 'password': password})
    resp = r.json()
    if 'http_error_code' not in resp:
        return resp
    raise Exception(resp['msg'])


def register(email, password, username):
    r = requests.post('%s/register' % AUTH_SERVER, data={
            'email': email,
            'name': username,
            'password': password,
            'password_conf': password,
            'service': 'skillsera'
            })
    resp = r.json()

    if 'http_error_code' not in resp and 'id' in resp:
        try:
            u = graph.User.get(email=email)
        except Exception:
            u = graph.User(email=email, username=username)
            u.create()
        return resp
    raise Exception(resp['msg'])


def activate(email, secret):
    r = requests.get('%s/activate?email=%s&secret=%s' % (AUTH_SERVER, email, secret))
    resp = r.json()
    if resp is True:
        return {'msg': 'Activation successful'}
    raise Exception(resp['msg'])


def login(email, password):
    """Authenticates user and returns session"""
    resp = authenticate(email, password)
    if 'http_error_code' not in resp and 'session' in resp:
        s = resp.get('session')
        email = s.get('email')
        if not email:
            raise Exception("Account corrupt, has no email")

        try:
            u = graph.User.get(email=email)
        except Exception as e:
            username = s.get('username')
            u = graph.User(email=email, username=username)
            u.create()

        s['id'] = u.id
        s['logged'] = True
        return s
    raise Exception(resp['msg'])


def _signout_single_signon():
    requests.post('%s/logout' % AUTH_SERVER)
