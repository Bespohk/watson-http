# -*- coding: utf-8 -*-
from watson.http import sessions, messages


class TestToCookie(object):

    def test_session_to_cookie(self):
        request = messages.Request(environ={})
        response = messages.Response()
        assert not sessions.session_to_cookie(request, response)

    def test_not_modified(self):
        request = messages.Request(
            environ={
                'watson.session.class': 'watson.http.sessions.Memory',
                'watson.session.options': {}
            }
        )
        response = messages.Response()
        assert not sessions.session_to_cookie(request, response)
