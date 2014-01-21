# -*- coding: utf-8 -*-
from pytest import raises
from watson.http.sessions import StorageMixin


class TestStorageMixin(object):

    def test_create(self):
        session = StorageMixin(id=123, timeout=30, autosave=False)
        session['test'] = 'blah'
        assert session.timeout == 30
        assert session.autosave is False
        assert session.id == 123
        assert repr(
            session) == '<watson.http.sessions.abc.StorageMixin id:123>'
        assert session['test'] == 'blah'
        assert session.get('test') == 'blah'

    def test_cookie_params(self):
        session = StorageMixin()
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
        session = StorageMixin()
        assert session.data is None

    def test_missing_load_implementation(self):
        with raises(Exception):
            session = StorageMixin()
            session._load()

    def test_missing_save_implementation(self):
        with raises(Exception):
            session = StorageMixin()
            session._save()

    def test_missing_destroy_implementation(self):
        with raises(Exception):
            session = StorageMixin()
            session._destroy()

    def test_missing_exists_implementation(self):
        with raises(Exception):
            session = StorageMixin()
            session._exists()
