# Handoff — df_naar_csv

## Huidige status

**Branch:** `feature/pdf-summary`
**Repo (dev):** `/Users/miketenhoonte/PycharmProjects/df_naar_csv/`
**Repo (productie):** `/Users/miketenhoonte/PRODUCTION/DJANGO-l02-app03-dev/df_naar_csv/`

### Wat werkt

- **Django app (productie):** VDP CSV-generatie, summary XLSX/HTML, formulier met alle parameters, order history view
- **PDF summary (dev):** header banner, metrics bar, parameter tabellen, banen overzicht met VDP-groepering, footer met opmerkingen. Tests: 3/3 passing (`uv run pytest test_pdf_summary.py -v`)
- **FastAPI integratie (dev):** volledige API met endpoints — zie `README_API.md`. Niet in productie; bewaard voor toekomstig gebruik
- **Dependency management:** overgestapt van pip/requirements.txt naar uv (`pyproject.toml` + `uv.lock`)

### Architectuur

```
Productie (Django)                Dev repo
─────────────────                ─────────
df_naar_csv/                     app/
├── core/                        ├── core/
│   ├── business_logic.py        │   ├── business_logic.py  ← grotendeels identiek
│   └── processing.py            │   └── ...
├── views.py                     ├── services/
├── forms.py                     │   └── calculation_service.py
├── models.py                    ├── api/  (FastAPI)
├── migrations/                  │   └── routes.py
└── templates/                   calculations.py
                                 summary.py
                                 pdf_summary.py
                                 rollen.py
```

**Let op:** Dev en productie repo's bevatten veel gedupliceerde code (zie bevinding #4 hieronder). Bij wijzigingen altijd beide repo's synchroniseren of eerst de duplicatie oplossen.

---

## Code Review Bevindingen

Volledige review uitgevoerd op 2026-03-02. Issues gesorteerd op prioriteit.

### KRITIEK — direct fixen voor merge/deploy

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 1 | **Missing `summary_pdf` artifact type in migration** | Prod: `migrations/0001_initial.py:36` + `core/processing.py:228` | Migration definieert alleen `vdp_csv`, `summary_xlsx`, `summary_html`. Code maakt `summary_pdf` artifacts aan → crasht bij DB save. **Fix:** nieuwe migration toevoegen met `summary_pdf` choice. |
| 2 | **XSS in HTML writer** | Prod: `core/business_logic.py:442`, Dev: `summary.py:132` | User input (opmerkingen via `**kwargs`) wordt ongeëscaped in HTML geschreven: `print(f" <p><b>{key}</b> : {value}<p/>", ...)`. **Fix:** `html.escape()` toepassen op `key` en `value`. |
| 3 | **Broken HTML in summary** | Dev: `summary.py:127` | `<meta charset='UTF-8>'` — quote staat op verkeerde plek (moet `'UTF-8'`). Ook `<p/>` i.p.v. `</p>` op regel 132. |

### HOOG

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 4 | **Code duplicatie dev ↔ prod** | Dev `app/core/` vs Prod `core/` | 6+ functies 100% identiek. Risico op drift. Overweeg: dev repo als single source of truth, productie als Django-wrapper. |
| 5 | **`__pycache__` in git** | Root + `app/` dirs | `.gitignore` bevat `__pycache__/` maar bestanden zijn al getracked. **Fix:** `git rm -r --cached **/__pycache__/` |
| 6 | **Print statements i.p.v. logging** | Dev: 15× in `business_logic.py`, Prod: 21× | Alle `print()` calls vervangen door `logging.getLogger(__name__)` calls. |
| 7 | **Geen zoekfunctie in order historie** | Prod: `views.py:79` | `VDPJob.objects.all().order_by('-created_at')` — geen filter, search, of paginatie. Bij veel orders wordt dit traag en onbruikbaar. |

### MEDIUM

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 8 | **`materiaal = 145` hardcoded** | Prod: `core/business_logic.py:42` | Hardcoded waarde in wikkelformule. Zou configureerbaar moeten zijn (form field of Django setting). |
| 9 | **`file_to_generator()` retourneert `None` stil** | Dev: `app/core/business_logic.py:36` | Bij onbekend bestandstype (niet .csv/.xlsx/.xls) returned de functie `None` zonder warning. |
| 10 | **Geen error handling op file parsing** | Dev: `app/core/business_logic.py:31-35` | `pd.read_csv()` / `pd.read_excel()` zonder try/except. Corrupte bestanden geven onheldere errors. |
| 11 | **File handle leak in `_create_artifact()`** | Prod: `core/processing.py:247-248` | `open()` zonder context manager bij exceptie in vervolg-code. Gebruik `with open(...) as f:` patroon. |
| 12 | **Duplicate functie `headers_for_totaal_kolommen()`** | Dev: `calculations.py:83` + `calculations.py:346` | Exact dezelfde functie 2× gedefinieerd. Tweede overschrijft de eerste. Eén verwijderen. |
| 13 | **Minimale test coverage** | Dev: `test_pdf_summary.py` | Alleen 3 PDF tests. Geen tests voor: splitter, wikkelberekening, file parsing, edge cases, calculations. |

