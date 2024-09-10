from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Agent(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=255)
    n_convenio = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    cnpj = models.CharField(max_length=18, unique=True)
    ie = models.CharField(max_length=20, unique=True)
    factory = models.CharField(max_length=255)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='companies')

    def __str__(self):
        return self.name

class SurfaceFinish(models.Model):
    MILL_FINISH = 'Mill Finish'
    SILVER_ANODIZED = 'Silver Anodized (FAYP01)'
    WHITE_POWDER_COAT = 'White Powder Coat'
    BRONZE_ANODIZED = 'Bronze Anodized (FAYP03)'
    BLACK_ANODIZED = 'Black Anodized (FAYP06)'
    ELECT_CHAMPAGNE = 'Elect. Champagne (FAYH02)'
    WOOD_FINISH_FA2134 = 'Wood Finish (FA2134-1)'
    WOOD_FINISH_LIGHT = 'Wood Finish (Light)'
    RUST_FINISH = 'Rust Finish'

    SURFACE_TYPES = [
        (MILL_FINISH, 'Mill Finish'),
        (SILVER_ANODIZED, 'Silver Anodized (FAYP01)'),
        (WHITE_POWDER_COAT, 'White Powder Coat'),
        (BRONZE_ANODIZED, 'Bronze Anodized (FAYP03)'),
        (BLACK_ANODIZED, 'Black Anodized (FAYP06)'),
        (ELECT_CHAMPAGNE, 'Elect. Champagne (FAYH02)'),
        (WOOD_FINISH_FA2134, 'Wood Finish (FA2134-1)'),
        (WOOD_FINISH_LIGHT, 'Wood Finish (Light)'),
        (RUST_FINISH, 'Rust Finish'),
    ]

    type = models.CharField(max_length=50, choices=SURFACE_TYPES)
    

    def __str__(self):
        return self.type

class Product(models.Model):
    alumifont_code = models.CharField(max_length=50, unique=True)
    factory_code = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    length_mm = models.DecimalField(max_digits=10, decimal_places=2)
    temper_alloy = models.CharField(max_length=50)
    weight_m_kg = models.DecimalField(max_digits=10, decimal_places=3)
    surface_finish = models.ForeignKey(SurfaceFinish, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)

    def __str__(self):
        return self.alumifont_code

from math import ceil

class Order(models.Model):
    request_title = models.CharField(max_length=255)
    n_containers = models.PositiveIntegerField(default=0, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    percentage_under250 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)

    def calculate_percentage_under_250(self):
        products_under_250 = self.order_products.filter(product__weight_m_kg__lt=0.250)
        total_weight_under_250 = sum(order_product.product.weight_m_kg * order_product.quantity for order_product in products_under_250)
        if self.total_weight == 0:
            return 0
        percentage_under_250 = (total_weight_under_250 / self.total_weight) * 100
        return percentage_under_250

    def update_calculations(self):
        # Calcula o peso total dos produtos
        self.total_weight = sum(order_product.product.weight_m_kg * order_product.quantity for order_product in self.order_products.all())
        
        # Calcula o número de containers necessários
        CONTAINER_CAPACITY_KG = 28000  # Capacidade do container em kg
        self.n_containers = ceil(self.total_weight / CONTAINER_CAPACITY_KG)
        
        # Calcula a porcentagem de peso abaixo de 250g
        self.percentage_under250 = self.calculate_percentage_under_250()
        
        # Salva as alterações
        self.save(update_fields=['total_weight', 'n_containers', 'percentage_under250'])

    def __str__(self):
        return self.request_title 

class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    surface_finish = models.ForeignKey(SurfaceFinish, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('order', 'product', 'surface_finish')

    def __str__(self):
        return f'{self.quantity} x {self.product.alumifont_code} ({self.surface_finish.type})'

@receiver(post_save, sender=OrderProduct)
def update_order_on_order_product_save(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_calculations()

@receiver(post_delete, sender=OrderProduct)
def update_order_on_order_product_delete(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_calculations()
