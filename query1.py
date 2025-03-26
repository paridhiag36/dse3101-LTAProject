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

# API endpoint
base_url = "https://www.onemap.gov.sg/api/public/routingsvc/route"

# Authorization header
headers = {
    "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1ZDdkYzYyYWZmMDI0ZWU2NGIzZmY1MjMwYTJhYzUxMSIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9wYXNzd29yZCIsImlhdCI6MTc0Mjg4NzQ1NywiZXhwIjoxNzQzMTQ2NjU3LCJuYmYiOjE3NDI4ODc0NTcsImp0aSI6InkzWEU4NllNSEY4NnVMTzMiLCJ1c2VyX2lkIjo2MDY1LCJmb3JldmVyIjpmYWxzZX0.9QktvMZZy7oaQOeu3j1An-cOhDLltZTAbpumPEbgcQ0"
}

# Create an empty list to store results
ang_mo_kio_results = []
# Filter rows where 'Planning_Area' is 'Ang Mo Kio'
ang_mo_kio_df = df[df["Planning_Area"] == "Ang Mo Kio"]

# Loop through each row
for index, row in ang_mo_kio_df.iterrows():
    planning_area_name = row["Planning_Area"]
    start_lat, start_long = row["Subzone_Lat"], row["Subzone_Long"]
    end_lat, end_long = row["Hospital_Polyclinic_Lat"], row["Hospital_Polyclinic_Long"]
    subzone_name = row["Subzone"]
    hospital_name = row["Hospital_Polyclinic"]  

    # Construct API request URLs
    np_wkday_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date=03-19-2025&time=15:00:00&mode=TRANSIT&numItineraries=3"
    p_wkday_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date=03-19-2025&time=18:00:00&mode=TRANSIT&numItineraries=3"
    np_wkend_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date=03-22-2025&time=15:00:00&mode=TRANSIT&numItineraries=3"
    p_wkend_url = f"{base_url}?start={start_lat},{start_long}&end={end_lat},{end_long}&routeType=pt&date=03-22-2025&time=18:00:00&mode=TRANSIT&numItineraries=3"

    # Make the GET request
    response_1 = requests.get(np_wkday_url, headers=headers)
    response_2 = requests.get(p_wkday_url, headers=headers)
    response_3 = requests.get(np_wkend_url, headers=headers)
    response_4 = requests.get(p_wkend_url, headers=headers)
    

    # Check for rate limit
    if response_1.status_code == 429 or response_2.status_code == 429 or response_3.status_code == 429 or response_4.status_code == 429:
        print(f"Rate limit exceeded for Route {index + 1}. Retrying after a delay...")
        # Sleep for a minute or adjust based on the rate limit headers, like 'Retry-After'
        time.sleep(60)  # Wait for 60 seconds before retrying the request
        response_1 = requests.get(np_wkday_url, headers=headers)  # Retry the requests
        response_2 = requests.get(p_wkday_url, headers=headers)
        response_3 = requests.get(np_wkend_url, headers=headers)
        response_4 = requests.get(p_wkend_url, headers=headers)
        

    # Process the response
    if response_1.status_code == 200 and response_2.status_code == 200 and response_3.status_code == 200 and response_4.status_code == 200:
        data_1 = response_1.json()
        data_2 = response_2.json()
        data_3 = response_3.json()
        data_4 = response_4.json()

        # Extract itineraries
        if "plan" in data_1 and "itineraries" in data_1["plan"]:
            for itinerary in data_1["plan"]["itineraries"]:
                duration = itinerary.get("duration", 0)  # Total duration in seconds
                walk_time = itinerary.get("walkTime", 0)  # Walking time in seconds
                walk_distance = itinerary.get("walkDistance", 0)  # Walking distance in meters
                transfers = itinerary.get("transfers", 0)  # Number of transfers
                transit_time = itinerary.get("transitTime", 0) #Transit time in seconds

                # Convert duration, walkTime and transiTime to minutes
                duration_minutes = round(duration / 60, 2)
                walk_time_minutes = round(walk_time / 60, 2)
                transit_time_minutes = round(transit_time / 60, 2)

                # Store in results list
                ang_mo_kio_results.append({
                    "Planning_Area" : planning_area_name,
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
                    "TransitTime (min)":transit_time_minutes,
                    "Weekend" : 0,
                    "Peak Hour": 0
                })

                print(f"Route {index + 1}: Subzone={subzone_name}, Hospital={hospital_name}, Duration={duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}")
         # Extract itineraries
        if "plan" in data_2 and "itineraries" in data_2["plan"]:
             for itinerary in data_2["plan"]["itineraries"]:
                 duration = itinerary.get("duration", 0)  # Total duration in seconds
                 walk_time = itinerary.get("walkTime", 0)  # Walking time in seconds
                 walk_distance = itinerary.get("walkDistance", 0)  # Walking distance in meters
                 transfers = itinerary.get("transfers", 0)  # Number of transfers
                 transit_time = itinerary.get("transitTime", 0) #Transit time in seconds

                 # Convert duration, walkTime and transiTime to minutes
                 duration_minutes = round(duration / 60, 2)
                 walk_time_minutes = round(walk_time / 60, 2)
                 transit_time_minutes = round(transit_time / 60, 2)

                 # Store in results list
                 ang_mo_kio_results.append({
                     "Planning_Area" : planning_area_name,
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
                     "TransitTime (min)":transit_time_minutes,
                     "Weekend" : 0,
                     "Peak Hour": 1
                 })

                 print(f"Route {index + 1}: Subzone={subzone_name}, Hospital={hospital_name}, Duration={duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}")
          # Extract itineraries
        if "plan" in data_3 and "itineraries" in data_3["plan"]:
              for itinerary in data_3["plan"]["itineraries"]:
                  duration = itinerary.get("duration", 0)  # Total duration in seconds
                  walk_time = itinerary.get("walkTime", 0)  # Walking time in seconds
                  walk_distance = itinerary.get("walkDistance", 0)  # Walking distance in meters
                  transfers = itinerary.get("transfers", 0)  # Number of transfers
                  transit_time = itinerary.get("transitTime", 0) #Transit time in seconds

                  # Convert duration, walkTime and transiTime to minutes
                  duration_minutes = round(duration / 60, 2)
                  walk_time_minutes = round(walk_time / 60, 2)
                  transit_time_minutes = round(transit_time / 60, 2)

                  # Store in results list
                  ang_mo_kio_results.append({
                      "Planning_Area" : planning_area_name,
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
                      "TransitTime (min)":transit_time_minutes,
                      "Weekend" : 1,
                      "Peak Hour": 0
                  })

                  print(f"Route {index + 1}: Subzone={subzone_name}, Hospital={hospital_name}, Duration={duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}")
         # Extract itineraries         
        if "plan" in data_4 and "itineraries" in data_4["plan"]:
              for itinerary in data_4["plan"]["itineraries"]:
                  duration = itinerary.get("duration", 0)  # Total duration in seconds
                  walk_time = itinerary.get("walkTime", 0)  # Walking time in seconds
                  walk_distance = itinerary.get("walkDistance", 0)  # Walking distance in meters
                  transfers = itinerary.get("transfers", 0)  # Number of transfers
                  transit_time = itinerary.get("transitTime", 0) #Transit time in seconds

                  # Convert duration, walkTime and transiTime to minutes
                  duration_minutes = round(duration / 60, 2)
                  walk_time_minutes = round(walk_time / 60, 2)
                  transit_time_minutes = round(transit_time / 60, 2)

                  # Store in results list
                  ang_mo_kio_results.append({
                      "Planning_Area" : planning_area_name,
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
                      "TransitTime (min)":transit_time_minutes,
                      "Weekend" : 1,
                      "Peak Hour": 1
                  })

                  print(f"Route {index + 1}: Subzone={subzone_name}, Hospital={hospital_name}, Duration={duration_minutes} min, WalkTime={walk_time_minutes} min, WalkDistance={walk_distance} m, Transfers={transfers}, TransitTime = {transit_time_minutes}")
    #else:
        #print(f"Route {index + 1}: API request failed with status {response.status_code}")

    # Sleep to avoid hitting the rate limit
    time.sleep(1)  # Sleep for 1 second between each request

# WEEKDAY PEAK HOUR
# WEEKEND NON PEAK HOUR
# WEEKEND NON PEAK HOUR
# Convert results into a DataFrame
amk_results_df = pd.DataFrame(ang_mo_kio_results)

# Display the DataFrame
print(amk_results_df)

# Save to CSV
output_path = "/Users/paridhiagarwal/dse3101-LTAProject/amk_onemap_results.csv"
amk_results_df.to_csv(output_path, index=False)
print(f"Results saved to {output_path}")
