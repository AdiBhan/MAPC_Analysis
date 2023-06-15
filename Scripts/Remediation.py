import os
import sys
from FetchData import FetchData as FD
import pymongo as pm
import requests
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

#####################################################################################
# Remediation.py
# Author: Adi Bhan
# This script is used to generate PDFS of issues found by the scan.
###############################################################################################################

# Custom HRFlowable class to change the color of the line.
# Documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf


class CustomHRFlowable(HRFlowable):
    def __init__(self, width="100%", thickness=1, spaceBefore=0, spaceAfter=0):
        super().__init__(width=width, thickness=thickness,
                         spaceBefore=spaceBefore, spaceAfter=spaceAfter)


class Remediation(FD):

    def __init__(self, IPS):

        super().__init__()

        # MongoDB setup

        self.remediation_collection = self.DB['Remediation']

        # Directory setup
        self.remediation_dir = os.path.join(os.getcwd(), "Remediation")

        if not os.path.exists(self.remediation_dir):
            os.makedirs(self.remediation_dir)
            print("Created Remediation Directory")

        self.IPS = IPS
        self.date = datetime.datetime.now().strftime("%m-%d-%Y")

        # Data setup
        self.remediation_data = []
        self.issues = []
        self.why_is_it_risky = []

        # Top Risky Issues (based on Analysis)

        self.top_risks = [
            'CAA not enabled',
            'Weak cipher suites supported in TLS 1.2',
            'CSP is not implemented',
            'HTTP Strict Transport Security (HSTS) not enforced',
            'X-Content-Type-Options is not nosniff',
            'Insecure SSL/TLS versions available'
        ]

        for IP in self.IPS:
            self.fetch_data(IP)
            self.generate_report(IP)

    def fetch_data(self, IP):
        """Fetch NERAC Region data from UpGuard and store in MongoDB. 
        Helper method for the constructor.
        """
        params = {
            "hostname": {IP},
            "primary_hostname": {IP},
        }

        RISK_URL = "https://cyber-risk.upguard.com/api/public/risks/vendors"
        SCORE_URL = "https://cyber-risk.upguard.com/api/public/vendor"

        risk_response = requests.get(
            RISK_URL, headers=self.headers, params=params)
        score_response = requests.get(
            SCORE_URL, headers=self.headers, params=params)

        if risk_response.status_code == 200:
            score_json = score_response.json()
            overall_score = score_json['score']
            category_scores = score_json['categoryScores']
            web_score = category_scores['websiteSecurity']
            email_score = category_scores['emailSecurity']
            network_score = category_scores['networkSecurity']
            phishing_score = category_scores['phishing']
            brand_score = category_scores['brandProtection']

            risks_json = risk_response.json()
            risks = risks_json['risks']

            issue_data = []
            for risk in risks:
                issue = risk['finding']
                why_is_it_risky = risk['risk']
                description = risk['description']
                hostnames = risk['hostnames']

                issue_data.append({
                    "Issue": issue,
                    "Why is it risky": why_is_it_risky,
                    "Description": description,
                    "Host": hostnames[0],
                    "Overall Score": overall_score,
                    "Web Score": web_score,
                    "Email Score": email_score,
                    "Network Score": network_score,
                    "Phishing Score": phishing_score,
                    "Brand Score": brand_score,
                })

            self.remediation_data.append({IP: issue_data})

            existing_data = self.remediation_collection.find_one({"IP": IP})
            if existing_data is None:
                self.remediation_collection.insert_one(
                    {"IP": IP, "Data": issue_data})
            else:
                print(f"Data for {IP} already exists in MongoDB")

        else:
            print("Error in fetching data from UpGuard API",
                  risk_response.status_code, risk_response.text, sep="\n")

    def generate_report(self, IP):
        """Method generates PDF report based on UpGuard Data"""

        Title = IP.replace("ma.gov", "").replace("-", "").capitalize()
        Data = self.remediation_collection.find_one({"IP": IP})['Data']
        IP_Scores = [str(Data[0][key]) for key in ['Overall Score', 'Web Score', 'Email Score',
                                                   'Network Score', 'Phishing Score', 'Brand Score']]

        doc = SimpleDocTemplate(os.path.join(
            self.remediation_dir, f"{Title}.pdf"), pagesize=letter)
        story = []  # This list will hold the document's contents

        # Get the default style and customize it
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))

        styles.add(ParagraphStyle(
            name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))

        # Adding the title and date to the story
        story.append(Paragraph(
            f"<font size=24 color=green>{Title} Remediation Report</font>", styles['Center']))
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(f"<font size=12>Date Created: {self.date}</font>", styles['Italic']))
        story.append(Spacer(1, 12))

        # Adding the scores to the story
        story.append(Paragraph(
            f"<font size=14>Overall Score {IP_Scores[0]} / 850</font>", styles['Center']))
        story.append(Spacer(1, 12))

        score_headings = ['Website Security', 'Email Security',
                          'Network Security', 'Phishing Score', 'Brand Score']
        scores_text = ' | '.join(
            [f"{heading}: {score}" for heading, score in zip(score_headings, IP_Scores)])
        story.append(Paragraph(scores_text, styles['BodyText']))
        story.append(CustomHRFlowable())
        story.append(Spacer(1, 12))

        # Adding each issue and its description
        for index, data in enumerate(Data, start=1):

            story.append(
                Paragraph(f"<font size=14>Issue #{index}: <font size=12>{data['Issue']} </font></font>", styles['Bold']))
            story.append(Spacer(1, 12))
            for key in ['Why is it risky', 'Description']:
                story.append(Paragraph(f"<b>{key}:</b>", styles['BodyText']))
                story.append(Paragraph(data[key], styles['BodyText']))
                story.append(Spacer(1, 12))
            story.append(CustomHRFlowable())

        doc.build(story)
        print(f"-" * 50)
        print(f"\n\nReport for {Title} has been generated successfully\n\n")
        print(f"-" * 50)


if __name__ == '__main__':
    NERAC_REGIONS = ["danversma.gov", "middletonma.gov",
                     "topsfield-ma.gov", "wenhamma.gov"]
    Remediate = Remediation(NERAC_REGIONS)
