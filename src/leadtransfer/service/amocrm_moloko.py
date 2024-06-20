from datetime import datetime
import json
import requests
import time

from django.conf import settings
from django.core.mail import send_mail


def _save_token_data(data: dict):
    url = f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/oauth2/access_token"
    response = requests.post(url, json=data).json()
    data = {
        "access_token": response['access_token'],
        "refresh_token": response['refresh_token'],
        "token_type": response['token_type'],
        "expires_in": response['expires_in'],
        "end_token_time": response['expires_in'] + time.time(),
    }
    with open(settings.BASE_DIR / 'moloko_refresh_token.txt', 'w') as outfile:
        json.dump(data, outfile)
    return data["access_token"]


def _auth():
    data = {
        'client_id': settings.AMO_MOLOKO_INTEGRATION_CLIENT_ID,
        'client_secret': settings.AMO_MOLOKO_INTEGRATION_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': settings.AMO_MOLOKO_INTEGRATION_CODE,
        'redirect_uri': settings.AMO_MOLOKO_INTEGRATION_REDIRECT_URI,
    }
    return _save_token_data(data)


def _update_access_token(refresh_token: str):
    data = {
        "client_id": settings.AMO_MOLOKO_INTEGRATION_CLIENT_ID,
        "client_secret": settings.AMO_MOLOKO_INTEGRATION_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": settings.AMO_MOLOKO_INTEGRATION_REDIRECT_URI,
    }
    return _save_token_data(data)


def _get_access_token():
    with open(settings.BASE_DIR / 'moloko_refresh_token.txt') as json_file:
        token_info = json.load(json_file)
        if token_info["end_token_time"] - 60 < time.time():
            return _update_access_token(token_info["refresh_token"])
        else:
            return dict(token_info)["access_token"]


def get_contact_id_by_lead_id(lead_id: str):
    headers = {
        "Authorization": f"Bearer {_get_access_token()}",
    }
    url = f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}/links"
    response = requests.get(url, headers=headers).json()
    links = response.get("_embedded", {}).get("links", [])
    if links:
        for link in links:
            if link.get("to_entity_type", "") == "contacts":
                return link.get("to_entity_id", "")
    return ""


def get_contact_by_id(contact_id: str):
    headers = {
        "Authorization": f"Bearer {_get_access_token()}",
    }
    url = f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/api/v4/contacts/{contact_id}"
    return requests.get(url, headers=headers).json()


def _get_phone_number(contact_data):
    custom_fields = contact_data.get("custom_fields_values", [])
    for field in custom_fields:
        if field.get("field_name", "") == "Телефон":
            return field.get("values")[0].get("value", "")
    return ""


def _get_lead_by_id(lead_id: str):
    headers = {
        "Authorization": f"Bearer {_get_access_token()}",
    }
    url = f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}"
    return requests.get(url, headers=headers).json()


def _get_last_lead_comment(lead_id: str):
    headers = {
        "Authorization": f"Bearer {_get_access_token()}",
    }
    lead_links = requests.get(
        f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}/links",
        headers=headers
    ).json()
    company_id = lead_links['_embedded']['links'][1]['to_entity_id']
    company_notes = requests.get(
        f"https://{settings.AMO_MOLOKO_INTEGRATION_SUBDOMAIN}.amocrm.ru/api/v4/companies/{company_id}/notes",
        headers=headers
    ).json()
    comments = [note["params"]["text"] for note in company_notes["_embedded"]["notes"] if "text" in note["params"]]
    return comments[-1]


def handle_deal(lead_id: str):
    lead = _get_lead_by_id(lead_id)
    if lead["pipeline_id"] != 8137234:
        return
    contact_id = get_contact_id_by_lead_id(lead_id)
    contact_data = get_contact_by_id(contact_id)
    phone_number = _get_phone_number(contact_data)
    send_mail(
        "Лид",
        f"Номер телефона: {phone_number}\nКомментарий: {_get_last_lead_comment(lead_id)}",
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_RECEIVER],
        fail_silently=False,
    )
