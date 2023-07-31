from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import reverse, render, redirect, get_object_or_404
from django.views import generic
from cart.models import Order, OrderItem, Product
from .forms import ContactForm, EditUserForm, FirmForm, EditFirmForm
from django.core import mail
from django.core.mail import EmailMessage
from .models import CustomUserModel, Firm
from cart.utils import get_or_set_order_session


# Class Based Views
class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({
            "orders": Order.objects.filter(user=self.request.user, ordered=True)
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


# Def Views
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
        'user': user
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
        'user': user
    }
    return render(request, 'firm/add-firm.html', context)


def view_firms(request):
    user = request.user
    firms = Firm.objects.filter(user=user)

    context = {
        'firms': firms,
        'user': user
    }
    return render(request, 'firm/view-firms.html', context)


def remove_firm(request, firm_id):
    firm = get_object_or_404(Firm, id=firm_id)
    context = {
        'firm': firm
    }
    firm.delete()
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

#
# class EditFirmView(generic.FormView):
#     form_class = EditFirmForm
#     template_name = 'firm/edit-firms.html'
#
#     def get_success_url(self):
#         return reverse("view-firms")
#
#     def form_valid(self, form):
#         firm = Firm.objects.get(id=self.kwargs['firm_id'])
#         form = EditFirmForm(request.POST, instance=firm)
#         form.save()
#         return super(EditFirmForm, self).form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super(EditFirmView, self).get_context_data(**kwargs)
#         context['firm'] = Firm.objects.get(id=self.kwargs['firm_id'])
#         context['form'] = self.form_class(instance=context['firm'])
#         return context

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
        'firm': firm
    }
    return render(request, 'firm/edit-firms.html', context)