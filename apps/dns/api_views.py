from rest_framework import generics, serializers
from .models import Domain, DomainPayment


class DomainPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DomainPayment
        fields = ('id', 'paid_date', 'amount_usd', 'paid_by', 'notes')


class DomainSerializer(serializers.ModelSerializer):
    site_name      = serializers.CharField(source='site.name',      read_only=True)
    registrar_name = serializers.CharField(source='registrar.name', read_only=True)
    status         = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    payments       = DomainPaymentSerializer(many=True, read_only=True)

    class Meta:
        model  = Domain
        fields = '__all__'


class DomainListView(generics.ListCreateAPIView):
    serializer_class = DomainSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = Domain.objects.select_related('site', 'registrar').prefetch_related('payments')
        site_id = self.request.query_params.get('site')
        if site_id:
            qs = qs.filter(site_id=site_id)
        elif not user.is_admin:
            qs = qs.filter(site__in=user.get_accessible_sites())
        return qs.order_by('site__name', 'name')


class DomainDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all()
