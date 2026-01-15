from django.db import models

class GeminiGenerationStats(models.Model):
    total_images = models.IntegerField(default=0)



