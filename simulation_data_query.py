# import requests
# url = "https://www.onemap.gov.sg/api/public/routingsvc/route?start=1.320981%2C103.844150&end=1.326762%2C103.8559&routeType=pt&date=08-13-2023&time=07%3A35%3A00&mode=TRANSIT&maxWalkDistance=1000&numItineraries=1"
    
# headers = {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ZDliMDU5ODk1NjZkMTc4OGY5MTQ5NGM0ZTFkZWEwMCIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9wYXNzd29yZCIsImlhdCI6MTc0MjE5ODkxMiwiZXhwIjoxNzQyNDU4MTEyLCJuYmYiOjE3NDIxOTg5MTIsImp0aSI6IndBT3ZBYUM1SmI4UWxBWWYiLCJ1c2VyX2lkIjo2NDA0LCJmb3JldmVyIjpmYWxzZX0.mS32yNePZes-de8gJ3uDRkmqQKRn-z0p3gavtUc6y0U"}
    
# response = requests.request("GET", url, headers=headers)
    
# print(response.text)

import pandas as pd
import requests
import time  # For sleep functionality

# Load the top5_healthcare CSV file
file_path = "top5_healthcare.csv"
df = pd.read_csv(file_path)

# Filter the dataset to include rows 1 to 580 only, planning areas from Ang Mo Kio to Hougang.
#df = df.iloc[1500:]



base_url = "https://www.onemap.gov.sg/api/public/routingsvc/route"

# Authorization header
headers = {
    "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlNzM2ODg3M2I3OGIzNmEwOTFhOGU5YjQ4YzdmODk1MyIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9zZXNzaW9uIiwiaWF0IjoxNzQ0MDMwOTA1LCJleHAiOjE3NDQyOTAxMDUsIm5iZiI6MTc0NDAzMDkwNSwianRpIjoidjJIdDBNbTNyQVZpMXhORyIsInVzZXJfaWQiOjYwMjIsImZvcmV2ZXIiOmZhbHNlfQ.Ozauv6MNmsjCdS78_8sKxM7GsAIOL9MpqLElwxT_aCI",
  "expiry_timestamp": "1744290105" }

# Create an empty list to store results
results = []
# Loop through each row


def f(x):
    return x['transitLeg']
counter=0
for index, row in df.iterrows():

    counter+=1
    print(counter)


    
    planning_area_name = row["Planning_Area"]
    start_lat, start_long = row["Subzone_Lat"], row["Subzone_Long"]
    end_lat, end_long = row["Hospital_Polyclinic_Lat"], row["Hospital_Polyclinic_Long"]
    subzone_name = row["Subzone"]
    hospital_name = row["Hospital_Polyclinic"]  
    heuristic_dist = row["Distance_km"]


    
    # Time configurations, weekday, weekend, non-peak and peak hours
    
    date="03-19-2025"
    time_str= "15:00:00"
    weekend=0
    peak=0
    
    
    query_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date={date}&time={time_str}&mode=TRANSIT&numItineraries=1"
    response = requests.get(query_url, headers=headers)
        
    if response.status_code == 429:
        print(f"Rate limit exceeded at row {index}. Retrying in 60s...")
        time.sleep(60)
        response = requests.get(query_url, headers=headers)
        
    if response.status_code == 200:
        data = response.json()

        
        if "plan" in data and "itineraries" in data["plan"]:
            itinerary_num=0
            for itinerary in data["plan"]["itineraries"]:
                
                
                duration_minutes = round(itinerary.get("duration", 0) / 60, 2)
                walk_time_minutes = round(itinerary.get("walkTime", 0) / 60, 2)
                transit_time_minutes = round(itinerary.get("transitTime", 0) / 60, 2)
                walk_distance = itinerary.get("walkDistance", 0)
                transfers = itinerary.get("transfers", 0)
                
                row={"Planning_Area": planning_area_name,
                        "Subzone": subzone_name,
                        "Subzone_Lat": start_lat,
                        "Subzone_Long": start_long,
                        "Hospital_Polyclinic": hospital_name,
                        "Hospital_Polyclinic_Lat": end_lat,
                        "Hospital_Polyclinic_Long": end_long,
                        "itinerary_num": itinerary_num,
                        "Duration (min)": duration_minutes,
                        "WalkTime (min)": walk_time_minutes,
                        "WalkDistance (m)": walk_distance,
                        "Transfers": transfers,
                        "TransitTime (min)": transit_time_minutes,
                    }
                
                itinerary_num+=1
                if 'legs' in itinerary:
                    transit_leg = list(map(f, itinerary['legs']))
                    
                    if len(transit_leg)>0 and transit_leg is not None and any(transit_leg):
                        first_true = next((i for i, value in enumerate(transit_leg) if value), None)
                        last_true = len(transit_leg) - 1 - next((i for i, value in enumerate(reversed(transit_leg)) if value), None)
                        first_type= itinerary['legs'][first_true]['mode']
                        last_type=itinerary['legs'][last_true]['mode']

                        row['first_type']=first_type
                        row['last_type']=last_type
                        if len(itinerary['legs'][first_true]['intermediateStops'])>0:
                            row['first_stop_name']=itinerary['legs'][first_true]['intermediateStops'][0]['name']
                            row['first_stop_long']=itinerary['legs'][first_true]['intermediateStops'][0]['lon']
                            row['first_stop_lat']=itinerary['legs'][first_true]['intermediateStops'][0]['lat']
                            row['last_stop_name']='no value'
                            row['last_stop_long']='no value'
                            row['last_stop_lat']='no value'
                            row['first_type']=itinerary['legs'][first_true]['mode']
                            
                            

                        else:
                            row['first_stop_name']='no value'
                            row['first_stop_long']='no value'
                            row['first_stop_lat']='no value'
                            row['last_stop_name']='no value'
                            row['last_stop_long']='no value'
                            row['last_stop_lat']='no value'
                            results.append(row)
                        if len(itinerary['legs'][last_true]['intermediateStops'])>0:
                            row['last_stop_name']=itinerary['legs'][last_true]['intermediateStops'][-1]['name']
                            row['last_stop_long']=itinerary['legs'][last_true]['intermediateStops'][-1]['lon']
                            row['last_stop_lat']=itinerary['legs'][last_true]['intermediateStops'][-1]['lat']
                        
                        results.append(row)
                    else:
                            row['first_stop_name']='no value'
                            row['first_stop_long']='no value'
                            row['first_stop_lat']='no value'
                            row['last_stop_name']='no value'
                            row['last_stop_long']='no value'
                            row['last_stop_lat']='no value'
                            results.append(row)
                            
                else:
                    row['first_stop_name']='no value'
                    row['first_stop_long']='no value'
                    row['first_stop_lat']='no value'
                    row['last_stop_name']='no value'
                    row['last_stop_long']='no value'
                    row['last_stop_lat']='no value'
                   
                    results.append(row)

                
        
    time.sleep(1)  # Avoid rate limits

# Convert results into a DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
output_path = "full_simulation.csv"
results_df.to_csv(output_path, index=False)
print(f"Results saved to {output_path}")
