from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField

from reviews.models import Review, Comment


class ReviewSerializer(serializers.Serializer):
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
        fields = ('title_id', 'text', 'author', 'score', 'pub_date')

    def validate_title_id(self, value):
        user = self.context['request'].user
        if Review.objects.filter(user=user, title_id=value).exists():
            raise serializers.ValidationError(
                'Вы не можете дважды дать отзыв на одно произведение.'
            )
        return value


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
