# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import six
from django.http import HttpResponse
from django.conf import settings
from django.urls import NoReverseMatch
from django.utils.translation import get_language_from_path
from constance import config


class BasicAuthMiddleware(object):

    def strip_language(self, path):
        # taken from aldryn-sso
        language_prefix = get_language_from_path(path)

        if not language_prefix:
            return path
        # strip the language prefix by getting the length of the language
        # then slice the path
        return "/" + "/".join(path.split("/")[len(language_prefix):])

    def is_white_list_url(self, request):
        """
        Returns true if the request path matches a configured
        list of "white listed" url paths. (c) aldryn-sso
        """
        path = request.path_info

        if settings.APPEND_SLASH and not path.endswith('/'):
            path += '/'

        path_without_prefix = self.strip_language(request.path)

        while_list = getattr(settings, 'ALDRYN_BASIC_AUTH_WHITE_LIST', [])

        for exclusive_path in while_list:
            # do not fail if we cannot process the url.
            try:
                exclusive_path = six.text_type(exclusive_path)
            except NoReverseMatch:
                continue
            exclusive_path_without_prefix = self.strip_language(exclusive_path)

            if exclusive_path == path:
                return True
            elif exclusive_path_without_prefix == path_without_prefix:
                return True
            elif re.match(exclusive_path, path):
                return True
            elif re.match(exclusive_path_without_prefix, path_without_prefix):
                return True
        return False


    def unauthed(self):
        response = HttpResponse(
            """<html><title>Auth required</title><body>
            <h1>Authorization Required</h1></body></html>""",
            content_type="text/html",
        )
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def process_request(self, request):
        # do not proceed if basic auth is not enabled
        if not config.ALDRYN_BASICAUTH_ACTIVE:
            return

        # white list aldryn-clint live sync
        if self.is_white_list_url(request):
            # skipping the authentication check
            return

        # check if even need to validate the credentials
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self.unauthed()
        authentication = request.META['HTTP_AUTHORIZATION']
        (authmeth, auth) = authentication.split(' ', 1)
        if 'basic' != authmeth.lower():
            return self.unauthed()

        # validate the username and passowrd
        auth = auth.strip().decode('base64')
        username, password = auth.split(':', 1)
        if (username == config.ALDRYN_BASICAUTH_USERNAME and
                password == config.ALDRYN_BASICAUTH_PASSWORD):
            return

        return self.unauthed()
