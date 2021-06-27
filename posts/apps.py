from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "posts"

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import posts.signals  # noqa
