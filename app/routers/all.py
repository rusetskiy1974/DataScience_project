from app.routers.users import router as router_users
from app.routers.checkers import router as router_checkers
from app.routers.auth import router as router_auth
from app.routers.parking import router as router_parking

all_routers = [
    router_users,
    router_checkers,
    router_auth,
    router_parking,  # Add more routers here as needed.
]
