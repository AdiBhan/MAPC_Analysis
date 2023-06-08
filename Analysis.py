import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from Utilities import FetchData


class Analysis:
    def __init__(self):
        self.name_to_score_map = {}
        self.name_to_emailsecurity_map = {}
        self.name_to_websecurity_map = {}
        self.name_to_networksecurity_map = {}
        
        self.read_file()
        
    def read_file(self)->None:
        
        """ read_file method reads the Data.csv file and stores the data in dictionaries.
            Serves as a helper function to create_graphs method"""
            
        data_dir = os.getcwd() + "/Data/"
        with open(data_dir + "Muncipalities.csv", "r") as file:
            for line in file:
                data = json.loads(line)
                
                
                score = data["score"]
                name = data["name"]
                self.name_to_score_map[name] = score
                
                
                self.emailsecurity = data["categoryScores"]["emailSecurity"] if "emailSecurity" in data["categoryScores"] else 0
                self.name_to_emailsecurity_map[name] = self.emailsecurity

                self.websecurity = data["categoryScores"]["websiteSecurity"] if "websiteSecurity" in data["categoryScores"] else 0
                self.name_to_websecurity_map[name] = self.websecurity
                
                self.networksecurity = data["categoryScores"]["networkSecurity"] if "networkSecurity" in data["categoryScores"] else 0
                self.name_to_networksecurity_map[name] = self.networksecurity 


    def create_graphs(self, score_map:dict, xaxis_label:str, yaxis_label:str, file_name:str, graph_title:str)->None:
        
        """ create_graphs method creates a graph of the data in the Data.csv file"""
        
        print(score_map)
        ScoreSeries = pd.Series(self.sort_dictionaries(score_map))
        print(ScoreSeries.index, ScoreSeries.values)
        plt.figure(figsize=(20, 12))
       
        sns.barplot(x=ScoreSeries.index, y=ScoreSeries.values, edgecolor='black', ci=None, saturation=30)
        plt.title(graph_title)
        plt.xticks(rotation=90)  
        plt.xlabel(xaxis_label)
        plt.ylabel(yaxis_label)
        plt.tight_layout() 
        curdir = os.getcwd() + "/graphs/"
        plt.savefig(curdir + file_name)
  
    def create_stacked_bar_graph(self, score_map:dict , email_security_map:dict, web_security_map:dict, network_security_map:dict,   xaxis_label:str, yaxis_label:str, file_name:str, graph_title:str)->None:
        
        """ create_stacked_bar_graph method creates a stacked bar graph of the data from all categories of vulnerabilities """

        score_map = self.sort_dictionaries(score_map)
        email_security_map = self.sort_dictionaries(email_security_map)
        web_security_map = self.sort_dictionaries(web_security_map)
        network_security_map = self.sort_dictionaries(network_security_map)
        
    
        data = pd.DataFrame({'Email Security': list(email_security_map.values()),
                            'Web Security': list(web_security_map.values()), 'Network Security': list(network_security_map.values())},
                            index=list(score_map.keys()))
        plt.figure(figsize=(14, 8))
        data.plot(kind='bar', stacked=True)
     
        plt.xlabel(xaxis_label)
        plt.ylabel(yaxis_label)
        plt.xticks(rotation=90)  
        plt.title(graph_title)
        plt.legend()
        plt.tight_layout()
        
        curdir = os.getcwd() + "/graphs/"
        plt.savefig(curdir + file_name)
        plt.show()

    def sort_dictionaries(self, dict_name:dict)->dict:
        
        """ **Helper Function to create_graphs function**
            sort_dictionaries method sorts a dictionary by its values and returns a sorted dictionary"""
            
        sorted_dict = {}
        sorted_dict_values = sorted(dict_name.values())
        for num, names in zip(sorted_dict_values, dict_name.keys()):
            sorted_dict[names] = num
        return sorted_dict
    
    def create_histogram(self, score_map:dict, xaxis_label:str, yaxis_label:str, file_name:str, graph_title:str)->None:
        
        """Create a histogram of the data in score_map."""

        ScoreSeries = pd.Series(score_map.values())
        
        plt.figure(figsize=(20, 12))
        sns.histplot(ScoreSeries, bins=30, edgecolor='black', color='blue', kde=True, line_kws={'color': 'lightblue'})  
        plt.title(graph_title)
        plt.xlabel(xaxis_label)
        plt.ylabel(yaxis_label)
        plt.tight_layout() 

        curdir = os.getcwd() + "/graphs/"
        plt.savefig(curdir + file_name)
        plt.show()

    def create_vulnerability_frequency_graph(self, vulnerability_table:list, xaxis_label:str, yaxis_label:str, file_name:str, graph_title:str)->None:
        
        """create_vulnerability_frequency_graph method creates a graph which measures the frequency of each vulnerability."""
        
        vulnerability_frequency = {}
        for dict_ in vulnerability_table:
            for city_, vulnerabilities in dict_.items():
                for vulnerability in vulnerabilities:
                    vulnerability_frequency[vulnerability] = vulnerability_frequency.get(vulnerability, 0) + 1
     
        sorted_vulnerabilities = self.sort_dictionaries(vulnerability_frequency)

        # Getting the top 15 vulnerabilities to save to a csv file
        top_vulnerabilities_15 = list(reversed(list(sorted_vulnerabilities.items())))[:15]
        
        # Getting top 5 vulnerabilities for csv file
        
        top_vulnerabilities = list(reversed(list(sorted_vulnerabilities.items())))[:5]
        

        # create lists of vulnerabilities and their frequencies
        vulnerabilities = [item[0] for item in top_vulnerabilities]
        frequencies = [item[1] for item in top_vulnerabilities]

        plt.figure(figsize=(25, 20))
        sns.set(font_scale=1.2)
        vulnerabilities = [textwrap.fill(item[0], 40) for item in top_vulnerabilities]  
        # Plot the bar chart
        sns.barplot(x=vulnerabilities, y=frequencies, edgecolor='black', palette='Blues_d')
        plt.xticks(rotation=90)  # Rotate x-axis labels for better display
        plt.xlabel(xaxis_label)
        plt.ylabel(yaxis_label)
        plt.title(graph_title)
        plt.legend()
        plt.tight_layout()

        # Save the figure and display it
        curdir = os.getcwd() + "/graphs/"
        plt.savefig(curdir + file_name, dpi=300)
        
        
        
        with open(curdir + "top_vulnerabilities.csv", "w") as file:
            for key, value in top_vulnerabilities_15:
                file.write(f"{key} , {value}\n")
        plt.show()
        
        
        
            
            

