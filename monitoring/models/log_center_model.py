from django.db import models


class LogCenterModel(models.Model):
    class Meta:
        managed = False
        app_label = "monitoring"
        verbose_name = "Log Center"
        verbose_name_plural = "Log Center"

    def __str__(self):
        return "Log Center"
