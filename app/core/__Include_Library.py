
import os
import time
import random
import json
from django import forms
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, DetailView, ListView, View
from django.utils.deprecation import MiddlewareMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission
from calendar import monthrange
from random import randrange
from xml.dom import minidom
from pprint import pprint
from itertools import chain
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import re
import json
from urllib.request import urlopen
from urllib import parse
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from functools import partial
from django.utils.functional import cached_property
import math
from django.db import transaction
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.decorators import method_decorator