# test.py
from email_classifier import GemmaEmailClassifier
import os
files = os.listdir(r"C:\Users\manda\Projects\phishing_pot\email")

clf = GemmaEmailClassifier(labels=["phishing", "spam", "benign"])
for file in files[:11]:
    filename = os.path.join(r"C:\Users\manda\Projects\phishing_pot\email", file)
    res = clf.classify_eml_file(filename)
    print(f"File: {res.file}")
    print(f"Chosen: {res.chosen}")
    print(f"From: {res.sender} -> To: {res.recipient}")
    print(f"Scores: {res.scores}")
    print(f"Subject: {res.subject}")