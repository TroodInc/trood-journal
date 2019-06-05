FROM python:3.6

ENV APPDIR=/home/src
ENV PYTHONPATH=$PYTHONPATH:$APPDIR

RUN mkdir -p $APPDIR

WORKDIR $APPDIR

COPY ./journal $APPDIR/journal
COPY ./manage.py $APPDIR/
COPY ./requirements.txt $APPDIR/
COPY ./pytest.ini $APPDIR/
COPY ./entry-point.sh $APPDIR/

RUN pip install -r $APPDIR/requirements.txt

EXPOSE 8000
CMD sh entry-point.sh