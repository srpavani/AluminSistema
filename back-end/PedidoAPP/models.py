from django.db import models

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)

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

class Order(models.Model):
    request_title = models.CharField(max_length=255)
    n_containers = models.PositiveIntegerField()
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    percentage_under250 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    products = models.ManyToManyField(Product, related_name='orders')

    def calculate_percentage_under_250(self):
        products_under_250 = self.products.filter(weight_m_kg__lt=0.250)
        total_weight_under_250 = sum([product.weight_m_kg for product in products_under_250])
        if self.total_weight == 0:
            return 0
        percentage_under_250 = (total_weight_under_250 / self.total_weight) * 100
        return percentage_under_250

    def save(self, *args, **kwargs):
        self.percentage_under250 = self.calculate_percentage_under_250()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_title
