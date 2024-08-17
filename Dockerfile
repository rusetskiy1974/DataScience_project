# Використовуйте офіційний образ Python як базовий
FROM python:3.11

# Встановіть робочу директорію
WORKDIR /app

# Встановіть Poetry
RUN pip install poetry

# Скопіюйте файли конфігурації Poetry
COPY pyproject.toml poetry.lock ./

# Встановіть залежності за допомогою Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

# Скопіюйте залишок коду вашого додатку до контейнера
COPY . .

# Виставте команду для запуску додатку
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
