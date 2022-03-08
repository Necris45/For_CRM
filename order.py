import requests
import json


class Order:
    def __init__(self, auth_data, order_data):
        # в этой переменной данные аутентификации
        self.auth = auth_data
        # в этой переменной словарь с данными по заказу, для создания товара на bepaid
        # передаем json-строку с данными
        self.data = order_data
        temp_data = json.dumps(self.data)
        # Запрос размещает заказ на bepaid
        response = requests.post(url='https://api.bepaid.by/products',
                                 auth=self.auth,
                                 headers={'Content-Type': 'application/json'},
                                 data=temp_data)
        # ответ сервера преобразуем в словарь
        response_dict = json.loads(response.text)
        # вытаскиваем из него id товара на платформе bepaid
        self.order_id = response_dict['id']
        # создаем ссылку на оплату
        response = requests.get(url=f'https://api.bepaid.by/products/{self.order_id}/pay',
                                auth=auth)
        # в ответе получаем ссылку
        self.paid_url = response.url
        # ссылка в виде строки, извлекаем из нее токен платежа
        self.token = self.paid_url.split('=')[1]

    def check_payment(self):
        # запрашиваем
        response = requests.get(url=f'https://checkout.bepaid.by/ctp/api/checkouts/{self.token}',
                                auth=self.auth,
                                headers={'Content-Type': 'application/json',
                                         'Accept': 'application/json',
                                         'X-API-Version': '2.1'})
        resp_dict = json.loads(response.text)
        if resp_dict['checkout']['gateway_response'] is None:
            answer = "Оплата еще не произведена"
        else:
            answer = resp_dict['checkout']['gateway_response']['payment']['status']
        return answer


def create_order_data(data_dict, auth_data):
    """
    :param auth_data:
    :param data_dict:
    :return:
    словарь data_dict должен быть со следующими ключами: name (название продукта), description (описание продукта),
    currency(валюта), amount (стоимость продукта в минимальных единицах),
    lang (язык, по умолчанию возможно имеет смысл сделать "ru"),
    return_url (ссылка для переадресации после оплаты),
    test(для определения тестовый платеж(True) или нет(False))
    """
    order_data = {"name": data_dict['name'],
                  "description": data_dict['description'],
                  "currency": data_dict['currency'],
                  "amount": data_dict['amount'],
                  "quantity": "1",
                  "infinite": False,
                  "visible_fields": [],
                  "test": data_dict['test'],
                  "immortal": True,
                  "return_url": data_dict['return_url'],
                  "shop_id": auth_data[0],
                  "language": data_dict['lang'],
                  "transaction_type": "payment",
                  "product": {
                      "shop_id": auth_data[0],
                      "name": data_dict['name'],
                      "description": data_dict['description'],
                      "currency": data_dict['currency'],
                      "amount": data_dict['amount'],
                      "quantity": "1",
                      "infinite": False,
                      "language": data_dict['lang'],
                      "immortal": True,
                      "transaction_type": "payment",
                      "visible_fields": [],
                      "test": data_dict['test']}
                  }
    return order_data


# example
# в auth первым элементом будет Shop_id, вторым Secret_key
auth = ('19230', '9152b2670a7451696563556481070cc6a8deaa93da408a41dfd5ba61300eb48b')
order_dict = {'name': 'Заказ №539', 'description': 'Пробный заказ', 'currency': 'RUB', 'amount': '550000', 'lang': 'ru',
              'return_url': 'https://docs.salebot.pro', 'test': True}
data = create_order_data(data_dict=order_dict, auth_data=auth)
new_order = Order(auth_data=auth, order_data=data)
print(new_order.token)
print(new_order.paid_url)
print(new_order.data)
print(new_order.check_payment())
