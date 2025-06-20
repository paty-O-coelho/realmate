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
# ✅ Testes Unitarios
Para executar os testes unitários:

```docker-compose exec django python manage.py test conversations```

# 🧭 Acessos Rápidos
- Swagger UI: http://localhost:8000/swagger/

---


---
![image](https://github.com/user-attachments/assets/eb1095f8-7079-46be-af06-78bf72ec4c3e)


---

# Print do script para testar o webhook

![image](https://github.com/user-attachments/assets/e5324ce8-a701-434e-88c5-d28e301dd37c)

---

![image](https://github.com/user-attachments/assets/2b72519d-4a40-48b7-b283-591da6e128fc)


