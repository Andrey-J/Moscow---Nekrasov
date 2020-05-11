# импортируем библиотеки
from flask import Flask, request
import logging

# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нем содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например,
# произошло внутри модуля logging, то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

Pizza = {
    'Маргарита': ['997614/06d35bab9f968c3d4798'],
    'Гавайская': ['997614/8dc2efea2c121089c3cc'],
    'Четыре сыра': ['1030494/fe0ffc3379b9f9ad51cf']
}

Drinks = {
    'Coca Cola': ['864203/06d35dab9u7r8c3k5096'],
    'Pepsi Cola': ['246218/34gh547gl349cr39a73w'],
    'Soda': ['594301/276rf24plr108pe679u']
}

Sauces = {
    'Cheese Sauce': ['497316/197pf2467jgf21hi189d'],
    'Barbecue Sauce': ['197280/kl489fo167erj093ioa5'],
    'Teriyaki Sauce': ['371520/rt1846sbt728ae453mhq'],
    'Mustard Sauce': ['094721/zu4830etnp81qmg346al']
}

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)

sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}')


    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи
    # библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Хочешь пиццу?!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'хорошо',
        'хочу',
        'ну ладно',
        'пожалуй я возьму пиццу Маргариту.',
        'можно пожалуйста две пиццы Четыре Сыра?',
        'я возьму Гавайскую пиццу',
        'а какие пиццы у вас есть?'
    ]:

        #Пользователь согласился, предоставляем пицерии.
        res['response']['text'] = 'Всю информацию по пиццам(стоимость, разновидность, напитки, соуса и т.д.) вы можете узнать на нашем официальном сайте. "https://market.yandex.ru/search?text=пицца". Если будут вопросы, задавайте их здесь.'
        res['response']['end_session'] = True
        return


    # Если нет, то убеждаем его купить пиццу!
    res['response']['text'] = \
        f"Зачем говорить: '{req['request']['original_utterance']}', когда можно сказать: Хочу пиццу!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на сайт пицерии.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=пицца",
            "hide": True
        })


    return suggests


if __name__ == '__main__':
    app.run()