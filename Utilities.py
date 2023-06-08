import requests
import os
from dotenv import load_dotenv
import time


#####################################################################################
# Utilities.py
# Author: Adi Bhan
# This script will pull all vendors from UpGuard API and generate important analytics

###############################################################################################################

class FetchData:
    def __init__(self):
        """ Constructor for FetchData class
            Loads environment variables from .env file to be used for UpGuard API"""
        
        load_dotenv()  # take environment variables from .env.
        self.API_KEY = os.getenv("UPGUARD_API_KEY")
        self.BASE_URL = os.getenv("UPGUARD_BASE_URL")
        self.EMAIL = os.getenv("UPGUARD_EMAIL")
        self.PASSWORD = os.getenv("UPGUARD_PASSWORD")
        self.VENDOR_URL = "https://cyber-risk.upguard.com/api/public/vendor"
        self.VULNERABILITY_URL = "https://cyber-risk.upguard.com/api/public/vulnerabilities/vendor"
        

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
        
        self.VULNERABILITY_TABLE = self.parse_vulnerabilities()
    
  
        
    def parse_vulnerabilities(self) -> list:
        
        """ parse_and_store_vulnerabilities method parses all vulnerabilities from UpGuard API and stores them in a csv file"""
  
        vulnerability_table = []
        
        for municipality in self.muncipalities:
            params = {
                "hostname": self.muncipalities[municipality],
                "vendor_primary_hostname": self.muncipalities[municipality],
                "ip": self.muncipalities[municipality],
                "primary_hostname": self.muncipalities[municipality]
            }
            response = requests.get(self.VULNERABILITY_URL, headers=self.headers, params=params)
            
            municipality_vulnerabilities = {municipality: [] }
            vulnerability_table.append(municipality_vulnerabilities)

            for i in range(0, len(response.json()["vulnerabilities"])-1):
                vulnerability = response.json()["vulnerabilities"][i]['cve']['description']
                municipality_vulnerabilities[municipality].append(vulnerability)
                        
                        
        return vulnerability_table
               
    def test_vendors(self)->None:
        
        """ test_vendors used for testing purposes to make sure Vendor endpoint can be reached from UpGuard API** 
            ** If assert error is thrown, check the municipality name and URL in the muncipalities dictionary **"""
        for municipality in self.muncipalities:
            
            params = {
                "hostname": self.muncipalities[municipality],
            }
            response = requests.get(self.VENDOR_URL, headers=self.headers, params=params)
            
            if (response.status_code == 200):
                print(municipality)
                print(response.json(), "\n")
                print()
            else:
                assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"
        print(f"Success! All muncipalities endpoints work properly. Total number of municipalities: {len(self.muncipalities)}")

    def store_vendors_in_csv(self) -> None:
        
        """ store_in_csv method storess all municipality data in a csv file locally """

        for municipality in self.muncipalities:
            params = {
                "hostname": self.muncipalities[municipality]
            }
            response = requests.get(self.VENDOR_URL, headers=self.headers, params=params)
            if (response.status_code == 200):
                cur_dir = os.getcwd() + "/Data/"
                with open(cur_dir + "Muncipalities.csv", "a") as file:
                    file.write(response.text)
                    file.write("\n")
            else:
              assert response.status_code == 200, f"\n | Error: {response.status_code} City: {municipality} URL: {self.muncipalities[municipality]}| \n"
        print("Success! All muncipalities are stored in Data.csv file")


if __name__ == "__main__":
    utilities = FetchData()
   
    