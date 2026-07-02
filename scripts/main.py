import base64
import os

import requests
from dotenv import load_dotenv
from ms_graph import generate_access_token


def draft_attachment(file_path, is_inline=False, content_id=None):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    with open(file_path, "rb") as upload:
        media_content = base64.b64encode(upload.read())

    data_body = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "contentBytes": media_content.decode("utf-8"),
        "name": os.path.basename(file_path),
    }

    if is_inline and content_id:
        data_body["isInline"] = True
        data_body["contentId"] = content_id

    return data_body


load_dotenv()

APP_ID = os.environ.get("APP_ID")
TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")

SCOPES = ["Mail.Send", "Mail.ReadWrite"]

access_token = generate_access_token(app_id=APP_ID, scopes=SCOPES, tenant_id=TENANT_ID)

headers = {"Authorization": "Bearer " + access_token}

with open("./html/email.html", "r", encoding="utf-8") as f:
    html_content = f.read()

attachments_list = []

footer_img = draft_attachment(
    "html/footer/urrea_footer.png", is_inline=True, content_id="urreaFooterId"
)
if footer_img:
    attachments_list.append(footer_img)

# normal_file = draft_attachment("../images/monkey.jpg")
# if normal_file:
#     attachments_list.append(normal_file)

request_body = {
    "message": {
        "toRecipients": [{"emailAddress": {"address": "manuel.pina.olivas@gmail.com"}}],
        "subject": "Reporte Ejecutivo - Resumen",
        "importance": "normal",
        "body": {
            "contentType": "HTML",
            "content": html_content,
        },
        "attachments": attachments_list,
    }
}

GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
endpoint = GRAPH_ENDPOINT + "/me/sendMail"

response = requests.post(endpoint, headers=headers, json=request_body)
if response.status_code == 202:
    print("Email sent successfully!")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
