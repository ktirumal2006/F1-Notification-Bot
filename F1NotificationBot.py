import json
import boto3
import requests
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
    
    today = datetime.utcnow().date()
    next_sunday = today + timedelta((6 - today.weekday()) % 7)  # Sunday of this week
    
    print("Today (UTC):", today)
    print("Checking races up to:", next_sunday)
    
    # Get 2025 F1 meetings from OpenF1 API
    try:
        races = get_f1_races_2025()
        print(f"Found {len(races)} races for 2025:")
        for race in races:
            print(f"{race['raceName']} → {race['date']}")
    except Exception as e:
        print(f"Error fetching races from OpenF1 API: {e}")
        # Fallback to manual list if API fails
        races = get_fallback_races()
        print("Using fallback race list")
    
    # Check for race between now and Sunday
    race_this_weekend = None
    for race in races:
        race_date = datetime.strptime(race['date'], "%Y-%m-%d").date()
        if today <= race_date <= next_sunday:
            race_this_weekend = race
            break
    
    if race_this_weekend:
        sns = boto3.client('sns')
        message = f"🏁 Race this weekend: {race_this_weekend['raceName']} on {race_this_weekend['date']}"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🏁 F1 Race Alert",
            Message=message
        )
        print("Alert Sent Via SNS")
    else:
        print("🚫 No race this weekend.")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Check complete.')
    }

def get_f1_races_2025():
    """
    Fetch 2025 F1 races from OpenF1 API
    """
    # Get all 2025 meetings
    meetings_url = "https://api.openf1.org/v1/meetings?year=2025"
    
    response = requests.get(meetings_url, timeout=10)
    response.raise_for_status()
    meetings = response.json()
    
    races = []
    for meeting in meetings:
        # Get race sessions for this meeting
        sessions_url = f"https://api.openf1.org/v1/sessions?meeting_key={meeting['meeting_key']}&session_name=Race"
        
        sessions_response = requests.get(sessions_url, timeout=10)
        sessions_response.raise_for_status()
        sessions = sessions_response.json()
        
        if sessions:  # If there's a race session
            race_session = sessions[0]  # Take the first (should be only) race session
            
            # Convert UTC datetime to date
            race_datetime = datetime.fromisoformat(race_session['date_start'].replace('Z', '+00:00'))
            race_date = race_datetime.strftime("%Y-%m-%d")
            
            races.append({
                "raceName": meeting['meeting_name'],
                "date": race_date,
                "location": meeting['location'],
                "country": meeting['country_name'],
                "meeting_key": meeting['meeting_key']
            })
    
    # Sort races by date
    races.sort(key=lambda x: x['date'])
    return races

def get_fallback_races():
    """
    Fallback race list in case OpenF1 API is unavailable
    This should be updated with the confirmed 2025 calendar
    """
    return [
        {"raceName": "Bahrain Grand Prix", "date": "2025-03-16"},
        {"raceName": "Saudi Arabian Grand Prix", "date": "2025-03-23"}, 
        {"raceName": "Australian Grand Prix", "date": "2025-04-06"},
        {"raceName": "Chinese Grand Prix", "date": "2025-04-20"},
        {"raceName": "Miami Grand Prix", "date": "2025-05-04"},
        {"raceName": "Emilia Romagna Grand Prix", "date": "2025-05-18"},
        {"raceName": "Monaco Grand Prix", "date": "2025-05-25"},
        {"raceName": "Spanish Grand Prix", "date": "2025-06-01"},
        {"raceName": "Canadian Grand Prix", "date": "2025-06-15"},
        {"raceName": "Austrian Grand Prix", "date": "2025-06-29"},
        {"raceName": "British Grand Prix", "date": "2025-07-06"},
        {"raceName": "Belgian Grand Prix", "date": "2025-07-27"},
        {"raceName": "Hungarian Grand Prix", "date": "2025-08-03"},
        {"raceName": "Dutch Grand Prix", "date": "2025-08-31"},
        {"raceName": "Italian Grand Prix", "date": "2025-09-07"},
        {"raceName": "Azerbaijan Grand Prix", "date": "2025-09-21"},
        {"raceName": "Singapore Grand Prix", "date": "2025-10-05"},
        {"raceName": "United States Grand Prix", "date": "2025-10-19"},
        {"raceName": "Mexican Grand Prix", "date": "2025-10-26"},
        {"raceName": "Brazilian Grand Prix", "date": "2025-11-09"},
        {"raceName": "Las Vegas Grand Prix", "date": "2025-11-22"},
        {"raceName": "Qatar Grand Prix", "date": "2025-11-30"},
        {"raceName": "Abu Dhabi Grand Prix", "date": "2025-12-07"}
    ]