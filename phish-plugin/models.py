import json

class EmailContent:
    def __init__(self, name, subject, message):
        self.name = name
        self.subject = subject
        self.message = message

class Payload:
    def __init__(self, technique, name, template, attachment_path):
        self.technique = technique
        self.name = name
        self.template = template
        self.attachment_path = attachment_path

class Recipient:
    def __init__(self, id, email):
        self.id = id
        self.email = email

def load_email_from_json(json_data):
    emails = []
    for item in json_data: # обрабатываем список JSON объектов
        for name, email_data in item.items():
            email_info = email_data['email']
            email = EmailContent(name, email_info['subject'], email_info['message'])
            emails.append(email)
    return emails

def load_payloads_from_json(json_data):
    payloads = []
    for technique, payload_list in json_data.items():
        for payload_data in payload_list:
            payload = Payload(technique, payload_data['name'], payload_data['template'], payload_data['attachment_path'])
            payloads.append(payload)
    return payloads

def load_recipients_from_json(json_data):
    recipients = []
    for item in json_data:
        recipients.append(Recipient(item['id'], item['email']))
    return recipients
        
# def load_recipients_from_json(json_data):
#     recipients = []
#     for id, payload_list in json_data.items():
#         for payload_data in payload_list:
#             payload = Payload(technique, payload_data['name'], payload_data['attachment_path'])
#             payloads.append(payload)
#     return payloads

def find_content(contents, target_content_name):

    for item in contents:
        if item.name == target_content_name:
            return item
    return