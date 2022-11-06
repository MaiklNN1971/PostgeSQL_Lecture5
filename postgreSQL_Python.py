import psycopg2
import csv
import io
#----------------------------------------------------------------------------------
def create_db(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            firstname VARCHAR(20),
            lastname VARCHAR(20),
            email VARCHAR(40) NOT NULL);
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            client_id INTEGER NOT NULL REFERENCES clients(id),
            phone VARCHAR(20) NOT NULL);
        """)
    conn.commit()

#----------------------------------------------------------------------------------
# удаляем содержимое таблиц
def delete_tabl(cur):
    cur.execute("""
        DELETE FROM phones;
        """)
    cur.execute("""
        DELETE FROM clients;
        """)
    cur.fetchall()

#----------------------------------------------------------------------------------
def add_client(cur, customer_data):
    if len(customer_data) < 3:
        print('Необходимо указать все данные клиента (Имя, Фамилия, e-mail) ')
        return
    print(f'введены данные: {customer_data[0],customer_data[1],customer_data[2]}')
    cur.execute("""
        INSERT INTO clients(firstname, lastname, email) VALUES(%s, %s, %s) RETURNING id, firstname, lastname;
        """, (customer_data[0], customer_data[1], customer_data[2]))
    cur.fetchone()

#----------------------------------------------------------------------------------
def all_clients(cur):
        cur.execute("""
            SELECT c.* , p.phone FROM clients c, phones p
            WHERE c.id=p.client_id;
            """)

        print(cur.fetchall())

#----------------------------------------------------------------------------------
def get_phone(cur, client_id, phone):
    cur.execute("""
        SELECT c.firstname, c.lastname, ph.phone FROM phones ph
         join clients c on c.id=ph.client_id
         WHERE client_id=%s AND ph.phone=%s;
        """, (client_id, phone))
    found_phone = cur.fetchall()
    print(found_phone)
    return found_phone

#----------------------------------------------------------------------------------
def add_phone(conn, cur, client_id, phone):
    # если телефона нет, заводим
    found_phone = get_phone(cur, client_id, phone)
    if found_phone is None or len(found_phone) == 0:
        print(found_phone, client_id, phone)
        cur.execute("""
            INSERT INTO phones(client_id, phone) VALUES(%s, %s);
            """, (client_id, phone))
        conn.commit()
#----------------------------------------------------------------------------------
def delete_phone(conn, cur, client_id, phone):
    cur.execute("""
        DELETE FROM phones WHERE client_id=%s and phone=%s;
        """, (client_id, phone))
    cur.execute("""
        SELECT * FROM phones WHERE client_id=%s;
        """, (client_id,))
    print(cur.fetchall())
    conn.commit()

#----------------------------------------------------------------------------------
def find_client(cur, sp_dann):
    if len(sp_dann) != 4:
        print('Введите все данные!')
        return
    first_name = sp_dann[0]
    last_name = sp_dann[1]
    email = sp_dann[2]
    phone = sp_dann[3]
    print(sp_dann[0],sp_dann[1],sp_dann[2],sp_dann[3])
    if phone is not None:
        cur.execute("""
            SELECT cl.*, p.phone FROM clients cl
            JOIN phones p ON p.client_id = cl.id
            WHERE p.phone=%s;
            """, (phone,))
        print(cur.fetchall())
    else:
        cur.execute("""
            SELECT * FROM clients 
            WHERE firstname=%s OR lastname=%s OR email=%s;
            """, (first_name, last_name, email))
    print(cur.fetchall())

# ----------------------------------------------------------------------------------
def delete_client(conn, cur, client_id):
        cur.execute("""
            DELETE FROM phones WHERE client_id=%s;
            """, (client_id,))
        cur.execute("""
            DELETE FROM clients WHERE id=%s;
            """, (client_id,))
        cur.execute("""
            SELECT * FROM clients;
            """)
        print(cur.fetchall())
        conn.commit()

#----------------------------------------------------------------------------------
def change_client(conn, cur, sp_dann):
    if len(sp_dann) != 4:
        print('Введите все данные!')
        return
    client_id = sp_dann[0]
    first_name = sp_dann[1]
    last_name = sp_dann[2]
    email = sp_dann[3]
    phone = sp_dann[4]
    if first_name is not None:
        cur.execute("""
            UPDATE clients SET firstname=%s WHERE id=%s
            """, (first_name, client_id))
    if last_name is not None:
        cur.execute("""
            UPDATE clients SET lastname=%s WHERE id=%s
            """, (last_name, client_id))
    if email is not None:
        cur.execute("""
            UPDATE clients SET email=%s WHERE id=%s
            """, (email, client_id))
    if phone is not None:
        add_phone(conn, cur, client_id, phone)

    cur.execute("""
        SELECT * FROM clients;
        """)
    cur.fetchall()
    conn.commit()


#----------------------------------------------------------------------------------
def search():
    while True:
        user_input = input("""Введите команду для работы в программе.
        
                           1 - ввод клиента (формат ввода запроса: Имя, Фамилия, электронная почта):
                           2 - вывод всех клиентов из БД
                           3 - добавить телефон для клиента (формат ввода запроса: ID-клиента, Номер телефона):
                           4 - изменяем данные о клиента (формат ввода запроса: ID-клиента, Имя, Фамилия, электронная почта, телефон):
                           5 - удаляем телефон клиента (формат ввода запроса: ID-клиента, Номер телефона):
                           6 - удаляем клиента (формат ввода запроса: ID-клиента):
                           7 - поиск клиента (формат ввода запроса: Имя, Фамилия, электронная почта, телефон):
                           100 - выход :___""")
        if user_input == '1':
            customer_data = input('введите данные клиента:')
            sp_dann=customer_data.split(",")
            add_client(cur, sp_dann)
        elif user_input == '2':
            all_clients(cur)
        elif user_input == '3':
            id_cl = input('введите ID клиента из БД:')
            phone_cl = input('введите телефон для клиента:')
            add_phone(conn, cur, id_cl, phone_cl)
        elif user_input == '4':
            customer_data = input('введите данные клиента:')
            sp_dann=customer_data.split(",")
            change_client(conn, cur, sp_dann)
        elif user_input == '5':
            id_cl = input('введите ID клиента из БД:')
            phone_cl = input('введите телефон для клиента:')
            delete_phone(conn, cur, id_cl, phone_cl)
        elif user_input == '6':
            id_cl = input('введите ID клиента из БД:')
            delete_client(conn, cur, id_cl)
        elif user_input == '7':
            customer_data = input('введите данные клиента:')
            sp_dann = customer_data.split(",")
            find_client(cur, sp_dann)
        elif user_input == '100':
            print('Работа закончена.')
            break
        else:
            print('уточните команду')

#----------------------------------------------------------------------------------
if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="Legion2020") as conn:
        with conn.cursor() as cur:
            search()
