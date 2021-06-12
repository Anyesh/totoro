"""
GoogleCloudStorage extension classes for MEDIA and STATIC uploads
"""
# import datetime
# from urllib.parse import urljoin

# import google.auth
# import google.auth.compute_engine

# import google.auth.transport.requests
from django.conf import settings

# from django.core.cache import cache
from django.utils.deconstruct import deconstructible

# We'll take it on the chin if this moves
from google.cloud.storage.blob import _quote
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import clean_name, setting


@deconstructible
class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """
    Google file storage class which gives a media file path from MEDIA_URL not google generated one.
    """

    bucket_name = setting("GS_MEDIA_BUCKET_NAME")
    CACHE_KEY = "GoogleCloudStorageAccessToken.signing_extras"

    def url(self, name):
        """
        Gives correct MEDIA_URL and not google generated url.
        """
        name = self._normalize_name(clean_name(name))
        blob = self.bucket.blob(name)
        no_signed_url = self.default_acl == "publicRead" or not self.querystring_auth

        if not self.custom_endpoint and no_signed_url:
            return blob.public_url
        elif no_signed_url:
            return "{storage_base_url}/{quoted_name}".format(
                storage_base_url=self.custom_endpoint,
                quoted_name=_quote(name, safe=b"/~"),
            )
        elif not self.custom_endpoint:
            return blob.generate_signed_url(self.expiration, **self.signed_url_extra())
        else:
            return blob.generate_signed_url(
                expiration=self.expiration,
                api_access_endpoint=self.custom_endpoint,
                **self.signed_url_extra()
            )
        # return urljoin(settings.MEDIA_URL, name)

    def signed_url_extra(self):
        # value = cache.get(self.CACHE_KEY)
        # if value is not None:
        #     expiry, extra = value
        #     if expiry > datetime.datetime.utcnow():
        #         return extra

        credentials = settings.GS_CREDENTIALS
        # cache.set(self.CACHE_KEY, (credentials.expiry, extra))
        return {
            "service_account_email": credentials.service_account_email,
            "access_token": credentials.token,
            "credentials": credentials,
        }


class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """
    Google file storage class which gives a media file path from MEDIA_URL not google generated one.
    """

    bucket_name = setting("GS_STATIC_BUCKET_NAME")

    def url(self, name):
        """
        Gives correct STATIC_URL and not google generated url.
        """
        name = self._normalize_name(clean_name(name))
        blob = self.bucket.blob(name)
        no_signed_url = self.default_acl == "publicRead" or not self.querystring_auth

        if not self.custom_endpoint and no_signed_url:
            return blob.public_url
        elif no_signed_url:
            return "{storage_base_url}/{quoted_name}".format(
                storage_base_url=self.custom_endpoint,
                quoted_name=_quote(name, safe=b"/~"),
            )
        elif not self.custom_endpoint:
            return blob.generate_signed_url(self.expiration, **self.signed_url_extra())
        else:
            return blob.generate_signed_url(
                expiration=self.expiration,
                api_access_endpoint=self.custom_endpoint,
                **self.signed_url_extra()
            )
        # return urljoin(settings.MEDIA_URL, name)

    def signed_url_extra(self):
        # value = cache.get(self.CACHE_KEY)
        # if value is not None:
        #     expiry, extra = value
        #     if expiry > datetime.datetime.utcnow():
        #         return extra

        credentials = settings.GS_CREDENTIALS
        # cache.set(self.CACHE_KEY, (credentials.expiry, extra))
        return {
            "service_account_email": credentials.service_account_email,
            "access_token": credentials.token,
            "credentials": credentials,
        }
