from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QComboBox, QMessageBox, QStackedWidget
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QScreen
import sys
import requests
import json

OPENAI_API_KEY = 'YOUR_API_KEY'

# Класс WorkerThread1 наследуется от QThread для создания потока, который будет выполнять запросы к OpenAI
class WorkerThread1(QThread):
    # Создаем сигнал response_signal, который может передавать строковые данные (str)    
    response_signal = Signal(str)

    def __init__(self, user_input):
        # Вызываем конструктор базового класса для инициализации потока
        super().__init__()
        # Сохраняем пользовательский ввод для дальнейшего использования в потоке
        self.user_input = user_input

    def run(self):
        # Создаем словарь с данными для API запроса
        APIBody = {
            "model": "gpt-3.5-turbo", # Указываем модель для генерации текста
            "messages": [{"role": "user", "content": self.user_input}] # Содержимое запроса пользователя
        }
        # Выводим в консоль информацию о запросе
        print(f"Отправляем запрос в OpenAI: {APIBody}")  # Log the request payload
        try:
            # Выполняем POST-запрос к OpenAI с заголовками и данными APIBody
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json", # Указываем тип содержимого запроса
                    "Authorization": f"Bearer {OPENAI_API_KEY}" # Авторизационный токен для API
                },
                data=json.dumps(APIBody) # Преобразуем словарь APIBody в JSON строку
            )
            # Если статус ответа 200 (успех), то обрабатываем полученные данные
            if response.status_code == 200:
                data = response.json() # Преобразуем ответ из JSON в словарь Python
                message_content = data['choices'][0]['message']['content'] # Извлекаем контент сообщения
                # Выводим в консоль полученный ответ
                print(f"Получен ответ от OpenAI: {message_content}")
                # Испускаем сигнал с полученным ответом
                self.response_signal.emit(message_content)
            else:
                # Если статус ответа не 200, сообщаем об ошибке
                error_message = f"Ошибка обработки вашего запроса. Код статуса: {response.status_code}"
                print(error_message)
                self.response_signal.emit(error_message)
        except Exception as e:
            # В случае исключения, выводим сообщение об ошибке
            error_message = f"Произошла ошибка: {e}"
            print(error_message)
            self.response_signal.emit(error_message)

# Класс WorkerThread2 наследуется от QThread для создания потока, который будет выполнять запросы к OpenAI
class WorkerThread2(QThread):
    # Создание сигнала response_signal, который может передавать две строки (str, str)
    response_signal = Signal(str, str)

    # Конструктор класса с параметрами для инициализации атрибутов
    def __init__(self, brand, ad_system, content_type, length, description):
        super().__init__() # Вызов конструктора базового класса QThread
        # Инициализация атрибутов класса значениями, полученными при создании экземпляра
        self.brand = brand  # Название бренда
        self.ad_system = ad_system  # Система рекламы
        self.content_type = content_type  # Тип контента
        self.length = length  # Длина контента
        self.description = description  # Описание контента

    # Метод run выполняется при запуске потока
    def run(self):
        # Формирование строки запроса с использованием форматирования строки f-string
        prompt = f"Напиши {self.description} для бренда {self.brand} длиной в {self.length} символов на Русском языке."
        # Вывод строки запроса в консоль
        print(f"WorkerThread2 - Отправка запроса с текстом: {prompt}")

        # Формирование словаря для тела запроса к API
        APIBody = {
            "model": "gpt-3.5-turbo", # Указание модели OpenAI
            "messages": [{"role": "user", "content": prompt}] # Содержимое запроса
        }
        # Обработка исключений при выполнении HTTP запроса
        try:
            # Отправка POST-запроса к OpenAI
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", # URL API
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}, # Заголовки авторизации
                json=APIBody # Тело запроса в формате JSON
            )
            # Проверка статуса ответа от API
            if response.status_code == 200:
                data = response.json() # Десериализация JSON ответа в словарь
                message_content = data['choices'][0]['message']['content'] # Извлечение текста ответа
                # Вывод полученного ответа в консоль
                print(f"WorkerThread2 - Received response for '{self.content_type}': {message_content}")
                # Испускание сигнала с полученными данными
                self.response_signal.emit(self.content_type, message_content)
            else:
                # Формирование сообщения об ошибке при неудачном статусе ответа
                error_message = f"Ошибка: Не удалось обработать ваш запрос. Код статуса: {response.status_code}, Ответ: {response.text}"
                print(f"WorkerThread2 - {error_message}")
                # Испускание сигнала с сообщением об ошибке
                self.response_signal.emit(self.content_type, "Ошибка: Ошибка обработки запроса.")
        except Exception as e:
            # В случае исключения, выводим сообщение об ошибке
            error_message = f"Произошла ошибка: {e}"
            print(f"WorkerThread2 - {error_message}")
            self.response_signal.emit(self.content_type, f"Произошла ошибка: {e}")

