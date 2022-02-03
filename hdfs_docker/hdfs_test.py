import http
import http.client
import urllib.parse


if __name__ == '__main__':
    conn = http.client.HTTPConnection('hdfs-server:9870')
    req = f'/webhdfs/v1/test?op=GETFILESTATUS'
    conn.request("GET", req)
    resp = conn.getresponse()
    resp_data = resp.read()
    if resp.status == http.HTTPStatus.OK:  # Directory exists, lets delete it
        print('Deleting test directory')
        req = f'/webhdfs/v1/test?op=DELETE&recursive=true'
        conn.request("DELETE", req)
        resp = conn.getresponse()
        resp_data = resp.read()

    # Create test directory
    print('Creating test directory')
    req = f'/webhdfs/v1/test?op=MKDIRS&permission=777'
    conn.request("PUT", req)
    resp = conn.getresponse()
    resp_data = resp.read()


    print('Creating test file')
    req = f'/webhdfs/v1/test/test.txt?op=CREATE'
    conn.request("PUT", req)
    resp = conn.getresponse()
    resp_data = resp.read()
    data_url = urllib.parse.urlparse(resp.headers['Location'])
    data_conn = http.client.HTTPConnection(data_url.netloc)
    req = f'{data_url.path}?{data_url.query}'
    data = b'Test data\n'
    data_conn.request("PUT", req, '', headers={'Content-Length': len(data)})
    data_conn.send(data)
    resp = data_conn.getresponse()
    data_conn.close()

    print('Reading test file')
    req = f'/webhdfs/v1/test/test.txt?op=OPEN'
    conn.request("GET", req)
    resp = conn.getresponse()
    resp_data = resp.read()
    data_url = urllib.parse.urlparse(resp.headers['Location'])
    data_conn = http.client.HTTPConnection(data_url.netloc)
    req = f'{data_url.path}?{data_url.query}'
    data_conn.request("GET", req, '', resp.headers)
    resp = data_conn.getresponse()
    resp_data = resp.read()
    data_conn.close()
    print(resp_data)

    conn.close()