### LAAG

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 14 | **`source.py` verwijderd, referenties niet opgeruimd** | Git status: `D source.py` | Controleer of imports/referenties naar `source.py` nog bestaan. |
| 15 | **`werkenmetcalc_temp.py` orphaned** | Dev repo root | Tijdelijk bestand, kan verwijderd worden. |
| 16 | **Form defaults hardcoded in `forms.py`** | Prod: `forms.py:21-91` | 13 initial-waarden (mes=4, vdp_aantal=7, kern=76, etc.) hardcoded in form. Overweeg Django settings of database config. |

---

## Future To-Do

### Nieuwe features

- [ ] **Meters per VDP feature** — Nieuw veld `max_meters_per_vdp` toevoegen aan formulier. Automatisch `vdp_aantal` berekenen op basis van totale meters en max per VDP. Vereist: form field, berekening in `business_logic.py`, validatie, test coverage.
- [ ] **Order zoekfunctie** — Search, filter (op datum, klantnaam, bestandsnaam), en paginatie toevoegen aan history view (`views.py:79`). Django `django-filter` + `Paginator` of vergelijkbaar.
- [ ] **Input data opslaan voor herproductie** — Excel/CSV input bestand bewaren bij de order zodat individuele rollen die in productie zijn gefaald opnieuw gegenereerd kunnen worden vanuit de order historie. Vereist: input file opslag in media, "opnieuw maken" actie per rol in history detail view.
- [ ] **PDF summary preview in webapp** — PDF summary inline tonen in een tab op de resultatenpagina (i.p.v. alleen download)
- [ ] **Batch PDF generatie** — Meerdere orders tegelijk verwerken
- [ ] **Email verzending** — Gegenereerde PDF's per mail versturen

### Kritieke bugs (voor deploy)

- [ ] **Migration fix** — `summary_pdf` toevoegen aan artifact type choices (bevinding #1)
- [ ] **XSS fix** — `html.escape()` toepassen in HTML writer (bevinding #2)
- [ ] **HTML fix** — charset meta tag en `</p>` closing tags (bevinding #3)

### Code kwaliteit

- [ ] **print → logger** — Alle print statements vervangen door Python logging (bevinding #6)
- [ ] **Code duplicatie oplossen** — Single source of truth voor gedeelde functies (bevinding #4)
- [ ] **`__pycache__` uit git** — `git rm --cached` en verificatie `.gitignore` (bevinding #5)
- [ ] **Duplicate functie verwijderen** — `headers_for_totaal_kolommen()` in `calculations.py` (bevinding #12)
- [ ] **Error handling** — try/except op file parsing, file handle fix (bevindingen #9, #10, #11)
- [ ] **Test coverage uitbreiden** — Tests voor splitter, wikkel, calculations, edge cases (bevinding #13)
- [ ] **Opruimen** — `werkenmetcalc_temp.py` en `source.py` referenties verwijderen (bevindingen #14, #15)

### PDF verbeteringen

- [ ] Paginering bij veel banen (multi-page PDF support)
- [ ] Logo/bedrijfsbranding toevoegen aan header
- [ ] Landscape optie voor orders met veel banen

### FastAPI (bewaard voor toekomst)

De FastAPI integratie is **compleet en functioneel** (zie `README_API.md` voor docs), maar draait **niet in productie**. De Django app is het primaire systeem.

Wanneer FastAPI nodig is:
- [ ] Authenticatie/autorisatie op API endpoints
- [ ] Rate limiting
- [ ] Deployment configuratie (naast of als vervanging van Django)
- [ ] Health check endpoint

### Technisch / infra

- [ ] CI/CD pipeline opzetten (GitHub Actions)
- [ ] Type hints toevoegen aan `calculations.py` en `summary.py`
- [ ] `materiaal = 145` configureerbaar maken (bevinding #8)
- [ ] Form defaults naar Django settings verplaatsen (bevinding #16)

---

## Dependency management

Overgestapt van pip naar **uv**:
```bash
uv run pytest test_pdf_summary.py -v   # tests draaien
uv sync                                 # dependencies installeren
uv add <package>                        # dependency toevoegen
```

## Productie-kopie

PDF summary is gekopieerd naar productie:
`/Users/miketenhoonte/PRODUCTION/DJANGO-l02-app03-dev/df_naar_csv/pdf_summary.py`

Bij wijzigingen aan `pdf_summary.py` moet de productie-kopie handmatig gesynchroniseerd worden (tot duplicatie-issue #4 is opgelost).
