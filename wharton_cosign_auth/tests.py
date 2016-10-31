from django.conf import settings
settings.configure()

from unittest.mock import Mock, patch, PropertyMock, call
from django.core.exceptions import PermissionDenied
from remote_user import WhartonRemoteUserBackend
from permissions import wharton_permission
from utilities import  call_wisp_api
from views import penn_logout

import unittest


class TestPermissions(unittest.TestCase):

    """ Test Suite for permissions.py """


    @patch('permissions.call_wisp_api', return_value={})
    def test_wharton_permission__permission_bad_request(self, _call_wisp_api):
        """ Test Case - Bad request has occured """

        request = Mock()
        request.META.get.return_value = 'remote_user_name'
        options = ['STAFF', 'WCIT']
        decorated_func = wharton_permission(options)
        response = decorated_func(request)
        x = response(request)

        self.assertEqual(x.status_code, 400)
        self.assertTrue(str(x), 'No groups found for user remote_user_name')

    @patch('permissions.call_wisp_api', return_value={'groups': 'WCIT'})
    def test_wharton_permission__permission_allowed(self, _call_wisp_api):
        """ Test Case - User does have permission """

        request = Mock()
        request.META.get.return_value = 'remote_user_name'
        options = ['STAFF', 'WCIT']
        decorated_func = wharton_permission(options)
        response = decorated_func(request)
        x = response(request)

        self.assertTrue(request.called)
        self.assertTrue(_call_wisp_api.called)

    @patch('permissions.call_wisp_api', return_value={'groups': 'WCIT'})
    def test_wharton_permission__list_is_not_passed(self, _call_wisp_api):
        """ Test Case - argument is not a list """

        request = Mock()
        request.META.get.return_value = 'remote_user_name'
        options = 'WCIT'
        decorated_func = wharton_permission(options)
        response = decorated_func(request)
        x = response(request)

        self.assertTrue(request.called)
        self.assertTrue(_call_wisp_api.called)

    def test_wharton_permission__permission_denied_no_remote_user(self):
        """ Test Case - There is no remote user """

        request = Mock()
        request.META.get.return_value = None
        options = ['STAFF', 'WCIT']
        decorated_func = wharton_permission(options)
        response = decorated_func(request)

        with self.assertRaises(PermissionDenied) as cm:
            response(request)
        klass_name = cm.exception.__class__.__name__
        self.assertEqual(klass_name, 'PermissionDenied')

    @patch('permissions.call_wisp_api', return_value={'groups': 'FAIL'})
    def test_wharton_permission__permission_denied(self, _call_wisp_api):
        """ Test Case - User does not have permissions """

        request = Mock()
        request.META.get.return_value = 'remote_user_name'
        options = ['STAFF', 'WCIT']
        decorated_func = wharton_permission(options)
        response = decorated_func(request)

        with self.assertRaises(PermissionDenied) as cm:
            response(request)
        klass_name = cm.exception.__class__.__name__
        self.assertEqual(klass_name, 'PermissionDenied')


class TestViews(unittest.TestCase):

    """ Test Suite for views.py """


    @patch('views.redirect')
    @patch('views.logout')
    def test_penn_logout__User_is_logged_out(self, _logout, _redirect):
        """ Test Case - Cosign session will be removed and user will be logged out  """

        redirect_url = 'https://weblogin.pennkey.upenn.edu/logout'
        request = Mock()
        response = penn_logout(request)
        method_calls = response.method_calls[0]

        self.assertTrue(response.delete_cookie.called)
        response.delete_cookie.called_once_with(request.META.get())
        _logout.assert_called_once_with(request)
        _redirect.assert_called_once_with(redirect_url)


