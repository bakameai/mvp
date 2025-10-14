from fastapi import APIRouter, Request
import logging

router = APIRouter()


@router.post("/incoming")
async def handle_telnyx_incoming(request: Request):
    body = await request.json()
    logging.info(f"Received Telnyx webhook: {body}")

    # Optionally inspect event type and act on it
    event_type = body.get("data", {}).get("event_type")
    if event_type == "call.initiated":
        logging.info("Incoming call initiated event received.")

    return {"status": "received", "event": event_type}
