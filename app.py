from flask import Flask, jsonify, request, abort
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

# Configure SPARQL endpoint
SPARQL_ENDPOINT = "http://localhost:8890/sparql"
sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

PREFIX = "PREFIX : <http://nepal.admin.trace/ontology#>\n"

# Helper to execute SPARQL
def run_query(query):
    sparql.setQuery(PREFIX + query)
    try:
        results = sparql.query().convert()
        return results.get("results", {}).get("bindings", [])
    except Exception as e:
        app.logger.error(f"SPARQL query failed: {e}")
        abort(500, description="Query execution error")

# Schema conversion
def format_unit(binding):
    return {
        'id': binding['unit']['value'],
        'name': binding['name']['value'] if 'name' in binding else binding['unit']['value'],
        'type': binding['type']['value'].split('#')[-1].lower()
    }

@app.route('/units/<unitType>/<unitId>/replacedBy', methods=['GET'])
def get_replacements(unitType, unitId):
    # Map path to class
    cls = unitType.capitalize()
    uri = f":{unitId}"
    query = f"SELECT ?unit ?repl WHERE {{ ?unit a :{cls}; :wasReplacedBy ?repl; FILTER(strends(str(?unit), \"{unitId}\")) }}"
    results = run_query(query)
    replacements = []
    for row in results:
        replacements.append({
            'id': row['repl']['value'],
            'type': unitType,
        })
    return jsonify(replacements)

@app.route('/units/<unitType>/<unitId>/history', methods=['GET'])
def get_history(unitType, unitId):
    cls = unitType.capitalize()
    # predecessors
    q_pred = f"SELECT ?pred WHERE {{ ?pred :wasReplacedBy ?current; FILTER(strends(str(?current), \"{unitId}\")) }}"
    preds = run_query(q_pred)
    # current
    current = { 'id': unitId, 'type': unitType }
    # successors
    q_succ = f"SELECT ?succ WHERE {{ :{unitId} :wasReplacedBy ?succ }}"
    succs = run_query(q_succ)
    return jsonify({
        'predecessors': [{'id': p['pred']['value']} for p in preds],
        'current': current,
        'successors': [{'id': s['succ']['value']} for s in succs]
    })

@app.route('/districts/<districtId>/changes', methods=['GET'])
def get_district_changes(districtId):
    q = (
        "SELECT (COUNT(DISTINCT ?old) AS ?numOld) (COUNT(DISTINCT ?new) AS ?numNew) "
        "WHERE { ?old a :VDC; :belongsTo ?d; :wasReplacedBy ?new . FILTER(strends(str(?d), \""" + districtId + "\")) }"
    )
    res = run_query(q)
    if not res:
        abort(404)
    row = res[0]
    return jsonify({
        'district': districtId,
        'numOldUnits': int(row['numOld']['value']),
        'numNewUnits': int(row['numNew']['value'])
    })

@app.route('/search', methods=['GET'])
def search_units():
    term = request.args.get('query')
    if not term:
        abort(400, description="Missing search query parameter")
    q = (
        "SELECT ?unit WHERE { ?unit ?p ?o . FILTER regex(str(?unit), \""" + term + "\", 'i') } LIMIT 50"
    )
    results = run_query(q)
    return jsonify([{'id': row['unit']['value']} for row in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
