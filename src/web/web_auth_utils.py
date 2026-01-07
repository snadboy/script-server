import logging
from urllib.parse import urlencode

import tornado.concurrent
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket

from auth.auth_base import AuthRejectedError, AuthFailureError
from utils import tornado_utils
from utils.tornado_utils import redirect_relative
from web.web_utils import identify_user

LOGGER = logging.getLogger('web_server')

webpack_prefixed_extensions = ['.css', '.js.map', '.js', '.jpg', '.woff', '.woff2', '.png']


def check_authorization_sync(func):
    wrapper = check_authorization(func)

    def sync_wrapper(self, *args, **kwargs):
        return tornado_utils.run_sync(wrapper(self, *args, **kwargs))

    return sync_wrapper


# In case of REST requests we don't redirect explicitly, but reply with Unauthorized code.
# Client application should provide redirection in the way it likes
def check_authorization(func, ):
    async def wrapper(self, *args, **kwargs):
        auth = self.application.auth
        authorizer = self.application.authorizer

        login_url = self.get_login_url()
        request_path = self.request.path

        login_resource = is_allowed_during_login(request_path, login_url, self)
        if login_resource:
            return func(self, *args, **kwargs)

        try:
            authenticated = await auth.is_authenticated(self)
        except (AuthRejectedError, AuthFailureError) as e:
            message = 'On-fly auth rejected'
            LOGGER.warning(message + ': ' + str(e))
            code = 401
            if isinstance(self, tornado.websocket.WebSocketHandler):
                self.close(code=code, reason=message)
                return
            else:
                raise tornado.web.HTTPError(code, message)

        access_allowed = authenticated and authorizer.is_allowed_in_app(identify_user(self))

        if authenticated and (not access_allowed):
            user = identify_user(self)
            LOGGER.warning('User ' + user + ' is not allowed')
            code = 403
            message = 'Access denied. Please contact system administrator'
            if isinstance(self, tornado.websocket.WebSocketHandler):
                self.close(code=code, reason=message)
                return
            else:
                if isinstance(self, tornado.web.StaticFileHandler) and request_path.lower().endswith('.html'):
                    login_url += "?" + urlencode(dict(next=request_path, redirectReason='prohibited'))
                    redirect_relative(login_url, self)
                    return
                else:
                    raise tornado.web.HTTPError(code, message)

        if authenticated and access_allowed:
            return func(self, *args, **kwargs)

        # User is not authenticated
        message = 'Not authenticated'
        code = 401
        LOGGER.warning('%s %s %s: user is not authenticated' % (code, self.request.method, request_path))

        if isinstance(self, tornado.websocket.WebSocketHandler):
            self.close(code=code, reason=message)
            return

        # For HTML files (except login.html), return 401 to enforce server-side auth
        # This prevents unauthenticated users from seeing any HTML content
        if isinstance(self, tornado.web.StaticFileHandler) and request_path.lower().endswith('.html'):
            raise tornado.web.HTTPError(code, message)

        if not isinstance(self, tornado.web.StaticFileHandler):
            raise tornado.web.HTTPError(code, message)

        # For non-HTML static files (JS, CSS, images), redirect to login
        login_url += "?" + urlencode(dict(next=request_path))
        redirect_relative(login_url, self)

        return

    return wrapper


def is_allowed_during_login(request_path, login_url, request_handler):
    if request_handler.request.method != 'GET':
        return False

    if request_path == '/favicon.ico':
        return True

    if request_path == login_url:
        return True

    # Allow theme files
    if request_path.startswith('/theme/'):
        return True

    # Allow font files (needed for login page)
    if request_path.startswith('/fonts/'):
        return True

    # Allow Vite-built assets (login-*.js, login-*.css, etc.)
    # These have hashed filenames like /assets/login-DCU7EOYu.js
    if request_path.startswith('/assets/'):
        filename = request_path.split('/')[-1]
        # Allow login-related assets and shared dependencies
        if filename.startswith('login-') or filename.startswith('main-') or filename.startswith('index-'):
            return True
        # Allow CSS files needed for login
        if filename.endswith('.css'):
            return True

    # Legacy Vue 2 login resources (for backwards compatibility)
    request_path_normalized = remove_webpack_suffixes(request_path)
    login_resources = ['/js/login.js',
                       '/js/login.js.map',
                       '/js/chunk-login-vendors.js',
                       '/js/chunk-login-vendors.js.map',
                       '/css/login.css',
                       '/css/chunk-login-vendors.css',
                       '/img/titleBackground_login.jpg',
                       '/img/gitlab-icon-rgb.png']

    return request_path_normalized in login_resources


def remove_webpack_suffixes(request_path):
    if request_path.endswith('.js.map'):
        extension_start = len(request_path) - 7
    else:
        extension_start = request_path.rfind('.')

    extension = request_path[extension_start:]

    if extension not in webpack_prefixed_extensions:
        return request_path

    if extension_start < 0:
        return request_path

    prefix_start = request_path.rfind('.', 0, extension_start)
    if prefix_start < 0:
        return request_path

    return request_path[:prefix_start] + extension
