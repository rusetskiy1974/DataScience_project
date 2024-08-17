from app.routers.users import router as router_users
from app.routers.checkers import router as router_checkers

all_routers = [
    router_users,
    router_checkers,
]
