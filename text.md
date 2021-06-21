# Инструкция
## Инструкция для студента

При первом запуске бота введите 
```sh
/start
```
Затем укажите ФИО
После регистрации Вы сможете проходить тесты
#### Пройти тест
Чтобы пройти тест Вам надо:
- Нажать кнопку "Пройти лабораторную работу"
- Ввести ID лабораторной работы, который вам дал преподаватель
- Если вопрос с вариантами ответов, то Вы увидите список возможных ответов
- Если вопрос без вариантов, то Вы должны ввести текст
- В конце теста, Вы получите список своих ответов

> Note: Для того чтобы пройти лабораторную работу, у вас  должна быть законченная предыдущая работа

## Инструкция для преподавателя

При первом запуске бота введите 
```sh
/start
```
Затем укажите ФИО
После регистрации Вы сможете проходить тесты, но не создавать их
#### Повышение пользователя в правах
Чтобы создать тест или дать возможность другому человеку его создавать, введите эту команду:
```sh
/grant PASSWORD ID
PASSWORD - пароль (по умолчанию: 1530)
ID - ID пользователя выданный ему после регистрации

Пример
/grant 1530 460688017
```

#### Понижение пользователя в правах
Чтобы запретить пользователю создавать тесты, введите эту команду:
```sh
/revoke PASSWORD ID
PASSWORD - пароль (по умолчанию: 1530)
ID - ID пользователя, выданный ему после регистрации

Пример
/revoke 1530 460688017
```
#### Создание теста
Чтобы создать тест, нажмите кнопку "Создать лабораторную работу"
Затем пришлите ссылку на Google Таблицу 
[Пример](https://docs.google.com/spreadsheets/d/1QmmRlZcEP_9ul_0iEXkivNYeGDjeZDXbPTC5G_Kjcf8/edit?usp=sharing) - https://docs.google.com/spreadsheets/d/1QmmRlZcEP_9ul_0iEXkivNYeGDjeZDXbPTC5G_Kjcf8/edit?usp=sharing
> Note: Таблица должна быть открыта для анонимных пользователей

После создания лабораторной работы, Вы получите её ID и ссылку на Google таблицу, в которую будут записываться ответы