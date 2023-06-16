import os
import requests
from dotenv import load_dotenv
import pymongo as pm
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

        # Directory settings
        self.graph_dir = os.path.join(os.getcwd(), "graphs")

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
            "Lowell": "lowellma.gov",
            "Lynn": "lynnma.gov",
            "Lynnfield": "town.lynnfield.ma.us",
            "Malden": "cityofmalden.org",
            "Manchester": "manchester.ma.us",
            "Marblehead": "marblehead.org",
            "Marlborough": "marlborough-ma.gov",
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

        for municipality in self.muncipalities:
            params = {
                "hostname": self.muncipalities[municipality]
            }
            response = requests.get(
                self.VENDOR_URL, headers=self.headers, params=params)

            municipality_data = response.json()

            if (response.status_code == 200):

                # store data locally in Muncipalities.csv file

                print(os.path.join(self.graph_dir, "Muncipalities.csv"))
                with open(os.path.join(self.graph_dir, "Muncipalities.csv"), "a") as file:
                    file.write(str(municipality_data))
                    file.write("\n")
            else:
                assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"

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

        print(response.json()['risks'])

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
            else:

                print(f"Document already exists for {muncipality} ")

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
            vulnerability_table.append(municipality_vulnerabilities)

            if (response.status_code == 200):
                for i in range(0, len(response.json()["vulnerabilities"])-1):
                    vulnerability = response.json(
                    )["vulnerabilities"][i]['cve']['description']
                    municipality_vulnerabilities[municipality].append(
                        vulnerability)
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


if __name__ == "__main__":
    utilities = FetchData()
    utilities.test_endpoints()
