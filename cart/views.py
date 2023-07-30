from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .forms import AddToCartForm, AddressForm
from django.core import mail
from django.core.mail import EmailMessage
from .models import Product, OrderItem, Address, Payment, Order, Category, BankAccount
from core.models import OwnerFirm
from .utils import get_or_set_order_session
from reportlab.lib import (pagesizes, units)
from reportlab.pdfgen import canvas
from reportlab.platypus.paragraph import Paragraph
from datetime import date, timezone
import io
import datetime
import json


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

        order.save()
        messages.info(
            self.request, "Успешно добавихте адреса си!")
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
    template_name = 'cart/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        context['CALLBACK_URL'] = self.request.build_absolute_uri(reverse("cart:thank-you"))
        return context


class ConfirmOrderView(generic.View):
    @staticmethod
    def post(request, *args, **kwargs):
        order = get_or_set_order_session(request)
        # body = json.loads(request.body)
        # payment = Payment.objects.create(
        #     order=order,
        #     successful=True,
        #     raw_response=json.dumps(body),
        #     amount=float(body["purchase_units"][0]["amount"]["value"]),
        #     payment_method='Наложен платеж',
        # )
        order.ordered = True
        order.ordered_date = datetime.date.today()
        order.save()
        return JsonResponse({"data": "Success"})


class ThankYouView(generic.TemplateView):
    template_name = 'cart/thanks.html'
    template_for_email = 'cart/email_success_order.html'

    def get(self, request, *args, **kwargs):
        order = get_or_set_order_session(self.request)
        user = self.request.user
        firm = OwnerFirm.objects.first()
        order_items = OrderItem.objects.filter(order=order)
        date_of_order = date.today()
        date_time = datetime.datetime.now()
        order.ordered_date = date_time
        order.ordered = True
        order.save()
        data = []
        context = {"order": order, "user": user, "order_items": order_items, "firm": firm, "date": date_of_order}
        html_content = render_to_string(self.template_for_email, context, request=self.request)
        emails = [email for email in settings.ADMINS]
        emails.append(settings.NOTIFY_EMAIL)
        emails.append(settings.EMAIL_HOST_USER)
        subject = f"Поръчка: {order.order_number}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = emails
        # emails.append(user.email)
        for i in order_items:
            data.append({'product_name': i.product.title, 'quantity': i.quantity, 'price': i.product.get_price(),
                         'total': i.get_total_item_price()})
        send_mail(subject, "Вашата поръчка е успешно поръчана", from_email, recipient_list,
                  fail_silently=False, html_message=html_content)
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
        context = {
            'bank': bank,
            'order': order
        }
        return render(self.request, 'cart/bank-payment.html', context)


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
    pass
