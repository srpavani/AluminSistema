from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, CompanyViewSet, SurfaceFinishViewSet, ProductViewSet, OrderViewSet
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

router = DefaultRouter()
router.register(r'agents', AgentViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'surfacefinishes', SurfaceFinishViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
