
from django.urls import path
from .views import (
    SignupView, SigninView, ChangePasswordView, ChangeUsernameView,
    PredictView, SimilarityView, PredictionHistoryView, SimilarityHistoryView,
    FeedbackView, UserStatisticsView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-username/', ChangeUsernameView.as_view(), name='change-username'),


    path('predict/', PredictView.as_view(), name='predict'),
    path('similarity/', SimilarityView.as_view(), name='similarity'),
    
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    
    path('history/predictions/', PredictionHistoryView.as_view(), name='prediction-history'),
    path('history/similarities/', SimilarityHistoryView.as_view(), name='similarity-history'),
    path('history/similarities/<int:history_id>/', SimilarityHistoryView.as_view(), name='similarity-history-delete'),
    
    path('user/statistics/', UserStatisticsView.as_view(), name='user-statistics'),

]