# Класс WorkerThread3 наследуется от QThread для создания потока, который будет выполнять запросы к OpenAI
class WorkerThread3(QThread):
    # Создаем сигнал `response_signal`, который будет использоваться для отправки данных обратно в главный поток
    response_signal = Signal(str)

    def __init__(self, brand, length, topic):
        # Конструктор класса вызывает конструктор родительского класса `QThread`
        super().__init__()
        # Инициализация атрибутов класса
        self.brand = brand
        self.length = length
        self.topic = topic

    def run(self):
        # Формирование строки запроса для API
        prompt = f"Напиши рекламную статью для бренда {self.brand} длиной в {self.length} символов на тему {self.topic} на Русском языке."
        # Вывод информации о запросе в консоль
        print(f"WorkerThread3 - Отправка запроса с текстом: {prompt}")

        # Создание тела запроса в формате JSON
        APIBody = {
            "model": "gpt-3.5-turbo", # Указание используемой модели
            "messages": [{"role": "user", "content": prompt}] # Содержимое запроса
        }
        try:
             # Отправка запроса на API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", # URL API
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}, # Заголовки запроса, включая ключ API
                json=APIBody # Данные запроса в формате JSON
            )
            if response.status_code == 200: # Проверка на успешный ответ от сервера
                # Декодирование JSON-ответа
                data = response.json()
                # Извлечение содержимого сообщения из ответа
                message_content = data['choices'][0]['message']['content']
                # Вывод полученного ответа в консоль
                print(f"WorkerThread3 - Получен ответ: {message_content}")
                # Отправка содержимого сообщения через сигнал `response_signal`
                self.response_signal.emit(message_content)
            else:
                # Создание сообщения об ошибке, если статус ответа не равен 200
                error_message = f"Ошибка: Ошибка обработки запроса. Код статуса: {response.status_code}, Ответ: {response.text}"
                # Вывод сообщения об ошибке в консоль
                print(f"WorkerThread3 - {error_message}")
                # Отправка сообщения об ошибке через сигнал `response_signal`
                self.response_signal.emit("Error: Failed to process your request.")
        except Exception as e:
            # В случае исключения, выводим сообщение об ошибке
            error_message = f"Exception: {e}"
            print(f"WorkerThread3 - {error_message}")
            self.response_signal.emit(f"Exception: {e}")

# Реализация окна 1
class Window1(QWidget):
    # Конструктор класса
    def __init__(self):
        super().__init__() # Вызов конструктора базового класса
        self.layout = QVBoxLayout(self) # Создание вертикального макета

        # Создание виджета для отображения текстовых сообщений
        self.messages = QTextEdit()
        self.messages.setReadOnly(True) # Сделать виджет только для чтения
        self.layout.addWidget(self.messages) # Добавить виджет в макет

        # Создание поля для ввода текста
        self.input_field = QLineEdit()
        # Создание кнопки отправки запроса
        self.submit_button = QPushButton("Отправить запрос")
        # Подключение события нажатия на кнопку к методу on_submit
        self.submit_button.clicked.connect(self.on_submit)
        
        # Создание горизонтального макета для поля ввода и кнопки
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field) # Добавить поле ввода в макет
        input_layout.addWidget(self.submit_button) # Добавить кнопку в макет
        self.layout.addLayout(input_layout) # Добавить горизонтальный макет в вертикальный

    # Метод, вызываемый при нажатии на кнопку отправки
    def on_submit(self):
        user_input = self.input_field.text().strip() # Получить и обрезать введенный текст
        # Если текст не пустой
        if user_input:
            self.display_message(f"Запрос: {user_input}") # Отобразить введенный запрос
            self.input_field.clear() # Очистить поле ввода

            # Создание и запуск потока для обработки запроса
            self.worker = WorkerThread1(user_input)
            # Подключение сигнала завершения работы потока к методу handle_response
            self.worker.response_signal.connect(self.handle_response)
            # Запуск потока
            self.worker.start()

    # Метод для добавления сообщения в виджет отображения сообщений
    def display_message(self, message):
        self.messages.append(message + "\n") # Добавить сообщение и перенос строки
    
    # Метод обработки полученного ответа от потока
    def handle_response(self, message):
        self.display_message(f"Результат поиска: {message}") # Отобразить полученный ответ

