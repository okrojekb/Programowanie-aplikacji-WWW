from django.apps import AppConfig


class BookSiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "book_site"

    def ready(self):
        pass
