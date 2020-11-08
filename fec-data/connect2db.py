from db import DB

db = DB()
print("CONNECTED")

# cnxn = mysql.connector.connect(**config)
# cursor = cnxn.cursor()  # initialize connection cursor
# cursor.execute('CREATE DATABASE pacdata')  # create a new 'testdb' database
# cnxn.close()  # close connection because we will be reconnecting to testdb


schema = "CREATE TABLE candidates (" + \
                "CAND_ID varchar(9) not null PRIMARY KEY," + \
                "CAND_NAME varchar(200)," + \
                "CAND_PTY_AFFILIATION varchar(3)," + \
                "CAND_ELECTION_YR DOUBLE," + \
                "CAND_OFFICE_ST varchar(2)," + \
                "CAND_OFFICE varchar(1)," + \
                "CAND_OFFICE_DISTRICT varchar(2)," + \
                "CAND_ICI varchar(1)," + \
                "CAND_STATUS varchar(1)," + \
                "CAND_PCC varchar(9)," + \
                "CAND_ST1 varchar(34)," + \
                "CAND_ST2 varchar(34)," + \
                "CAND_CITY varchar(30)," + \
                "CAND_ST varchar(2)," + \
                "CAND_ZIP varchar(9));" 

db.execute("exec", "DROP TABLE IF EXISTS `candidates`;")
db.execute("exec", schema)

query = "INSERT INTO candidates (CAND_ID, CAND_NAME, CAND_PTY_AFFILIATION, CAND_ELECTION_YR, CAND_OFFICE_ST, CAND_OFFICE, CAND_OFFICE_DISTRICT, CAND_ICI, CAND_STATUS, CAND_PCC, CAND_ST1, CAND_ST2, CAND_CITY, CAND_ST, CAND_ZIP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
db.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/cn.txt", query)
print("cn")

# Create the individual expenditures table from itpas2.txt
query = "CREATE TABLE individualexpenditures (CMTE_ID varchar(9) not null PRIMARY KEY,AMNDT_IND varchar(1),RPT_TP varchar(3),TRANSACTION_PGI varchar(5),IMAGE_NUM varchar(18),TRANSACTION_TP varchar(3),ENTITY_TP varchar(3),NAME varchar(200),CITY varchar(30),STATE varchar(2),ZIP_CODE varchar(9),EMPLOYER varchar(38),OCCUPATION varchar(38),TRANSACTION_DT varchar(8),TRANSACTION_AMT DOUBLE,OTHER_ID varchar(9),CAND_ID varchar(9),TRAN_ID varchar(32),FILE_NUM DOUBLE,MEMO_CD varchar(1),MEMO_TEXT varchar(100),SUB_ID DOUBLE);"
db.execute("exec", 'DROP TABLE IF EXISTS `individualexpenditures`;')
db.execute("exec", query)

# Populate the individual expenditures table
query = "INSERT INTO individualexpenditures (CMTE_ID, AMNDT_IND, RPT_TP, TRANSACTION_PGI, IMAGE_NUM, TRANSACTION_TP, ENTITY_TP, NAME, CITY, STATE, ZIP_CODE, EMPLOYER, OCCUPATION, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID, CAND_ID, TRAN_ID, FILE_NUM, MEMO_CD, MEMO_TEXT, SUB_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
db.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/itpas2.txt", query)
print("itpas2")

# Create the pac summary table from webk20.txt
query = "CREATE TABLE pacsummary (CMTE_ID varchar(9) not null PRIMARY KEY,CMTE_NM varchar(200),CMTE_TP varchar(1),CMTE_DSGN varchar(1),CMTE_FILING_FREQ varchar(1),TTL_RECEIPTS DOUBLE,TRANS_FROM_AFF DOUBLE,INDV_CONTRIB DOUBLE,OTHER_POL_CMTE_CONTRIB DOUBLE,CAND_CONTRIB DOUBLE,CAND_LOANS DOUBLE,TTL_LOANS_RECEIVED DOUBLE,TTL_DISB DOUBLE,TRANF_TO_AFF DOUBLE,INDV_REFUNDS DOUBLE,OTHER_POL_CMTE_REFUNDS DOUBLE,CAND_LOAN_REPAY DOUBLE,LOAN_REPAY DOUBLE,COH_BOP DOUBLE,COH_COP DOUBLE,DEBTS_OWED_BY DOUBLE,NONFED_TRANS_RECEIVED DOUBLE,CONTRIB_TO_OTHER_CMTE DOUBLE,IND_EXP DOUBLE,PTY_COORD_EXP DOUBLE,NONFED_SHARE_EXP DOUBLE,CVG_END_DT varchar(10);"
db.execute("exec", 'DROP TABLE IF EXISTS `pacsummary`;')
db.execute("exec", query)

# Populate the pac summary table
query = "INSERT INTO pacsummary ( CMTE_ID, CMTE_NM, CMTE_TP, CMTE_DSGN, CMTE_FILING_FREQ, TTL_RECEIPTS, TRANS_FROM_AFF, INDV_CONTRIB, OTHER_POL_CMTE_CONTRIB, CAND_CONTRIB, CAND_LOANS, TTL_LOANS_RECEIVED, TTL_DISB, TRANF_TO_AFF, INDV_REFUNDS, OTHER_POL_CMTE_REFUNDS, CAND_LOAN_REPAY, LOAN_REPAY, COH_BOP, COH_COP, DEBTS_OWED_BY, NONFED_TRANS_RECEIVED, CONTRIB_TO_OTHER_CMTE, IND_EXP, PTY_COORD_EXP, NONFED_SHARE_EXP, CVG_END_DT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
db.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/webk20.txt", query)
print("webk20")

# db.execute("select", "select ps.CMTE_NM, ie.TRANSACTION_AMT, c.CAND_NAME from pacsummary ps, individualexpenditures ie, candidates c where ps.CMTE_ID = ie.CMTE_ID and c.CAND_ID = ie.CAND_ID LIMIT 20;")
# db.execute("select e.CMTE_ID, e.NAME from individualexpenditures e LIMIT 5;")

db.close()



