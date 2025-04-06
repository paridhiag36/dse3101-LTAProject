# import requests
# url = "https://www.onemap.gov.sg/api/public/routingsvc/route?start=1.320981%2C103.844150&end=1.326762%2C103.8559&routeType=pt&date=08-13-2023&time=07%3A35%3A00&mode=TRANSIT&maxWalkDistance=1000&numItineraries=1"
    
# headers = {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ZDliMDU5ODk1NjZkMTc4OGY5MTQ5NGM0ZTFkZWEwMCIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9wYXNzd29yZCIsImlhdCI6MTc0MjE5ODkxMiwiZXhwIjoxNzQyNDU4MTEyLCJuYmYiOjE3NDIxOTg5MTIsImp0aSI6IndBT3ZBYUM1SmI4UWxBWWYiLCJ1c2VyX2lkIjo2NDA0LCJmb3JldmVyIjpmYWxzZX0.mS32yNePZes-de8gJ3uDRkmqQKRn-z0p3gavtUc6y0U"}
    
# response = requests.request("GET", url, headers=headers)
    
# print(response.text)

import pandas as pd
import requests
import time  # For sleep functionality

# Load the top5_healthcare CSV file
file_path = "/Users/paridhiagarwal/dse3101-LTAProject/top5_healthcare.csv"
df = pd.read_csv(file_path)

# Filter the dataset to include rows 581 to 1080 only, planning areas from Jurong East to Queenstown
df = df.iloc[580:1080]

# API endpoint
base_url = "https://www.onemap.gov.sg/api/public/routingsvc/route"

# Authorization header
headers = {
    "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1ZDdkYzYyYWZmMDI0ZWU2NGIzZmY1MjMwYTJhYzUxMSIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9wYXNzd29yZCIsImlhdCI6MTc0MzkxNDY0NywiZXhwIjoxNzQ0MTczODQ3LCJuYmYiOjE3NDM5MTQ2NDcsImp0aSI6IkRpRjBaT3pNd0hiYXJaMXQiLCJ1c2VyX2lkIjo2MDY1LCJmb3JldmVyIjpmYWxzZX0.jgu0H2SoAIMP8v217jCwminx79X3PjOYwFZiYuf_gSI"
}

# Create an empty list to store results
results = []

# Loop through each row
for index, row in df.iterrows():
    planning_area_name = row["Planning_Area"]
    start_lat, start_long = row["Subzone_Lat"], row["Subzone_Long"]
    end_lat, end_long = row["Hospital_Polyclinic_Lat"], row["Hospital_Polyclinic_Long"]
    subzone_name = row["Subzone"]
    hospital_name = row["Hospital_Polyclinic"]  
    heuristic_dist = row["Distance_km"]
    
    # Time configurations, weekday, weekend, non-peak and peak hours
    time_configs = [
        ("03-19-2025", "15:00:00", 0, 0),  # Weekday non-peak
        ("03-19-2025", "18:00:00", 0, 1),  # Weekday peak
        ("03-22-2025", "15:00:00", 1, 0),  # Weekend non-peak
        ("03-22-2025", "18:00:00", 1, 1)   # Weekend peak
    ]
    
    for date, time_str, weekend, peak in time_configs:
        query_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date={date}&time={time_str}&mode=TRANSIT&numItineraries=3"
        response = requests.get(query_url, headers=headers)
        
        if response.status_code == 429:
            print(f"Rate limit exceeded at row {index}. Retrying in 60s...")
            time.sleep(60)
            response = requests.get(query_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "plan" in data and "itineraries" in data["plan"]:
                for itinerary in data["plan"]["itineraries"]:
                    duration_minutes = round(itinerary.get("duration", 0) / 60, 2)
                    walk_time_minutes = round(itinerary.get("walkTime", 0) / 60, 2)
                    transit_time_minutes = round(itinerary.get("transitTime", 0) / 60, 2)
                    walk_distance = itinerary.get("walkDistance", 0)
                    transfers = itinerary.get("transfers", 0)
                    
                    results.append({
                        "Planning_Area": planning_area_name,
                        "Subzone": subzone_name,
                        "Subzone_Lat": start_lat,
                        "Subzone_Long": start_long,
                        "Hospital_Polyclinic": hospital_name,
                        "Hospital_Polyclinic_Lat": end_lat,
                        "Hospital_Polyclinic_Long": end_long,
                        "Duration (min)": duration_minutes,
                        "WalkTime (min)": walk_time_minutes,
                        "WalkDistance (m)": walk_distance,
                        "Transfers": transfers,
                        "TransitTime (min)": transit_time_minutes,
                        "Heuristic Distance (km)" : heuristic_dist,
                        "Weekend": weekend,
                        "Peak Hour": peak
                    })
                    
                    print(f"Route {index}: {subzone_name} -> {hospital_name}, Duration: {duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}")
        
        time.sleep(1)  # Avoid rate limits

# Convert results into a DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
output_path = "/Users/paridhiagarwal/dse3101-LTAProject/healthcare_query2.csv"
results_df.to_csv(output_path, index=False)
print(f"Results saved to {output_path}")
