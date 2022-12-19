from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from db import DB
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# db = DB()
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def fipsDict():
    infile = open("fips.txt", 'r')
    ret = dict()
    for line in infile:
        x = line.split("|")
        ret[x[0]] = x[2].strip("\n")
    infile.close()
    return ret

def state2fips():
    infile = open("fips.txt", 'r')
    ret = dict()
    for line in infile:
        x = line.split("|")
        print(x)
        ret[x[1]] = x[0]
    infile.close()
    return ret

def getNationalJSON():
    payer = []
    payer_info = db.execute("select", 'select c.CMTE_NM, ie.CMTE_ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total from individualexpenditures ie, pacsummary c where c.CMTE_ID = ie.CMTE_ID group by c.CMTE_NM, ie.CMTE_ID order by total desc;')
    for i in range(len(payer_info)):
        payer.append({ 
            "name": payer_info[i][0], 
            "id": i, 
            "total_expenditure": float(payer_info[i][2]) 
            })
    payee = []
    payee_info = db.execute("select", 'select c.CAND_NAME, f.ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total from individualexpenditures ie, candidates c, fips f where c.CAND_ID = ie.CAND_ID and f.STATE_ABBR = c.CAND_OFFICE_ST group by c.CAND_NAME, f.ID order by total desc;')
    for i in range(len(payee_info)):
        payee.append({ 
            "name": payee_info[i][0], 
            "id": payee_info[i][1], 
            "total_expenditure": float(payee_info[i][2]) })
    links = []
    # links_info = d.execute()
    return { 
        "max_payer_expenditure": float(payer_info[0][2]), 
        "payer": payer, 
        "max_payee_expenditure": float(payee_info[0][2]),
        "payee": payee,
        "links": links,
        }


@app.route('/')
def home():
    return """
    <body>
        <h>HackRPI Fall 2020</h>
        <p>API created for pac-finder, a HackRPI project created by Samarth Patel, Derek Li, and Raunak Shrestha.</p>
        <p>Base URL: https://pac-finder.ue.r.appspot.com/api/v1/</p>
        <p>Available Endpoints:</p>
        <ul>
            <li> GET: <a href="https://pac-finder.ue.r.appspot.com/api/v1/national">/national</a>
            <li> GET: <a href="https://pac-finder.ue.r.appspot.com/api/v1/state?fips=1">/state?fips=[FIPS-code]</a>
        </ul>
    </body>
    """

@app.route('/api/v1/candidates', methods=["GET"])
@cross_origin()
def candidates():
    out = db.execute("select", "select * from candidates limit 10")
    data = [row for row in out]
    return jsonify(data)

@app.route('/api/v1/national', methods=["GET"])
@cross_origin()
def national():
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    return data

@app.route('/api/v1/treemap/national', methods=["GET"])
@cross_origin()
def treemap_national():
    infile = open("json-cache/national.json", "r")
    data = json.load(infile)
    treelist = []
    convert = state2fips()
    for entry in data["payee"]:
        print(entry)
        treelist.append({
            "name": entry["name"],
            "value": entry["total_expenditure"],
            "fips": convert[entry["name"]]
        })
    return {
        "children": treelist
    }

@app.route('/api/v1/state', methods=["GET"])
@cross_origin()
def state():
    fips = int(request.args.get('fips'))
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    s_payer = []
    s_payee = []
    s_links = []
    payer_ids = set()
    for ele in data["links"]:
        if int(ele["payee"]) == fips: 
            s_links.append(ele)
            payer_ids.add(int(ele["payer"]))
    for ele in data["payer"]:
        if int(ele["id"]) in payer_ids: s_payer.append(ele)
    for ele in data["payee"]:
        if int(ele["id"]) == fips: s_payee.append(ele)
    return {
        "max_payer_expenditure": s_payer[0]["total_expenditure"],
        "max_payee_expenditure": s_payee[0]["total_expenditure"],
        "payer": s_payer,
        "payee": s_payee,
        "links": s_links
    }

@app.route('/api/v1/treemap/state', methods=["GET"])
@cross_origin()
def treemap_state():
    fips = int(request.args.get('fips'))
    filter = request.args.get('filter')
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    payer_ids = set()
    treelist = []
    infile = open("industry.json", 'r')
    ftr = json.load(infile)
    infile.close()
    new_filter = dict()
    for ele in ftr["industry"]:
        for key in ele:
            if key not in new_filter: new_filter[key] = {ele[key]}
            else: new_filter[key].add(ele[key])
    for ele in data["links"]:
        if int(ele["payee"]) == fips: payer_ids.add(int(ele["payer"]))
    for ele in data["payer"]:
        if int(ele["id"]) in payer_ids and (filter == None or filter == "" or (filter in new_filter and ele["name"] in new_filter[filter])):
            treelist.append({
                "name": ele["name"],
                "value": ele["total_expenditure"] 
            })
    return {
        "children": treelist
    }

@app.route('/api/v1/treemap/everything', methods=["GET"])
@cross_origin()
def everything():
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    statelevel = data["payee"]
    return {
        "children": statelevel
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

