# Rest_api_connector.py

import json
import requests

class RestApiConnector:
    def __init__(self, username="", password=""):
        # Initialize general args.
        self.username = username
        self.password = password
        self.session = self.__init_session()


    def __set_base_url(self, base_url):
        if not base_url.endswith("/"):
          base_url = base_url + "/"
        return base_url


    def __init_session(self):
        # Initialize session to cluster
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        return session
    
    
    def invoke_rest_call(self, base_url, path, method, session=True, force_refresh=None, body={}, headers=None):
        base_url = self.__set_base_url(base_url)
        if path.startswith("/"):
            path = path[1:]
        
        url = base_url + path

         # update header
        if force_refresh is not None:
            self.session.headers['Force-Refresh'] = "True"
        if headers is not None:
            for header_entry in headers:
                for key, value in header_entry.items():
                    self.session.headers[key] = value

        # if session is set to false no headers are sent and thus no basic auth
        if session:

            if method == "GET" or method == "DELETE":
                req = requests.Request(method, url)
            else:
                # if the method is either POST or PUT
                # check if body is formatted correct
                try:
                    json.dumps(body)
                except Exception as error_message:
                    raise f'ERROR: {error_message}'

                # formatting alright make call
                req = requests.Request(method, url, json=body)
            
            prepared_request = self.session.prepare_request(req)
            server_response = self.session.send(prepared_request)
            self.session.close()
        else:
            if method == "GET":
                server_response = requests.get(url, verify=False)
            elif method == "POST" or method == "PUT" or method == "PATCH":
                server_response = requests.post(url, verify=False, data=body)
            elif method == "DELETE":
                server_response = requests.delete(url, verify=False)
            else:
                raise Exception("ERROR unsupported method when running sessionless, please use session")
            
        if int(server_response.status_code) in [200, 201, 202, 203, 204]:
            if server_response.text == '': # NTX v2.0/cluster/public_keys/" + key['name'] gives empty response omg...
                return 'Request Sent - No confirmation from server side'
            return json.loads(server_response.text)
        else:
            raise Exception(f'ERROR Status Code not in [200, 201, 202, 203, 204]: {server_response.status_code}')