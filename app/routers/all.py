from app.routers.users import router as router_users
from app.routers.checkers import router as router_checkers
from app.routers.auth import router as router_auth

all_routers = [
    router_users,
    router_checkers,
    router_auth,
]
