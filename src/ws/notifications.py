from app.db.session import SessionLocal
from repository.buy.buy_repository import BuyRepository
from ws.manager import notification_manager


async def push_lead_notification(lead_ids: list[int], source_id: str) -> None:
    try:
        async with SessionLocal() as session:
            repo = BuyRepository(session)
            leads = await repo.get_leads_for_notification(lead_ids)

        for lead in leads:
            payload = {
                "sourceId": source_id,
                "lead": {
                    "id": lead["id"],
                    "customerName": lead["customer_name"],
                    "mobile": lead["mobile"],
                    "telecaller": lead["telecaller"],
                    "executive": lead["executive"],
                    "make": lead["make"],
                    "model": lead["model"],
                    "year": lead["year"],
                },
            }
            targets = [u for u in [lead["telecaller"], lead["executive"]] if u]
            await notification_manager.push_to_users(targets, payload)
    except Exception:
        pass
