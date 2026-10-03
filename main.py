# =====================================================================
#  API de Matrículas  -  KIT INICIAL
#  Integração de Aplicações - ESW231 · Prática em dupla ou trio
#
#  Missão: o App B do lab (Acadêmico/Vagas) vira uma API REST.
#  A rota GET /disciplinas já está pronta e documentada: use como MODELO.
#  As outras 4 rotas respondem 501 (Not Implemented) até vocês fazerem.
#  Procurem por "TODO" neste arquivo.
#
#  Rodar:   fastapi dev main.py      (ou: python -m fastapi dev main.py)
#  Docs:    http://127.0.0.1:8000/docs
#
#  Integrantes (nome completo): Kaique Alves de Souza e Fernando Dias de Andrade Silva
#    -
#    -
#    -
# =====================================================================

from fastapi import FastAPI, HTTPException  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel, Field  # pyright: ignore[reportMissingImports]

# ---------------------------------------------------------------------
# 1. Documentação geral da API (aparece no topo do /docs)
# ---------------------------------------------------------------------
app = FastAPI(
    title="API de Matrículas",
    description="API para consultar disciplinas e realizar ou cancelar matrículas. As matrículas consomem vagas disponíveis e credits deve ser maior que zero.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Disciplinas", "description": "Consulta das disciplinas e das vagas disponíveis."},
        {"name": "Matrículas", "description": "Criação, consulta e cancelamento de matrículas."},
    ],
)

# ---------------------------------------------------------------------
# 2. Modelos: o formato dos dados que entram e saem (o "contrato")
# ---------------------------------------------------------------------
class Disciplina(BaseModel):
    # MODELO: cada campo tem tipo, descrição e exemplo. Façam igual nos outros.
    course_id: str = Field(description="Código da disciplina", examples=["BD101"])
    name: str = Field(description="Nome da disciplina", examples=["Banco de Dados I"])
    seats_total: int = Field(description="Total de vagas da disciplina", examples=[5])
    seats_available: int = Field(description="Vagas que ainda estão livres", examples=[4])


class MatriculaEntrada(BaseModel):
    """O que chega no POST /matriculas: o mesmo JSON que o App A deixava na inbox/."""

    # TODO (documentação): coloque description e examples em cada campo.
    # TODO (regra): credits precisa ser um inteiro MAIOR que zero.
    #     Dica: credits: int = Field(gt=0, ...)  -> o FastAPI devolve 422 sozinho.
    student_id: str = Field(description="ID do estudante", examples=["123456"])
    course_id: str = Field(description="Código da disciplina", examples=["BD101"])
    term: str = Field(description="Período da matrícula", examples=["2024.1"])
    credits: int = Field(description="Créditos da disciplina", examples=[6], gt=0)


class Matricula(BaseModel):
    """O que a API devolve sobre uma matrícula."""

    # TODO (documentação): coloque description e examples em cada campo.
    id: int = Field(description="Número da matrícula", examples=[1])
    student_id: str = Field(description="ID do estudante", examples=["123456"])
    course_id: str = Field(description="Código da disciplina", examples=["BD101"])
    term: str = Field(description="Período da matrícula", examples=["2024.1"])
    credits: int = Field(description="Créditos da disciplina", examples=[6], gt=0)
    status: str = Field(description="Status da matrícula", examples=["pendente"])


class Erro(BaseModel):
    """Formato das respostas de erro (é o que o HTTPException devolve)."""

    detail: str = Field(description="Explicação do erro", examples=["Disciplina XYZ999 não encontrada"])


# ---------------------------------------------------------------------
# 3. "Banco de dados" em memória (igual ao dicionário seats do App B)
# ---------------------------------------------------------------------
DISCIPLINAS = {
    "BD101": {"course_id": "BD101", "name": "Banco de Dados I", "seats_total": 5, "seats_available": 5},
    "ENG200": {"course_id": "ENG200", "name": "Engenharia de Software II", "seats_total": 3, "seats_available": 3},
    "MAT150": {"course_id": "MAT150", "name": "Matemática Discreta", "seats_total": 2, "seats_available": 2},
}
MATRICULAS = {}  # número da matrícula -> dicionário com os dados da matrícula
proximo_id = 1   # próximo número de matrícula (dentro da função, use: global proximo_id)


# ---------------------------------------------------------------------
# 4. Rotas
# ---------------------------------------------------------------------

