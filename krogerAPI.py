# test for Kroger API:

import requests
import base64
import pandas as pd

#Kroger API credentials
CLIENT_ID = "foodinflationdashboard-bbc9fx2c"
CLIENT_SECRET = "hHBvXzT5FKHn3V1Xqnv-2q-dnbkN8Fub1qPkunyW"
TOKEN_URL = "https://api.kroger.com/v1/connect/oauth2/token"
PRODUCT_URL = "https://api.kroger.com/v1/products"

#Step 1: Get OAuth2 Access Token 


def get_access_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact profile.compact"
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    token = response.json().get("access_token")
    print("Access token works")
    return token

#Step 2: Search for grocery products 


def search_products(search_term="milk", limit=10):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"filter.term": search_term, "filter.limit": limit}

    response = requests.get(PRODUCT_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract product info
    products = []
    for item in data.get("data", []):
        info = {
            "Description": item.get("description"),
            "Brand": item.get("brand"),
            "Category": item.get("categories"),
            "Size": item.get("items", [{}])[0].get("size"),
            "Price": item.get("items", [{}])[0].get("price", {}).get("regular"),
            "Upc": item.get("upc")
        }
        products.append(info)

    df = pd.DataFrame(products)
    print(f"✅ Retrieved {len(df)} products for '{search_term}'")
    return df


#Step 3: Example 
if __name__ == "__main__":
    df = search_products("chicken", limit=5)
    print(df)
