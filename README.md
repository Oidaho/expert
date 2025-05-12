# expert

Качаешь Poetry:

```
pip install poetry
```

Потом делаешь конфигурацию Poetry:

```
poetry config virtualenvs.in-project true
```

Потом открываешь этот проект в VSCode (склонировав его, есесно)

И там уже пишешь:

```
poetry env use 3.10
```

```
poetry install
```

Ждешь пока установятся зависисмости

Потом выбираешь для локальной среды интерпретатор из .venv

Потом запускаешь проект через консоль VSCode:

```
python main.py
```
