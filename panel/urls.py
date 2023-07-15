from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    path('sms/', Sms.as_view(), name='sms'),
    path('statistics/', Statistics.as_view(), name='statistics'),
    path('today-projects/', TodayProjectListAPI.as_view(), name='project-list'),
    path('not-tracked/', NotTrackedProjectListAPI.as_view(), name='project-list'),
    path('project/create/', ProjectCreateAPI.as_view(), name='project-create'),
    path('project/<int:projectId>/', ProjectRetrieveAPI.as_view(), name='project-retrieve'),
    path('project-update/', ProjectUpdateAPI.as_view(), name='project-update'),
    path('search/', ProjectSearch.as_view(), name='search_project'),
    path('authontication/', Authontication.as_view(), name='authontication'),

]
