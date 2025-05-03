"""Контроллеры."""

import json

from rest_framework.permissions import (AllowAny,  # type: ignore
                                        IsAuthenticated)
from rest_framework import filters, viewsets, status  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from rest_framework.decorators import action  # type: ignore
from rest_framework.response import Response  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from django.conf import settings  # type: ignore
from rest_framework.views import APIView  # type: ignore
from django.http import HttpResponse  # type: ignore
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from django.db.models import Sum, F  # type: ignore
from django.shortcuts import redirect  # type: ignore

from products.models import Category, Subcategory, Product
from users.models import ShoppingCart
from .serializers import (CategorySerializer, SubcategorySerializer,
                          ProductSerializer, ShoppingSerializer,
                          UserReadSerializer, UserWriteSerializer,
                          PasswordSerializer, FavoriteCreateSerializer,
                          SubscriptionSerializer, ShoppingCreateSerializer,
                          AvatarSerializer, SubscriptionCreateSerializer)
from .permissions import AuthorOnly, ForbiddenPermission
from .filters import RecipeFilter
from .pagination import LimitPagination

User = get_user_model()


class BaseReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    """Базовый вьюсет для только чтения."""

    permission_classes = (AllowAny,)
    pagination_class = LimitPagination


class CategoryViewSet(BaseReadOnlyViewset):
    """Вьюсет категорий."""

    queryset = Category.objects.all().prefetch_related('subcategories')
    serializer_class = CategorySerializer


class SubcategoryViewSet(BaseReadOnlyViewset):
    """Вьюсет подкатегорий."""

    queryset = Subcategory.objects.all().select_related('category')
    serializer_class = SubcategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """Вьюсет товаров."""

    http_method_names = ('get',)
    pagination_class = LimitPagination
    queryset = Product.objects.all().prefetch_related('images')

    def get_permissions(self):
        """Разрешения."""
        if self.action in {'list', 'retrieve',}:
            self.permission_classes = (AllowAny,)
        elif self.action in {'download_shopping_cart',
                             'shopping_cart',
                             'delete_shopping_cart'}:
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (ForbiddenPermission,)
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in {'list', 'retrieve'}:
            return ProductSerializer
        if self.action == 'shopping_cart':
            return ShoppingSerializer
        return ProductSerializer

    def convert_shopping_cart_to_txt(self, products):
        """Конвертация корзины в TXT."""
        if not products:
            return 'Нет товаров в корзине.'
        

        recipe_ingredients = (RecipeIngredient.objects.
                              filter(recipe__in=recipes))
        ingredients = recipe_ingredients.values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            total_amount=Sum('amount')).order_by('name')
        if not ingredients.exists():
            return 'Нет ингредиентов для покупки.'
        txt = ['Список покупок.\n\n']
        txt.extend('\n'.join(
            ((f'{ingredient.get("name")}:  '
              f'{ingredient.get("measurement_unit")} '
              f'— {ingredient.get("total_amount")}')
             for ingredient in ingredients)
        ))
        return txt

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Получение корзины покупок в формате TXT."""
        user = request.user
        products = user.shopping_cart.all()
        txt = self.convert_to_txt(products)
        response = HttpResponse(txt, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping-list.txt"')
        return response

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление товара в корзину покупок."""
        self.lookup_field = 'pk'
        product = self.get_object()
        serializer = self.get_serializer(product,
                                         data={'id': pk},
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Удаление из корзины покупок."""
        user = request.user
        shopping = get_object_or_404(ShoppingCart,
                                     user=user,
                                     recipe__id=pk)
        shopping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=(AllowAny,),
        url_path='get-link',
        url_name='get_link',
    )
    def get_link(self, request, pk):
        """Получение короткой ссылки на товар."""
        self.lookup_field = 'pk'
        product = self.get_object()
        return Response({
            'short-link':
            (f'{settings.CURRENT_HOST}:{settings.CURRENT_PORT}'
             f'/s/{product.short_url}'),
        })


class ShortLinkView(APIView):
    """Класс коротких ссылок."""

    permission_classes = (AllowAny,)

    def get(self, request, short_link):
        """Получение товара по короткой ссылке."""
        product = get_object_or_404(Product, short_url=short_link)
        return redirect(f'/products/{product.id}')


class LoadDataView(APIView):
    """Класс загрузки данных."""

    permission_classes = (AllowAny,)

    def get(self, request):
        """Загрузка данных."""
        with open('data/ingredients.json', 'r', encoding='utf-8') as file:
            ingredients = json.load(file)
            for ingredient in ingredients:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )

        with open('data/tags.json', 'r', encoding='utf-8') as file:
            tags = json.load(file)
            for tag in tags:
                Tag.objects.get_or_create(
                    name=tag['name'],
                    slug=tag['slug']
                )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingItemViewSet(viewsets.ModelViewSet):
    """Просмотр, добавление, удаление отдельного товара пользователя."""
    serializer_class = ShoppingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # показываем только товары текущего пользователя
        return ShoppingCart.objects.filter(user=self.request.user)
