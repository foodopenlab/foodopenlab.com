import sys
import asyncio
from pathlib import Path

# Setup paths
_BACKEND_DIR = Path("c:/Users/hi/Documents/com.foodopenlab/com.auditor")
sys.path.insert(0, str(_BACKEND_DIR))
sys.path.insert(0, str(_BACKEND_DIR / "core"))
sys.path.insert(0, str(_BACKEND_DIR / "apps"))

from matrix.grid_oracle_database_manager import engine
from sqlalchemy import text

async def main():
    if engine is None:
        print("Engine is None")
        return
    async with engine.begin() as conn:
        # Get admin rows
        res = await conn.execute(text("SELECT id FROM admins"))
        admin_ids = [row[0] for row in res.fetchall()]
        print(f"Existing admins: {admin_ids}")
        
        # Check users table
        res = await conn.execute(text("SELECT id FROM users"))
        user_ids = [row[0] for row in res.fetchall()]
        print(f"Existing users: {user_ids}")
        
        for aid in admin_ids:
            if aid not in user_ids:
                print(f"Inserting user for admin {aid}...")
                await conn.execute(text(
                    "INSERT INTO users (id, user_type, created_at) VALUES (:id, 'admin', NOW())"
                ), {"id": aid})
                print(f"Inserted user for admin {aid}")
        
        # Check anonymous rows
        res = await conn.execute(text("SELECT id FROM anonymous"))
        anon_ids = [row[0] for row in res.fetchall()]
        print(f"Existing anonymous users: {anon_ids}")
        for aid in anon_ids:
            if aid not in user_ids:
                print(f"Inserting user for anonymous {aid}...")
                await conn.execute(text(
                    "INSERT INTO users (id, user_type, created_at) VALUES (:id, 'anonymous', NOW())"
                ), {"id": aid})
                print(f"Inserted user for anonymous {aid}")

        # Check expert_users rows
        res = await conn.execute(text("SELECT id FROM expert_users"))
        expert_ids = [row[0] for row in res.fetchall()]
        print(f"Existing expert users: {expert_ids}")
        for aid in expert_ids:
            if aid not in user_ids:
                print(f"Inserting user for expert {aid}...")
                await conn.execute(text(
                    "INSERT INTO users (id, user_type, created_at) VALUES (:id, 'expert', NOW())"
                ), {"id": aid})
                print(f"Inserted user for expert {aid}")

if __name__ == "__main__":
    asyncio.run(main())
