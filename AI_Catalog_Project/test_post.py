import json
from urllib import request

data = json.dumps({"name":"Test Product","description":"A small test"}).encode('utf-8')
req = request.Request('http://127.0.0.1:5000/generate', data=data, headers={'Content-Type':'application/json'})
resp = request.urlopen(req)
print(resp.read().decode())
