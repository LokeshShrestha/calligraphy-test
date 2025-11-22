from django.db import models
from django.contrib.auth.models import User


class PredictionHistory(models.Model):
    """Stores prediction history for each user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    image = models.ImageField(upload_to='predictions/%Y/%m/%d/')
    predicted_class = models.IntegerField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Prediction Histories'
    
    def __str__(self):
        return f"{self.user.username} - Class {self.predicted_class} ({self.created_at})"


class SimilarityHistory(models.Model):
    """Stores similarity comparison history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='similarities')
    prediction = models.ForeignKey(PredictionHistory, on_delete=models.CASCADE, null=True, blank=True)
    user_image = models.ImageField(upload_to='similarity/%Y/%m/%d/')
    reference_image = models.ImageField(upload_to='references/%Y/%m/%d/', null=True, blank=True)
    target_class = models.IntegerField()
    similarity_score = models.FloatField()
    distance = models.FloatField()
    is_same_character = models.BooleanField()
    blended_overlay = models.ImageField(upload_to='blended/%Y/%m/%d/', null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Similarity Histories'
    
    def __str__(self):
        return f"{self.user.username} - Class {self.target_class} ({self.similarity_score:.2f}%)"
