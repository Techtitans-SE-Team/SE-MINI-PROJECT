"""Create an Admin account:  python -m scripts.create_admin "Admin Name" admin@example.com 'Password123'"""
import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.main import init_db
from app.models import ROLE_ADMIN, Role, User
from app.security import hash_password

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    name, email, password = sys.argv[1:]
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email.lower())):
            sys.exit("User already exists")
        role = db.scalar(select(Role).where(Role.role_name == ROLE_ADMIN))
        db.add(User(name=name, email=email.lower(), password_hash=hash_password(password), role_id=role.role_id))
        db.commit()
        print(f"Admin {email} created")
