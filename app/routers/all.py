from app.routers.auth import router as router_auth
from app.routers.checkers import router as router_checkers
from app.routers.users import router as router_users

all_routers = [
    router_auth,
    router_users,
    router_checkers,
]
