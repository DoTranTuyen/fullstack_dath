from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from web_01.models import Table, Session, Customer
from authentication.serializers import TableSerializer, TableReservationSerializer, TableReservation
from django.utils.timezone import now


class TableViewSet(ViewSet):
    """API quản lý bàn trong nhà hàng"""

    @action(detail=False, methods=['get'], url_path='list')
    def list_tables(self, request):
        """
        📌 Lấy danh sách bàn, có thể lọc theo trạng thái
        - `status`: Lọc theo trạng thái ('available', 'occupied', 'reserved')
        - Loại bỏ bàn có đặt trước với trạng thái [pending, confirmed]
        """
        status_filter = request.query_params.get('status', None)

        # Prefetch reservations để tối ưu truy vấn ManyToOne
        tables = Table.objects.all().prefetch_related("reservations")

        # # Loại bỏ bàn có đặt trước với trạng thái "pending" hoặc "confirmed"
        # tables = tables.exclude(reservations__status__in=["pending", "confirmed"]).distinct()

        # Lọc theo trạng thái nếu có request
        if status_filter:
            tables = tables.filter(status=status_filter)

        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TableReservationViewSet(ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer

    def create(self, request, *args, **kwargs):
        """Tạo đơn đặt bàn mới"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            table_id = serializer.validated_data['table'].id
            date = serializer.validated_data['date']
            phone_number = request.data.get("phone_number")

            existing_reservation = TableReservation.objects.filter(phone_number=phone_number, status__in=['pending', 'confirmed']).first()
            if existing_reservation:
                return Response(
                    {"message": "Bạn đã có đặt bàn và đây là chi tiết bàn của bạn!", "reservation": TableReservationSerializer(existing_reservation).data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Kiểm tra bàn đã đặt chưa
            if TableReservation.objects.filter(table_id=table_id, date=date, status__in=['pending', 'confirmed']).exists():
                return Response({"error": f"Bàn này đã được đặt bàn ngày {date}"}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            return Response({
                "message": "Đặt bàn thành công!",
                "reservation": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Hủy đặt bàn"""
        instance = self.get_object()

        # Nếu trạng thái đang chờ xác nhận thì cho phép hủy
        if instance.status == "pending":
            instance.status = "cancelled"
            instance.save()

            # Serialize dữ liệu đặt bàn sau khi hủy
            serializer = TableReservationSerializer(instance)

            return Response(
                {
                    "message": "Hủy đặt bàn thành công!",
                    "reservation": serializer.data  # Trả về thông tin đặt bàn đã hủy
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Bạn không thể hủy đặt bàn được! Xin hãy liên hệ chúng tôi"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='by-phone')
    def get_by_phone(self, request):
        """
        📌 Lấy chi tiết đặt bàn theo số điện thoại
        - Truyền `phone_number` qua query params: `/api/tables/reservations/by-phone/?phone_number=0987654321`
        """
        phone_number = request.query_params.get("phone_number")
        if not phone_number:
            return Response({"message": "Vui lòng cung cấp số điện thoại!"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = TableReservation.objects.filter(phone_number=phone_number, status__in=['pending', 'confirmed']).first()
        if not reservation:
            return Response({"message": "Không tìm thấy đặt bàn nào với số điện thoại này!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TableReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
