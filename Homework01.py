from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other): # Перевірка на відповідність
        if isinstance(other, Field):
            return self.value == other.value
        return False
    
class Birthday(Field):
    def __init__(self, value):
            try:
                parsed_date = datetime.strptime(value, "%d.%m.%Y")
                super().__init__(parsed_date)
            except ValueError:
                raise ValueError("Невірний формат дати. Використовуйте ДД.ММ.РРРР")

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone):
        self._value = None
        self.value = phone  

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, phone):
        if not re.fullmatch(r'\d{10}', phone):
            raise ValueError("Телефон має бути з 10 цифр.")
        self._value = phone

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name) if isinstance(name, str) else name
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
        if phone:
            self.add_phone(phone) # Записали новий номер

    def add_phone(self, phone):
        phone_obj = Phone(phone) if isinstance(phone, str) else phone
        self.phones.append(phone_obj) # Добавка номера

    def remove_phone(self, phone):
        phone_value = phone if isinstance(phone, str) else phone.value # Видалення номера
        self.phones = [p for p in self.phones if p.value != phone_value]

    def edit_phone(self, old_phone, new_phone): # коризування номера
        old_value = old_phone if isinstance(old_phone, str) else old_phone.value
        new_obj = Phone(new_phone) if isinstance(new_phone, str) else new_phone
        for idx, p in enumerate(self.phones):
            if p.value == old_value:
                self.phones[idx] = new_obj
                return True
        return False

    def find_phone(self, phone_value): # Пошук номера
        for p in self.phones:
            if p.value == phone_value:
                return p
        return None
    
    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday_str = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else "не вказано"
        return f"Ім'я контакту: {self.name.value}, телефон: {phones}, день народження: {birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args

def input_error(func): # Переверка на помилки
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Value error: {e}"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
        except TypeError:
            return "Invalid input format."
    return inner


@input_error
def add_contact(args, contacts: AddressBook):
    if len(args) < 2:
        raise IndexError("Потрібно щонайменше ім'я і номер телефону.")
    
    name = args[0]
    phone = args[1]
    birthday = args[2] if len(args) >= 3 else None

    record = contacts.find(name)
    if record:
        record.add_phone(phone)
        if birthday:
            record.birthday = Birthday(birthday)
    else:
        record = Record(name, phone, birthday)
        contacts.add_record(record)
    return f"Контакт '{name}' створений/оновлений."


@input_error
def change_contact(args, contacts: AddressBook):
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if not record:
        raise KeyError
    success = record.edit_phone(old_phone, new_phone)
    if success:
        return "Телефонний номер оновлений"
    return "Старий номер телефону не знайдений."


@input_error
def show_phone(args, contacts: AddressBook):
    name = args[0]
    record = contacts.find(name)
    if record:
        return str(record)
    raise KeyError

@input_error
def delete_contact(args, contacts: AddressBook):
    name = args[0]
    success = contacts.delete(name)
    if success:
        return f"Контакт '{name}' видалений."
    else:
        return f"Контакт '{name}' не знайдено."

@input_error
def find_contact_by_name(args, contacts: AddressBook):
    name = args[0]
    record = contacts.find(name)
    if record:
        return f"Знайдено: {record}"
    else:
        return f"Контакт з іменем '{name}' не знайдено."

@input_error
def add_birthday(args, book: AddressBook):
    name, bday_str = args
    record = book.find(name)
    if not record:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    record.birthday = Birthday(bday_str)
    return f"День народження для '{name}' додано/оновлено."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError(f"Контакт '{name}' не знайдено.")
    if not record.birthday:
        return f"У контакта '{name}' немає збереженого дня народження."
    return f"День народження '{name}': {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book: AddressBook):
    today = datetime.today().date()
    end_of_greetings = today + timedelta(days=7)
    greetings = {}

    for record in book.data.values():
        if not record.birthday:
            continue

        bday = record.birthday.value.date()
        bday_this_year = bday.replace(year=today.year)

        if today <= bday_this_year <= end_of_greetings:
            greeting_date = bday_this_year
            if greeting_date.weekday() == 5:  # субота
                greeting_date += timedelta(days=2)
            elif greeting_date.weekday() == 6:  # неділя
                greeting_date += timedelta(days=1)

            date_str = greeting_date.strftime("%Y-%m-%d")
            if date_str not in greetings:
                greetings[date_str] = []
            greetings[date_str].append(record.name.value)

    if not greetings:
        return "Немає днів народження у найближчі 7 днів."

    result = "План привітань на тиждень:\n"
    for date_str in sorted(greetings):
        names = ', '.join(greetings[date_str])
        result += f"{date_str}: {names}\n"

    return result.strip()

def all_phone(contacts: AddressBook):
    if not contacts.data:
        return "Контакти не знайдено"
    return str(contacts)


def main():
    contacts = AddressBook()
    print("Привіт, вітаю вас в боті асистенті")

    while True:
        user_input = input("Введіть команду: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Бувай друже!")
            break
        elif command in ["hello", "hi"]:
            print("Чим можу допомогти?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(all_phone(contacts))
        elif command in ["delete", "del"]:
            print(delete_contact(args, contacts))
        elif command == "find":
            print(find_contact_by_name(args, contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(args, contacts))
        elif command == "help":
            print("Доступні команди:\n"
                "add <name> <phone> [birthday у форматі ДД.ММ.РРРР]\n"
                "change <name> <old_phone> <new_phone>\n"
                "delete <name>\n"
                "phone <name>\n"
                "find <name>\n"
                "add-birthday <name> <ДД.ММ.РРРР>\n"
                "show-birthday <name>\n"
                "birthdays\n"
                "all\n"
                "exit / close")
        else:
            print("Невідома команда. Введіть 'help' щоб переглянути список доступних команд.")


if __name__ == "__main__":
    main()

