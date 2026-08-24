# Monitor de Concursos — Backend

API pessoal em **Python + FastAPI** para monitorar concursos no PCI Concursos,
conforme a especificação do projeto. Implementa exatamente o escopo descrito:
sem autenticação, sem múltiplos usuários, SQLite como único banco.

## Estrutura

```
backend/
├── app/
│   ├── main.py                 # cria o FastAPI, inclui as rotas
│   ├── config.py                # settings (.env)
│   ├── schemas.py                # Pydantic (API + scraper)
│   │
│   ├── api/
│   │   ├── filters.py            # GET /filters, PUT /filters
│   │   └── scraper.py            # GET|POST /scraper/run
│   │
│   ├── scraper/
│   │   └── pci.py                # TODO parsing de HTML fica aqui (RNF03)
│   │
│   ├── services/
│   │   ├── filter_service.py     # CRUD do registro único de filtros + regra de match
│   │   ├── notification_service.py # dedupe (URL já notificada?)
│   │   ├── cleanup_service.py    # remove registros com +3 meses
│   │   ├── email_service.py      # monta e envia o e-mail consolidado
│   │   └── scraper_run_service.py # orquestra o fluxo completo (seção 21)
│   │
│   └── database/
│       ├── database.py           # engine/session SQLAlchemy
│       └── models.py             # concursos_notificados, filtros
│
├── requirements.txt
├── vercel.json                   # build + cron diário
└── .env.example
```

## Rodando localmente

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env com sua RESEND_API_KEY e EMAIL_FROM

uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação automática (Swagger) em
`http://localhost:8000/docs`.

## Endpoints

| Método    | Rota           | Descrição                                    |
| --------- | -------------- | --------------------------------------------- |
| GET       | `/filters`     | Retorna os filtros salvos                     |
| PUT       | `/filters`     | Atualiza os filtros (todos os campos opcionais) |
| GET/POST  | `/scraper/run` | Executa o monitoramento completo (usado pelo cron) |                        |

## Variáveis de ambiente

Veja `.env.example`. Principais:

- `DATABASE_URL` — string de conexão SQLAlchemy. Em produção na Vercel,
  **não** use um arquivo SQLite local (o filesystem de funções serverless
  não é persistente); use algo como [Turso](https://turso.tech) ou hospede
  o backend em um servidor com disco persistente.
- `RESEND_API_KEY` / `EMAIL_FROM` — envio de e-mail via [Resend](https://resend.com).
  Para trocar de provedor, edite apenas `app/services/email_service.py`.
- `CRON_SECRET` — opcional. Se definido, `/scraper/run` só executa com o
  header `Authorization: Bearer <CRON_SECRET>`. A Vercel envia esse header
  automaticamente quando a mesma variável `CRON_SECRET` está configurada no
  projeto.

## Sobre o scraper (`app/scraper/pci.py`)

Os seletores CSS usados para localizar título, órgão, cargo, salário e
local dentro de cada `[data-url]` são uma primeira aproximação baseada na
especificação. Antes de colocar em produção, **inspecione o HTML real do
PCI Concursos** (DevTools → Elements) e ajuste as constantes
`SELECTOR_*`/`SELECTORS_*` no topo do arquivo. Esse isolamento é
intencional (RNF03): o site pode mudar o layout a qualquer momento, e o
ajuste deve ficar restrito a esse único arquivo — filtros, banco e e-mail
não precisam ser tocados.

## Deploy na Vercel

1. Configure as variáveis de ambiente do projeto na Vercel (mesmas do `.env`).
2. `vercel.json` já define o build da função Python e o cron diário
   (`0 9 * * *` — ajuste o horário como preferir).
3. Configure um banco SQLite persistente/hospedado (Turso é a opção mais
   simples) e aponte `DATABASE_URL` para ele — ver observação na seção 24
   da especificação.
