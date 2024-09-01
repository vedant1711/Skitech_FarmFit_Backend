from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os
import pickle
import pandas as pd
from Skitech_FarmFit_Backend.settings import BASE_DIR
from statistics import mean
from dotenv import load_dotenv


load_dotenv()

def crop_classifier():
    model_path = os.path.join(BASE_DIR, 'app/utils/models/RandomForest.pkl')
    crop_recommendation_model = pickle.load(open(model_path, 'rb'))
    return crop_recommendation_model


def weather_fetch(lat, long):
    """
    Fetch and return the temperature, humidity, and average rainfall of a location.
    :param long: longitude
    :param lat: latitude
    :return: Tuple of (temperature, humidity, avg_rainfall) or None if there is an error
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/3.0/onecall?"
    complete_url = f"{base_url}lat={lat}&lon={long}&exclude=minutely,current,hourly&appid={api_key}"
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        # Get current temperature and humidity from the first day's data
        current_data = data["daily"][0]
        temperature = round((current_data["temp"]["day"] - 273.15), 2)  # Convert from Kelvin to Celsius
        humidity = current_data["humidity"]

        # Calculate average rainfall for the next 7 days
        rainfall_data = [day.get("rain", 0) for day in
                         data["daily"][:7]]  # Get rain data for 7 days, default to 0 if no rain
        avg_rainfall = round(mean(rainfall_data), 2)

        return temperature, humidity, avg_rainfall

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


class CropRecommendationAPIView(APIView):

    def post(self, request):
        data = request.data
        lat = data.get('lat')
        long = data.get('long')
        N = data.get('N')
        P = data.get('P')
        K = data.get('K')
        ph = data.get('ph')

        weather_data = weather_fetch(lat, long)
        if weather_data:
            temperature, humidity, rainfall = weather_data
            feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=feature_names)
            prediction = crop_classifier().predict(data)
            return Response({
                'prediction': prediction[0],
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to fetch weather data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)