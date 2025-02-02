
from fastapi import FastAPI, Request
import uvicorn
from mail import mass_email_dispatch
from conf import load_conf
from log import log
from models import load_email_from_json, load_payloads_from_json, load_recipients_from_json
from models import find_content

CONFIG_FILE = "config/config.json"
RECIPIENTS_FILE = "config/recipients.json"
CONTENT_FILE = "config/contents.json"
PAYLOAD_CONF_FILE = "config/payloads.json"

# Инициализация FastAPI
app = FastAPI()

# API Endpoint для регистрации событий
@app.post("/api/{event}")
async def handle_event(event: str, request: Request):
    query_params = request.query_params
    recipient_id = query_params.get("q")

    if recipient_id:
        print(f"Event '{event}' triggered by recipient_id: {recipient_id}")
        return {"status": "success", "event": event, "recipient_id": recipient_id}
    else:
        return {"status": "error", "message": "Recipient ID not provided"}


# Пример использования
if __name__ == "__main__":
    
    try:
        configs = load_conf(CONFIG_FILE)
        recipients = load_recipients_from_json(load_conf(RECIPIENTS_FILE))
        mail_contents = load_email_from_json(load_conf(CONTENT_FILE))
        payloads = load_payloads_from_json(load_conf(PAYLOAD_CONF_FILE))
    except Exception as e:
        log(f"Error loading configuration: {e}", "ERROR")

    log(f"Configurations loaded.", "INFO")
    

    target_payload = find_content(payloads, "phishing_html_submit")
    target_content = find_content(mail_contents, "update")
    log(f"Payload type {target_payload.name} enabled.", "INFO")
    log(f"Message about {target_content.name} enabled.", "INFO")

    # Запуск массовой рассылки
    mass_email_dispatch(configs, target_content, target_payload, recipients)

    uvicorn.run(app, host="0.0.0.0", port=int(configs["PORT"]))