from django.db.models import Avg
from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField

from reviews.models import Review, Comment, User, Category, Title


class UserSerializer(serializers.ModelSerializer):  # удалить

    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):  # удалить

    class Meta:
        model = Category
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):  # удалить

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('title_id', 'text', 'author', 'score', 'pub_date', 'rating')

    def validate_title_id(self, value):
        user = self.context['request'].user
        if Review.objects.filter(user=user, title_id=value).exists():
            raise serializers.ValidationError(
                'Вы не можете дважды дать отзыв на одно произведение.'
            )
        return value

    def create(self, validated_data):
        Review.objects.create(**validated_data)
        title_id = self.context['request'].title_id
        updated_rating = Review.objects.filter(
            title_id=title_id
        ).aggregate(avg_rating=Avg('score'), default=None)
        Title.objects.update(rating=int(updated_rating))


class CommentSerializer(serializers.ModelSerializer):
    review_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('author', 'review_id', 'text', 'created', 'post')
        read_only_fields = ('post',)
