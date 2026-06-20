import webbrowser
from datetime import datetime
import json
import os
import msal

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def generate_access_token(app_id, scopes, tenant_id=None):
    access_token_cache = msal.SerializableTokenCache()

    # Safely load the token cache if it exists
    if os.path.exists('ms_graph_api_token.json'):
        with open('ms_graph_api_token.json', 'r') as _f:
            access_token_cache.deserialize(_f.read())

    if tenant_id:
        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    else:
        authority_url = "https://login.microsoftonline.com/common"

    client = msal.PublicClientApplication(
        client_id=app_id, 
        authority=authority_url,
        token_cache=access_token_cache
    )

    accounts = client.get_accounts()
    token_response = None
    
    if accounts:
        # MSAL handles expiration checks and token refreshing automatically here!
        token_response = client.acquire_token_silent(scopes, accounts[0])

    if not token_response:
        # Authenticate if no token was found, or if silent acquisition failed
        flow = client.initiate_device_flow(scopes=scopes)
        
        if 'user_code' not in flow:
            raise ValueError(f"Failed to create device flow. Error details: {json.dumps(flow, indent=2)}")
            
        print('user_code: ' + flow['user_code'])
        webbrowser.open(flow['verification_uri'])
        
        print("Waiting for Microsoft's server to confirm your login...")
        token_response = client.acquire_token_by_device_flow(flow)
        print("Microsoft confirmed the login!")

    # Save the updated token cache
    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise Exception(f"Failed to get access token: {token_response.get('error_description')}")

if __name__ == '__main__':
    ...