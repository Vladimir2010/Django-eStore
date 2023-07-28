from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import reverse, render, redirect
from django.views import generic
from cart.models import Order
from .forms import ContactForm, EditUserForm
from django.core import mail
from django.core.mail import EmailMessage
from .models import CustomUserModel


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

# TODO: GET USER, SET FORM INSTANCE TO USER INSTANCE, TO GIVE ACCESS TO FORM AND PROFILE IN TEMPLATE WITH CONTEXT
# class EditProfileView(LoginRequiredMixin, generic.FormView):
#     template_name = 'account/edit-user-profile.html'
#     form_class = EditUserForm
#
#
#     def post(self, request, *args, **kwargs):
#         user = self.request.user
#         form = self.get_form()
#         if form.is_valid():
#             form.save()
#             return reverse("profile")
#         else:
#             form = self.get_form()
#             return form
#
#     def get_context_data(self, **kwargs):
#         context = super(EditProfileView, self).get_context_data(**kwargs)
#         context["user"] = self.request.user
#         context["form"] = self.post(self, **kwargs)
#         return context

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