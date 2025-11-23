from jinja2 import Environment, pass_context
from django.urls import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from crispy_forms.utils import render_crispy_form
from datetime import datetime


@pass_context
def __crispy(context, form):
    crispy_form = render_crispy_form(form, context=context)
    crispy_form = crispy_form.replace('</form>', '')
    crispy_form = format_html(crispy_form)
    return crispy_form


@pass_context
def __crispy_file(context, form):
    crispy_form = render_crispy_form(form, context=context)
    return crispy_form


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'crispy_file': __crispy_file,
        'crispy': __crispy,
    })
    env.filters['commafy'] = lambda v: "{:,}".format(v)
    return env
