                                                          
                 
                                                          

import requests
from urllib.parse import quote


                                                          
                    
                                                          

def kqx(
    upi_id: str,
    amount: int,
    plan_name: str = "",
    merchant_name: str = ""
) -> str:
    """
    Generate a UPI payment QR URL.

    Parameters:
        upi_id       : Admin's UPI ID
        amount       : Exact payment amount
        plan_name    : Selected button/plan name
        merchant_name: Optional merchant name

    Returns:
        QR Server URL containing a complete UPI payment URI.
    """

    if not upi_id:
        raise ValueError("UPI ID is required.")

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

                  
    upi_id = str(upi_id).strip()
    plan_name = str(plan_name).strip()
    merchant_name = str(merchant_name).strip()

                            
    params = [
        f"pa={quote(upi_id, safe='')}",
        f"am={amount}",
        "cu=INR"
    ]

                                       
    if plan_name:
        params.append(
            f"tn={quote(plan_name, safe='')}"
        )

                            
    if merchant_name:
        params.append(
            f"pn={quote(merchant_name, safe='')}"
        )

                      
    upi_uri = "upi://pay?" + "&".join(params)

                                        
    qr_data = quote(upi_uri, safe="")

                   
    qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        f"?size=500x500&margin=10&data={qr_data}"
    )

    return qr_url


                                                          
                  
                                                          

def kzz(url: str, timeout: int = 10) -> dict:
    """
    Fetch data from a URL.

    Returns:
        {
            "status": True/False,
            "data": "...",
            "error": "..."
        }
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/151.0 Safari/537.36"
                )
            }
        )

        if response.status_code == 200:
            return {
                "status": True,
                "data": response.text
            }

        return {
            "status": False,
            "error": f"HTTP {response.status_code}"
        }

    except requests.RequestException as e:
        return {
            "status": False,
            "error": str(e)
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }


                                                          
                 
                                                          

def zzv(
    url: str,
    proxies: list = None,
    timeout: int = 10
) -> dict:
    """
    Try a URL through multiple proxies.

    If no proxies are supplied, a direct request is used.
    """

    if not proxies:
        return kzz(
            url,
            timeout=timeout
        )

    for proxy in proxies:

        if not proxy:
            continue

        try:
            proxy = str(proxy).strip()

            proxy_dict = {
                "http": proxy,
                "https": proxy
            }

            response = requests.get(
                url,
                proxies=proxy_dict,
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "Chrome/151.0 Safari/537.36"
                    )
                }
            )

            if response.status_code == 200:
                return {
                    "status": True,
                    "data": response.text,
                    "proxy": proxy
                }

        except requests.RequestException:
            continue

        except Exception:
            continue

    return {
        "status": False,
        "error": "All proxies failed"
    }
