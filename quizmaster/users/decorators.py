
from django.utils.translation import gettext_lazy as _
from functools import wraps
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
from django.contrib import messages
from .models import User

DEFAULT_MESSAGE = _("This page requires authentication. ")

ADMIN_USER_WEIGHT = [User.STAFF, User.SUPER, ]
USER_WEIGHT = [User.ANONYMOUS, User.GAMER, User.TESTER, ]


def user_passes_test(test_func, login_url=settings.LOGIN_URL, redirect_field_name=REDIRECT_FIELD_NAME, message=DEFAULT_MESSAGE):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            messages.error(request, message)
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=DEFAULT_MESSAGE):

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm, login_url=settings.LOGIN_URL, raise_exception=False, message=DEFAULT_MESSAGE):

    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url, message=message)


def gamer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role >= User.GAMER,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Gamer is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def anonymous_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role >= User.ANONYMOUS,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Anonymous is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def contributor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role >= User.CONTRIBUTOR,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Contributor is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role in ADMIN_USER_WEIGHT,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Admin is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Only Staff is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=settings.LOGIN_URL, message=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        message=message or _("Only Superuser is required"),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


