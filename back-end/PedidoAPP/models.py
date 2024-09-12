from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from math import ceil
from datetime import datetime

class Agent(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    n_convenio = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nome

class Factory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    ie = models.CharField(max_length=20, unique=True, null=True, blank=True)
    factories = models.ManyToManyField(Factory)  # Empresas podem fazer pedidos em várias fábricas
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='companies', null=True, blank=True)

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
    alumifont_code = models.CharField(max_length=50, unique=True)  # Sempre o mesmo, independente da fábrica
    ncm = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    length_mm = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)  # Sempre o mesmo (6000)
    temper_alloy = models.CharField(max_length=50, default='6063T5')
    surface_finish = models.ForeignKey(SurfaceFinish, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    enabled_companies = models.ManyToManyField(Company, related_name='enabled_products', blank=True)  # Empresas que têm acesso ao produto

    def __str__(self):
        return self.alumifont_code

class FactoryProduct(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name='factory_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='factory_products')
    factory_code = models.CharField(max_length=50)  # Código único de cada fábrica para o produto
    weight_m_kg = models.DecimalField(max_digits=10, decimal_places=3)  # Peso que pode ser diferente para cada fábrica

    def __str__(self):
        return f'{self.factory.name} - {self.product.alumifont_code}'

    class Meta:
        unique_together = ('factory', 'product')

class Order(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)  # Fábrica associada ao pedido
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Empresa associada ao pedido
    request_title = models.CharField(max_length=255, blank=True, null=True)  # Será gerado automaticamente
    n_containers = models.PositiveIntegerField(default=0, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    percentage_under250 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Gerar o título do pedido automaticamente com o formato [NOME DA EMPRESA] [MÊS].[ANO]-[PRIMEIRA LETRA DA FÁBRICA]
        if not self.request_title:
            today = datetime.today()
            self.request_title = f"{self.company.name} {today.month}.{today.year}-{self.factory.name[0]}"
        super().save(*args, **kwargs)

    def calculate_percentage_under_250(self):
        products_under_250 = self.order_products.filter(product__weight_m_kg__lt=0.250)
        total_weight_under_250 = sum(order_product.product.weight_m_kg * order_product.quantity for order_product in products_under_250)
        if self.total_weight == 0:
            return 0
        percentage_under_250 = (total_weight_under_250 / self.total_weight) * 100
        return percentage_under_250

    def update_calculations(self):
        self.total_weight = sum(order_product.product.weight_m_kg * order_product.quantity for order_product in self.order_products.all())
        
        CONTAINER_CAPACITY_KG = 28000  # Capacidade do container em kg
        self.n_containers = ceil(self.total_weight / CONTAINER_CAPACITY_KG)
        
        self.percentage_under250 = self.calculate_percentage_under_250()
        self.save(update_fields=['total_weight', 'n_containers', 'percentage_under250'])

    def __str__(self):
        return self.request_title 

class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(FactoryProduct, on_delete=models.CASCADE, related_name='order_products')  # Relaciona-se a um FactoryProduct
    surface_finish = models.ForeignKey(SurfaceFinish, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('order', 'product', 'surface_finish')

    def __str__(self):
        return f'{self.quantity} x {self.product.product.alumifont_code} ({self.surface_finish.type})'

@receiver(post_save, sender=OrderProduct)
def update_order_on_order_product_save(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_calculations()

@receiver(post_delete, sender=OrderProduct)
def update_order_on_order_product_delete(sender, instance, **kwargs):
    if instance.order:
        instance.order.update_calculations()
