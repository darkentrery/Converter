FROM pdf2htmlex/pdf2htmlex:0.18.8.rc2-master-20200820-ubuntu-20.04-x86_64

ENV APP_USER=appuser
ENV HOME=/home/$APP_USER
ENV TEMP_PATH=/tmp
ENV APP_HOME=$HOME/app
ENV PATH="$HOME/.local/bin/:$PATH"

#Создаем группу appuser, создаем пользователя appuser без возможности входа в систему
RUN groupadd --gid 2000 $APP_USER \
    && useradd --uid 2000 --gid 2000 -d /home/appuser --create-home -s /sbin/nologin -c "Docker image user" $APP_USER

#Выбираем рабочую директорию нашего проекта
WORKDIR $HOME

#Даем права на все файлы приложения пользователю appuser
RUN chown -R appuser:appuser $HOME
RUN chown -R appuser:appuser $TEMP_PATH

COPY ./entrypoint.sh $APP_HOME/

RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
#RUN chmod +x $APP_HOME/entrypoint.sh
WORKDIR $TEMP_PATH
ENTRYPOINT ["/home/appuser/app/entrypoint.sh"]