
import os
import requests
from dotenv import load_dotenv
import pymongo as pm
import openpyxl
from geopy.geocoders import Nominatim

#####################################################################################
# FetchData.py
# Author: Adi Bhan
# This script will pull all data from vendors using UpGuard API and store it locally

###############################################################################################################


class FetchData:
    def __init__(self):
        """ Constructor for FetchData class
            Loads environment variables from .env file to be used for UpGuard API"""

        load_dotenv()  # take environment variables from .env.

        # UpGuard API settings
        self.API_KEY = os.getenv("UPGUARD_API_KEY")
        self.BASE_URL = os.getenv("UPGUARD_BASE_URL")
        self.EMAIL = os.getenv("UPGUARD_EMAIL")
        self.PASSWORD = os.getenv("UPGUARD_PASSWORD")
        self.VENDOR_URL = "https://cyber-risk.upguard.com/api/public/vendor"
        self.VULNERABILITY_URL = "https://cyber-risk.upguard.com/api/public/vulnerabilities/vendor"
        self.RISKS_URL = "https://cyber-risk.upguard.com/api/public/risks"
        self.geolocator = Nominatim(user_agent="MAPC_DATA")

        # Directory settings

        self.graph_dir = os.path.join(os.getcwd(), "data")

        # MongoDB settings
        self.MongoDB_URI = os.getenv("MONGO_URI")

        # Initalize connection to MongoDB for storing data

        self.client = pm.MongoClient(self.MongoDB_URI)

        if self.client.server_info():
            print("Connected to MongoDB successfully")
        else:
            print("Failed to connect to MongoDB")

        self.DB = self.client["Cluster0"]
        self.collection_scores = self.DB["Municipality_Scores"]
        self.collection_vulnerabilities = self.DB["Municipality_Vulnerabilities"]
        self.collection_risks = self.DB["Muncipality_Risks"]

        self.headers = {
            "Authorization": self.API_KEY
        }
        # Dictionary of all municipalities and their respective domains used for querying UpGuard API
        self.muncipalities = {

            "Maynard": "townofmaynard-ma.gov",
            "Medford": "medfordma.org",
            "Melrose": "cityofmelrose.org",
            "Merrimac": "merrimac01860.info",
            "Methuen": "cityofmethuen.net",
            "Middleton": "middletonma.gov",
            "Nahant": "nahant.org",
            "Newbury": "townofnewbury.org",
            "Newburyport": "cityofnewburyport.com",
            "Newton": "newtonma.gov",
            "North Andover": "northandoverma.gov",
            "North Reading": "northreadingma.gov",
            "Peabody": "peabody-ma.gov",
            "Pepperell": "town.pepperell.ma.us",
            "Reading": "readingma.gov",
            "Rockport": "rockportma.gov",
            "Rowley": "townofrowley.org",
            "Salem": "salemma.gov",
            "Salisbury": "salisburyma.gov",
            "Saugus": "saugus-ma.gov",
            "Sherborn": "sherbornma.org",
            "Shirley": "shirley-ma.gov",
            "Stoneham": "stoneham-ma.gov",
            "Stow": "stow-ma.gov",
            "Sudbury": "sudbury.ma.us",
            "Swampscott": "swampscottma.gov",
            "Tewksbury": "tewksbury-ma.gov",
            "Topsfield": "topsfield-ma.gov",
            "Townsend": "townsend.ma.us",
            "Tyngsborough": "tyngsboroughma.gov",
            "Wakefield": "wakefield.ma.us",
            "WaterTown": "watertown-ma.gov",
            "Wayland": "wayland.ma.us",
            "Westford": "westfordma.gov",
            "Weston": "weston.org",
            "Wilmington": "wilmingtonma.gov",
            "Winchester": "winchester.us",
            "Woburn": "cityofwoburn.com",
            "Georgetown": "georgetownma.gov",
            "Gloucester": "gloucester-ma.gov",
            "Groveland": "grovelandma.com",
            "Hamilton": "hamiltonma.gov",
            "Haverhill": "cityofhaverhill.com",
            "Groton": "townofgroton.org",
            "Ipswich": "ipswichma.gov",
            "Lawrence": "cityoflawrence.com",
            "Lexington": "lexingtonma.gov",
            "Littleton": "littletonma.org",
            "Lynn": "lynnma.gov",
            "Lynnfield": "town.lynnfield.ma.us",
            "Malden": "cityofmalden.org",
            "Manchester": "manchester.ma.us",
            "Marblehead": "marblehead.org",
            "Marlborough": "marlborough-ma.gov",
            "Acton": "acton-ma.gov",
            "Amesbury": "amesburyma.gov",
            "Andover": "andoverma.gov",
            "Arlington": "arlingtonma.gov",
            "Ayer": "ayer.ma.us",
            "Bedford": "bedfordma.gov",
            "Belmont": "belmont-ma.gov",
            "Billercia": "town.billerica.ma.us",
            "Beverly": "beverlyma.gov",
            "Boxborough": "boxborough-ma.gov",
            "Burlington": "burlington.org",
            "Chelmsford": "chelmsfordma.gov",
            "Concord": "concordma.gov",
            "Danvers": "danversma.gov",
            "Dracut": "dracutma.gov",
            "Dunstable": "dunstable-ma.gov",
            "Essex": "essexma.org",
            "Frameingham": "framinghamma.gov",
            "Holliston": "townofholliston.us",
            "Hopkinton": "hopkintonma.gov",
            "Lowell": "lowellma.gov",
        }
        # self.VULNERABILITY_TABLE = self.__parse_vulnerabilities()

    def test_vendors(self) -> None:
        """ test_vendors used for testing purposes to make sure Vendor endpoint can be reached from UpGuard API** 
            ** If assert error is thrown, check the municipality name and URL in the muncipalities dictionary **"""
        for municipality in self.muncipalities:

            params = {
                "hostname": self.muncipalities[municipality],
            }
            response = requests.get(
                self.VENDOR_URL, headers=self.headers, params=params)

            if (response.status_code == 200):
                print(municipality)
                print(response.json(), "\n")
                print()
            else:
                assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"
        print(
            f"Success! All muncipalities endpoints work properly. Total number of municipalities: {len(self.muncipalities)}")

    def vendor_scores(self) -> None:
        """ get_vendor_scores method pulls all vendor scores from UpGuard API and stores them locally in a csv file and MongoDB under collection: Municipality_Scores"""
        locations = []
        for municipality in self.muncipalities:
            params = {
                "hostname": self.muncipalities[municipality]
            }
            response = requests.get(
                self.VENDOR_URL, headers=self.headers, params=params)

            municipality_data = response.json()

            # get coordinates for each municipality, and adding to municipality_data dictionary
            location = self.geolocator.geocode(
                municipality + ", Massachusetts, USA")
            print(municipality, location)

            locations.append(location)
            if location is not None:
                municipality_data["longitude"], municipality_data["latitude"] = location.longitude, location.latitude
                municipality_data["location"] = [
                    location.longitude, location.latitude]
                print("Success! Coordinates found",
                      municipality_data["longitude"], municipality_data["latitude"])
            else:
                print(f'Failed to get coordinates for {municipality}')

            if (response.status_code == 200):

                # store data locally in Muncipalities.csv file

                print(os.path.join(self.graph_dir, "Muncipalities.csv"))
                with open(os.path.join(self.graph_dir, "Muncipalities.csv"), "a") as file:
                    file.write(str(municipality_data))
                    file.write("\n")
            else:
                assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"

            # finally, send municipality data to MongoDB for storage
            self.__send_to_mongodb(
                municipality_data, municipality, self.collection_scores)

        print("Success! All muncipalities are stored in Data.csv file")

    def test_endpoints(self) -> None:
        params = {
            "hostname": "danversma.gov",
            "primary_hostname": "danversma.gov",
        }
        URL = "https://cyber-risk.upguard.com/api/public/risks/vendors"

        response = requests.get(URL, headers=self.headers, params=params)

        print(response.json())

    def __send_to_mongodb(self, data, muncipality, cluster) -> None:
        """ send_to_mongodb method sends data to MongoDB server. 
             ** HELPER METHOD, DO NOT CALL DIRECTLY ** """
        # cluster_name = cluster.name.split(' | ')[1]

        try:
            # Check if the municipality already exists in the MongoDB cluster

            does_document_exist = cluster.find_one({"name": muncipality})

            if (not does_document_exist):
                # Structure data in the way MongoDB expects, with 'municipality' as the key

                if (cluster == self.collection_scores):
                    data_to_insert = data_to_insert = {
                        "name": muncipality, "data": data}
                if (cluster == self.collection_vulnerabilities):
                    data_to_insert = {"name": muncipality,
                                      "vulnerabilities": data[muncipality]}

                cluster.insert_one(data_to_insert)
                print(f"Successfully inserted {muncipality} into MongoDB ")
            # else:

                # print(f"Document already exists for {muncipality} ")

        except Exception as e:
            print(f"Error with inserting into MongoDB: {e}")

    def __parse_vulnerabilities(self) -> list:
        """ parse_and_store_vulnerabilities method parses all vulnerabilities from UpGuard API and stores them in a csv file
            ** HELPER METHOD, DO NOT CALL DIRECTLY ** """

        vulnerability_table = []

        for municipality in self.muncipalities:
            params = {
                "hostname": self.muncipalities[municipality],
                "vendor_primary_hostname": self.muncipalities[municipality],
                "ip": self.muncipalities[municipality],
                "primary_hostname": self.muncipalities[municipality]
            }
            response = requests.get(
                self.VULNERABILITY_URL, headers=self.headers, params=params)

            municipality_vulnerabilities = {municipality: []}

            if (response.status_code == 200):
                for i in range(0, len(response.json()["vulnerabilities"])-1):
                    severity = response.json(
                    )["vulnerabilities"][i]['cve']['severity']
                    vulnerability = response.json(
                    )["vulnerabilities"][i]['cve']['description']

                    municipality_vulnerabilities[municipality].append({

                        "Vulnerability": vulnerability,
                        "Severity": severity},)
            else:
                assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"

            self.__send_to_mongodb(
                municipality_vulnerabilities, municipality, self.collection_vulnerabilities)

        return vulnerability_table

    def query_db(self, collection, municipality) -> dict:
        """ query_db method queries MongoDB for a specific municipality
            Returns a dictionary of the municipality's data"""
        try:
            query = collection.find_one({"name": municipality})
        except Exception as e:
            print(f"Error with querying MongoDB: {e}")

        return query

    def clear_db(self, collection) -> None:
        """ clear_db removes all values from a collection"""
        try:
            collection.delete_many({})
            print(f"Successfully cleared {collection.name}")
        except Exception as e:
            print(f"Error with clearing MongoDB: {e}")

    def risk_timeseries(self) -> None:
        """Method to get Risk, Date, Severity, and Category/Type Data from UpGuard API and store it in MongoDB under collection: Municipality_Risk to be used for time series graphing (Risk over 2023)
            URL: https://cyber-risk.upguard.com/api/public/risk"""
        total_risk = []
        for city in self.muncipalities:
            self.params = {
                "hostname": self.muncipalities[city],
                "vendor_primary_hostname": self.muncipalities[city],
                "ip": self.muncipalities[city],
                "primary_hostname": self.muncipalities[city]

            }
            response = requests.get(
                self.RISKS_URL, headers=self.headers, params=self.params)

            # Parsing out the Risk, Date, Severity, and Category/Type Data from the API for each city and storing it in a list of dictionaries

            for i in range(0, len(response.json()['risks'])-1):

                data = response.json()['risks'][i]

                # If any of the data is missing, skip it
                if (not data.get("riskSubtype", None) or not data.get("severity", None) or not data.get("category", None) or not data.get("description", None)):
                    continue
                else:
                    # If the data is from 2021, skip it (we only want data from 2023
                    if (data["firstDetected"].split("-")[0] == "2021"):
                        continue
                    # Data is in format: "YEAR_MONTH_DAY" -> "MONTH_DAY_YEAR"
                    date = data["firstDetected"].split(
                        "-")[1] + "-" + data["firstDetected"].split(
                        "-")[2][0:2] + "-" + data["firstDetected"].split("-")[0]

                    severity = data["severity"]
                    category = data["category"]

                    risk = data["risk"]
                    total_risk.append({"Risk": risk, "Date": date,
                                      "Severity": severity, "Category": category,
                                       "Name": city})

        # Send data to MongoDB
        self.collection_risks.insert_many(total_risk)
        print(
            f"\nSuccessfully inserted data into MongoDB  {self.collection_risks}\n")

    def save_to_exel(self) -> None:

        # Function to save data to excel file using openpyxl

        pass


if __name__ == "__main__":

    utilities = FetchData()
    utilities.clear_db(utilities.collection_risks)
    utilities.risk_timeseries()
