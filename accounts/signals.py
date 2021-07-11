import hashlib
from typing import List

from allauth.account.signals import user_signed_up
from django.db.models import Model
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
    ManyToOneRel,
    OneToOneRel,
)
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from totoro.utils import get_client_ip

from .models import Profile, User


@receiver(post_save, sender=User)
def create_or_update_superuser_profile(sender, instance, created, **kwargs):
    if instance.is_superuser:

        Profile.objects.update_or_create(user=instance)
        instance.profile.save()


@receiver(user_signed_up)
def create_or_update_user_profile(sociallogin, user, **kwargs):
    preferred_avatar_size_pixels = 256

    picture_url = "http://www.gravatar.com/avatar/{0}?s={1}".format(
        hashlib.md5(user.email.encode("UTF-8")).hexdigest(),
        preferred_avatar_size_pixels,
    )
    f_name = None
    l_name = None
    work = None
    tagline = None
    hometown = None

    if sociallogin and sociallogin.account.provider == "google":
        f_name = sociallogin.account.extra_data.get("given_name")
        l_name = sociallogin.account.extra_data.get("family_name")

        # verified = sociallogin.account.extra_data['verified_email']
        picture_url = sociallogin.account.extra_data.get("picture")

    if sociallogin and sociallogin.account.provider == "github":
        name = sociallogin.account.extra_data.get("name")
        if name:
            f_name, l_name = name.split(" ")
        tagline = sociallogin.account.extra_data.get("bio")
        work = sociallogin.account.extra_data.get("company")
        hometown = sociallogin.account.extra_data.get("location")

        picture_url = sociallogin.account.extra_data.get("avatar_url")

    if sociallogin and sociallogin.account.provider == "discord":
        f_name = sociallogin.account.extra_data.get("given_name")
        l_name = sociallogin.account.extra_data.get("family_name")
        picture_url = (
            "https://cdn.discordapp.com/avatars"
            f"/{sociallogin.account.extra_data.get('id')}"
            f"/{sociallogin.account.extra_data.get('avatar')}.png"
        )

    ip = get_client_ip()
    Profile.objects.create(
        user=user,
        current_ip=ip,
        avatar=picture_url,
        first_name=f_name,
        last_name=l_name,
        work=work,
        hometown=hometown,
        tagline=tagline,
    )
    user.profile.save()


@receiver(pre_delete, sender=User)
def change_deleted_user_data(sender, instance, **kwargs):
    delete_user_and_replace_with_substitute(instance)


def get_all_relations(model: Model) -> List[ForeignObjectRel]:
    """
    Return all Many to One Relation to point to the given model
    """
    result: List[ForeignObjectRel] = []
    for field in model._meta.get_fields(include_hidden=True):

        if isinstance(field, ManyToOneRel) and not isinstance(field, OneToOneRel):
            result.append(field)
    return result


def print_updated(name, number):
    """
    Simple Debug function
    """
    if number > 0:
        print(f"Update {number} {name}")


def delete_user_and_replace_with_substitute(user_to_delete: User):
    """
    Replace all relations to user with fake replacement user
    :param user_to_delete: the user to delete
    """
    DELETED_USER = "deleted_user"

    if user_to_delete.username == DELETED_USER:
        return
    replacement_user = User.objects.get(
        username="deleted_user"
    )  # define your replacement user

    for field in get_all_relations(user_to_delete):
        # field: ManyToOneRel
        target_model = field.related_model
        target_field: str = field.remote_field.name
        updated: int = target_model.objects.filter(
            **{target_field: user_to_delete}
        ).update(**{target_field: replacement_user.user_id})
        print_updated(target_model._meta.verbose_name, updated)
    # user_to_delete.delete()
