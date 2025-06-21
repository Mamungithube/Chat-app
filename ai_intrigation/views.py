from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ai_intrigation.predictor import make_prediction

class PredictAPIView(APIView):
    def post(self, request):
        try:
            features = request.data.get("features")
            if not features:
                return Response({"error": "Features are required"}, status=400)

            prediction = make_prediction(features)
            return Response({"prediction": prediction})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
