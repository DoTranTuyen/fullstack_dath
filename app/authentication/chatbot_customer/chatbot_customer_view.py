from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.chatbot_customer.gemini_service_customer import CustomerChatbot


class CustomerChatAPI(APIView):
    def get(self, request):
        user_message = request.GET.get("message", "")
        print('user_message', user_message)
        if not user_message.strip():
            return Response({"error": "Message is required"}, status=400)

        bot = CustomerChatbot()
        reply = bot.ask(user_message)

        return Response({"reply": reply}, status=status.HTTP_200_OK)
