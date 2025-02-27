FROM python:3.11
#Используем образ python 3.11 (легковесный)

# Устанавливаем dependecies
RUN apt-get update && apt-get install -y \
    docker.io \
    default-jre \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-java-common \
    uno-libs-private \
    libuno-cppu3 \
    libuno-cppuhelpergcc3-3 \
    libuno-purpenvhelpergcc3-3 \
    libuno-sal3 \
    libuno-salhelpergcc3-3 \
    wkhtmltopdf \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Запускаем приложение от пользователя appuser,
# т.к. от пользователя root запускать приложение совершенно не секурно
ENV APP_USER=appuser
ENV HOME=/home/$APP_USER
ENV APP_HOME=$HOME/app
ENV PATH="$HOME/.local/bin/:$PATH"

#Создаем группу appuser, создаем пользователя appuser без возможности входа в систему
RUN groupadd --gid 2000 $APP_USER \
    && useradd --uid 2000 --gid 2000 -d /home/appuser --create-home -s /sbin/nologin -c "Docker image user" $APP_USER

#Выбираем рабочую директорию нашего проекта
WORKDIR $HOME

#копируем нужные нам файлы и помещаем в раб директорию
COPY ./converter .

#Даем права на все файлы приложения пользователю appuser
RUN chown -R appuser:appuser $HOME

#Изменяем пользователя

RUN pip3 install --no-cache poetry && poetry config virtualenvs.create false \
    && poetry install --no-cache --no-interaction --no-ansi

#USER $APP_USER
#TODO Пока не получается запустить докер из под appuser
USER root

ENTRYPOINT ["uvicorn", "app.api:app", "--log-level", "debug", "--host", "0.0.0.0", "--port", "3000"]
