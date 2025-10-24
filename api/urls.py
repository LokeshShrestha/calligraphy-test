
from django.urls import path
from .views import (
    SignupView, SigninView, ChangePasswordView, ChangeUsernameView,
    PredictView, SimilarityView, GradCAMView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-username/', ChangeUsernameView.as_view(), name='change-username'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('similarity/', SimilarityView.as_view(), name='similarity'),

    # Extra feature if you want to :) but boring thing 
    # path('gradcam/', GradCAMView.as_view(), name='gradcam'),
]
