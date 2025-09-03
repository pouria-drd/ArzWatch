from django.db import models


class SystemInfoModel(models.Model):
    class Meta:
        managed = False
        app_label = "monitoring"
        verbose_name = "System Info"
        verbose_name_plural = "System Info"

    def __str__(self):
        return "System Info"
