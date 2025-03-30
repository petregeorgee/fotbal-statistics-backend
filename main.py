from flask import Flask, jsonify, request
import http.client
import configparser
import json
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Allow all origins
countries_data = []

def load_properties(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['default']


properties = load_properties('config.properties')


headers = {
    'x-rapidapi-host': properties.get('api_host'),
    'x-rapidapi-key': properties.get('api_key')
}


def fetch_countries():
    """Fetch countries from the API and store them globally."""
    global countries_data
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/countries", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Convert JSON response to Python dictionary
    response_json = json.loads(data.decode("utf-8"))

    # Extract only the relevant 'response' field
    if "response" in response_json:
        countries_data = response_json["response"]
    else:
        countries_data = []  # Fallback if the response structure is unexpected


# Call API once at startup to populate the data
fetch_countries()


continent_mapping = {
    "Europe": ["AL", "AD", "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LT", "LU", "MT", "MD" "MC", "NL", "NO", "PL", "PT", "RO", "RU", "SM", "RS", "SK", "SI", "ES", "SE", "CH", "UA", "GB", "XK"],
    "Africa": ["DZ", "AO", "BJ", "BW", "BF", "BI", "CM", "CV", "CF", "TD", "KM", "CG", "CD", "DJ", "EG", "GQ", "ER", "SZ", "ET", "GA", "GM", "GH", "GN", "GW", "CI", "KE", "LS", "LR", "LY", "MG", "MW", "ML", "MR", "MU", "MA", "MZ", "NA", "NE", "NG", "RW", "ST", "SN", "SC", "SL", "SO", "ZA", "SS", "SD", "TZ", "TG", "TN", "UG", "ZM", "ZW"],
    "Asia": ["AF", "AM", "AZ", "BH", "BD", "BT", "BN", "KH", "CN", "GE", "IN", "ID", "IR", "IQ", "IL", "JP", "JO", "KZ", "KW", "KG", "LA", "LB", "MO", "MY", "MV", "MN", "MM", "NP", "KP", "OM", "PK", "PH", "QA", "SA", "SG", "KR", "LK", "SY", "TW", "TJ", "TH", "TR", "TM", "AE", "UZ", "VN", "YE"],
    "North America": ["AG", "BS", "BB", "BZ", "CA", "CR", "CU", "DM", "DO", "SV", "GD", "GT", "HT", "HN", "JM", "MX", "NI", "PA", "KN", "LC", "VC", "TT", "US"],
    "South America": ["AR", "BO", "BR", "CL", "CO", "EC", "GY", "PY", "PE", "SR", "UY", "VE"],
    "Oceania": ["AU", "FJ", "KI", "MH", "FM", "NR", "NZ", "PW", "PG", "WS", "SB", "TO", "TV", "VU"],
    "World": ["WL"]
}


@app.route("/continents", methods=["GET"])
def get_continents():
    """Returns the list of continents"""
    return jsonify(list(continent_mapping.keys()))


@app.route("/countries", methods=["GET"])
def get_countries_by_continent():
    """Returns the list of countries for a given continent"""
    continent = request.args.get("continent")

    if not continent or continent not in continent_mapping:
        return jsonify({"error": "Invalid or missing continent parameter"}), 400

    country_codes = set(continent_mapping[continent])
    if str(continent).__eq__("World"):
        filtered_countries = [{"code": "WL", "flag": None, "name": "World"}]
    else:
        filtered_countries = [country for country in countries_data if country["code"] in country_codes]

    return jsonify(filtered_countries)

@app.route('/')
def hello_world():
    # return 'hello test'
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/teams/statistics?season=2023&team=33&league=39", headers=headers)
    res = conn.getresponse()
    return res.read()



@app.route('/leagues')
def get_leagues():
    # TODO: get the most important competitions for each country!!!

    country = request.args.get("country", "Spain")  # Default to "Spain" if not provided

    conn = http.client.HTTPSConnection(properties.get('api_host'))

    conn.request("GET", f"/leagues?country={country}&season={properties.get('season')}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    data = json.loads(data)

    leagues = [{"id": league["league"]["id"], "name": league["league"]["name"]}
               for league in data["response"]
               if len(league["league"]["name"]) <= 150]

    # Sort the leagues by id in ascending order
    leagues.sort(key=lambda x: x["id"])

    return json.dumps(leagues, indent=1)

@app.route('/standings')
def get_standings():
    league_id = request.args.get("league", "140")  # Default to "140" if not provided

    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/standings?league=" + league_id + "&season=" + properties.get('season'), headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    return data


@app.route('/next_fixtures')
def get_next_fixtures():
    # TODO: do something for returning all next fixtures from all the leagues in that country
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    league_id = request.args.get("league", "140")  # Default to "140" if not provided

    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/fixtures?league=" + league_id + "&season=" + properties.get('season') + "&from=" + today + "&to=" + tomorrow, headers=headers) # TODO: fix to and from.
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    data = json.loads(data)

    fixtures = [{
        "fixture_id": fixture["fixture"]["id"],
        "home_id": fixture["teams"]["home"]["id"],
        "home_team_name": fixture["teams"]["home"]["name"],
        "away_id": fixture["teams"]["away"]["id"],
        "away_team_name": fixture["teams"]["away"]["name"],
        "date": fixture["fixture"]["date"]
    } for fixture in data["response"]]  # Access the "response" part of the JSON

    output = json.dumps(fixtures, indent=4)
    # print(output)
    return output


@app.route('/predictions')
def get_predictions():
    fixture_id = request.args.get("fixture_id", "1208748")  # Default to "140" if not provided

    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/predictions?fixture=" + fixture_id, headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    return data


@app.route('/team_stats', methods=["GET"]) # statistici legate de goluri/ HT/ FT
@cross_origin()
def get_team_stats():
    team_id = request.args.get("team", "529")  # Default to "529" if not provided

    # Connect to the external API
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/fixtures?team=" + team_id + "&season=2024", headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')

    # Parse the JSON response
    response_json = json.loads(data)

    # Sort the "response" list by the "timestamp" field in descending order
    if "response" in response_json:
        response_json["response"].sort(key=lambda x: x["fixture"]["timestamp"], reverse=True)

    # Return the sorted JSON as a string
    return jsonify(response_json)


@app.route('/fixture_team_stats')  # More detailed statistics
def get_fixture_team_stats():
    # Get query parameters with defaults if not provided
    fixture_id = request.args.get("fixture_id", "529")  # Default to "529"
    team_id = request.args.get("team_id", "529")  # Default to "529"

    # Connect to the external API
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    # Properly format query string with '&' between parameters
    endpoint = "/fixtures/statistics?fixture=" + fixture_id + "&team=" +team_id
    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')

    return data



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)