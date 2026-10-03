# API de Matrículas

**Integrantes:** Kaique Alves de Souza, Fernando Dias de Andrade Silva

## O que a API faz

  "API do sistema acadêmico para consultar disciplinas e registrar ou cancelar matrículas. "
  "A cada matrícula, a disciplina deve ter vagas disponíveis. O campo credits deve ser maior que zero "
  "e a disponibilidade de vagas é atualizada em tempo real."

## Como rodar

1. `python -m pip install -r requirements.txt`
2. `fastapi dev main.py`
3. Abrir http://127.0.0.1:8000/docs

## Rotas

| Método | Rota | O que faz | Respostas possíveis |
| --- | --- | --- | --- |
| GET | /disciplinas | Lista as disciplinas e as vagas livres | 200 |
| GET | /disciplinas/{course_id} | | 200, 404 |
| POST | /matriculas | | 201, 404, 409, 422 |
| GET | /matriculas | | 200 |
| DELETE | /matriculas/{matricula_id} | | 200, 404 |

## Exemplo de uso

Pedido (`POST /matriculas`):

```json
{"student_id": "A100", "course_id": "BD101", "term": "2026.1", "credits": 4}
```

Resposta (201):
{
  "id": 2,
  "student_id": "A100",
  "course_id": "BD101",
  "term": "2026.1",
  "credits": 4,
  "status": "ativa"
}

## Bônus que fizemos

- [ ] Duplicados: o mesmo `event_id` não gasta vaga duas vezes
- [ ] Vagas salvas em arquivo (não somem quando a API reinicia)
- [ ] `cliente.py` que manda matrículas e mede o tempo de resposta
