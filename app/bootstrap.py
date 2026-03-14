from sqlalchemy import select
from app.db import SessionLocal
from app.models import User, Agent, Organization
from app.utils import now_ts
import os

ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")


def bootstrap_system():
    db = SessionLocal()

    try:
        # ------------------------------------------------
        # Ensure organization exists
        # ------------------------------------------------
        org_slug = "patroai"

        org = db.execute(
            select(Organization).where(Organization.slug == org_slug)
        ).scalar_one_or_none()

        if not org:
            org = Organization(
                slug=org_slug,
                name="PatroAI"
            )
            db.add(org)
            db.commit()

        # ------------------------------------------------
        # Ensure admin user exists
        # ------------------------------------------------
        admin = db.execute(
            select(User).where(User.role == "admin")
        ).scalar_one_or_none()

        if not admin and ADMIN_EMAILS:
            admin = User(
                org_slug=org_slug,
                email=ADMIN_EMAILS[0],
                name="Super Admin",
                role="admin",
                approved_at=now_ts()
            )
            db.add(admin)
            db.commit()

        # ------------------------------------------------
        # Ensure core agents exist
        # ------------------------------------------------
        core_agents = ["Orkio", "Chris", "Orion"]

        for agent_name in core_agents:

            existing = db.execute(
                select(Agent).where(
                    Agent.org_slug == org_slug,
                    Agent.name == agent_name
                )
            ).scalar_one_or_none()

            if not existing:
                agent = Agent(
                    org_slug=org_slug,
                    name=agent_name,
                    system_prompt=f"{agent_name} core system agent",
                    active=True
                )

                db.add(agent)

        db.commit()

    finally:
        db.close()
