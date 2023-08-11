import datetime
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.template.loader import render_to_string
from django.views import generic

from core.models import OwnerFirm
from .forms import AddToCartForm, AddressForm, AddFirmToOrder
from .models import Product, OrderItem, Address, Order, Category, BankAccount, Facture
from .utils import get_or_set_order_session


class ProductListView(generic.ListView):
    template_name = 'cart/product_list.html'

    def get_queryset(self):
        qs = Product.objects.all()
        category = self.request.GET.get('category', None)
        if category:
            qs = qs.filter(Q(primary_category__name=category) |
                           Q(secondary_categories__name=category)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class ProductDetailView(generic.FormView):
    template_name = 'cart/product_detail.html'
    form_class = AddToCartForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_success_url(self):
        return reverse("cart:summary")

    def get_form_kwargs(self):
        kwargs = super(ProductDetailView, self).get_form_kwargs()
        kwargs["product_id"] = self.get_object().id
        return kwargs

    def get_queryset(self):
        qs = Product.objects.all()
        category = self.request.GET.get('category', None)
        if category:
            qs = qs.filter(Q(primary_category__name=category) |
                           Q(secondary_categories__name=category)).distinct()
        return qs

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(product=product)

        if item_filter.exists():
            item = item_filter.first()
            item.quantity += int(form.cleaned_data['quantity'])
            item.save()

        else:
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()

        return super(ProductDetailView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['product'] = self.get_object()
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class CartView(generic.TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class IncreaseQuantityView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.save()
        return redirect("cart:summary")


class DecreaseQuantityView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save()
        return redirect("cart:summary")


class RemoveFromCartView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:summary")


class PaymentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/payment-options.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        context['CALLBACK_URL'] = self.request.build_absolute_uri(reverse("cart:thank-you"))
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class ConfirmOrderView(generic.View):
    @staticmethod
    def post(request, *args, **kwargs):
        order = get_or_set_order_session(request)
        order.ordered = True
        order.ordered_date = datetime.date.today()
        order.save()
        return JsonResponse({"data": "Success"})


class ThankYouView(generic.TemplateView):
    template_name = 'cart/thanks.html'
    template_for_email_to_admins = 'cart/email_success_order.html'
    template_for_email_to_user = 'cart/email_success_order_client.html'

    def get(self, request, *args, **kwargs):
        order = get_or_set_order_session(self.request)
        user = self.request.user
        firm = OwnerFirm.objects.first()
        order_items = OrderItem.objects.filter(order=order)
        if order_items.exists():
            date_of_order = date.today()
            date_time = datetime.datetime.now()
            order.ordered_date = date_time
            order.ordered = True
            order.payment_method = order.get_payment_method
            order.save()
            if order.payment_method == "Наложен Платеж":
                type = "Фактура"
            else:
                type = "Проформа Фактура"
            if order.facture_need:
                facture = Facture.objects.create(
                    order=order,
                    number_of_facture=order.order_number,
                    type_of_facture=type,
                    date_of_facture=date_of_order,
                    user=user,
                    firm=order.firm,
                    owner_firm=OwnerFirm.objects.first(),
                    bank=BankAccount.objects.first(),
                )
                # return redirect("cart:facture", facture.id) + f'?order={order}&facture={facture}&order_items={order_items}'
                context['facture'] = facture
            for order_item in order_items:
                order_item.product.stock -= order_item.quantity
                order_item.product.save()
            context = {"order": order, "user": user, "order_items": order_items, "firm": firm, "date": date_of_order,
                       "categories": Category.objects.values("name")}
            data = []
            html_content_for_admins = render_to_string(self.template_for_email_to_admins, context, request=self.request)
            html_content_for_users = render_to_string(self.template_for_email_to_user, context, request=self.request)
            emails_admins = [email for email in settings.ADMINS]
            emails_admins.append(settings.NOTIFY_EMAIL)
            emails_admins.append(settings.EMAIL_HOST_USER)
            email_user = [user.email]
            subject = f"Поръчка: {order.order_number}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list_for_admins = emails_admins
            recipient_list_for_users = email_user
            for i in order_items:
                data.append({'product_name': i.product.title, 'quantity': i.quantity, 'price': i.product.get_price(),
                             'total': i.get_total_item_price()})
            send_mail(subject, "Нова поръчка", from_email, recipient_list_for_admins,
                      fail_silently=False, html_message=html_content_for_admins)
            send_mail(subject, "Вашата поръчка е успешно поръчана", from_email, recipient_list_for_users,
                      fail_silently=False, html_message=html_content_for_users)
            return render(self.request, 'cart/thanks.html', context)

        else:
            context = {"order": order, "user": user, "order_items": order_items, "firm": firm,
                       "categories": Category.objects.values("name")}
            return render(self.request, 'cart/not_order.html', context)


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'order.html'
    queryset = Order.objects.all()
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class BankPayment(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/bank-payment.html'

    def get(self, request, *args, **kwargs):
        bank = BankAccount.objects.first()
        order = get_or_set_order_session(self.request)
        order.payment_method = "Банков път"
        order.save()
        context = {
            'bank': bank,
            'order': order,
            'categories': Category.objects.values("name")
        }
        return render(self.request, 'cart/bank-payment.html', context)


class DeliveryPayment(LoginRequiredMixin, generic.TemplateView):
    template_name = "cart/delivery-payment.html"

    def get(self, request, *args, **kwargs):
        order = get_or_set_order_session(self.request)
        order.payment_method = "Наложен Платеж"
        order.save()
        context = {
            'order': order,
            'categories': Category.objects.values("name")
        }
        return render(self.request, 'cart/delivery-payment.html', context)


class FactureView(LoginRequiredMixin, generic.TemplateView):
    def get(self, request, *args, **kwargs):
        # Facture, order_items, order
        facture = Facture.objects.get(id=kwargs['facture_id'])
        order = facture.order
        order_items = OrderItem.objects.filter(order=order)
        bank = BankAccount.objects.first()
        count = order_items.count()
        template_count = range(count)
        # template = get_template('cart/invoice-2.html')
        context = {
            'order': order,
            "facture": facture,
            'order_items': order_items,
            'count': template_count,
            'categories': Category.objects.values("name"),
            'bank': bank
        }

        return render(self.request, 'cart/invoice.html', context)


def search_view(request):
    query = request.GET.get('q')
    if query == '':
        object_list = Product.objects.all()
    else:
        object_list = Product.objects.filter(title__icontains=query)
    product_list = Product.objects.all()
    categories = Category.objects.values("name")
    context = {
        'object_list': object_list,
        'categories': categories,
        'product_list': product_list
    }
    return render(request, 'cart/product_list.html', context)


@login_required
def checkout(request):
    user = request.user
    user_id = request.user.id
    order = get_or_set_order_session(request)
    shipping_form = AddressForm(user_id=user_id)
    firm_form = AddFirmToOrder(user_id=user_id)
    facture = request.POST.get('facture')
    is_facture = facture == 'on'
    if is_facture:
        order.facture_need = True
        order.save()
    if request.method == "POST":
        add_firm = request.POST.get('add-firm')
        is_firm_added = add_firm == 'on'
        if is_firm_added:
            shipping_form = AddressForm(request.POST, user_id=user_id)
            firm_form = AddFirmToOrder(request.POST, user_id=user_id)

            if shipping_form.is_valid() and firm_form.is_valid():
                selected_firm = firm_form.cleaned_data.get('selected_firm_for_order')
                selected_shipping_address = shipping_form.cleaned_data.get('selected_shipping_address')

                if selected_firm:
                    order.firm = selected_firm
                    firm_form.fields['selected_firm_for_order'].label = "Избери Фирма за фактура"
                    firm_form.fields['name_of_firm'].required = False
                    firm_form.fields['bulstat'].required = False
                    firm_form.fields['VAT_number'].required = False
                    firm_form.fields['address_by_registration'].required = False
                    firm_form.fields['owner_of_firm'].required = False
                    firm_form.fields['mobile_number'].required = False
                    firm_form.fields['static_number'].required = False
                    firm_form.fields['email'].required = False
                else:
                    firm_form.fields['selected_firm_for_order'].label = "Избери Фирма за фактура"
                    firm_form.fields['name_of_firm'].required = True
                    firm_form.fields['bulstat'].required = True
                    firm_form.fields['VAT_number'].required = True
                    firm_form.fields['address_by_registration'].required = True
                    firm_form.fields['owner_of_firm'].required = True
                    firm_form.fields['mobile_number'].required = True
                    firm_form.fields['static_number'].required = True
                    firm_form.fields['email'].required = True
                    firm = firm_form.save(commit=False)
                    firm.user = user
                    firm.save()
                    order.firm = firm
                    order.save()
                if selected_shipping_address:
                    order.shipping_address = selected_shipping_address
                    shipping_form.fields['selected_shipping_address'].label = "Избери адрес за доставка"
                    shipping_form.fields['address_line_1'].required = False
                    shipping_form.fields['address_line_2'].required = False
                    shipping_form.fields['zip_code'].required = False
                    shipping_form.fields['city'].required = False
                else:
                    shipping_form.fields['selected_shipping_address'].label = "Избери адрес за доставка"
                    shipping_form.fields['address_line_1'].required = True
                    shipping_form.fields['address_line_2'].required = True
                    shipping_form.fields['zip_code'].required = True
                    shipping_form.fields['city'].required = True
                    shipping = shipping_form.save(commit=False)
                    shipping.user = user
                    order.shipping_address = shipping.save()
                order.save()
                return redirect("cart:payment")

        else:
            shipping_form = AddressForm(request.POST, user_id=user_id)
            if shipping_form.is_valid():
                selected_shipping_address = shipping_form.cleaned_data.get('selected_shipping_address')
                if selected_shipping_address:
                    order.shipping_address = selected_shipping_address
                else:
                    if selected_shipping_address:
                        order.shipping_address = selected_shipping_address
                        shipping_form.fields['selected_shipping_address'].label = "Избери адрес за доставка"
                        shipping_form.fields['address_line_1'].required = False
                        shipping_form.fields['address_line_2'].required = False
                        shipping_form.fields['zip_code'].required = False
                        shipping_form.fields['city'].required = False
                    else:
                        shipping_form.fields['selected_shipping_address'].label = "Избери адрес за доставка"
                        shipping_form.fields['address_line_1'].required = True
                        shipping_form.fields['address_line_2'].required = True
                        shipping_form.fields['zip_code'].required = True
                        shipping_form.fields['city'].required = True
                        shipping = shipping_form.save(commit=False)
                        shipping.user = user
                        order.shipping_address = shipping.save()
                order.save()
                return redirect("cart:payment")

    context = {
        "order": order,
        "firm_form": firm_form,
        "shipping_form": shipping_form,
        "user_id": user_id,
        "categories": Category.objects.values("name")
    }
    return render(request, "cart/checkout.html", context)
