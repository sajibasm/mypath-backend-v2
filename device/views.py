from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import SessionData, SensorData
from .utils.crypto import encrypt_session_id, decrypt_session_id
from .models import SessionData
from collections import defaultdict
from dateutil.relativedelta import relativedelta  # pip install python-dateutil


class MonthlySessionSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.today()
        months = []

        # Accurate month stepping: current month and previous 5
        for i in range(5, -1, -1):  # Oldest → Newest
            month_date = today - relativedelta(months=i)
            months.append((month_date.year, month_date.month))

        # Filter from the start of the oldest month
        oldest_year, oldest_month = months[0]
        oldest_start = datetime(oldest_year, oldest_month, 1)
        oldest_start_ts_ms = int(oldest_start.timestamp() * 1000)

        sessions = SessionData.objects.filter(start_timestamp__gte=oldest_start_ts_ms)

        # Count sessions by (year, month)
        month_count = defaultdict(int)
        for session in sessions:
            try:
                dt = datetime.fromtimestamp(session.start_timestamp / 1000)
                key = (dt.year, dt.month)
                month_count[key] += 1
            except Exception:
                continue

        # Build clean summary
        summary = []
        for year, month in months:
            label = datetime(year, month, 1).strftime("%b")
            summary.append({
                "month": label,
                "count": month_count.get((year, month), 0)
            })

        return Response(summary)


class SessionSummaryReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.today().date()
        start_date = today - timedelta(days=29)

        start_timestamp_ms = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)

        # Query sessions in the last 30 days (based on milliseconds)
        sessions = SessionData.objects.filter(start_timestamp__gte=start_timestamp_ms)

        # Group and count by date
        date_count = defaultdict(int)
        for session in sessions:
            try:
                session_date = datetime.fromtimestamp(session.start_timestamp / 1000).date()
                date_count[session_date] += 1
            except Exception:
                continue

        # Construct 30-day summary with formatted date string
        summary = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            formatted_date = day.strftime("%b %d")  # e.g., "Apr 28"
            summary.append({
                "date": formatted_date,
                "count": date_count.get(day, 0)
            })

        return Response(summary)


class SessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        data = request.data

        wheelchair_id = data.get('wheelchair_id')
        start_timestamp = data.get('start_timestamp')
        end_timestamp = data.get('end_timestamp')
        version = 'v2.0'  # Optional, defaults to "old"

        if not wheelchair_id:
            return Response({"error": "wheelchair_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not start_timestamp or not end_timestamp:
            return Response({"error": "start_timestamp and end_timestamp are required."}, status=status.HTTP_400_BAD_REQUEST)

        session = SessionData(
            user_id=user_id,
            wheelchair_id=wheelchair_id,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            version=version
        )

        session.save()  # This sets duration_ms too

        encrypted_id = encrypt_session_id(session.id)

        return Response({
            "sensor_session_id": encrypted_id,
            "version": session.version,
            "message": "Session created successfully."
        }, status=status.HTTP_201_CREATED)

class SensorUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        encrypted_session_id = data.get("sensor_session_id")
        sensor_batch = data.get("data", [])

        if not encrypted_session_id:
            return Response({"error": "Missing 'event' (encrypted session ID)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session_id = decrypt_session_id(encrypted_session_id)
        except Exception:
            return Response({"error": "Invalid session ID."}, status=status.HTTP_400_BAD_REQUEST)

        if not SessionData.objects.filter(id=session_id).exists():
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if not sensor_batch:
            return Response({"error": "No sensor data provided."}, status=status.HTTP_400_BAD_REQUEST)

        session_id_str = int(session_id)  # Because event is stored as CharField

        sensor_objects = []
        for item in sensor_batch:
            sensor_objects.append(SensorData(
                timestamp=item.get("timestamp", ""),
                event=session_id_str,
                session_id=session_id_str,
                accel_x=item.get("accel_x", ""),
                accel_y=item.get("accel_y", ""),
                accel_z=item.get("accel_z", ""),
                gyro_x=item.get("gyro_x", ""),
                gyro_y=item.get("gyro_y", ""),
                gyro_z=item.get("gyro_z", ""),
                mag_x=item.get("mag_x", ""),
                mag_y=item.get("mag_y", ""),
                mag_z=item.get("mag_z", ""),
                latitude=item.get("latitude", ""),
                longitude=item.get("longitude", ""),
                pressure=item.get("pressure", ""),
                speed=item.get("speed", "")
            ))

        SensorData.objects.bulk_create(sensor_objects, batch_size=500)
        # Count records for this session ID (as stored in `event`)
        total_records = SensorData.objects.filter(session_id=session_id_str).count()

        return Response({
            "message": "Sensor data saved successfully.",
            "records_added": len(sensor_objects),
            "total_records": total_records
        }, status=status.HTTP_201_CREATED)