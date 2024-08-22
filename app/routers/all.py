from app.routers.auth import router as router_auth
from app.routers.checkers import router as router_checkers
from app.routers.users import router as router_users
from app.routers.cars import router as router_cars
from app.routers.parking import router as router_parking

all_routers = [
    router_auth,
    router_users,
    router_cars,
    router_parking,
    router_checkers,
]
