from flask import Flask, jsonify, request
import http.client
import configparser
import json
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

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
    "Europe": ["AL", "AD", "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LT", "LU", "MT", "MD" "MC", "NL", "NO", "PL", "PT", "RO", "RU", "SM", "RS", "SK", "SI", "ES", "SE", "CH", "UA", "GB-ENG", "XK"],
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


def get_predictions_not_api_endpoint(fixture_id):
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/predictions?fixture=" + fixture_id, headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = data.decode('utf-8')
    return data


@app.route('/headtohead', methods=['GET'])
def get_head_to_head(h2h=None, league=None, season=None):
    # Use provided arguments or fallback to query parameters
    h2h = h2h or request.args.get("h2h", "170-157")  # Default team IDs
    league = league or request.args.get("league", "78")  # Default Premier League
    season = season or request.args.get("season", "2023")  # Default season
    yesterday = datetime.now() - timedelta(days=1)
    # Set up API connection
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    endpoint = f"/fixtures/headtohead?h2h={h2h}&league={league}&season={season}"

    # Make API request
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')

    return data

@app.route('/h2h', methods=['GET'])
def get_h2h_data():
    fixture_id = request.args.get("fixture_id", "1224222")  # Default to "140" if not provided

    return fetch_and_analyze_headtohead(fixture_id)


def fetch_and_analyze_headtohead(fixture_id):
    response = get_predictions_not_api_endpoint(fixture_id)
    fixtures_data = json.loads(response)
    data = {}

    # data['data'] = '2024-05-12'  # TODO.
    data['home_team_name'] = fixtures_data['response'][0]['teams']['home']['name']
    data['home_team_logo'] = fixtures_data['response'][0]['teams']['home']['logo']
    data['home_team_league_form'] = fixtures_data['response'][0]['teams']['home']['league']['form'][-5:] # get last 5 characters
    data['home_team_form'] = fixtures_data['response'][0]['teams']['home']['last_5']['form']
    data['home_team_attack'] = fixtures_data['response'][0]['teams']['home']['last_5']['att']
    data['home_team_defence'] = fixtures_data['response'][0]['teams']['home']['last_5']['def']
    data['home_team_goals_for'] = fixtures_data['response'][0]['teams']['home']['last_5']['goals']['for']['total']
    data['home_team_goals_for_avg'] = fixtures_data['response'][0]['teams']['home']['last_5']['goals']['for']['average']
    data['home_team_goals_against'] = fixtures_data['response'][0]['teams']['home']['last_5']['goals']['against']['total']
    data['home_team_goals_against_avg'] = fixtures_data['response'][0]['teams']['home']['last_5']['goals']['against']['total']

    data['away_team_name'] = fixtures_data['response'][0]['teams']['away']['name']
    data['away_team_logo'] = fixtures_data['response'][0]['teams']['away']['logo']
    data['away_team_league_form'] = fixtures_data['response'][0]['teams']['away']['league']['form'][-5:] # get last 5 characters
    data['away_team_form'] = fixtures_data['response'][0]['teams']['away']['last_5']['form']
    data['away_team_attack'] = fixtures_data['response'][0]['teams']['away']['last_5']['att']
    data['away_team_defence'] = fixtures_data['response'][0]['teams']['away']['last_5']['def']
    data['away_team_goals_for'] = fixtures_data['response'][0]['teams']['away']['last_5']['goals']['for']['total']
    data['away_team_goals_for_avg'] = fixtures_data['response'][0]['teams']['away']['last_5']['goals']['for']['average']
    data['away_team_goals_against'] = fixtures_data['response'][0]['teams']['away']['last_5']['goals']['against']['total']
    data['away_team_goals_against_avg'] = fixtures_data['response'][0]['teams']['away']['last_5']['goals']['against']['total']


    data['matches'] = []
    head_to_head_extract(data, fixtures_data['response'][0]['h2h'])

    home_team_id = fixtures_data['response'][0]['teams']['home']['id']
    away_team_id = fixtures_data['response'][0]['teams']['away']['id']
    extract_team_stats_goals_gaussian(home_team_id, data, 'home_team')
    extract_team_stats_goals_gaussian(away_team_id, data, 'away_team')

    return data


