from django.contrib import admin
from .models import PredictionHistory, SimilarityHistory


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'predicted_class', 'confidence', 'created_at']
    list_filter = ['predicted_class', 'created_at', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Prediction Details', {
            'fields': ('image', 'predicted_class', 'confidence')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation from admin (only through API)
        return False


@admin.register(SimilarityHistory)
class SimilarityHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'target_class', 'similarity_score', 'is_same_character', 'created_at']
    list_filter = ['target_class', 'is_same_character', 'created_at', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'prediction')
        }),
        ('Comparison Details', {
            'fields': ('user_image', 'target_class', 'comparison_image')
        }),
        ('Results', {
            'fields': ('similarity_score', 'distance', 'is_same_character')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation from admin (only through API)
        return False
