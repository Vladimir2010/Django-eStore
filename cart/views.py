import datetime
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.template.loader import render_to_string
from django.views import generic

from core.models import OwnerFirm
from .forms import AddToCartForm, AddressForm
from .models import Product, OrderItem, Address, Order, Category, BankAccount
from core.models import Firm
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


class CheckoutView(LoginRequiredMixin, generic.FormView):
    template_name = 'cart/checkout.html'
    form_class = AddressForm

    def get_success_url(self):
        return reverse("cart:payment")

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        # selected_firm_for_order = form.cleaned_data.get(
        #     'selected_firm_for_order')
        selected_shipping_address = form.cleaned_data.get(
            'selected_shipping_address')

        if selected_shipping_address:
            order.shipping_address = selected_shipping_address
        else:
            address = Address.objects.create(
                address_type='S',
                user=self.request.user,
                address_line_1=form.cleaned_data['shipping_address_line_1'],
                address_line_2=form.cleaned_data['shipping_address_line_2'],
                zip_code=form.cleaned_data['shipping_zip_code'],
                city=form.cleaned_data['shipping_city'],
            )
            order.shipping_address = address

        # if selected_firm_for_order:
        #     order.firm = selected_firm_for_order
        # else:
        #     firm = Firm.objects.create(
        #         user = self.request.user,
        #         name_of_firm = form.cleaned_data['name_of_firm'],
        #         bulstat = form.cleaned_data['bulstat'],
        #         VAT_number = form.cleaned_data['VAT_number'],
        #         address_by_registration = form.cleaned_data['address_by_registration'],
        #         owner_of_firm = form.cleaned_data['owner_of_firm'],
        #     )
        #     order.firm = firm

        order.save()
        messages.info(
        self.request, "Успешно добавихте адреса си!")
        messages.info(
            self.request, "Успешно добавихте фирмата си!")
        return super(CheckoutView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CheckoutView, self).get_form_kwargs()
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        return context


class PaymentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/payment-options.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        context['CALLBACK_URL'] = self.request.build_absolute_uri(reverse("cart:thank-you"))
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
        date_of_order = date.today()
        date_time = datetime.datetime.now()
        order.ordered_date = date_time
        order.ordered = True
        order.payment_method = order.get_payment_method
        order.save()
        for order_item in order_items:
            order_item.product.stock -= order_item.quantity
        data = []
        context = {"order": order, "user": user, "order_items": order_items, "firm": firm, "date": date_of_order}
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
        return render(self.request, 'cart/thanks.html')


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'order.html'
    queryset = Order.objects.all()
    context_object_name = 'order'


class BankPayment(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/bank-payment.html'

    def get(self, request, *args, **kwargs):
        bank = BankAccount.objects.first()
        order = get_or_set_order_session(self.request)
        order.payment_method = "Банков път"
        order.save()
        context = {
            'bank': bank,
            'order': order
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
        }
        return render(self.request, 'cart/delivery-payment.html', context)


#
# def pdf_invoice(request):
#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
#     object = pdf.beginText()
#     object.setTextOrigin(inch, inch)
#     # object.setFont("Arial", 20)
#     order = get_or_set_order_session(request)
#     items = order.items
#     from reportlab.pdfbase import pdfmetrics
#     from reportlab.pdfbase.ttfonts import TTFont
#     pdfmetrics.registerFont(TTFont('arial', 'fonts/Arial.ttf'))
#     # p = Paragraph(data.decode('utf-8'), style=styNormal)
#
#     lines = [
#         "Проформа Фактура",
#         "Номер: : " + str(order.id),
#         "от: " + order.ordered_date,
#         'Получател: ' + order.get_full_user_name,
#         "Адрес: " + order.shipping_address,]
#
#     for line in lines:
#         p = Paragraph(line.decode('utf-8'), style=styNormal)
#         object.textLine(p)
#
#     pdf.drawText(object)
#     pdf.showPage()
#     pdf.save()
#     buffer.seek(0)
#
#     return FileResponse(buffer, as_attachment=True, filename='invoice.pdf')

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
