from flask import Flask

class Site:
    def __init__(self, name, url, field, category):
        self.name = name
        self.url = url
        self.field = field # eg fashon
        self.category = category # eg form, main page
        # self.assessmentCriteria = assessmentCriteria if assessmentCriteria is not None else []


    def display_info(self):
        print(f"Name: {self.name}")
        print(f"URL: {self.url}")
        print(f"Field: {self.field}")
        print(f"category: {self.category}")
        # print(f"Assesment Criteria: {', '.join(self.assessmentCriteria)}")




