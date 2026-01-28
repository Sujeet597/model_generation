from django.db import models
from django.contrib.auth.models import User

class ImageGenerationSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="generation_summaries"
    )

    total_images = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} | {self.total_images} images | ${self.total_cost}"
class ImageGenerationHistory(models.Model):
    summary = models.ForeignKey(
        ImageGenerationSummary,
        on_delete=models.CASCADE,
        related_name="history"
    )

    timestamp = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    bodytype = models.CharField(max_length=50)

    uploaded_images = models.JSONField()
    generated_images = models.JSONField()

    generated_count = models.PositiveIntegerField()

    cost_per_image = models.DecimalField(max_digits=6, decimal_places=2)
    total_images = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} | {self.generated_count} images"
