import razorpay
import backoff
import httpx
import os

BASE_URL = os.getenv("RAZORPAY_API_URL")
API_KEY = os.getenv("RAZORPAY_API_KEY")
API_SECRET = os.getenv("RAZORPAY_API_SECRET")
TIMEOUT = int(os.getenv("RAZORPAY_TIMEOUT", 10))
MAX_RETRIES = int(os.getenv("RAZORPAY_MAX_RETRIES", 3))

client =  razorpay.Client(auth=(API_KEY, API_SECRET))

@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=MAX_RETRIES)
def create_order(amount: int, receipt: str="", notes: dict={}) -> dict:
    try:
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": receipt,
            "notes": notes,
            "payment_capture": 1
        }, timeout=TIMEOUT)
        return order
    except Exception as e:
        raise e

@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=MAX_RETRIES)
def verify_order(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)
        return True
    
    except razorpay.errors.SignatureVerificationError as e1:
        return False
    
    except Exception as e:
        return False
