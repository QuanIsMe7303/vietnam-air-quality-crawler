import requests
import csv
import os
import json
import pathlib
from zoneinfo import ZoneInfo
from datetime import datetime

API_KEY = ""
BASE_URL = "https://api.waqi.info/feed/geo:{lat};{lon}/?token=" + API_KEY

CITIES = [
    {
        "name": "hanoi",
        "display_name": "Hà Nội",
        "station_locations": [
            (21.0811211, 105.8180306),
            (21.01525, 105.80013),
            (21.0491, 105.8831),
            (21.0215063, 105.8188748),
            (21.035584, 105.852771),
            (21.04975, 105.74187),
            (21.148273, 105.913306),
            (21.002383, 105.718038)
        ]
    },
    {
        "name": "hue",
        "display_name": "Thừa Thiên Huế",
        "station_locations": [
            (16.46226, 107.596351)
        ]
    },
    {
        "name": "danang",
        "display_name": "Đà Nẵng",
        "station_locations": [
            (16.043252, 108.206826),
            (16.074, 108.217)
        ]
    }
]

def get_vietnam_time():
    """Get current time in Vietnam timezone (GMT+7)"""
    return datetime.now(ZoneInfo("Asia/Bangkok"))  # Bangkok uses GMT+7 like Vietnam

def get_air_quality(lat, lon):
    """Lấy thông tin chất lượng không khí từ API"""
    url = BASE_URL.format(lat=lat, lon=lon)
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return {
                    "timestamp": data["data"]["time"]["s"],
                    "station_id": data["data"]["idx"],
                    "city_name": data["data"]["city"]["name"],
                    "url": data["data"]["city"]["url"],
                    "latitude": lat,
                    "longitude": lon,
                    "aqi": data["data"]["aqi"],
                    "co": data["data"].get("iaqi", {}).get("co", {}).get("v", "N/A"),
                    "temperature": data["data"].get("iaqi", {}).get("t", {}).get("v", "N/A"),
                    "wind": data["data"].get("iaqi", {}).get("w", {}).get("v", "N/A"),
                    "atmospheric_pressure": data["data"].get("iaqi", {}).get("p", {}).get("v", "N/A"),
                    "humidity": data["data"].get("iaqi", {}).get("h", {}).get("v", "N/A"),
                    "pm25": data["data"].get("iaqi", {}).get("pm25", {}).get("v", "N/A"),
                    "pm10": data["data"].get("iaqi", {}).get("pm10", {}).get("v", "N/A"),
                    "o3": data["data"].get("iaqi", {}).get("o3", {}).get("v", "N/A"),
                    "no2": data["data"].get("iaqi", {}).get("no2", {}).get("v", "N/A")
                }
            else:
                return {"timestamp": get_vietnam_time().strftime("%Y-%m-%d %H:%M:%S"), "error": "Không lấy được dữ liệu", "latitude": lat, "longitude": lon}
        else:
            return {"timestamp": get_vietnam_time().strftime("%Y-%m-%d %H:%M:%S"), "error": "Lỗi kết nối API", "latitude": lat, "longitude": lon}
    except Exception as e:
        return {"timestamp": get_vietnam_time().strftime("%Y-%m-%d %H:%M:%S"), "error": str(e), "latitude": lat, "longitude": lon}

def save_to_csv(data, city_name: str):
    """Lưu dữ liệu vào file CSV theo tháng/năm"""
    if not data:
        return

    now = get_vietnam_time()
    result_dir = pathlib.Path(f"result/{city_name}")
    result_dir.mkdir(parents=True, exist_ok=True)

    filename = result_dir / f"air_quality_{city_name}_{now.month:02d}_{now.year}.csv"

    # Determine if file exists to decide whether to write headers
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        # Use the keys of the first data item as fieldnames
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write headers only if file does not exist
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(data)

def crawl_all_cities():
    """Lấy dữ liệu chất lượng không khí cho tất cả các thành phố"""
    all_results = {}
    
    for city in CITIES:
        city_name = city["name"]
        stations = city["station_locations"]
        
        # Lấy dữ liệu từ tất cả các trạm của thành phố
        city_results = []
        for lat, lon in stations:
            result = get_air_quality(lat, lon)
            city_results.append(result)
        
        # Lưu dữ liệu của từng thành phố vào CSV
        save_to_csv(city_results, city_name)
        
        # Lưu kết quả vào dictionary để in ra màn hình
        all_results[city_name] = city_results
    
    return all_results

if __name__ == "__main__":
    try:
        print("Starting Air Quality Data Crawler...")
        print(f"Current time in Vietnam: {get_vietnam_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        results = crawl_all_cities()
        
        print("\nCrawled data:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e