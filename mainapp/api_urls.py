from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'camps', api_views.RescueCampViewSet)
router.register(r'persons', api_views.PersonViewSet)

urlpatterns = [
    path('camplist/', api_views.CampList.as_view(), name='api_camplist'),
    path('request-dashboard/district/', api_views.RequestDashboardDistrictAPI.as_view(), name='api_request_dashboard_district'),
    path('request-dashboard/location/', api_views.RequestDashboardLocationAPI.as_view(), name='api_request_dashboard_location'),
    path('request-dashboard/map/', api_views.RequestDashboardMapAPI.as_view(), name='api_request_dashboard_map'),
]

urlpatterns += router.urls
