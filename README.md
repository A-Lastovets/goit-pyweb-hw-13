# goit-pyweb-hw-11

Дані доступу до БД прописані у файлі .env

Запустити докер контейнер :  docker-compose up -d

Створиться два контейнери :  Container HW11_postgres                 Started                   
                             Container HW11_pgadmin                  Started 

                            Додатково створив ще один для того щоб підключитись до бази даних через локальну програму pgАdmin 4

Додаток запускається командою :  uvicorn main:app --reload


Тестування CRUD операцій: У Swagger UI можливо протестувати основні функції:

POST /contacts – створити новий контакт.
GET /contacts – отримати список всіх контактів.
GET /contacts/{id} – отримати контакт за ідентифікатором.
PUT /contacts/{id} – оновити контакт.
DELETE /contacts/{id} – видалити контакт.

Тестування пошуку і нагадування:

GET /contacts/search – пошук за ім'ям, прізвищем або email.
GET /contacts/upcoming-birthdays – отримати список контактів з днями народження на найближчі 7 днів.
