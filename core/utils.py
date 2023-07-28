from .models import CustomUserModel


def get_or_set_user_session(request):
    user_id = request.session.get('user_id', None)

    if user_id is None:
        user = CustomUserModel()
        user.save()
        request.session['user_id'] = user.id

    else:
        try:
            user = CustomUserModel.objects.get(id=user_id)
        except Order.DoesNotExist:
            order = Order()
            order.save()
            request.session['order_id'] = order.id

    if request.user.is_authenticated and order.user is None:
        order.user = request.user
        order.save()
    return user
