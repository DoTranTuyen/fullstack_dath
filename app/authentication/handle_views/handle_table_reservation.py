from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import TableSerializer, TableReservation, BookTableSerializer
from django.utils.timezone import now

class BookaTableViewSet(ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = BookTableSerializer

    def create(self, request, *args, **kwargs):
        """📌 API tạo đơn đặt bàn"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            many_person = serializer.validated_data['many_person']
            date = serializer.validated_data['date']
            hour = serializer.validated_data['hour']
            phone_number = serializer.validated_data['phone_number']
            table = serializer.validated_data.get('table', None) 

            # ✅ Kiểm tra người dùng đã đặt bàn chưa (đang chờ hoặc đã xác nhận)
            existing_reservation = TableReservation.objects.filter(
                phone_number=phone_number,
                date=date,
                status__in=['pending', 'confirmed']
            ).first()
            if existing_reservation:
                return Response(
                    {
                        "message": "Bạn đã có đặt bàn và đây là chi tiết bàn của bạn!",
                        "reservation": BookTableSerializer(existing_reservation).data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Kiểm tra bàn đã bị đặt cùng ngày chưa
            if TableReservation.objects.filter(
                table=table,
                name=name,
                many_person=many_person,
                date=date,
                hour=hour,
                status__in=['pending', 'confirmed']
            ).exists():
                return Response(
                    {"error": f"Bàn này đã được đặt vào ngày {date} lúc {hour}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Lưu đặt bàn mới
            self.perform_create(serializer)
            return Response(
                {
                    "message": "Đặt bàn thành công!",
                    "reservation": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