# Реализация окна 2
class Window2(QWidget):
    # Конструктор класса
    def __init__(self):
        super(Window2, self).__init__()  # Вызов конструктора базового класса
        self.setup_ui()  # Инициализация пользовательского интерфейса
        self.threads = []  # Список для хранения рабочих потоков

    # Метод инициализации пользовательского интерфейса
    def setup_ui(self):
        self.layout = QVBoxLayout(self)  # Создание вертикального макета

        # Ввод названия бренда
        self.layout.addWidget(QLabel("Введите название бренда:"))  # Добавление метки
        self.brand_entry = QLineEdit()  # Создание поля для ввода
        self.layout.addWidget(self.brand_entry)  # Добавление поля для ввода в макет

        # Выбор системы рекламы
        self.layout.addWidget(QLabel("Выберите систему рекламы:")) # Добавление метки
        self.system_combo = QComboBox() # Создание выпадающего списка
        self.system_combo.addItems(["Яндекс Директ", "VK Реклама"]) # Добавление вариантов выбора в выпадающий список
        self.layout.addWidget(self.system_combo) # Добавление списка в макет
        self.system_combo.currentIndexChanged.connect(self.update_ad_system_ui)  # Подключение события изменения выбора к методу update_ad_system_ui

        # Кнопка генерации текстов
        self.generate_button = QPushButton("Генерировать тексты")
        # Подключение события нажатия на кнопку к методу generate_texts
        self.generate_button.clicked.connect(self.generate_texts)
        self.layout.addWidget(self.generate_button) # Добавление кнопки в макет

         # Области отображения текста
        self.title_label = QLabel("Заголовок:")
        self.title_text = QLineEdit()
        self.title_text.setReadOnly(True) # Сделать поле только для чтения
        self.description_label = QLabel("Описание:")
        self.description_text = QLineEdit()
        self.description_text.setReadOnly(True) # Также только для чтения

        # Виджеты для быстрой ссылки (отображаются по условию)
        self.quick_link_label = QLabel("Быстрая ссылка:")
        self.quick_link_text = QLineEdit()
        self.quick_link_text.setReadOnly(True) # Только для чтения

        # Добавление виджетов в макет
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_text)
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_text)

        # Условное добавление виджетов для быстрой ссылки
        self.update_ad_system_ui()
    
    # Метод обновления интерфейса в зависимости от выбранной рекламной системы
    def update_ad_system_ui(self):
        # Очистка текстовых полей при смене системы рекламы
        self.title_text.clear()
        self.description_text.clear()
        self.quick_link_text.clear()
        
        # Показать или скрыть виджеты для быстрой ссылки
        if self.system_combo.currentText() == "Яндекс Директ":
            # Show Quick Link widgets for "Яндекс Директ"
            if not self.quick_link_label.isVisible():
                self.layout.addWidget(self.quick_link_label)
                self.layout.addWidget(self.quick_link_text)
            self.quick_link_label.setVisible(True)
            self.quick_link_text.setVisible(True)
        else:
            # Hide Quick Link widgets for "VK Реклама"
            self.quick_link_label.setVisible(False)
            self.quick_link_text.setVisible(False)

    # Метод генерации текстов в зависимости от выбранной системы рекламы
    def generate_texts(self):
        brand = self.brand_entry.text().strip()  # Получение и обрезка введенного бренда
        ad_system = self.system_combo.currentText().strip()  # Получение выбранной системы рекламы

        # Определение длин и описаний для рекламных текстов
        ad_lengths = {
            "Яндекс Директ": {"Заголовок": 56, "Описание": 81, "Быстрая ссылка": 30},
            "VK Реклама": {"Заголовок": 25, "Описание": 90}
        }

        ad_descriptions = {
            "Яндекс Директ": {
                "Заголовок": "заголовок для рекламного объявления",
                "Описание": "описание для рекламного объявления",
                "Быстрая ссылка": "быструю ссылку (захватывающее внимание пары слов или словосочетания) для рекламного объявления"
            },
            "VK Реклама": {
                "Заголовок": "заголовок для рекламного объявления",
                "Описание": "описание для рекламного объявления"
            }
        }

        # Генерация текстов в зависимости от выбранной системы рекламы
        if ad_system == "Яндекс Директ":
            for key in ["Заголовок", "Описание", "Быстрая ссылка"]:
                self.generate_ad_text(brand, ad_system, key, ad_lengths[ad_system][key], ad_descriptions[ad_system][key])
        elif ad_system == "VK Реклама":
            for key in ["Заголовок", "Описание"]:
                self.generate_ad_text(brand, ad_system, key, ad_lengths[ad_system][key], ad_descriptions[ad_system][key])

     # Метод создания и запуска рабочего потока для генерации текста
    def generate_ad_text(self, brand, ad_system, content_type, length, description):
        worker = WorkerThread2(brand, ad_system, content_type, length, description)
        worker.response_signal.connect(self.display_generated_text)
        # Подключение события завершения работы потока к методу thread_finished
        worker.finished.connect(lambda worker=worker: self.thread_finished(worker))
        worker.start() # Запуск потока
        self.threads.append(worker) # Добавление потока в список

    # Метод отображения сгенерированного текста
    def display_generated_text(self, content_type, text):
        if content_type == "Заголовок":
            self.title_text.setText(text)
        elif content_type == "Описание":
            self.description_text.setText(text)
        elif content_type == "Быстрая ссылка" and self.system_combo.currentText() == "Яндекс Директ":
            self.quick_link_text.setText(text)

    # Метод, вызываемый при завершении работы потока
    def thread_finished(self, worker):
        # Удаление потока из списка
        self.threads.remove(worker)

