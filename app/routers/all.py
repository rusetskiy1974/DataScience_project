from app.routers.auth import router as router_auth
from app.routers.parking import router as router_parking
from app.routers.checkers import router as router_checkers
from app.routers.users import router as router_users
from app.routers.cars import router as router_cars
from app.routers.parking import router as router_parking
from app.routers.me import router as router_me
from app.routers.payments import router as router_payment
from app.routers.rates import router as router_rate
from app.routers.transactions import router as router_transactions
from app.routers.black_list import router as router_black_list

all_routers = [
    router_auth,
    router_me,
    router_users,
    router_cars,
    router_parking,
    router_checkers,
    router_payment,
    router_rate,
    router_transactions,
    router_black_list,
]
