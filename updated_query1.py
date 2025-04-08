import pandas as pd
import requests
import time  # For sleep functionality

# Load the top5_healthcare CSV file
file_path = "/Users/paridhiagarwal/dse3101-LTAProject/top5_healthcare.csv"
df = pd.read_csv(file_path)

# Filter the dataset to include specific ows 

df = df.iloc[insert rows here>]

# API endpoint
base_url = "https://www.onemap.gov.sg/api/public/routingsvc/route"

# Authorization header
headers = {
    "Authorization": "<insert api here>"
}

# Time string to period name and peak status mapping
time_mapping = {
    "06:30:00": ("Non-peak Morning", "Non Peak"),
    "08:30:00": ("Morning Peak", "Peak"),
    "10:45:00": ("Non-peak Late Morning", "Non Peak"),
    "13:00:00": ("Lunch Peak", "Peak"),
    "15:30:00": ("Non-peak Afternoon", "Non Peak"),
    "18:30:00": ("Evening Peak", "Peak"),
    "21:00:00": ("Non-peak Evening", "Non Peak"),
    "23:30:00": ("Late Night Non-peak", "Non Peak")
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

    # Day configurations (dummy values)
    day_configs = [
        ("03-19-2025", "Weekday"),
        ("03-22-2025", "Weekend"),
        ("08-09-2025", "Public Holiday")
    ]

    # Full time configurations with dummy values for Peak, Weekday, Weekend, Public Holiday
    time_configs = []
    for date, day_type in day_configs:
        for time_str in time_mapping:
            period_name, peak_status = time_mapping[time_str]
            peak_binary = 1 if peak_status == "Peak" else 0
            time_configs.append((date, time_str, day_type, period_name, peak_status, peak_binary))

    for date, time_str, day_type, period_name, peak_status, peak in time_configs:
        query_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date={date}&time={time_str}&mode=TRANSIT&numItineraries=1"
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

                    # Append results with dummy values for Peak, Weekday, Weekend, and Public Holiday
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
                        "Heuristic Distance (km)": heuristic_dist,
                        "Day Type": day_type,
                        "Period Name": period_name,
                        "Peak Hour": peak_binary,  # 0 for non-peak, 1 for peak
                        "Time": time_str,  # Time
                        "Weekday": 1 if day_type == "Weekday" else 0,  # Dummy value for Weekday
                        "Weekend": 1 if day_type == "Weekend" else 0,  # Dummy value for Weekend
                        "Public Holiday": 1 if day_type == "Public Holiday" else 0  # Dummy value for Public Holiday
                    })

                    print(f"Route {index}: {subzone_name} -> {hospital_name}, Duration: {duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}, Period = {period_name}, Time = {time_str}, Peak = {peak_status}, Weekday = {1 if day_type == 'Weekday' else 0}, Weekend = {1 if day_type == 'Weekend' else 0}, Public Holiday = {1 if day_type == 'Public Holiday' else 0}")

        time.sleep(1)  # To avoid rate limits

# Convert results into a DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
output_path = "/Users/paridhiagarwal/dse3101-LTAProject/<Query_name>.csv"
results_df.to_csv(output_path, index=False)
print(f"Results saved to {output_path}")

