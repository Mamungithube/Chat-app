from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .backend import get_bondly_response

# Dummy user context (in production, fetch from DB or token)
USER_DATA = {
    "first_name": "Alex",
    "partner_names": "Jamie",
    "relationship_status": "partnered",
    "tone_preference": "warm & encouraging",
    "money_personality": "planner",
    "financial_goals": [
        {"type": "Save for house", "target_amount": 50000, "target_date": "2026-01-01", "saved_amount": 10000}
    ],
    "risk_profile": "moderate",
    "investment_timeline": "medium-term",
    "conflict_patterns": "some disagreements around budgeting",
    "granted_consents": {}
}

conversation_history = []  # For production, store per user/session

class BondlyChatAPIView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        global conversation_history  # 🔧 Declare global BEFORE using it

        response_text, updated_history = get_bondly_response(
        user_message,
        USER_DATA,
        conversation_history
        )

        conversation_history = updated_history


        return Response({"response": response_text})
