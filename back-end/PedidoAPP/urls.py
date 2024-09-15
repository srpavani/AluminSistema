from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AgentViewSet, CompanyViewSet, SurfaceFinishViewSet, ProductViewSet, OrderViewSet, OrderUploadViewSet
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .planilhaViewSet import ExcelUploadViewSet

router = DefaultRouter()
router.register(r'agents', AgentViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'surfacefinishes', SurfaceFinishViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'upload-orders', OrderUploadViewSet, basename='order-upload')
router.register(r'order-planilhas', ExcelUploadViewSet, basename='order-planilha')



from .views import create_order, load_factories, load_products, order_success
from .viewsorder import create_orderonly, load_factoriesonly, load_productsonly,add_to_orderonly,order_detail

urlpatterns = [
    path('', include(router.urls)),
    path('create-order/', create_order, name='create_order'),
    path('ajax/load-factories/', load_factories, name='load_factories'),
    path('ajax/load-products/', load_products, name='load_products'),# AJAX para carregar produtos
    path('order-success/', order_success, name='order_success'),
    path('create-orderonly/', create_orderonly, name='create_order'),  # Página principal para criar o pedido
    path('load-factoriesonly/', load_factoriesonly, name='load_factoriesonly'),  # AJAX para carregar fábricas
    path('load-productsonly/', load_productsonly, name='load_productsonly'),  # AJAX para carregar produtos
    path('add-to-orderonly/', add_to_orderonly, name='add_to_orderonly'),  # AJAX para adicionar produto ao pedido
    path('order-successonly/', order_success, name='order_successonly'),
    path('order/<int:order_id>/', order_detail, name='order_detail')# Página de sucesso do pedido
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

