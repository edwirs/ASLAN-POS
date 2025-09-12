import requests
from django.conf import settings
from datetime import timedelta

FACTUS_API_URL = "https://api-sandbox.factus.com.co"
CLIENT_ID = "9e990a1c-e566-4172-9957-6226cd9e7f91"
CLIENT_SECRET = "NIq8gczyPGTJ6zEHJmqwtOyZeTkWBi1wNkynCWk1"
USERNAME = "sandbox@factus.com.co"
PASSWORD = "sandbox2024%"

def get_token():
    url = f"{FACTUS_API_URL}/oauth/token"
    data = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def create_invoice(sale):
    token = get_token()

    start_date = sale.date_joined.date()
    end_date = start_date + timedelta(days=1)

    # Cliente
    customer = {
        "identification": sale.client.dni,
        "dv": sale.client.dni[-1] if sale.client.dni.isdigit() else "0",
        "company": "",
        "trade_name": sale.client.names,
        "names": sale.client.names,
        "address": sale.client.address or "Sin dirección",
        "email": sale.client.email or "correo@demo.com",
        "phone": sale.client.mobile or "0000000000",
        "legal_organization_id": "1",       # persona jurídica
        "tribute_id": "21",                 # régimen común
        "identification_document_id": "3",  # CC
        "municipality_id": "980"            # Bogotá (ajusta según tu cliente)
    }

    # Items
    items = []
    for detail in sale.saledetail_set.all():
        discount_rate = float(detail.dscto or 0) * 100
        discount = float(detail.total_dscto or 0)
        tax_rate = "19.00" if detail.product.with_tax else "0.00"

        items.append({
            "scheme_id": "0",  # fijo por ahora
            "note": "",
            "code_reference": detail.product.code,
            "name": detail.product.name,
            "quantity": float(detail.cant),
            "discount_rate": discount_rate,
            "discount": discount,
            "price": float(detail.price),
            "tax_rate": tax_rate,
            "unit_measure_id": 70,
            "standard_code_id": 1,
            "is_excluded": 0,
            "tribute_id": 1,
            "withholding_taxes": []
        })

    payload = {
        "numbering_range_id": 8,
        "reference_code": str(sale.id),
        "observation": f"Factura generada desde POS - Venta #{sale.id}",
        "payment_form": "1" if getattr(sale, "typemethods", "") == "contado" else "2",
        "payment_due_date": str(getattr(sale, "expiration_date", "")) if getattr(sale, "typemethods", "") == "credito" else str(end_date),
        "payment_method_code": "10" if getattr(sale, "paymentmethod", "") == "efectivo" else "42",
        "operation_type": 10,
        "send_email": False,
        "order_reference": {
            "reference_code": f"sale-{sale.id}",
            "issue_date": str(sale.date_joined.date())
        },
        "billing_period": {
            "start_date": str(start_date),
            "start_time": "00:00:00",
            "end_date": str(end_date),
            "end_time": "23:59:59"
        },
        "customer": customer,
        "items": items
    }

    url = f"{FACTUS_API_URL}/v1/bills/validate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("========== PAYLOAD ENVIADO A FACTUS ==========")
    import json
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    response = requests.post(url, json=payload, headers=headers)

    # Si falla, imprime respuesta de factus para ver el detalle
    if response.status_code != 200:
        print("========== RESPUESTA FACTUS ==========")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)
        return {"error": f"Error {response.status_code}", "detail": error_detail}

    return response.json()


