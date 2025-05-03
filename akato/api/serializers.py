"""Сериализаторы."""

import base64

from rest_framework import serializers  # type: ignore
from django.core.files.base import ContentFile  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore

from products.models import Category, Subcategory, Product, ProductImage
from users.models import ShoppingCart

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле для картинки."""

    def to_internal_value(self, image_data):
        """Преобразование в картинку."""
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            image_data = ContentFile(base64.b64decode(imgstr),
                                     name=f'temp.{ext}')

        return super().to_internal_value(image_data)
    

class CategoryInSubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории при упоминании в подкатегории."""
    image = Base64ImageField()
    class Meta:
        """Настройки сериализатора."""

        model = Category
        fields = ('id',
                  'name',
                  'slug',
                  'image',
                  )  


class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегорий."""
    image = Base64ImageField()
    category = CategoryInSubcategorySerializer()

    class Meta:
        """Настройки сериализатора."""

        model = Subcategory
        fields = ('id',
                  'name',
                  'slug',
                  'image',
                  'category',
                  )  


class SubcategoryInCategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегорий при упоминании в категории."""
    image = Base64ImageField()

    class Meta:
        """Настройки сериализатора."""

        model = Subcategory
        fields = ('id',
                  'name',
                  'slug',
                  'image',
                  )         


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""
    image = Base64ImageField()
    subcategories = SubcategoryInCategorySerializer(
        many=True,
        read_only=True
    )


    class Meta:
        """Настройки сериализатора."""

        model = Category
        fields = ('id',
                  'name',
                  'slug',
                  'image',
                  'subcategories',
                  )      


class ProductImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображений товара."""
    # по умолчанию DRF отдает .url для ImageField
    class Meta:
        model = ProductImage
        fields = ('id', 'order', 'image')


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор товара."""
    images = ProductImageSerializer(many=True, read_only=True)
    subcategory = SubcategorySerializer()

    class Meta:
        model = Product
        fields = ('id',
                  'name',
                  'slug', 
                  'subcategory',  
                  'price',                                                  
                  'images',
                  )
    
    def convert_to_short_link(self, recipe_id):
        """Конвертация в короткую ссылку."""
        number = []
        while recipe_id:
            number.append(chr(97 + recipe_id % 23))
            recipe_id //= 23
        return ''.join((str(digit) for digit in number))

    def create(self, validated_data):
        """Создание товара."""
        product = Product.objects.create(
            **validated_data)
        product.short_url = self.convert_to_short_link(product.id)
        product.save()
        return product


class ShoppingReadSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    # для записи – указываем id товара
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    # пользователя подтягиваем из запроса
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'product', 'product_id', 'quantity')


class ShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор объектов корзины покупок."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'product', 'quantity')
    
    def create(self, validated_data):
        user = validated_data['user']
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)

        obj, created = ShoppingCart.objects.get_or_create(
            user=user, product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            obj.quantity += quantity
            obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    id = serializers.IntegerField(min_value=1)

    def get_user(self):
        """Получение пользователя из запроса."""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('10. Нет данных запроса.')
        user = request.user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                'Пользователь не аутентифицирован.')
        return request.user

    def to_representation(self, instance):
        return ShoppingReadSerializer(instance,
                                  context=self.context).data

    def validate(self, data_to_validate):
        """Валидация добавления в список покупок."""
        user = self.get_user()
        product_id = data_to_validate.get('id')
        if not product_id:
            raise serializers.ValidationError('Нет id товара.')
        if ShoppingCart.objects.filter(
                product__id=product_id,
                user=user).exists():
            data_to_validate['already_exists'] = True
        else:
            data_to_validate['already_exists'] = False    
        product = get_object_or_404(Product, id=product_id)
        data_to_validate['user'] = user
        data_to_validate['product'] = product
        return data_to_validate

    def save(self):
        """Добавление товара в корзину покупок."""
        return self.validated_data.get('user').shopping_cart.add(
            self.validated_data.get('product'))
