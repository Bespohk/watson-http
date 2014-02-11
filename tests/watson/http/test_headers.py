# -*- coding: utf-8 -*-
from watson.http.headers import HeaderCollection, ServerCollection


class TestHeaders(object):

    def test_add_header(self):
        d = HeaderCollection()
        d.add('CONTENT_TYPE', 'text/html')
        d.add('HOST', '127.0.0.1')
        assert d.get('Content-Type') == 'text/html'
        assert d.get('CONTENT_TYPE') == 'text/html'

    def test_add_option(self):
        d = HeaderCollection()
        d.add('CONTENT_TYPE', 'text/html', charset='utf-8')
        assert d.get('Content-Type') == 'text/html; charset=utf-8'
        assert d.get_option('Content-Type', 'charset') == 'utf-8'
        assert d.get_option('Content-Type', 'random', 'test') == 'test'

    def test_add_overwrite_header(self):
        d = HeaderCollection()
        d.add('CONTENT_TYPE', 'text/html', charset='utf-8')
        assert len(d) == 1
        d.add('CONTENT_TYPE', 'text/plain', charset='utf-8', replace=True)
        assert len(d) == 1

    def test_delete_header(self):
        d = HeaderCollection()
        d['Content-Type'] = 'test'
        d['Test'] = 'test'
        assert d.get('Content-Type')
        del d['Content-Type']
        assert not d.get('Content-Type')

    def test_tuple_pairs(self):
        d = HeaderCollection.from_environ({'CONTENT_TYPE': 'text/html'})
        assert d() == [('Content-Type', 'text/html')]

    def test_tuple_pairs_multiple(self):
        d = HeaderCollection()
        d.add('Content-Type', 'text/html')
        d.add('Content-Type', 'text/xml')
        assert ('Content-Type', 'text/html') in d()
        assert ('Content-Type', 'text/xml') in d()
