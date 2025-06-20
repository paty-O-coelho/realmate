---
# 🚀 Instruções para Executar o Projeto

Este documento orienta como configurar e executar localmente o projeto utilizando Docker 
e como realizar testes com um script automatizado.


# 🧩 Estrutura Esperada

O projeto inclui os seguintes serviços, orquestrados via Docker:

- Django (API)

- Celery (worker)

- PostgreSQL (banco de dados)

- Redis (broker Celery)


# 🐳 Subindo os Serviços
Com o .env configurado corretamente, rode:
- Rodar e buildar o docker

```docker-compose up --build```

- Remover o docker caso necessario

```docker-compose down --volumes --remove-orphans```
# ✅ Testes Automatizados
Para executar os testes unitários:

```docker-compose exec django python manage.py test conversations```

# 🧭 Acessos Rápidos
- Swagger UI: http://localhost:8000/swagger/

---
