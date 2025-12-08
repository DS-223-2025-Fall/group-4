import requests
import streamlit as st
from typing import Optional, Dict, Any, Tuple

BASE_URL = None

def init(api_url: str):
    global BASE_URL
    BASE_URL = api_url.rstrip('/')

def _params_to_tuple(params: Optional[Dict[str, Any]]) -> Tuple[Tuple[str, Any], ...]:
    if not params:
        return ()
    return tuple(sorted([(k, v) for k, v in params.items()]))

@st.cache_data(ttl=300)
def _cached_get(full_url: str, params_tuple: Tuple[Tuple[str, Any], ...], token: Optional[str]):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    resp = requests.get(full_url, params=dict(params_tuple), headers=headers, timeout=12)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return resp.text

def _handle_request(func, *args, **kwargs):
    try:
        with st.spinner("Loading..."):
            return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        # Extract user-friendly error message from response
        error_msg = f"API Error: {e}"
        try:
            if e.response is not None:
                error_detail = e.response.json().get('detail', str(e))
                error_msg = f"Error: {error_detail}"
        except:
            pass
        st.error(error_msg)
        return None
    except requests.exceptions.Timeout as e:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError as e:
        st.error("Unable to connect to the API. Please check if the service is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def get(path: str, params: Optional[Dict[str, Any]] = None):
    if BASE_URL is None:
        st.error("API client not initialized (BASE_URL is None)")
        return None

    full_url = f"{BASE_URL}{path if path.startswith('/') else '/' + path}"
    token = st.session_state.get('auth_token')

    # Demo mode fallback: if running in demo, return None here; callers should handle.
    if st.session_state.get('demo_mode'):
        return None

    def _do_get():
        params_tuple = _params_to_tuple(params)
        try:
            return _cached_get(full_url, params_tuple, token)
        except requests.exceptions.HTTPError as e:
            # Don't show error for 404/422, just return None
            if e.response.status_code in [404, 422]:
                return None
            raise
    
    return _handle_request(_do_get)

def post(path: str, payload: Dict[str, Any]):
    if BASE_URL is None:
        st.error("API client not initialized (BASE_URL is None)")
        return None
    full_url = f"{BASE_URL}{path if path.startswith('/') else '/' + path}"
    token = st.session_state.get('auth_token')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    def _do_post():
        resp = requests.post(full_url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text

    return _handle_request(_do_post)

def put(path: str, payload: Dict[str, Any]):
    if BASE_URL is None:
        st.error("API client not initialized (BASE_URL is None)")
        return None
    full_url = f"{BASE_URL}{path if path.startswith('/') else '/' + path}"
    token = st.session_state.get('auth_token')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    def _do_put():
        resp = requests.put(full_url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text

    return _handle_request(_do_put)

def auth_login(email: str, password: str):
    if BASE_URL is None:
        st.error("API client not initialized (BASE_URL is None)")
        return None
    full_url = f"{BASE_URL}/auth/login"

    # Demo fallback
    if st.session_state.get('demo_mode'):
        st.session_state.auth_token = "demo-token"
        return {"token": "demo-token", "user": {"email": email, "name": "Demo User"}}

    def _do_login():
        resp = requests.post(full_url, json={"email": email, "password": password}, timeout=12)
        resp.raise_for_status()
        return resp.json()

    result = _handle_request(_do_login)
    if result and isinstance(result, dict) and 'token' in result:
        st.session_state.auth_token = result['token']
    return result