class TestRemoteBackend(unittest.TestCase):

    """ Test Suite for remote_user.py """


    def test_configure_user__User_Exists_And_Is_Apart_of_Wharton(self):
        """ Test Case - configure user will add user to django model """

        response = {'results': [{'first_name': 'Tester', 'last_name': 'Dude', 'email': 'x@skip.exchange.com' }]}
        user = Mock(username='dude')
        x = WhartonRemoteUserBackend()
        x.configure_user(user, response)

        self.assertFalse(user.is_staff)
        self.assertEqual(user.last_name, 'Dude')
        self.assertEqual(user.first_name, 'Tester')
        self.assertEqual(user.email, 'x@skip.com')
        self.assertTrue(user.save.called)

    def test_authenticate__no_remote_user(self):
        """ Test Case - no remote user is returned from cosign """

        x = WhartonRemoteUserBackend()
        user = x.authenticate(None)
        self.assertIsNone(user)

    @patch('remote_user.WhartonRemoteUserBackend.configure_user', return_value='created_user')
    @patch('remote_user.call_wisp_api', return_value={'results':
        [{'first_name': 'Tester', 'last_name': 'Dude', 'email': 'x@skip.exchange.com' }]})
    @patch('remote_user.get_user_model')
    def test_autenticate__create_unknown_user_who_is_wharton(self, _get_user_model, _call_wisp_api, _configure_user):
        """ Test Case - create unknown user who is apart of wharton  """

        _get_user_model()._default_manager.get_or_create.return_value = ('created_user', True)
        _get_user_model().USERNAME_FIELD = 'username'
        x = WhartonRemoteUserBackend()
        user = x.authenticate('tester')

        self.assertEqual(user, 'created_user')
        self.assertTrue(_configure_user.called)
        _get_user_model()._default_manager.get_or_create.assert_called_once_with(username='tester')
        _call_wisp_api.assert_called_once_with(
            'https://apps.wharton.upenn.edu/wisp/api/v1/adusers', {'username': 'tester'})

    @patch('remote_user.WhartonRemoteUserBackend.configure_user', return_value='created_user')
    @patch('remote_user.call_wisp_api', return_value={'results':
        [{'first_name': 'Tester', 'last_name': 'Dude', 'email': 'x@skip.exchange.com' }]})
    @patch('remote_user.get_user_model')
    def test_autenticate__user_already_created_who_is_wharton(self, _get_user_model, _call_wisp_api, _configure_user):
        """ Test Case - user already exists and they are a member of the school """

        _get_user_model()._default_manager.get_or_create.return_value = ('created_user', False)
        _get_user_model().USERNAME_FIELD = 'username'
        x = WhartonRemoteUserBackend()
        user = x.authenticate('tester')

        self.assertEqual(user, 'created_user')
        self.assertFalse(_configure_user.called)
        _get_user_model()._default_manager.get_or_create.assert_called_once_with(username='tester')
        _call_wisp_api.assert_called_once_with(
            'https://apps.wharton.upenn.edu/wisp/api/v1/adusers', {'username': 'tester'})

    @patch('remote_user.get_user_model')
    def test_autenticate__do_not_create_unknown_user(self, _get_user_model):
        """ Test Case - setting is set to no create an unknown user """

        _get_user_model()._default_manager.get_by_natural_key.return_value = 'tester'
        x = WhartonRemoteUserBackend()
        x.create_unknown_user = False
        user = x.authenticate('tester')

        self.assertEqual(user, 'tester')
        _get_user_model()._default_manager.get_by_natural_key.assert_called_once_with('tester')


class TestUtilities(unittest.TestCase):

    """ Test Suite for utilities.py """


    @patch('utilities.settings', new_callable=PropertyMock)
    @patch('utilities.requests', autospec=True)
    def test_call_wisp_api__response_with_no_args(self, _requests, _settings):
        """ Test Case - call to wisp api with None set for url and params """

        _settings.WISP_TOKEN = 'Test'
        _json = Mock()
        _json.json.return_value = 'A String'
        _requests.get.return_value = _json

        response = call_wisp_api()
        expected = call(None, headers={'Authorization': 'Token Test'}, params=None)

        self.assertTrue(_json.json.called)
        self.assertTrue(_requests.get.called)
        self.assertTrue(_requests.get.call_args == expected)

    @patch('utilities.settings', new_callable=PropertyMock)
    @patch('utilities.requests', autospec=True)
    def test_call_wisp_api__response_with_params(self, _requests, _settings):
        """ Test Case - call to wisp api with None set for url and params """

        _settings.WISP_TOKEN = 'Test'
        _json = Mock()
        _json.json.return_value = 'A String'
        _requests.get.return_value = _json

        response = call_wisp_api(url='https://testers.com', params={'user_id': 'tester'})
        expected = call('https://testers.com', headers={'Authorization': 'Token Test'}, params={'user_id': 'tester'})
        self.assertTrue(_json.json.called)
        self.assertTrue(_requests.get.called)
        self.assertTrue(_requests.get.call_args == expected)

    @patch('utilities.settings', new_callable=PropertyMock)
    @patch('utilities.requests')
    def test_class_wisp_api__wisp_api_is_down_exception_will_raise(self, _requests, _settings):
        """ Test Case - call wisp api but api is down an exception will raise """

        _settings.WISP_TOKEN = 'Test'
        _requests.get.side_effect = ValueError

        with self.assertRaises(Exception) as cm:
            response = call_wisp_api(url='https://testers.com', params={'user_id': 'tester'})

        self.assertEqual('WISP did not return valid JSON. This may be due to WISP API being down.', str(cm.exception))

if __name__ == '__main__':
    unittest.main()
