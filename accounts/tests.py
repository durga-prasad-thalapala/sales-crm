
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from accounts.models import User
from accounts.permissions import (
    IsAdmin,
    IsSalesManagerOrAdmin,
    IsSalespersonOrAbove,
)


class RolePermissionTests(SimpleTestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin = User(
            username="admin_test",
            role=User.Role.ADMIN,
        )
        self.manager = User(
            username="manager_test",
            role=User.Role.SALES_MANAGER,
        )
        self.salesperson = User(
            username="salesperson_test",
            role=User.Role.SALESPERSON,
        )

        self.request = self.factory.get("/")

    def check_permission(self, permission_class, user):
        self.request.user = user
        permission = permission_class()
        return permission.has_permission(self.request, view=None)

    def test_only_admin_passes_admin_permission(self):
        self.assertTrue(
            self.check_permission(IsAdmin, self.admin)
        )
        self.assertFalse(
            self.check_permission(IsAdmin, self.manager)
        )
        self.assertFalse(
            self.check_permission(IsAdmin, self.salesperson)
        )

    def test_admin_and_manager_pass_manager_permission(self):
        self.assertTrue(
            self.check_permission(
                IsSalesManagerOrAdmin, self.admin
            )
        )
        self.assertTrue(
            self.check_permission(
                IsSalesManagerOrAdmin, self.manager
            )
        )
        self.assertFalse(
            self.check_permission(
                IsSalesManagerOrAdmin, self.salesperson
            )
        )

    def test_all_roles_pass_salesperson_or_above_permission(self):
        for user in (
            self.admin,
            self.manager,
            self.salesperson,
        ):
            with self.subTest(role=user.role):
                self.assertTrue(
                    self.check_permission(
                        IsSalespersonOrAbove, user
                    )
                )

    def test_anonymous_user_is_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        self.request.user = AnonymousUser()

        for permission_class in (
            IsAdmin,
            IsSalesManagerOrAdmin,
            IsSalespersonOrAbove,
        ):
            with self.subTest(
                permission=permission_class.__name__
            ):
                self.assertFalse(
                    permission_class().has_permission(
                        self.request, view=None
                    )
                )
