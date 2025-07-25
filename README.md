# 🧠 ELD Log API (Django Backend)

This is the backend API built with **Django REST Framework** for the Spotter AI full-stack assessment. It calculates FMCSA-compliant trip plans for truck drivers using pickup and dropoff locations, hours used, and generates:

- Daily driving schedules
- Error messages if driver exceeds allowed on-duty hours
- GPS coordinates for mapping
- Support for 70-hour weekly HOS logic

---

## 🚀 Features

- Function-based Django views with `@api_view`
- Geocoding via Heigit API
- Distance routing between addresses
- FMCSA-compliant trip planner
- Clear error messages for time-limit violations

---

## ⚙️ Tech Stack

- Django
- Django REST Framework
- Python
- Requests
- CORS Headers

---

## 🧪 API Endpoint

POST /api/trip/plan/

**Request:**

```json
{
  "current_location": "Atlanta, GA",
  "pickup_location": "Nashville, TN",
  "dropoff_location": "Chicago, IL",
  "hours_used": 12
}

Response:

{
  "schedule": [...],
  "total_miles": 470,
  "pickup_coords": [36.236907, -86.834683],
  "dropoff_coords": [41.87897, -87.66063],
  "fuel_stops": [1000],
  "pickup_duration": 1,
  "dropoff_duration": 1
}

Error Example

{
  "error": "You do not have enough available hours to complete this trip. Please take a 34-hour reset or reduce trip distance."
}

---
Setup Instructions

git clone https://github.com/Dannyurfavdev/eldlogs.git
cd eldlogs
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

# Set your API key
export MAP_API_KEY=your_key_here

# Run server
python manage.py runserver

---
Live API URL

https://eldlogs-xkka.onrender.com/api/trip/plan/

---
Loom Video Walkthrough

https://loomvideo
