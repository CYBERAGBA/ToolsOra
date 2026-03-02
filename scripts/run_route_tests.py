import urllib.request, urllib.parse, json, sys

urls = [
    ('GET','http://127.0.0.1:5000/'),
    ('GET','http://127.0.0.1:5000/auth/login'),
    ('GET','http://127.0.0.1:5000/auth/register'),
    ('GET','http://127.0.0.1:5000/dashboard'),
    ('GET','http://127.0.0.1:5000/api/status'),
    ('GET','http://127.0.0.1:5000/api/health'),
    ('GET','http://127.0.0.1:5000/modules/education/lessons'),
    ('GET','http://127.0.0.1:5000/modules/education/quiz/1'),
    ('GET','http://127.0.0.1:5000/modules/automation/run_report'),
    ('GET','http://127.0.0.1:5000/modules/automation/schedule_report'),
    ('POST','http://127.0.0.1:5000/payments/paypal/create'),
    ('GET','http://127.0.0.1:5000/payments/paypal/execute?token=simulated')
]


def do(req_type, url):
    try:
        if req_type == 'GET':
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.getcode(), r.read().decode('utf-8')[:2000]
        else:
            data = json.dumps({'amount':2.5}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.getcode(), r.read().decode('utf-8')[:2000]
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
        except Exception:
            body = ''
        return e.code, body[:2000]
    except Exception as e:
        return None, str(e)


if __name__ == '__main__':
    for t,u in urls:
        code, body = do(t,u)
        print(f"== {t} {u} => {code} ==")
        if body:
            print(body)
        print()
