from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import reverse, render, redirect, get_object_or_404
from django.views import generic
from cart.models import Order, OrderItem, Product, Category
from .forms import ContactForm, EditUserForm, FirmForm, EditFirmForm, RemoveFirmForm
from django.core import mail
from django.core.mail import EmailMessage
from .models import CustomUserModel, Firm
from cart.utils import get_or_set_order_session
from django.views.defaults import (page_not_found, server_error, bad_request, permission_denied,
    server_error)

from django.shortcuts import render
from django.template import RequestContext


# Class Based Views
class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({
            "orders": Order.objects.filter(user=self.request.user, ordered=True),
            "categories": Category.objects.values('name')
        })
        return context


class HomeView(generic.TemplateView):
    template_name = 'index.html'


class ContactView(generic.FormView):
    form_class = ContactForm
    template_name = 'contact.html'

    def get_success_url(self):
        return reverse("contact")

    def form_valid(self, form):
        messages.info(
            self.request, "Благодарим Ви, че се свързахте с нас!")
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')
        emails = [email for email in settings.ADMINS]
        print(emails)
        emails.append(settings.NOTIFY_EMAIL)
        print(emails)
        full_message = f"""
            Получено съобщение от: {name}, {email}
            ________________________

            {message}
            """
        with mail.get_connection() as connection:
            mail.EmailMessage(
                subject="Получена обратна връзка!",
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=emails,
                connection=connection,
            ).send()
        # send_mail(
        #     subject="Получена обратна връзка!",
        #     message=full_message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[settings.NOTIFY_EMAIL, settings.ADMINS]
        # )
        return super(ContactView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


def handler400(request, *args, **argv):
    return render(request, '400.html', status=404)


def handler500(request, *args, **argv):
    return render(request, '500.html', status=404)


def handler403(request, *args, **argv):
    return render(request, '403.html', status=404)




def edit_profile_view(request):
    user = request.user
    form = EditUserForm(instance=user)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    context = {
        'form': form,
        'user': user,
        "categories": Category.objects.values("name")
    }
    return render(request, 'account/edit-user-profile.html', context)


def add_firm_view(request):
    user = request.user
    form = FirmForm()
    if request.method == 'POST':
        form = FirmForm(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.user = user
            object.save()
            return redirect('profile')
    context = {
        'form': form,
        'user': user,
        "categories": Category.objects.values("name")
    }
    return render(request, 'firm/add-firm.html', context)


def view_firms(request):
    user = request.user
    firms = Firm.objects.filter(user=user)

    context = {
        'firms': firms,
        'user': user,
        "categories": Category.objects.values("name")
    }
    return render(request, 'firm/view-firms.html', context)


def remove_firm(request, firm_id):
    firm = get_object_or_404(Firm, id=firm_id)
    form = RemoveFirmForm(instance=firm)
    context = {
        'firm': firm,
        'form': form,
        "categories": Category.objects.values("name")
    }

    if request.method == 'POST':
        form = RemoveFirmForm(request.POST, instance=firm)
        if form.is_valid():
            firm.delete()
            return redirect('view-firms')

    return render(request, 'firm/remove-firm.html', context)


def update_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order = get_or_set_order_session(request)
    if OrderItem.objects.filter(product=product, order=order).exists():
        order_item = OrderItem.objects.get(product=product, order=order)
        if order_item.product.stock < order_item.quantity + 1:
            pass
        else:
            order_item.quantity += 1
            order_item.save()
    else:
        order_item = OrderItem.objects.create(product=product, order=order)
        if order_item.product.stock < 1:
            pass
        else:
            order_item.quantity = 1
            order_item.save()

    return redirect("cart:summary")

    return render(request, 'cart/update-cart.html')


def edit_firms(request, firm_id):
    firm = Firm.objects.get(id=firm_id)
    form = EditFirmForm(instance=firm)
    if request.method == 'POST':
        form = EditFirmForm(request.POST, instance=firm)
        if form.is_valid():
            form.save()
            return redirect('view-firms')
    context = {
        'form': form,
        'firm': firm,
        "categories": Category.objects.values("name")
    }
    return render(request, 'firm/edit-firms.html', context)