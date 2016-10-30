from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import get_user_model

from wharton_cosign_auth.utilities import call_wisp_api


class WhartonRemoteUserBackend(RemoteUserBackend):

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed. Moving here for future proof of apps running
        on django >= 1.10
        """

        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def authenticate(self, remote_user):
        """
        Ask django to perform its normal authenticate and checking the wisp
        API that the user is a Wharton user. Otherwise return None and not
        create them in the set user model
        """

        if not remote_user:
            return
        user = None

        UserModel = get_user_model()

        if self.create_unknown_user:
            response = call_wisp_api(
                'https://apps.wharton.upenn.edu/wisp/api/v1/adusers', {'username': remote_user})
            if response['results']:
                user, created = UserModel._default_manager.get_or_create(**{
                    UserModel.USERNAME_FIELD: remote_user
                })
                if created:
                    user = self.configure_user(user, response)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(remote_user)
            except UserModel.DoesNotExist:
                pass

        return user if self.user_can_authenticate(user) else None

    def configure_user(self, user, response):
        """
        Set base attributed for newly created user based on ADUSER from
        the Wisp API
        """

        results = response['results'][0]
        user.first_name = results['first_name']
        user.last_name = results['last_name']
        user.email = results['email'].replace('exchange.', '')
        user.is_staff = False
        user.save()

        return user
