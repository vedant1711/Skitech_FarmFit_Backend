from rest_framework.response import Response
from rest_framework.views import APIView
from app.serializers import WeatherDataSerializer


class WeatherInsightsView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = WeatherDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        temperature = data['temperature']
        wind_speed = data['wind_speed']
        humidity = data['humidity']
        pressure = data['pressure']

        actionable_insight = self.get_actionable_insight(temperature, wind_speed, humidity, pressure)

        return Response({"actionable_insight": actionable_insight})

    def get_actionable_insight(self, temperature, wind_speed, humidity, pressure):
        if temperature < 20 and wind_speed < 1.5 and humidity > 80 and pressure < 1000:
            return "No need to water your crops right now as the soil is already wet. Wait to spray any chemicals or pesticides since they might not work well in this weather."

        if 20 <= temperature <= 30 and wind_speed < 1.5 and 50 <= humidity <= 80 and 1000 <= pressure <= 1015:
            return "This is a good time to plant seeds. Keep an eye out for weeds, as they may grow quickly in this weather."

        if temperature > 30 and 1.5 <= wind_speed <= 5 and humidity < 50 and pressure > 1015:
            return "Water your crops more often as the hot weather can dry them out quickly. Use a layer of straw or leaves on the soil to keep it cool and moist."

        if temperature > 30 and wind_speed > 5 and 50 <= humidity <= 80 and pressure < 1000:
            return "Don’t spray pesticides or fertilizers now, as the wind might blow them away. Protect your young plants from strong winds by using barriers or planting trees."

        if temperature < 20 and wind_speed > 5 and humidity > 80 and 1000 <= pressure <= 1015:
            return "Cover your crops early in the morning to protect them from cold weather. Watch out for diseases in your crops due to the wet and cold weather."

        if 20 <= temperature <= 30 and 1.5 <= wind_speed <= 5 and 50 <= humidity <= 80 and pressure < 1000:
            return "Don’t harvest your fruits or vegetables now; they might spoil quickly in this humid weather. Make sure your storage areas are dry and airy to prevent mold."

        if temperature > 30 and wind_speed < 1.5 and humidity < 50 and 1000 <= pressure <= 1015:
            return "Use drip irrigation to save water and ensure your crops get enough moisture. Avoid digging or plowing the soil right now, as it might dry out quickly."

        if 20 <= temperature <= 30 and wind_speed > 5 and humidity < 50 and pressure > 1015:
            return "Protect your soil from being blown away by the wind. You can plant trees or use windbreaks. Water your crops more often to keep the soil moist."

        if temperature < 20 and wind_speed < 1.5 and 50 <= humidity <= 80 and pressure > 1015:
            return "This weather is good for moving small plants from one place to another. Water your crops lightly, just enough to keep the soil from drying out."

        if temperature > 30 and 1.5 <= wind_speed <= 5 and humidity > 80 and pressure < 1000:
            return "Don’t spray any chemicals on your crops right now; they might wash away. Harvest your crops early in the morning before it gets too hot."

        return "No specific actionable insights available for the given weather conditions."
