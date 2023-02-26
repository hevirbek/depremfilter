import requests
from bs4 import BeautifulSoup
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
import sys
import os

# Dünyanın yaklaşık yarıçapı
R = 6373.0

# iki nokta arasındaki mesafeyi hesaplayan fonksiyon
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


# Earthquake class
class Earthquake:
    def __init__(self, datetime: datetime, latitude: float, longitude: float, depth: float, magnitude: float, region: str, city:str, feature: str):
        self.date = datetime
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth
        self.magnitude = magnitude
        self.region = region
        self.city = city
        self.feature = feature



def get_earthquake_data() -> pd.DataFrame:
    url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"

    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    pre = soup.find("pre")
    split_by_newline = pre.text.split("\n")[7:]

    earthquakes = []

    for line in split_by_newline:
        line = line.strip()
        if line == "":
            continue

        splitted = line.split()
        date = datetime.strptime(splitted[0].strip(), "%Y.%m.%d").date()
        time = datetime.strptime(splitted[1].strip(), "%H:%M:%S").time()
        latitude = float(splitted[2].strip())
        longitude = float(splitted[3].strip())
        depth = float(splitted[4].strip())
        ml = float(splitted[6].strip())
        magnitude = ml 
        region = " ".join(splitted[8:-1]).strip()
        city = region[region.find("(")+1:region.find(")")]
        region = region[:region.find("(")].strip()
        feature = splitted[-1].strip()

        earthquake = Earthquake(datetime.combine(date, time), latitude, longitude, depth, magnitude, region,city, feature)
        earthquakes.append(earthquake)

    df = pd.DataFrame([vars(e) for e in earthquakes])

    return df


def add_distance_column(df: pd.DataFrame, lat: float, lon: float) -> pd.DataFrame:
    df["distance"] = df.apply(lambda row: calculate_distance(lat, lon, row["latitude"], row["longitude"]), axis=1)

    return df

def filter_data(df: pd.DataFrame, min_magnitude: float, min_distance: float, city: str) -> pd.DataFrame:
    df = df[df["distance"] < min_distance]
    df = df[df["magnitude"] > min_magnitude]

    if city != "HEPSİ":
        df = df[df["city"] == city]
        
    return df


def add_my_location(df: pd.DataFrame, lat: float, lon: float) -> pd.DataFrame:
    df = pd.concat([df, pd.DataFrame([[lat, lon, 0.0, 0.0, "My Location", "My Location"]], columns=["latitude", "longitude", "depth", "magnitude", "region", "feature"])], ignore_index=True)
    return df



def get_cities(df: pd.DataFrame) -> list:
    cities = df["city"].unique()
    cities.sort()
    cities_list = list(cities.copy())
    cities_list.insert(0, "HEPSİ")
    return cities_list


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


