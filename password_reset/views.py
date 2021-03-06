import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.core import signing
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.utils import timezone
from django.views import generic

from .forms import PasswordRecoveryForm, PasswordResetForm
from password_reset.mail import send_templated_mail


class SaltMixin(object):
    salt = 'password_recovery'
    url_salt = 'password_recovery_url'


def loads_with_timestamp(value, salt):
    """Returns the unsigned value along with its timestamp, the time when it
    got dumped."""
    try:
        signing.loads(value, salt=salt, max_age=-1)
    except signing.SignatureExpired as e:
        age = float(str(e).split('Signature age ')[1].split(' >')[0])
        timestamp = timezone.now() - datetime.timedelta(seconds=age)
        return timestamp, signing.loads(value, salt=salt)


class RecoverDone(SaltMixin, generic.TemplateView):
    fail_noexistent_user = True
    template_name = "password_reset/reset_sent.html"

    def get_context_data(self, **kwargs):
        ctx = super(RecoverDone, self).get_context_data(**kwargs)
        try:
            ctx['timestamp'], ctx['email'] = loads_with_timestamp(
                self.kwargs['signature'], salt=self.url_salt,
            )
        except signing.BadSignature:
            if self.fail_noexistent_user:
                raise Http404
        return ctx
recover_done = RecoverDone.as_view()


class Recover(SaltMixin, generic.FormView):
    case_sensitive = True
    form_class = PasswordRecoveryForm
    template_name = 'password_reset/recovery_form.html'
    email_template = 'password_reset/recovery_letter.html'
    search_fields = ['username', 'email']
    fail_noexistent_user = True

    def get_success_url(self):
        return reverse('password_reset_sent', args=[self.mail_signature])

    def get_context_data(self, **kwargs):
        kwargs['url'] = self.request.get_full_path()
        return super(Recover, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(Recover, self).get_form_kwargs()
        kwargs.update({
            'case_sensitive': self.case_sensitive,
            'search_fields': self.search_fields,
            'fail_noexistent_user': self.fail_noexistent_user,
        })
        return kwargs

    def get_email_context(self):
        return {
            'site': RequestSite(self.request),
            'user': self.user,
            'token': signing.dumps(self.user.pk, salt=self.salt),
            'secure': self.request.is_secure(),
        }

    def send_notification(self):
        send_templated_mail(email_template=self.email_template,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[self.user.email],
                            context=self.get_email_context())

    def form_valid(self, form):
        self.user = form.cleaned_data['user']
        if self.user:
            self.send_notification()
            if (
                len(self.search_fields) == 1 and
                self.search_fields[0] == 'username'
            ):
                # if we only search by username, don't disclose the user email
                # since it may now be public information.
                email = self.user.username
            else:
                email = self.user.email
            self.mail_signature = signing.dumps(email, salt=self.url_salt)
        else:
            # we never send anything, but user should not know that
            self.mail_signature = signing.dumps(form.cleaned_data['username_or_email'], salt='fake-send')
        return super(Recover, self).form_valid(form)
recover = Recover.as_view()


class Reset(SaltMixin, generic.FormView):
    form_class = PasswordResetForm
    token_expires = 3600 * 48  # Two days
    template_name = 'password_reset/reset.html'
    success_url = reverse_lazy('password_reset_done')

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        try:
            pk = signing.loads(kwargs['token'], max_age=self.token_expires,
                               salt=self.salt)
        except signing.BadSignature:
            return self.invalid()

        self.user = get_object_or_404(User, pk=pk)
        return super(Reset, self).dispatch(request, *args, **kwargs)

    def invalid(self):
        return self.render_to_response(self.get_context_data(invalid=True))

    def get_form_kwargs(self):
        kwargs = super(Reset, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(Reset, self).get_context_data(**kwargs)
        if 'invalid' not in ctx:
            ctx.update({
                'username': self.user.username,
                'token': self.kwargs['token'],
            })
        return ctx

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())
reset = Reset.as_view()


class ResetDone(generic.TemplateView):
    template_name = 'password_reset/recovery_done.html'


reset_done = ResetDone.as_view()
