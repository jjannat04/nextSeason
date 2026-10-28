from django.urls import path
from next_season.api.views import health,rotation_plan,environment_profile,water_commons_options,water_commons_analyze

urlpatterns=[path("api/health",health),path("api/rotation-plan",rotation_plan),path("api/environment-profile",environment_profile),path("api/water-commons/options",water_commons_options),path("api/water-commons/analyze",water_commons_analyze)]
