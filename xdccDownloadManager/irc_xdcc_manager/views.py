from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.views import View
from .models import IRCConnection, IRCChannel, XDCCOffer
from django.db.models import Avg, Subquery, OuterRef, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import serializers, filters, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.apps import apps


import logging

logger = logging.getLogger(__name__)

# Create your views here.


class MainPageView(LoginRequiredMixin, TemplateView):    
    template_name = 'home.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['irc_connections'] = IRCConnection.objects.all()
        return context
    

# Serializers

class IRCConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IRCConnection
        fields = '__all__'

class IRCChannelSerializer(serializers.ModelSerializer):
    class Meta:
        server = IRCConnectionSerializer(many=False, read_only=True)
        model = IRCChannel
        fields = '__all__'
        
class XDCCOfferSerializer(serializers.ModelSerializer):
    class Meta:
        channel = IRCChannelSerializer(many=False, read_only=True)
        model = XDCCOffer
        fields = '__all__'

# Permissions

class AdminOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff

# Pagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 9999
    
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['pageinfo'] = {
            'page': self.page.number,
            'num_pages': self.page.paginator.num_pages,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'num_objects': self.page.paginator.count,
        }
        return response 

# API Views

class IRCConnectionViewSet(ModelViewSet):
    permission_classes = [AdminOnlyPermission]
    pagination_class = StandardResultsSetPagination
    queryset = IRCConnection.objects.all()
    serializer_class = IRCConnectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['active', 'use_sasl', 'ssl']
    ordering_fields = ['server', 'active', 'created', 'updated']
    search_fields = ['server']
    
    
class IRCChannelViewSet(ModelViewSet):
    permission_classes = [AdminOnlyPermission]
    pagination_class = StandardResultsSetPagination
    queryset = IRCChannel.objects.all()
    serializer_class = IRCChannelSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['active']
    ordering_fields = ['channel', 'active', 'created', 'updated']
    search_fields = ['channel']
    
    
class XDCCOfferViewSet(ModelViewSet):
    permission_classes = [AdminOnlyPermission]
    pagination_class = StandardResultsSetPagination
    queryset = XDCCOffer.objects.all()
    serializer_class = XDCCOfferSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['channel', 'bot', 'pack_number']
    ordering_fields = ['channel', 'bot', 'pack_number', 'created', 'updated']
    search_fields = ['channel', 'bot', 'pack_name']
    
    
class RunningIRCConnectionsAPI(LoginRequiredMixin, APIView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    def get(self, request, format=None):
        app_config = apps.get_app_config('irc_xdcc_manager')
        if not hasattr(app_config, 'irc_clients'):
            return Response(status=404)
        irc_clients = app_config.irc_clients
        response = []
        for client in irc_clients:
            response.append({
                'server': client['server'],
                'config': client['client'].config
            })
        return Response(response)