if __name__ == "__main__":
    Work = Analysis()
    Work.create_histogram(Work.name_to_score_map, "Scores", "Frequency", "histogram.png", "Histogram of Scores across all municipalities")
    Utility = FetchData()
    Work.create_vulnerability_frequency_graph(Utility.VULNERABILITY_TABLE, "Municipalities", "Number of Vulnerabilities", "vulnerability_frequency_graph.png", "Most common vulnerabilities across all municipalities")
   
    Work.create_graphs(Work.name_to_score_map, "Municipalities", "General Scores", "general_map.png", "Scores across all municipalities")
    Work.create_graphs(Work.name_to_emailsecurity_map, "Municipalities", "Email Security Scores", "email_security_map.png", "Email Security Scores across all municipalities")
    Work.create_graphs(Work.name_to_websecurity_map, "Municipalities", "Web Security Scores", "web_security_map.png", "Web Security Scores across all municipalities")
    Work.create_graphs(Work.name_to_networksecurity_map, "Municipalities", "Network Security Scores", "network_security_map.png", "Network Security Scores across all municipalities")
    Work.create_stacked_bar_graph(Work.name_to_score_map, Work.name_to_emailsecurity_map, Work.name_to_websecurity_map, Work.name_to_networksecurity_map, "Municipalities", "Scores", "stacked_bar_graph.png", "Stacked Bar Graph of all categories of vulnerabilities")
    