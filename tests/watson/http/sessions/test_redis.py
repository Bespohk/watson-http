# -*- coding: utf-8 -*-
from unittest.mock import Mock, create_autospec
from pytest import raises
from watson.http import sessions


class TestRedisStorage(object):

    def setup(self):
        self.mock_redis = Mock()

    def test_create(self):
        session = sessions.Redis(
            id=123,
            timeout=30,
            autosave=False,
            config={
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'encoding': 'utf-8',
                'serializer_class': 'watson.http.sessions.serializers.Json'
            })
        assert session.autosave is False
        assert session.timeout == 30
        assert session.id == 123

    def test_open_connection(self):
        with raises(ImportError):
            session = sessions.Redis()
            session.open()

    def test_cookie_params(self):
        session = sessions.Redis()
        params = {
            'expires': 0,
            'path': '/',
            'domain': None,
            'secure': False,
            'httponly': True,
            'comment': 'Watson session id'
        }
        session.cookie_params = params
        assert session.cookie_params == params

    def test_data(self):
        session = sessions.Redis()
        assert session.data is None

    def test_save_data(self):
        session = sessions.Redis()
        sessions.Redis.client = self.mock_redis
        sessions.Redis.client.get.return_value = b'{"test": [1, 2, 3]}'
        session['test'] = [1, 2, 3]
        session.load()
        assert session['test'] == [1, 2, 3]

    def test_load(self):
        session = sessions.Redis()
        sessions.Redis.client = self.mock_redis
        sessions.Redis.client.get.return_value = {}
        session.load()
        assert not session.data

    def test_exists(self):
        session = sessions.Redis()
        sessions.Redis.client = self.mock_redis
        sessions.Redis.client.get.return_value = None
        exists = create_autospec(session.exists, return_value=None)
        assert not exists()

    def test_close(self):
        session = sessions.Redis()
        sessions.Redis.client = self.mock_redis
        assert session.close()

    def test_destroy(self):
        session = sessions.Redis()
        sessions.Redis.client = self.mock_redis
        session['test'] = 'blah'
        sessions.Redis.client.get.return_value = 'blah'
        assert session['test'] == 'blah'
        session.destroy()
        exists = create_autospec(session.exists, return_value=None)
        assert not exists()
