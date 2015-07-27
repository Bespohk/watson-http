# -*- coding: utf-8 -*-
from io import BytesIO, BufferedReader
import json
from pytest import raises
from watson.http.messages import Response, Request, MessageMixin
from watson.http import sessions
from tests.watson.http.support import sample_environ, start_response


class TestMixin(object):
    def test_version(self):
        message = MessageMixin()
        message.version = '1.2'
        assert message.version == '1.2'


class TestRequest(object):
    def test_create(self):
        data = 'test'
        environ = sample_environ(CONTENT_LENGTH=len(data))
        environ['wsgi.input'] = BufferedReader(BytesIO(data.encode('utf-8')))
        request = Request.from_environ(environ)
        assert request.method == 'GET'
        assert not request.is_method('PUT', 'PATCH')
        assert repr(request) == '<watson.http.messages.Request method:GET url:http://127.0.0.1/>'
        assert 'Content-Length: 4' in str(request)
        assert "\r\n\r\ntest" in str(request)

    def test_get_vars(self):
        environ = sample_environ(
            QUERY_STRING='blah=something&someget=test&arr[]=a&arr[]=b')
        request = Request.from_environ(environ)
        assert len(request.get['arr[]']) == 2
        assert request.get['blah'] == 'something'

    def test_empty_get_vars(self):
        request = Request.from_environ({})
        assert not request.get

    def test_headers(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        assert len(request.headers) == 1

    def test_server(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        assert request.server['PATH_INFO'] == '/'

    def test_cookies(self):
        environ = sample_environ(HTTP_COOKIE='test=something;')
        request = Request.from_environ(environ)
        assert request.cookies['test'].value == 'something'

    def test_is_method(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        assert request.is_method('get')

    def test_url(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        assert request.url.path == '/'

    def test_host(self):
        environ = sample_environ(HTTP_X_FORWARDED_FOR='10.11.12.13')
        request = Request.from_environ(environ)
        assert request.host() == '10.11.12.13'

    def test_is_xml_http_request(self):
        environ = sample_environ(HTTP_X_REQUESTED_WITH='XmlHttpRequest')
        request = Request.from_environ(environ)
        assert request.is_xml_http_request()

    def test_is_secure(self):
        environ = sample_environ(HTTPS='HTTPS')
        request = Request.from_environ(environ)
        assert request.is_secure()
        request = Request.from_environ({'PATH_INFO': '/', 'wsgi.url_scheme': 'https', 'HTTP_HOST': '127.0.0.1'})
        assert request.is_secure()

    def test_no_post(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        assert not request.post

    def test_post(self):
        data = 'test=test'
        environ = sample_environ(REQUEST_METHOD='POST', CONTENT_LENGTH=len(data))
        environ['wsgi.input'] = BufferedReader(BytesIO(data.encode('utf-8')))
        request = Request.from_environ(environ)
        assert request.post['test'] == 'test'

    def test_create_put_from_environ(self):
        data = 'HTTP_REQUEST_METHOD=PUT'
        environ = sample_environ(REQUEST_METHOD='POST', CONTENT_LENGTH=len(data))
        environ['wsgi.input'] = BufferedReader(BytesIO(data.encode('utf-8')))
        request = Request.from_environ(environ)
        assert request.post['HTTP_REQUEST_METHOD'] == 'PUT'
        assert not request.files
        assert request.is_method('PUT')

    def test_body(self):
        environ = sample_environ()
        request = Request.from_environ(environ)
        request.body = 'Test'
        assert request.raw_body == b'Test'
        assert request.body == 'Test'
        # environ = sample_environ()
        # environ['wsgi.input'] = b'Test'
        # request = Request.from_environ(environ)
        # assert request.body == b'Test'

    def test_json_body(self):
        json_str = '{"test": [1, 2, 3]}'
        environ = sample_environ(CONTENT_TYPE='application/json; charset=utf-8',
                                 CONTENT_LENGTH=len(json_str),
                                 REQUEST_METHOD='put')
        environ['wsgi.input'] = BufferedReader(
            BytesIO(json_str.encode('utf-8')))
        request = Request.from_environ(environ)
        json_output = json.loads(request.body)
        assert 'test' in json_output
        assert 'test' in request.json_body

    def test_session(self):
        environ = sample_environ(HTTP_COOKIE='watson.session=123456;')
        request = Request.from_environ(environ,
                                       session_class='watson.http.sessions.Memory')
        assert request.session.id == '123456'
        assert isinstance(request.session, sessions.Memory)

    def test_session_from_https_request(self):
        environ = sample_environ(HTTPS='HTTPS')
        request = Request.from_environ(environ,
                                       session_class='watson.http.sessions.Memory')
        assert request.is_secure()
        request.session['arbitrary'] = 'value'
        sessions.session_to_cookie(request, Response())
        cookie = request.cookies[sessions.COOKIE_KEY]
        assert cookie['httponly']
        assert cookie['secure']

    def test_session_cant_save(self):
        with raises(Exception):
            mixin = sessions.StorageMixin()
            mixin.save()

    def test_from_dicts(self):
        get = {'get1': 1, 'get2': 2}
        post = {'post1': 1, 'post2': 2}
        request = Request.from_dict(get=get, post=post)
        assert request.get['get1'] == '1'
        assert request.post['post2'] == '2'

    def test_session_load_iter(self):
        with raises(NotImplementedError):
            mixin = sessions.StorageMixin()
            for key, value in mixin:
                assert True


class TestResponse(object):

    def test_create(self):
        response = Response(200, body='This is the body', version='1.2')
        assert response.body == 'This is the body'
        assert response.status_line == '200 OK'
        assert response.version == '1.2'

    def test_output(self):
        response = Response(200, body='Something here')
        response.headers.add('Content-Type', 'text/html')
        string_output = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nSomething here"
        raw_output = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nSomething here'
        assert str(response) == string_output
        assert response.raw() == raw_output

    def test_encoding(self):
        response = Response(200)
        assert response.encoding == 'utf-8'

    def test_encode_body(self):
        response = Response(200, body='Test')
        assert response(start_response) == [b'Test']

    def test_set_headers(self):
        response = Response(200, body='test')
        response.headers = {'test': 'test'}
        assert response.headers.environ['test'] == 'test'

    def test_set_cookies(self):
        response = Response(200)
        assert not response.cookies

    def test_raw_body(self):
        response = Response(200)
        assert isinstance(response.raw_body, bytes)

    def test_start(self):
        response = Response()
        status_line, headers = response.start()
        assert status_line == '200 OK'
        assert headers == []

    def test_set_cookie(self):
        response = Response(200, body='Test')
        response.cookies.add('test', 'value')
        assert str(
            response) == "HTTP/1.1 200 OK\r\nSet-Cookie: test=value; Path=/\r\n\r\nTest"
