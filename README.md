# Nepal Admin Trace API

This project provides a RESTful API for querying historical administrative changes in Nepal, tracking how Village Development Committees (VDCs) and wards were reorganized into municipalities and new ward numbers during the 2017 reform. It uses an OWL ontology loaded into a Virtuoso triple store and exposes SPARQL-backed endpoints via Flask.

## Features

- **Replacement Lookup**: Retrieve the successor unit(s) of any old administrative entity.
- **Historical Lineage**: Trace predecessors and successors for a specific unit.
- **District Summary**: Get counts of old VDCs and new municipalities within a district.
- **Name Search**: Search units by partial or full name.

## Prerequisites

- Python 3.7 or higher
- [Virtuoso Open‑Source Edition](https://vos.openlinksw.com/owiki/wiki/VOS/) running locally or remote
- The Nepal Admin Trace OWL ontology loaded into Virtuoso under a named graph (e.g., `http://nepal.admin.trace/ontology`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/nepal-admin-trace-api.git
   cd nepal-admin-trace-api
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure SPARQL endpoint**
   - By default, the Flask app connects to `http://localhost:8890/sparql`.
   - To change this, edit the `SPARQL_ENDPOINT` constant in `app.py` or set the environment variable `SPARQL_ENDPOINT` before running.

## Running the Server

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=4000
```

The API will be available at `http://localhost:4000`.

## Endpoints

| Method | Path                                         | Description                                          |
| ------ | -------------------------------------------- | ---------------------------------------------------- |
| GET    | `/units/{unitType}/{unitId}/replacedBy`      | List replacement units for a given entity            |
| GET    | `/units/{unitType}/{unitId}/history`         | Full lineage (predecessors, current, successors)     |
| GET    | `/districts/{districtId}/changes`            | Summary of VDC-to-municipality changes in a district |
| GET    | `/search?query={name}`                       | Search units by name (partial, case‑insensitive)     |

- **`unitType`**: one of `vdc`, `municipality`, `ward`, `district`.
- **`unitId`**: the identifier string matching the ontology individual (e.g., `ShreenathkotVDC`).

## Example Usage

```bash
curl http://localhost:4000/units/vdc/ShreenathkotVDC/replacedBy
```

```json
[
  {
    "id": "http://nepal.admin.trace/ontology#SiranchowkRM",
    "type": "vdc"
  }
]
```

## Testing

Add tests under `tests/` and run with pytest:

```bash
pytest
```

## Contributing

Contributions welcome! Please open issues or pull requests for:

- Additional endpoints or query patterns
- Improved error handling and validation
- Authentication and rate limiting
- Dockerization and CI/CD workflows

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


