from db import DB
import json

db = DB()



def fipsDict():
    infile = open("/mnt/c/Users/shresr/Desktop/Projects/pac-finder/data/fips.txt", 'r')
    ret = dict()
    for line in infile:
        x = line.split("|")
        ret[x[0]] = x[2].strip("\n")
    infile.close()
    return ret

def createCandsJSON():
    cand_info = db.execute("select", 'select * from candidates;')
    info = dict()
    for row in cand_info:
        info[row[1]] = row[5]
    return info


def getNationalJSON():
    payer = []
    id2index = dict()
    payer_info = db.execute("select", 'select c.CMTE_NM, ie.CMTE_ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total from individualexpenditures ie, pacsummary c where c.CMTE_ID = ie.CMTE_ID group by c.CMTE_NM, ie.CMTE_ID order by total desc;')
    for i in range(len(payer_info)):
        id2index[payer_info[i][1]] = i
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

    payee_dict = dict()
    fips = fipsDict()
    for entry in payee:
        if entry["id"] not in payee_dict.keys():
            payee_dict[entry["id"]] = entry["total_expenditure"]
        else:
            payee_dict[entry["id"]] += entry["total_expenditure"]

    extraData = dict()
    newPayeeInfo = []
    for key in payee_dict.keys():
        extraData[int(key)] = float(payee_dict[key])
        newPayeeInfo.append({
            "name": fips[key],
            "id": key,
            "total_expenditure": payee_dict[key]
        })
    output=open("json-cache/fips2expenditure.json", "w+")
    json.dump(extraData, output)
    output.close()
    payee = newPayeeInfo

    links = []
    links_info = db.execute("select", 'select ie.CMTE_ID, c.ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total, ie.TRANSACTION_TP from individualexpenditures ie inner join (select cs.CAND_ID, f.ID from candidates cs, fips f where f.STATE_ABBR = cs.CAND_OFFICE_ST) c on ie.CAND_ID = c.CAND_ID group by ie.CMTE_ID, c.ID, ie.TRANSACTION_TP;')
    for i in range(len(links_info)):
        if links_info[i][0] not in id2index: continue
        links.append({
            "payer": id2index[links_info[i][0]],
            "payee": links_info[i][1],
            "expenditure": float(links_info[i][2]),
            "type": links_info[i][3]
        })
    return { 
        "max_payer_expenditure": float(payer_info[0][2]), 
        "payer": payer, 
        "max_payee_expenditure": float(payee_info[0][2]),
        "payee": payee,
        "links": links,
        }
        
def getStateJSON():
    fips = 5#int(request.args.get('fips'))
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

def getNationalTreeJSON():
    infile = open("json-cache/national.json", "r")
    data = json.load(infile)
    treelist = []
    for entry in data["payee"]:
        treelist.append({
            "name": entry["name"],
            "value": entry["total_expenditure"]
        })
    return {
        "children": treelist
    }
    
def getStateTreeJSON():
    fips = 5#int(request.args.get('fips'))
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    s_payer = []
    s_links = []
    payer_ids = set()
    treelist = []
    for ele in data["links"]:
        if int(ele["payee"]) == fips: payer_ids.add(int(ele["payer"]))
    for ele in data["payer"]:
        if int(ele["id"]) in payer_ids:
            treelist.append({
                "name": ele["name"],
                "value": ele["total_expenditure"] 
            })
    return {
        "children": treelist
    }



def state2candJSON():
    payee_info = db.execute("select", 'select c.CAND_NAME, f.ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total from individualexpenditures ie, candidates c, fips f where c.CAND_ID = ie.CAND_ID and f.STATE_ABBR = c.CAND_OFFICE_ST group by c.CAND_NAME, f.ID order by total desc;')
    s2c = dict()
    c2e = dict() #candidate to expenditure
    fips = fipsDict()
    for i in range(len(payee_info)):
        state_abbrev = fips[payee_info[i][1]]
        if state_abbrev not in s2c: s2c[state_abbrev] = {payee_info[i][0]}
        else: s2c[state_abbrev].add(payee_info[i][0])
        if payee_info[i][0] not in c2e: c2e[payee_info[i][0]] = float(payee_info[0][2])
        else: c2e[payee_info[i][0]] += float(payee_info[0][2])
    return s2c, c2e

def cand2pac():
    infile = open('json-cache/candidates.json', 'r')
    data = json.load(infile)
    infile.close()
    id2c = dict() # id to candidate
    for cand in data:
        id2c[cand[0]] = cand[1]
    links_info = db.execute("select", 'select ie.CMTE_ID, c.ID, c.CAND_ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total, ie.TRANSACTION_TP from individualexpenditures ie inner join (select cs.CAND_ID, f.ID from candidates cs, fips f where f.STATE_ABBR = cs.CAND_OFFICE_ST) c on ie.CAND_ID = c.CAND_ID group by ie.CMTE_ID, c.ID, c.CAND_ID, ie.TRANSACTION_TP;')
    c2p = dict()
    pacs_info = db.execute("select", "select * from pacsummary")
    id2p = dict()
    for row in pacs_info:
        id2p[row[0]] = row[1]
    for row in links_info:
        if row[2] not in id2c or row[0] not in id2p: continue
        cand = id2c[row[2]]
        pac = id2p[row[0]]
        value = float(row[3])
        if cand not in c2p: c2p[cand] = {(pac, value)}
        else: c2p[cand].add((pac, value))
    return c2p


def everything():
    infile = open('json-cache/national.json', 'r')
    data = json.load(infile)
    infile.close()
    s2c, c2e = state2candJSON() #state_abbrev to candidate & candidate to expenditure
    c2p = createCandsJSON() # candidate to position
    cand2p = cand2pac()
    statelevel = []
    for key in data["payee"]:
        state = key["name"]
        candidates = []
        for state in s2c:
            for cand in s2c[state]:
                if cand not in cand2p: continue
                pacs = []
                for pair in cand2p[cand]:
                    pacs.append({
                        "name": pair[0],
                        "value": pair[1]
                    })
                candidates.append({
                    "name": cand,
                    "position": c2p[cand],
                    "children": pacs
                })
        statelevel.append({
            "name": state,
            "children": candidates
        })
    return {
        "children": statelevel
    }

# infile = open('json-cache/national.json', 'r')
#     data = json.load(infile)
#     infile.close()
#     s2c, c2e = state2candJSON() #state_abbrev to candidate & candidate to expenditure
#     c2p = createCandsJSON() # candidate to position
#     statelevel = []
#     ret = []
#     for key in data["payee"]:
#         state = key["name"]
#         candidates = []
#         for state in s2c:
#             for cand in s2c[state]:
#                 ret.append({
#                     "state": state,
#                     "candidate": cand,
#                     "pac": pacs,
#                     "value"
#                 })
#     return {
#         "children": statelevel
#     }

# outfile = open("json-cache/everything.json", "w+")
# json.dump(getStateTreeJSON(), outfile)
# outfile.close()


getNationalJSON()

# nationalJSON = getNationalJSON()
# outfile = open("json-cache/national.json", "w+")
# json.dump(nationalJSON, outfile)
# outfile.close()

# ntj = getNationalTreeJSON()
# outfile = open("json-cache/treemap-national.json", "w+")
# json.dump(ntj, outfile)
# outfile.close()

db.close()