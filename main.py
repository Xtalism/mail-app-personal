import base64
import os

import requests

from ms_graph import generate_access_token


def draft_attachment(file_path):
    if not os.path.exists(file_path):
        print("file not found...")
        return

    with open(file_path, "rb") as upload:
        media_content = base64.b64encode(upload.read())

    data_body = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "contentBytes": media_content.decode("utf-8"),
        "name": os.path.basename(file_path),
    }
    return data_body


APP_ID = ""  # Application (client) ID of the app registration in Azure AD
TENANT_ID = "consumers"
CLIENT_ID = ""  # Object ID of the app registration in Azure AD

SCOPES = ["Mail.Send", "Mail.ReadWrite"]

access_token = generate_access_token(app_id=APP_ID, scopes=SCOPES, tenant_id=TENANT_ID)

headers = {"Authorization": "Bearer " + access_token}

request_body = {
    "message": {
        "toRecipients": [{"emailAddress": {"address": "mail@gmail.com"}}],
        "subject": "You got an email",
        "importance": "normal",
        "body": {
            "contentType": "HTML",
            "content": (
                "<h3>HTML Table Test</h3>"
                "<table border='1' cellpadding='10' style='border-collapse: collapse;'>"
                "<tr><th>Item</th><th>Price</th><th>Quantity</th></tr>"
                "<tr><td>Apple</td><td>$1.00</td><td>3</td></tr>"
                "<tr><td>Banana</td><td>$0.50</td><td>5</td></tr>"
                "</table>"
            ),
        },
        "attachments": [draft_attachment("monkey.jpg")],
    }
}

GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
endpoint = GRAPH_ENDPOINT + "/me/sendMail"

response = requests.post(endpoint, headers=headers, json=request_body)
if response.status_code == 202:
    print("email sent")
else:
    print(response.status_code)
    print(response.text)
