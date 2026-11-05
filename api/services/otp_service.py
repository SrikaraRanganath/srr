import httpx
import backoff
import os

BASE_URL = os.getenv("OTP_API_URL")
TIMEOUT = int(os.getenv("OTP_TIMEOUT", 30))
AUTH_KEY = os.getenv("OTP_AUTH_KEY")
TEMPLATE_ID = os.getenv("OTP_TEMPLATE_ID")
OTP_EXPIRY = int(os.getenv("OTP_EXPIRY", 30))
OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))
MAX_RETRIES = int(os.getenv("OTP_MAX_RETRIES", 3))


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=MAX_RETRIES)
async def send_otp(mobile: str, type: str):
    if len(mobile) != 12 or not mobile.startswith("91"):
        return { 'type': 'error', 'message': 'Invalid request' }
    
    URL = f"{BASE_URL}?mobile={mobile}&authkey={AUTH_KEY}&template_id={TEMPLATE_ID}&otp_expiry={OTP_EXPIRY}&realTimeResponse=1&otp_length={OTP_LENGTH}"

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(URL, json={"var1": type}, headers=headers)
        response.raise_for_status()
        return response

@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=MAX_RETRIES)
async def verify_otp(mobile: str, otp: int):
    if len(mobile) != 12 or not mobile.startswith("91") or not (10**(OTP_LENGTH-1) <= otp < 10**OTP_LENGTH):
        return { 'type': 'error', 'message': 'Invalid request' }
    
    URL = f"{BASE_URL}/verify?mobile={mobile}&otp={otp}"

    headers = {
        "Content-Type": "application/json",
        "authkey": AUTH_KEY
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(URL, headers=headers)
        response.raise_for_status()
        return response
    
@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=MAX_RETRIES)
async def resend_otp(mobile: str):
    if len(mobile) != 12 or not mobile.startswith("91"):
        return { 'type': 'error', 'message': 'Invalid request' }

    URL = f"{BASE_URL}/retry?mobile={mobile}&authkey={AUTH_KEY}&retrytype=text"

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(URL, headers=headers)
        response.raise_for_status()
        return response