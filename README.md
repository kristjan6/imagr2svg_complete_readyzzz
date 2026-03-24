# Blueprint2DWG Complete Ready

Ferdig testbar applikasjon for opplasting av blueprints / tekniske tegninger og nedlasting av DXF.
DWG er klargjort som valgfritt steg via ODA File Converter.

## Hva som følger med

- Frontend: React + Nginx
- API: FastAPI
- Worker: RQ + Redis
- Database: PostgreSQL
- Objektlagring: MinIO (S3-kompatibel)
- Lokal kjøring: Docker Compose
- Preview og debug-bilder i UI
- Enkel vektoriseringspipeline for bilde/PDF -> DXF

## Rask start

### 1) Pakk ut
### 2) Lag `.env`
Kopier `.env.example` til `.env`

På macOS / Linux:
```bash
cp .env.example .env
```

På Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

### 3) Start alt
```bash
docker compose up --build
```

### 4) Åpne
- Webapp: http://localhost:8080
- API docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

Innlogging MinIO:
- user: minioadmin
- pass: minioadmin

## Hva som er klart
- Upload av PNG/JPG/TIFF/PDF
- Preview
- Jobbstatus med fremdrift
- Debug-bilder
- DXF-download
- S3-lagring via MinIO
- PostgreSQL-jobblogg
- Redis-kø med worker

## DWG
For ekte DWG:
1. installer ODA File Converter i worker-miljøet
2. sett `ENABLE_DWG=true`
3. sett `ODA_EXECUTABLE=/path/to/ODAFileConverter`

## Viktig
Denne versjonen er laget for å være **testbar og kjørbar lokalt** med minst mulig friksjon.
Den er en god base for videre produksjonsarbeid.
