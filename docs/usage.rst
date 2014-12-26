Usage
=====

.. tip::
    watson-http also works particularly well watson-form

Creating a Request
------------------

Requests can be instantiated directly from the class, or be created based on environ variables.

.. note::
    Instantiating from the class itself will not populate the Request object with the relevant data from the current server request.

From the environ
^^^^^^^^^^^^^^^^

.. code-block:: python

    from watson.http import messages

    def application(environ, start_response):
        request = messages.Request.from_environ(environ)
        print(request.method)

.. tip::
    watson-http also enables you to deal with other HTTP verbs that may not be accessible by a regular browser. Simply posting HTTP_REQUEST_METHOD and setting it to a valid HTTP verb will convert that request to the specific verb.

From watson.http.messages.Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from watson.http import messages

    def application(environ, start_response):
        request = messages.Request('get', get={'get_var': 'somevalue'})
        print(request.method) # get
        print(request.get('get_var')) # somevalue


Dealing with Sessions
^^^^^^^^^^^^^^^^^^^^^

.. tip::
    You can access many things from the Request, and most work similar to a regular ``dict``. These include: headers, server, cookies, get, post, files, url and sessions.

Earlier, we created a request with the `Request.from_environ` method. By default, all requests will be created with the `watson.http.sessions.File` backend for managing sessions. This however can be changed to a different backend by adding the `session_class` argument to the `from_environ` call. `session_class` must inherit from `watson.http.sessions.abc.StorageMixin`. If the class requires any additional configuration (the `http.sessions.file.Storage` class allows you to set the directory sessions are stored in), then you can also pass a dict of options via `session_options`.

.. code-block:: python

    from watson.http import messages

    def application(environ, start_response):
        request = messages.Request.from_environ(environ, session_class=YOUR_SESSION_CLASS, session_options={})

Creating a Response
-------------------

While you can simply return a list from a WSGI application, you still need to also call the start_response method. While this maybe sufficient for smaller applications, anything larger requires a more robust approach. A standard WSGI callable may look like below:

.. code-block:: python

    def application(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello World']

With watson-http this code turns into...

.. code-block:: python

    from watson.http import messages

    def application(environ, start_response):
        response = messages.Response(200, body='Hello World!')
        return response(start_response)

The response body by default is interpreted as utf-8, however this can be modified by accessing the response headers.

.. code-block:: python

    response = messages.Response(200)
    response.headers.add('Content-Type', 'text/html; charset=ENCODING')


Putting it all together
-----------------------

An example app that outputs get variables may look like:

.. code-block:: python

    from watson.http import messages

    def application(environ, start_response):
        request = messages.create_request_from_environ(environ)

        response = messages.Response(200, body='Hello {name}!'.format(request.get('name', 'World')))
        return response(start_response)

When you navigate to ``/`` you will be presented with 'Hello World!', however if you navigate to ``/?name=Simon``, you will be presented with 'Hello Simon!'
