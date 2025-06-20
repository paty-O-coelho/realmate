# Use imagem oficial do Python
FROM python:3.11-slim

# Variável ambiente para Python rodar sem buffer (bom para logs)
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho
WORKDIR /app

# Copia requirements e instala
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Coleta os arquivos estáticos
# RUN python manage.py collectstatic --noinput

# Copia o projeto inteiro
COPY . /app/

# Expõe porta 8000
EXPOSE 8000

# Comando padrão, pode ser sobrescrito no docker-compose
CMD ["gunicorn", "realmate_challenge.wsgi:application", "--bind", "0.0.0.0:8000"]

