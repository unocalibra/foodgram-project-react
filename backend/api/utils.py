from rest_framework import status
from rest_framework.response import Response


def post_instance(request, instance, serializer):
    """Добавление в избарнное или в корзину."""
    serializer = serializer(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_instance(request, name_model, instance, error_message):
    """Удаление из избарнного или в корзины."""
    if not name_model.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)
    name_model.objects.filter(user=request.user, recipe=instance).delete()
    return Response('Рецепт удален', status=status.HTTP_204_NO_CONTENT)
