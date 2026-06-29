# brevistay_client.py
import requests
import json
import time
import random
from typing import Dict, Optional

INDIAN_FIRST_NAMES = [
    "Arjun", "Aarav", "Vihaan", "Vivaan", "Ananya", "Diya", "Aadhya", "Sai", 
    "Rohan", "Siddharth", "Kunal", "Rahul", "Priya", "Neha", "Pooja", "Anjali",
    "Raj", "Amit", "Vikram", "Tarun", "Meera", "Kavya", "Ishita", "Tanvi",
    "Aditya", "Karthik", "Varun", "Dhruv", "Shreya", "Riya", "Sanya", "Navya"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Kumar", "Singh", "Reddy", "Gupta", "Joshi",
    "Nair", "Menon", "Shetty", "Rao", "Desai", "Mehta", "Choudhury", "Malhotra",
    "Khanna", "Kapoor", "Sinha", "Thakur", "Yadav", "Mishra", "Tripathi", "Dwivedi"
]

class BrevistayClient:
    def __init__(self):
        self.base_url = "https://cst.brevistay.com"
        self.web_url = "https://www.brevistay.com"
        self.api_holida = "https://api.holida.com"
        self.session = requests.Session()
        self.token = None
        self.cuid = None
        self.user_id = None
        self.user_name = None
        self.user_last_name = None
        self.user_email = None
        self.user_mobile = None
        
        self.default_headers = {
            "User-Agent": "okhttp/4.12.0",
            "Accept-Encoding": "gzip",
            "brevi-channel": "ANDROID",
            "brevi-channel-version": "6.0.8"
        }
        
        self.web_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.brevistay.customer",
            "Referer": "https://www.brevistay.com/"
        }
    
    def generate_random_name(self) -> tuple:
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        return first_name, last_name
    
    def generate_random_email(self, first_name: str, last_name: str, mobile: str) -> str:
        domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "hotmail.com"]
        random_num = random.randint(100, 999)
        return f"{first_name.lower()}.{last_name.lower()}{mobile[-4:]}{random_num}@{random.choice(domains)}"
    
    def send_login_otp(self, mobile: str) -> Dict:
        url = f"{self.base_url}/app-api/login"
        payload = {
            "is_otp": 1,
            "is_password": 0,
            "mobile": mobile,
            "otp": 123456,
            "password": ""
        }
        response = self.session.post(
            url,
            json=payload,
            headers={**self.default_headers, "Content-Type": "application/json; charset=UTF-8"}
        )
        return response.json()
    
    def login_existing_user(self, mobile: str, otp: str) -> Dict:
        url = f"{self.base_url}/app-api/verify-user"
        payload = {
            "channel": "MOBILE",
            "is_otp": 1,
            "is_password": 0,
            "mobile": mobile,
            "otp": int(otp),
            "ref_code": ""
        }
        response = self.session.post(
            url,
            json=payload,
            headers={**self.default_headers, "Content-Type": "application/json; charset=UTF-8"}
        )
        data = response.json()
        if data.get("token"):
            self.token = data["token"]
            self.cuid = data.get("cuid")
            self.user_id = data.get("userId")
            self.user_name = data.get("user_first_name")
            self.user_last_name = data.get("user_last_name")
            self.user_email = data.get("user_email_id")
            self.user_mobile = data.get("user_mobile_number")
            self.web_headers["authorization"] = f"Bearer {self.token}"
            self.default_headers["authorization"] = f"Bearer {self.token}"
        return data
    
    def register_new_user(self, email: str, mobile: int, name: str, last_name: str, 
                         otp: int, ref_code: str, password: str = "12345") -> Dict:
        url = f"{self.base_url}/app-api/verify-user"
        payload = {
            "channel": "MOBILE",
            "email": email,
            "is_otp": 1,
            "is_password": 0,
            "lastName": last_name,
            "mobile": mobile,
            "name": name,
            "otp": otp,
            "password": password,
            "ref_code": ref_code
        }
        response = self.session.post(
            url,
            json=payload,
            headers={**self.default_headers, "Content-Type": "application/json; charset=UTF-8"}
        )
        data = response.json()
        if data.get("token"):
            self.token = data["token"]
            self.cuid = data.get("cuid")
            self.user_id = data.get("userId")
            self.user_name = name
            self.user_last_name = last_name
            self.user_email = email
            self.user_mobile = mobile
            self.web_headers["authorization"] = f"Bearer {self.token}"
            self.default_headers["authorization"] = f"Bearer {self.token}"
        return data
    
    def get_user_profile(self) -> Dict:
        url = f"{self.base_url}/app-api/user-profile"
        response = self.session.post(
            url,
            headers={**self.default_headers, "Content-Length": "0"},
            data=""
        )
        return response.json()
    
    def resend_email_verification(self) -> Dict:
        url = f"{self.web_url}/cst/app-api/resend_email_verification"
        headers = {
            **self.web_headers,
            "authorization": f"Bearer {self.token}"
        }
        response = self.session.get(url, headers=headers)
        return response.json()
