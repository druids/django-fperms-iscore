from germanium.test_cases.rest import RESTTestCase
from germanium.annotations import login
from germanium.tools import assert_in
from germanium.tools.http import assert_http_unauthorized, assert_http_forbidden, assert_http_not_found

from .test_case import HelperTestCase, AsSuperuserTestCase


from fperms_iscore.models import IsCorePerm


class HttpExceptionsTestCase(AsSuperuserTestCase, HelperTestCase, RESTTestCase):
    ISSUE_API_URL = '/api/issue/'
    USER_API_URL = '/api/user/'
    ACCEPT_TYPES = ('application/json', 'text/xml', 'text/csv',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def set_up(self):
        IsCorePerm.objects.create_from_str(
            perms=[
                'core.issue_tracker.IssueIsCore.read',
                'core.issue_tracker.UserIsCore.read',
            ]
        )

    def test_401_exception(self):
        for accept_type in self.ACCEPT_TYPES:
            resp = self.get(self.ISSUE_API_URL, headers={'HTTP_ACCEPT': accept_type})
            assert_in(accept_type, resp['Content-Type'])
            assert_http_unauthorized(resp)

    @login(is_superuser=False)
    def test_403_exception(self):
        user = self.get_user_obj()
        for accept_type in self.ACCEPT_TYPES:
            resp = self.get('%s%s/' % (self.USER_API_URL, user.pk), headers={'HTTP_ACCEPT': accept_type})
            assert_in(accept_type, resp['Content-Type'])
            assert_http_forbidden(resp)

    @login(is_superuser=False)
    def test_404_exception(self):
        self.logged_user.user.perms.add('core.issue_tracker.IssueIsCore.read')
        for accept_type in self.ACCEPT_TYPES:
            resp = self.get('%s%s/' % (self.ISSUE_API_URL, 5), headers={'HTTP_ACCEPT': accept_type})
            assert_in(accept_type, resp['Content-Type'])
            assert_http_not_found(resp)

    @login(is_superuser=True)
    def test_403_csrf_exception(self):
        self.c = self.client_class(enforce_csrf_checks=True)
        for accept_type in self.ACCEPT_TYPES:
            resp = self.post(self.ISSUE_API_URL, {}, headers={'HTTP_ACCEPT': accept_type,
                                                              'CONTENT_TYPE': 'application/json'})
            assert_in(accept_type, resp['Content-Type'])
            assert_http_forbidden(resp)
