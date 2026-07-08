import os

from siliconvalley.adapter.outbound.client.n8n_client import N8nClient

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/siliconvalley")


def get_n8n_client() -> N8nClient:
    return N8nClient(webhook_url=N8N_WEBHOOK_URL)
