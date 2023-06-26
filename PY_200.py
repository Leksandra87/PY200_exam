import hashlib
import re
import random
import openpyxl
from itertools import count


class IdCounter:
    """ Генератор значений id """

    def __init__(self) -> None:
        self._get_id = None
        self.counter = count(1, 1)

    @property
    def get_id(self) -> int:
        self.init_id()
        return self._get_id

    def init_id(self) -> None:
        self._get_id = next(self.counter)


ID = IdCounter()  # id для продукта
UID = IdCounter()  # id для пользователя
PRODUCTS = 'plant_catalog.xlsx'


class ProductGenerate:
    """ Генерация информации о товаре """

    @staticmethod
    def generate_product():
        products = openpyxl.load_workbook(PRODUCTS, read_only=True)
        page = products['Лист1']
        first_line = 5
        last_line = 84
        product_gen = ([page[i][1].value, page[i][3].value, random.randint(2, 5)] for i in
                       range(first_line, last_line + 1))
        for product in product_gen:
            yield product


class Password:
    """ Устанавливает хеш-значение пароля, проверяет правильность введенного пароля"""

    def get_hash(self, password: str) -> str:
        self.is_valid_password(password)
        hash_object = hashlib.sha256(password.encode()).hexdigest()
        return hash_object

    @staticmethod
    def is_valid_password(password: str):
        if not isinstance(password, str):
            raise TypeError('Пароль должен быть строкового типа')
        if len(password) < 8:
            raise ValueError('Пароль должен состоять не менее чем из 8 знаков.')
        if not password.isalnum():
            raise TypeError('Пароль должен содержать только буквы и цифры.')
        if not (re.search(r'\D', password) and re.search(r'\d', password)):
            raise TypeError('Пароль должен содержать и буквы, и цифры.')

    @staticmethod
    def check_password(password: str, hash_object: str) -> bool:
        if hash_object == hashlib.sha256(password.encode()).hexdigest():
            return True
        else:
            return False


class Product:
    """
    Информация о продукте
    :param id: задается автоматически, изменить его невозможно
    :param name: название продукта, задается только при инициализации экземпляра класса
    :param price: стоимость продукта, доступна для редактирования
    :param rating: рейтинг продукта, доступен для редактирования
    """

    def __init__(self, name: str, price: float, rating: int) -> None:
        self._id = None
        self.set_id()
        self._name = None
        self.set_name(name)
        self.price = price
        self.rating = rating

    def set_id(self) -> None:
        if self._id is None:
            self._id = ID.get_id

    @property
    def id(self) -> int:
        return self._id

    def set_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError
        if self._name is None:
            self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, price: float) -> None:
        if not isinstance(price, (int, float)):
            raise TypeError
        if price < 0:
            raise ValueError
        self._price = price

    @property
    def rating(self) -> int:
        return self._rating

    @rating.setter
    def rating(self, rating: int) -> None:
        if not isinstance(rating, int):
            raise TypeError
        if rating < 0:
            raise ValueError
        self._rating = rating

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}_{self._id}_{self._name}_{self.price}_{self.rating}"

    def __str__(self) -> str:
        return f"{self._id:_>2}_{self._name:_<30}_{self.price}(руб)_{self.rating}(рейтинг)"


class Cart:
    """ Класс Корзина - список товаров, выбранных покупателем """

    def __init__(self):
        self._cart = None
        self.set_cart()

    def add_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError
        self._cart.append(product)

    def del_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError
        if product in self._cart:
            self._cart.remove(product)

    def set_cart(self):
        if self._cart is None:
            self._cart = []

    @property
    def cart(self) -> list:
        return self._cart

    def __repr__(self):
        return f'{self.cart}'


class User(Password, Cart):
    """
    Информация о покупателе
    :param id: задается автоматически, изменить его невозможно
    :param name: имя покупателя, задается только при инициализации экземпляра класса
    :param password: пароль, хранится в виде хеш-значения
    :param rating: рейтинг продукта, доступен для редактирования
    """

    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        self._id = None
        self.set_id()
        self._username = None
        self.set_username(username)
        self._password = None
        self.init_password(password)
        ...

    def set_id(self) -> None:
        if self._id is None:
            self._id = UID.get_id

    @property
    def id(self) -> int:
        return self._id

    def set_username(self, username: str) -> None:
        if not isinstance(username, str):
            raise TypeError
        if self._username is None:
            self._username = username

    @property
    def username(self) -> str:
        return self._username

    def init_password(self, password):
        if self._password is None:
            self._password = self.get_hash(password)

    @property
    def password(self) -> str:
        return self._password

    def __repr__(self) -> str:
        return f'{self._id}_{self._username}_{self._password}'

    def __str__(self) -> str:
        return f'{self._id}_{self._username}_"*пароль*"_{self._cart}'


class Store(ProductGenerate):
    """ Класс магазин (саженцев плодовых деревьев) """

    def __init__(self) -> None:
        self.user = None
        self.init_user()
        self.product_selection()

    def init_user(self) -> None:
        print('Добро пожаловать в магазин саженцев плодовых деревьев!\n'
              'Введите имя пользователя')
        name = input()
        print('Придумайте пароль (должен содержать не менее 8 символов и состоять из букв и цифр)')
        password = input()
        self.user = User(name, password)

    def product_selection(self) -> None:
        """ Выбор товаров, добавление выбранных товаров в корзину """
        print('Пожалуйста, выбирайте саженец по душе')
        product = self.generate_product()
        counter = 1
        pages = 8
        get = []
        while counter <= pages:
            for _ in range(10):
                val = next(product)
                obj = Product(val[0], val[1], val[2])
                get.append(obj)
                print(obj)
            counter += 1
            print('Ввведите номера понравившихся растений через пробел\n'
                  'Введите + чтобы перейти к продолжению списка\n'
                  'Введите stop, если больше ничего не нужно\n')
            answer = input()
            if answer.strip().lower() == 'stop':
                break
            elif answer.strip().lower() == '+':
                continue
            else:
                nums = [int(i) for i in answer.split()]
                for value in get:
                    if value.id in nums:
                        self.user.add_product(value)
        self.show_products()

    def remove_product(self) -> None:
        """ Удаление продукта из корзины по его номеру """
        print('Введите номера товаров, которые требуется удалить из корзины, в одну строку через пробел')
        nums = [int(i) for i in input().split()]
        to_del = []
        for value in self.user.cart:
            if value.id in nums:
                to_del.append(value)
        for value in to_del:
            self.user.del_product(value)
        self.show_products()

    def payment(self) -> None:
        """ Оплата покупки """
        pay = sum(value.price for value in self.user.cart)
        print(f'Итого к оплате {pay} рублей')
        print('Для подтверждения оплаты введите свой пароль')
        if self.user.check_password(input(), self.user.password):
            print('Спасибо за покупку!')
        else:
            print('К сожалению это неправильный пароль. До свидания.')

    def choose_action(self):
        """ Выбор дальнейшего действия """
        print('Чтобы перейти к оплате введите "pay"\n'
              'Чтобы продолжить выбор товаров введите "+"\n'
              'Для удаления позиций из корзины введите "-"\n')
        answer = input().strip().lower()
        if answer == 'pay':
            self.payment()
        elif answer == '+':
            self.product_selection()
        elif answer == '-':
            self.remove_product()
        else:
            print('Такая команда не предусмотрена')
            self.show_products()

    def show_products(self):
        """ Показать содержимое корзины """
        print('Содержимое вашей корзины:')
        for value in self.user.cart:
            print(value)
        self.choose_action()


if __name__ == '__main__':
    Store()
