# Handoff — df_naar_csv

## Huidige status

**Branch:** `master`
**Repo (dev):** `<dev-repo>/`
**Repo (productie):** `<productie-repo>/`

### Wat werkt

- **Django app (productie):** VDP CSV-generatie, summary XLSX/HTML/PDF, formulier met alle parameters incl. max meters per VDP, kern dropdown, verbeterde UX
- **Order historie:** zoeken op ordernummer, filteren op status/datum, paginatie (20/pagina), VDPs/Mes kolommen (PR #2 productie merged)
- **Rollen selectie:** bekijk rollen uit bestaande order, selecteer subset, herverwerk als nieuwe job met auto-herberekend vdp_aantal (PR #2 productie merged)
- **Herproductie:** order opnieuw verwerken met zelfde bestand + params, of rollen-selectie (PR #2 productie merged)
- **Order beheer:** verwijderen uit historie, origineel Excel downloaden (PR #2 productie merged)
- **Inline PDF viewing:** PDF/HTML summaries openen in nieuw tabblad (PR #2 productie merged)
- **Max meters per VDP:** automatische berekening van `vdp_aantal` op basis van max rollengte (PR #3 merged)
- **PDF summary:** header banner, metrics bar, parameter tabellen, banen overzicht met VDP-groepering, footer met opmerkingen (PR #2 merged)
- **Kritieke fixes:** migration summary_pdf, XSS fix html.escape(), broken HTML, __pycache__ uit git (PR #5 merged)
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

### KRITIEK — ~~direct fixen voor merge/deploy~~ OPGELOST (PR #5)

| # | Issue | Status | Details |
|---|-------|--------|---------|
| 1 | **Missing `summary_pdf` artifact type** | FIXED | Migration 0003 toegevoegd met `summary_pdf` choice. |
| 2 | **XSS in HTML writer** | FIXED | `html.escape()` toegepast op key en value in beide repo's. |
| 3 | **Broken HTML in summary** | FIXED | Charset quote en `</p>` closing tags gefixt. |

### HOOG

| # | Issue | Status | Details |
|---|-------|--------|---------|
| 4 | **Code duplicatie dev ↔ prod** | OPEN | 6+ functies identiek. Risico op drift. |
| 5 | **`__pycache__` in git** | FIXED | `git rm --cached` uitgevoerd (PR #5). |
| 6 | **Print statements i.p.v. logging** | FIXED | Alle print→logger in beide repo's (PR #6). |
| 7 | **~~Geen zoekfunctie in order historie~~** | FIXED | Zoeken, filteren, paginatie toegevoegd (productie PR #2). |

### MEDIUM

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 8 | **`materiaal = 145` hardcoded** | Prod: `core/business_logic.py:42` | Hardcoded waarde in wikkelformule. Zou configureerbaar moeten zijn (form field of Django setting). |
| 9 | **~~`file_to_generator()` retourneert `None` stil~~** | FIXED | Logger.warning + try/except toegevoegd in beide repo's (PR #6). |
| 10 | **~~Geen error handling op file parsing~~** | FIXED | try/except FileNotFoundError + generic Exception in `file_to_generator()` (PR #6). |
| 11 | **~~File handle leak in `_create_artifact()`~~** | FIXED | Al gefixt met `with open()` in processing.py (PR #5). |
| 12 | **~~Duplicate functie `headers_for_totaal_kolommen()`~~** | FIXED | Tweede exemplaar verwijderd uit `calculations.py` (PR #6). |
| 13 | **Minimale test coverage** | Dev: `test_pdf_summary.py` | Alleen 3 PDF tests. Geen tests voor: splitter, wikkelberekening, file parsing, edge cases, calculations. |

### LAAG

| # | Issue | Locatie | Details |
|---|-------|---------|---------|
| 14 | **~~`source.py` verwijderd, referenties niet opgeruimd~~** | FIXED | Geen referenties gevonden (PR #6). |
| 15 | **~~`werkenmetcalc_temp.py` orphaned~~** | FIXED | Bestand verwijderd (PR #6). |
| 16 | **Form defaults hardcoded in `forms.py`** | Prod: `forms.py` | Defaults bijgewerkt (mes=3, vdp=1, kern dropdown, max_meters=600) maar nog steeds hardcoded. Overweeg Django settings. |

---

## Future To-Do

### Nieuwe features

- [x] **Meters per VDP feature** — `max_meters_per_vdp` form field, auto-berekening `vdp_aantal`, kern dropdown, form UX overhaul (PR #3 merged)
- [x] **Order zoekfunctie** — Zoeken op ordernummer, filteren op status/datum, paginatie (20/pagina). Geïmplementeerd met Django `Paginator` (productie PR #2).
- [x] **Input data opslaan voor herproductie** — Excel input bewaard bij order. Rollen selectie pagina: bekijk alle rollen, selecteer subset, herverwerk als nieuwe job. Volledig herverwerken ook mogelijk. Order verwijderen uit historie (productie PR #2).
- [x] **PDF summary preview in webapp** — PDF/HTML summaries openen inline in nieuw tabblad via `?view` parameter op download URL (productie PR #2).
- [ ] **Batch PDF generatie** — Meerdere orders tegelijk verwerken
- [ ] **Email verzending** — Gegenereerde PDF's per mail versturen

### Business logic fixes

- [x] ~~**Omschrijving/Artikel kolom mapping**~~ — Omschrijving leeg bij normale etiketten, alleen gevuld bij sluitetiketten. (PR #4 merged)
- [ ] **Sluitbarcode uitbouwen voor CERM productnummers** — Huidige sluitbarcode komt uit Excel input. Uitbreiden zodat productnummers uit CERM orders gebruikt kunnen worden. Dummy banen gebruiken nu hardcoded `0` (business_logic.py `dummy_rol_is_baan()`). Form-velden `sluitbarcode_uitvul_waarde` en `posities_sluitbarcode` kunnen weg uit het formulier — deze data hoort in de Excel orderlijst te staan.
- [ ] **Sluitetiket bouwer** — Tool/feature om sluitetiketten te genereren/ontwerpen (layout, barcode, omschrijving, aantal) als onderdeel van de VDP workflow.

### Kritieke bugs (voor deploy)

- [x] ~~**Migration fix**~~ — Migration 0003 met `summary_pdf` choice (PR #5 merged)
- [x] ~~**XSS fix**~~ — `html.escape()` in beide repo's (PR #5 merged)
- [x] ~~**HTML fix**~~ — charset meta tag en `</p>` closing tags (PR #5 merged)

### Code kwaliteit

- [x] ~~**print → logger**~~ — Alle print statements vervangen door Python logging in beide repo's (PR #6)
- [ ] **Code duplicatie oplossen** — Single source of truth voor gedeelde functies (bevinding #4)
- [x] ~~**`__pycache__` uit git**~~ — `git rm --cached` uitgevoerd (PR #5 merged)
- [x] ~~**Duplicate functie verwijderen**~~ — Tweede `headers_for_totaal_kolommen()` verwijderd uit `calculations.py` (PR #6)
- [x] ~~**Error handling**~~ — try/except op `file_to_generator()` in beide repo's (PR #6)
- [ ] **Test coverage uitbreiden** — Tests voor splitter, wikkel, calculations, edge cases (bevinding #13)
- [x] ~~**Opruimen**~~ — `werkenmetcalc_temp.py` verwijderd, geen `source.py` referenties gevonden (PR #6)

### PDF verbeteringen

- [ ] **SPAN hiding labels** — `reportlab.platypus.flowables.Spacer` i.p.v. `<span>` tags die labels verbergen in PDF cellen
- [x] ~~**Opmerkingen escapen**~~ — `xml.sax.saxutils.escape()` toegepast in `_build_footer()`
- [x] ~~**Baan-blok layout**~~ — Elke baan als visueel blok met lichtblauwe header (subtotaal + meters), 3 kolommen per blok
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

## PR Historie

| PR | Branch | Status | Inhoud |
|----|--------|--------|--------|
| #1 | `feature/fastapi-integration` | MERGED | FastAPI REST API |
| #2 | `feature/pdf-summary` | MERGED | PDF summary, HANDOFF.md, code review |
| #3 | `feature/vdp-meters` | MERGED | Max meters per VDP, form UX, kern dropdown |
| #4 | `fix/business-logic-omschrijving` | MERGED | Omschrijving kolom fix (alleen sluitetiketten) |
| #5 | `fix/critical-issues` | MERGED | Migration, XSS, HTML, __pycache__ |

**Productie repo (Django-l02-app03):**

| PR | Branch | Status | Inhoud |
|----|--------|--------|--------|
| #2 | `feature/order-history-search-reprocess` | MERGED | Order historie zoeken/filteren/paginatie, rollen selectie, herproductie, verwijderen, input download, inline PDF viewing, code review fixes |

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
`<productie-repo>/pdf_summary.py`

Bij wijzigingen aan `pdf_summary.py` moet de productie-kopie handmatig gesynchroniseerd worden (tot duplicatie-issue #4 is opgelost).