def extract_team_stats_goals_gaussian(team_id, data, label):
    response = get_team_stats_not_api_endpoint(team_id)
    half_time_scores = []
    full_time_scores = []
    fixtures_data = json.loads(response.data)  # Parse JSON response
    # Extract scores from response
    for fixture in fixtures_data.get('response', []):
        if not str(fixture['fixture']['status']['long']).__eq__('Not Started'):
            halftime_score = fixture['score']['halftime']
            fulltime_score = fixture['score']['fulltime']

            if halftime_score and fulltime_score:
                if halftime_score.get('home') is None or halftime_score.get('away') is None:
                    continue
                home_halftime = halftime_score['home']
                away_halftime = halftime_score['away']

                if fulltime_score.get('home') is None or fulltime_score.get('away') is None:
                    continue
                home_fulltime = fulltime_score['home']
                away_fulltime = fulltime_score['away']

                half_time_scores.append(home_halftime + away_halftime)
                full_time_scores.append(home_fulltime + away_fulltime)
    data['gaussian_ht_goals_all_' + label] = predict_most_probable_goals(half_time_scores)
    data['gaussian_ft_goals_all_' + label] = predict_most_probable_goals(full_time_scores)


def head_to_head_extract(data, fixture_data):
    half_time_scores = []
    full_time_scores = []

    # Extract scores from response
    for fixture in fixture_data:
        match = {}
        if not str(fixture['fixture']['status']['long']).__eq__('Not Started'):
            match['teams'] = fixture['teams']['home']['name'] + " - " + fixture['teams']['away']['name']
            match['date'] = fixture['fixture']['date']
            halftime_score = fixture['score']['halftime']
            fulltime_score = fixture['score']['fulltime']

            match['ht_score'] = str(halftime_score['home']) + " - " + str(halftime_score['away'])
            match['ft_score'] = str(fulltime_score['home']) + " - " + str(fulltime_score['away'])

            if halftime_score and fulltime_score:
                if halftime_score.get('home') is None or halftime_score.get('away') is None:
                    continue
                home_halftime = halftime_score['home']
                away_halftime = halftime_score['away']

                if fulltime_score.get('home') is None or fulltime_score.get('away') is None:
                    continue
                home_fulltime = fulltime_score['home']
                away_fulltime = fulltime_score['away']

                half_time_scores.append(home_halftime + away_halftime)
                full_time_scores.append(home_fulltime + away_fulltime)
            data['matches'].append(match)
    data['gaussian_ht_goals_h2h'] = predict_most_probable_goals(half_time_scores)
    data['gaussian_ft_goals_h2h'] = predict_most_probable_goals(full_time_scores)


def predict_most_probable_goals(scores):
    scores_array = np.array(scores)
    scores_mean = np.mean(scores_array)
    return int(round(scores_mean))


def analyze_gaussian_distribution(half_time_scores, full_time_scores):
    half_time_array = np.array(half_time_scores)
    full_time_array = np.array(full_time_scores)

    half_time_mean = np.mean(half_time_array)
    half_time_std = np.std(half_time_array)

    full_time_mean = np.mean(full_time_array)
    full_time_std = np.std(full_time_array)

    x_half_time = np.linspace(min(half_time_array), max(half_time_array), 100)
    y_half_time = norm.pdf(x_half_time, loc=half_time_mean, scale=half_time_std)

    x_full_time = np.linspace(min(full_time_array), max(full_time_array), 100)
    y_full_time = norm.pdf(x_full_time, loc=full_time_mean, scale=full_time_std)

    plt.figure(figsize=(12, 6))

    # Half-Time Score Distribution
    plt.subplot(1, 2, 1)
    plt.plot(x_half_time, y_half_time, label=f"Mean: {half_time_mean:.2f}, Std Dev: {half_time_std:.2f}")
    plt.title("Gaussian Distribution of Half-Time Scores")
    plt.xlabel("Half-Time Score")
    plt.ylabel("Probability Density")
    plt.legend()

    # Full-Time Score Distribution
    plt.subplot(1, 2, 2)
    plt.plot(x_full_time, y_full_time, label=f"Mean: {full_time_mean:.2f}, Std Dev: {full_time_std:.2f}")
    plt.title("Gaussian Distribution of Full-Time Scores")
    plt.xlabel("Full-Time Score")
    plt.ylabel("Probability Density")
    plt.legend()

    plt.tight_layout()
    plt.show()


@app.route('/team_stats', methods=["GET"])
@cross_origin()
def get_team_stats():
    team_id = request.args.get("team", "529")  # Default team ID is 529
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


def get_team_stats_not_api_endpoint(team_id):
    # Connect to the external API
    conn = http.client.HTTPSConnection(properties.get('api_host'))
    conn.request("GET", "/fixtures?team=" + str(team_id) + "&season=2024", headers=headers)
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