# from flask_api import exceptions, parsers, status, mediatypes
import flask_api
from http.server import BaseHTTPRequestHandler
import io
import base64
import json

# refs: https://docs.python.org/3/library/http.server.html#http.server.BaseHTTPRequestHandler
class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = io.BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

class BodyParser:
    #refs: https://github.com/flask-api/flask-api/blob/ea01422031d2272cbb716fbf22266638859df06d/flask_api/tests/test_request.py
    mapping_content_type_to_parser = {
        'application/x-www-form-urlencoded': flask_api.parsers.URLEncodedParser(),
        'application/json': flask_api.parsers.JSONParser(),
        'multipart/form-data': flask_api.parsers.MultiPartParser()
    }

    def detect_content_type(self, string):
        try:
            json.loads(string.decode('utf-8'))
            return 'application/json'
        except json.decoder.JSONDecodeError:
            return 'application/x-www-form-urlencoded'

    def get_content_type(self, string):
        return string[:string.find(';')]

    def parse(self, raw_body, content_type_string):
        body_stream = io.BytesIO(raw_body)
        data = {}

        try:
            if 'boundary' in content_type_string:
                content_type = self.get_content_type(content_type_string)
                media_type = flask_api.mediatypes.MediaType(content_type_string)
                parser = self.mapping_content_type_to_parser[content_type]
                parts = parser.parse(body_stream, media_type, content_length=len(raw_body))
                data = {}
                for part in parts:
                    data.update(dict(part))
            else:
                content_type = self.detect_content_type(raw_body)
                parser = self.mapping_content_type_to_parser[content_type]
                data = parser.parse(body_stream, content_type)
        except KeyError:
            print("content-type: %s is not supported." % content_type)

        return data, content_type
