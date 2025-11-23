import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection and dynamically assign to groups based on notification type.
        """
        self.notification_type = self.scope['url_route']['kwargs']['notification_type']
        self.group_name = f"{self.notification_type}_notifications"

        print(f"WebSocket connected to group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Remove the WebSocket connection from the specified group on disconnect.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket data and process based on notification type.
        """
        print('text_data', text_data)
        data = json.loads(text_data)

        print('data', data)

        notification_data = await self.create_notification(data)

        # Sau khi tạo xong notification → broadcast
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "data": notification_data,
            },
        )

    async def send_notification(self, event):
        """
        Send notification to all WebSocket connections in the group.
        """
        print("Notified")
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Fetch user object by user ID.
        """
        from django.contrib.auth.models import User
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def create_notification(self, data):
        from web_01.models import Notification, Session
        notification_type = data['type']
        if (notification_type in ['product_status', 'end_session']):
            config = {
                'message': '',
                'level': '',
            }
            if (notification_type == 'end_session'):
                config['message'] = 'Kết thúc phiên bàn!'
                config['level'] = 'end_session'
            else:
                config['message'] = 'Cập nhật trạng thái đơn hàng!'
                config['level'] = 'product_status'
        else:

            session = Session.objects.get(id=data['session']['session_id'])

            table_number = session.table.table_number
            message_config = {
                'order_status': {
                    'message': f'Đơn hàng từ bàn {table_number} - {session.customer.user.first_name}.',
                    'level': 'info',
                },
                'promotion': {
                    'message': 'Ưu đãi mới vừa được cập nhật!',
                    'level': 'success',
                },
                'reminder': {
                    'message': f'Nhắc nhở cho bàn {table_number}.',
                    'level': 'warning',
                },
                'staff_call': {
                    'message': f'Bàn {table_number} cần hỗ trợ từ nhân viên.',
                    'level': 'info',
                },
                'custom': {
                    'message': data.get('message', '🔔 Thông báo tuỳ chỉnh.'),
                    'level': 'info',
                },
                'payment': {
                    'message': f'Thanh toán hoàn tất từ bàn {table_number} - {session.customer.user.first_name}.',
                    'level': 'success',
                },
                'session': {
                    'message': f'Kết thúc phiên bàn {table_number} - {session.customer.user.first_name}.',
                    'level': 'success',
                },
                'required_payment_cash': {
                    'message': f'Yêu cầu thanh toán bàn {table_number} - {session.customer.user.first_name}.',
                    'level': 'payment',
                },
            }

            notification_type = data.get('type', 'custom')
            config = message_config.get(notification_type, message_config['custom'])

            print('config', config)
            # Tạo notification trong DB (synchronous)
            Notification.objects.create(
                user=session.customer.user,
                type=notification_type,
                message=config['message'],
                data={
                    "session": session.id,
                    "extra_data": config
                }
            )

        return {
            'type': notification_type,
            'message': config.get('message'),
            'level': config.get('level'),
            "data": data
        }
