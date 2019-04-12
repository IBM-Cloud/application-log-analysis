# Builds a python image
# with Django installed and running the app
FROM python:3-slim
LABEL author="Vidyasagar Machupalli"
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY app app
# Copies the required files
COPY manage.py requirements.txt /code/
RUN pip install -r requirements.txt && \
        python manage.py migrate
EXPOSE 8001
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]