# ROTA MODELO (pronta): repare em tudo o que documenta a rota.
@app.get(
    "/disciplinas",                      # o recurso (um substantivo)
    response_model=list[Disciplina],     # o formato da resposta
    tags=["Disciplinas"],                # o grupo da rota no /docs
    summary="Listar disciplinas",        # o título da rota no /docs
    description="Devolve todas as disciplinas com o total de vagas e quantas ainda estão livres.",
)
def listar_disciplinas():
    return list(DISCIPLINAS.values())


# TODO 1 - GET /disciplinas/{course_id}
#   200: devolve a disciplina.
#   404: se o código não existir:
#        raise HTTPException(status_code=404, detail="Disciplina ... não encontrada")
#   Documente: response_model, tags, summary, description e
#        responses={404: {"model": Erro, "description": "Disciplina não encontrada"}}
@app.get(
    "/disciplinas/{course_id}",
    response_model=Disciplina,
    tags=["Disciplinas"],
    summary="Consultar disciplina",
    description="Devolve os dados de uma disciplina específica, incluindo quantas vagas ainda estão livres.",
    responses={404: {"model": Erro, "description": "Disciplina não encontrada"}},
)
def consultar_disciplina(course_id: str):
    if course_id in DISCIPLINAS:
        return DISCIPLINAS[course_id]
    raise HTTPException(status_code=404, detail=f"Disciplina {course_id} não encontrada")


# TODO 2 - POST /matriculas
#   201: matrícula criada. Use status_code=201 no @app.post(...).
#        Tire 1 vaga da disciplina, guarde em MATRICULAS com status "Matriculado"
#        e devolva a matrícula (com o id).
#   404: a disciplina não existe.
#   409: a disciplina não tem vaga (o antigo "SemVagas"). Não cria nada!
#   422: credits <= 0 ou campo faltando. O FastAPI faz sozinho se o modelo estiver certo.
#   Documente também os erros 404 e 409 em responses={...}.
@app.post(
    "/matriculas",
    response_model=Matricula,
    status_code=201,
    tags=["Matrículas"],
    summary="Criar matrícula",
    description="Cria uma matrícula e reduz em uma unidade as vagas disponíveis da disciplina.",
    responses={
        404: {"model": Erro, "description": "Disciplina não encontrada"},
        409: {"model": Erro, "description": "Disciplina sem vagas"},
    },
)
def criar_matricula(pedido: MatriculaEntrada):
    global proximo_id
    if pedido.course_id not in DISCIPLINAS:
        raise HTTPException(status_code=404, detail=f"Disciplina {pedido.course_id} não encontrada")
    disciplina = DISCIPLINAS[pedido.course_id]
    if disciplina["seats_available"] <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"SemVagas: a disciplina {pedido.course_id} não tem mais vagas",
        )
    disciplina["seats_available"] -= 1
    matricula = {
        "id": proximo_id,
        "student_id": pedido.student_id,
        "course_id": pedido.course_id,
        "term": pedido.term,
        "credits": pedido.credits,
        "status": "Matriculado"
    }
    MATRICULAS[proximo_id] = matricula
    proximo_id += 1
    return matricula


# TODO 3 - GET /matriculas
#   200: devolve a lista de todas as matrículas (o antigo finance_log.csv).
@app.get(
    "/matriculas",
    response_model=list[Matricula],
    tags=["Matrículas"],
    summary="Listar matrículas",
    description="Devolve todas as matrículas existentes.",
)
def listar_matriculas():
    return list(MATRICULAS.values())


# TODO 4 - DELETE /matriculas/{matricula_id}
#   200: cancela, devolve a vaga para a disciplina e responde algo como
#        {"message": "Matrícula 1 cancelada", "course_id": "BD101", "seats_available": 5}
#   404: a matrícula não existe (inclusive se já foi cancelada).
@app.delete(
    "/matriculas/{matricula_id}",
    tags=["Matrículas"],
    summary="Cancelar matrícula",
    description="Cancela uma matrícula e devolve a vaga à disciplina.",
    responses={404: {"model": Erro, "description": "Matrícula não encontrada"}},
)
def cancelar_matricula(matricula_id: int):
    if matricula_id not in MATRICULAS:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    matricula = MATRICULAS[matricula_id]
    course_id = matricula["course_id"]
    DISCIPLINAS[course_id]["seats_available"] += 1
    del MATRICULAS[matricula_id]
    return {
        "message": f"Matrícula {matricula_id} cancelada",
        "course_id": course_id,
        "seats_available": DISCIPLINAS[course_id]["seats_available"]
    }
