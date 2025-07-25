from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TripInputSerializer
import requests
from django.conf import settings

# Constants based on HOS rules
MAX_DRIVING_HOURS_PER_DAY = 11
MAX_ON_DUTY_HOURS_PER_DAY = 14
BREAK_AFTER_HOURS = 8
FUEL_EVERY_MILES = 1000
REST_DURATION_HOURS = 10
PICKUP_DROP_DURATION = 1
AVERAGE_SPEED = 60  # mph

def get_route_distance(pickup, dropoff):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": settings.MAP_API_KEY
    }
    params = {
        "start": get_coordinates(pickup),
        "end": get_coordinates(dropoff)
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        meters = data['features'][0]['properties']['summary']['distance']
        return round(meters / 1609.34)  # convert meters to miles
    return 0

def get_coordinates(location_name):
    geo_url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": settings.MAP_API_KEY,
        "text": location_name,
        "size": 1
    }

    response = requests.get(geo_url, params=params)
    if response.status_code == 200:
        data = response.json()
        coords = data['features'][0]['geometry']['coordinates']
        return f"{coords[0]},{coords[1]}"  # lon,lat for ORS
    return "0,0"

def calculate_trip_schedule(distance, hours_used):
    DAILY_DRIVE_LIMIT = 11
    DAILY_ON_DUTY_LIMIT = 14
    WEEKLY_LIMIT = 70  # Max 70 hours on-duty in 8 days

    # Check if hours used already exceeds the weekly limit
    if hours_used >= WEEKLY_LIMIT:
        return {
            "error": "You have exceeded the 70-hour limit for an 8-day period. Please reset before starting a new trip.",
            "schedule": [],
            "total_miles": distance,
            "fuel_stops": [],
            "pickup_duration": 1,
            "dropoff_duration": 1
        }

    avg_speed = 60  # miles per hour
    driving_hours_needed = distance / avg_speed

    # Ensure calc is within the remaining hours
    remaining_hours = WEEKLY_LIMIT - hours_used

    if driving_hours_needed > remaining_hours:
        return {
            "error": "You do not have enough available hours to complete this trip. Please take a 34-hour reset or reduce trip distance.",
            "schedule": [],
            "total_miles": distance,
            "fuel_stops": [],
            "pickup_duration": 1,
            "dropoff_duration": 1
        }
    days = 0
    schedule = []
    remaining_driving = driving_hours_needed

    while remaining_driving > 0 and remaining_hours > 0:
        drive_today = min(DAILY_DRIVE_LIMIT, remaining_driving, remaining_hours)
        on_duty_today = min(DAILY_ON_DUTY_LIMIT, remaining_hours)

        schedule.append({
            "day": days + 1,
            "driving_hours": round(drive_today, 2),
            "breaks": 1 if drive_today > 5 else 0,
            "total_on_duty": round(on_duty_today, 2)
        })

        remaining_hours -= on_duty_today
        remaining_driving -= drive_today
        days += 1

    # Fuel stop every 1000 miles
    fuel_stops = [i for i in range(1000, int(distance), 1000)]

    return {
        "schedule": schedule,
        "total_miles": distance,
        "fuel_stops": fuel_stops,
        "pickup_duration": 1,
        "dropoff_duration": 1
    } 

@api_view(['POST'])
def trip_plan_view(request):
    serializer = TripInputSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        # Get coordinates (returned as "lon,lat" string)
        pickup_coords = get_coordinates(data['pickup_location']).split(',')
        dropoff_coords = get_coordinates(data['dropoff_location']).split(',')

        # Route distance in miles
        total_distance = get_route_distance(data['pickup_location'], data['dropoff_location'])
        hours_used = data['hours_used']

        # Generate trip plan
        result = calculate_trip_schedule(total_distance, hours_used)

        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # Add coordinates for frontend map (lat, lon)
        result['pickup_coords'] = [float(pickup_coords[1]), float(pickup_coords[0])]
        result['dropoff_coords'] = [float(dropoff_coords[1]), float(dropoff_coords[0])]

        return Response(result)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