# Реализация окна 3
class Window3(QWidget):
    # Конструктор класса
    def __init__(self):
        super(Window3, self).__init__()  # Вызов конструктора базового класса для инициализации
        self.setup_ui()  # Вызов метода для настройки пользовательского интерфейса
        self.threads = []  # Список для хранения рабочих потоков
    
    # Метод для настройки пользовательского интерфейса
    def setup_ui(self):
        layout = QVBoxLayout()  # Создание вертикального макета

        # Ввод названия бренда
        layout.addWidget(QLabel("Введите название бренда:"))  # Добавление метки
        self.brand_entry = QLineEdit()  # Создание поля для ввода текста
        layout.addWidget(self.brand_entry)  # Добавление поля ввода в макет

        # Ввод длины статьи
        layout.addWidget(QLabel("Введите длину статьи:"))  # Добавление метки
        self.length_entry = QLineEdit()  # Создание поля для ввода текста
        layout.addWidget(self.length_entry)  # Добавление поля ввода в макет

        # Ввод темы статьи
        layout.addWidget(QLabel("Введите тему статьи:"))  # Добавление метки
        self.topic_entry = QLineEdit()  # Создание поля для ввода текста
        layout.addWidget(self.topic_entry)  # Добавление поля ввода в макет

        # Кнопка для генерации статьи
        self.generate_button = QPushButton("Сгенерировать статью")  # Создание кнопки
        self.generate_button.clicked.connect(self.generate_article)  # Привязка события клика к методу generate_article
        layout.addWidget(self.generate_button)  # Добавление кнопки в макет

        # Кнопка для очистки полей
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_fields)  # Привязка метода очистки к кнопке
        layout.addWidget(self.clear_button)

        # Область для отображения сгенерированной статьи
        layout.addWidget(QLabel("Ваша статья:"))  # Добавление метки
        self.article_text = QTextEdit()  # Создание текстового поля
        self.article_text.setReadOnly(True)  # Установка режима только для чтения
        layout.addWidget(self.article_text)  # Добавление текстового поля в макет

        self.setLayout(layout)  # Применение макета к виджету
    
    def clear_fields(self):
        # Очистка полей ввода и текстового поля
        self.brand_entry.clear()
        self.length_entry.clear()
        self.topic_entry.clear()
        self.article_text.clear()

    def generate_article(self):
        brand = self.brand_entry.text().strip()  # Получение текста из поля ввода и удаление пробелов
        length = self.length_entry.text().strip()  # Аналогично для длины статьи
        topic = self.topic_entry.text().strip()  # Аналогично для темы статьи

        # Проверка на заполненность всех полей
        if not brand or not length.isdigit() or not topic:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля корректно.")
            return # Возврат из функции, если проверка не пройдена

        worker = WorkerThread3(brand, length, topic)  # Создание рабочего потока
        worker.response_signal.connect(self.display_generated_article)  # Подключение сигнала к слоту
        worker.finished.connect(lambda worker=worker: self.thread_finished(worker))  # Подключение события завершения к методу
        worker.start()  # Запуск потока
        self.threads.append(worker)  # Добавление потока в список

    # Метод для отображения сгенерированной статьи
    def display_generated_article(self, article):
        self.article_text.setText(article) # Установка текста статьи в текстовое поле

    # Метод, вызываемый при завершении работы потока
    def thread_finished(self, worker):
        self.threads.remove(worker) # Удаление потока из списка

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Вызов конструктора базового класса QMainWindow
        self.setWindowTitle("Chat Bot")  # Установка названия главного окна
        self.central_widget = QWidget()  # Создание центрального виджета
        self.setCentralWidget(self.central_widget)  # Установка центрального виджета для главного окна

        # Установка стилей для приложения для увеличения размера шрифта и высоты элементов управления
        self.setStyleSheet("""
            QWidget {
                font-size: 16pt;  /* Increase the base font size */
            }
            QLineEdit, QTextEdit, QPushButton, QLabel, QComboBox {
                min-height: 30px;  /* Set a minimum height for input fields and buttons */
            }
        """)

        self.stacked_widget = QStackedWidget()  # Создание виджета со стеком для переключения между окнами
        self.window1 = Window1()  # Создание первого окна
        self.window2 = Window2()  # Создание второго окна
        self.window3 = Window3()  # Создание третьего окна
        # Добавление созданных окон в стек
        self.stacked_widget.addWidget(self.window1)
        self.stacked_widget.addWidget(self.window2)
        self.stacked_widget.addWidget(self.window3)

        # Инициализация главного макета для центрального виджета
        self.main_layout = QVBoxLayout(self.central_widget)  # Создание вертикального макета
        self.main_layout.addWidget(self.stacked_widget)  # Добавление виджета со стеком в макет

        # Инициализация панели навигации
        self.init_nav()

        # Установка размера окна относительно размера экрана
        self.init_size()
    
    def init_size(self):
       # Получение размера экрана
        screen = QApplication.primaryScreen().size()
        width = screen.width()  # Ширина экрана
        height = screen.height()  # Высота экрана

        # Установка размера окна как процент от размера экрана
        percentage_width = 0.8  # 80% от ширины экрана
        percentage_height = 0.8  # 80% от высоты экрана
        self.resize(int(width * percentage_width), int(height * percentage_height))  # Изменение размера окна

    def init_nav(self):
        nav_bar = QHBoxLayout() # Создание горизонтального макета для панели навигации
        btn1 = QPushButton("Поисковик-помощник") # Кнопка для переключения на первое окно
        btn2 = QPushButton("Генерация рекламных объявлений") # Кнопка для переключения на второе окно
        btn3 = QPushButton("Генерация статей") # Кнопка для переключения на третье окно
        
        # Соединение сигналов нажатия кнопок с соответствующими слотами для переключения окон
        btn1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Добавление кнопок в панель навигации
        nav_bar.addWidget(btn1)
        nav_bar.addWidget(btn2)
        nav_bar.addWidget(btn3)

        # Добавление панели навигации в главный макет
        self.main_layout.addLayout(nav_bar)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())