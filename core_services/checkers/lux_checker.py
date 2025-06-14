from .base_checker import BaseChecker
import requests
from requests.exceptions import RequestException

class LuxChecker(BaseChecker):
    def __init__(self, card_data_str):
        super().__init__(card_data_str)
        self.parse_card_data()

    def parse_card_data(self):
        parts = self.card_data.strip().split('|')
        if len(parts) < 4:
            raise ValueError("Invalid card data format.")
        self.card_number, self.month, self.year, self.cvv = parts[:4]
        self.month = self.month.zfill(2)  # Ensure month is two digits
        self.year = self.year[-2:]  # Use last two digits of the year

    def check(self):
        url = "https://mirror1.luxchecker.vc/apiv2/ck.php"
        params = {
            'cardnum': self.card_number,
            'expm': self.month,
            'expy': self.year,
            'cvv': self.cvv,
            'key': 'c172ea5a3c2762789cba0cd334a78382',
            'username': 'markccshop',  
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                # data = {'result': 0, 'cvv_response': 'Matched', 'auth_message': 'APPROVAL', 'error': 'none', 'credits': '306', 'auth_code': '0'}
                # print(data)
                if 'error' in data and data['error'] != 'none':
                    raise Exception(data['error'])
                return data  # Return the JSON response directly
            else:
                raise Exception(f"Checker API call failed with status code {response.status_code}")
        except RequestException as e:
            raise Exception(f"Request to checker API failed: {e}")
