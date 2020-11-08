import mysql.connector
from mysql.connector.constants import ClientFlag
from config import SQLPASSWORD, HOSTIP

class DB:
    def __init__(self):
        self.config = {
                        'user': 'root',
                        'password': SQLPASSWORD,
                        'host': HOSTIP,
                        'client_flags': [ClientFlag.SSL],
                        'ssl_ca': 'ssl/server-ca.pem',
                        'ssl_cert': 'ssl/client-cert.pem',
                        'ssl_key': 'ssl/client-key.pem'
                        }
        self.connectToDB("pacdata")

    def createDB(self, dbname):
        self.cnxn = mysql.connector.connect(**self.config)
        self.cursor = self.cnxn.cursor()
        self.cursor.execute("CREATE DATABASE %s"% dbname)
        self.cnxn.close()

    def connectToDB(self, dbname):
        self.config['database'] = dbname  # add new database to config dict
        self.cnxn = mysql.connector.connect(**self.config)
        self.cursor = self.cnxn.cursor()
    
    def loadDB(self):
        # Create the candidates table from cn.txt
        # query = "CREATE TABLE candidates (CAND_ID varchar(9) not null PRIMARY KEY,CAND_NAME varchar(200),CAND_PTY_AFFILIATION varchar(3),CAND_ELECTION_YR DOUBLE,CAND_OFFICE_ST varchar(2),CAND_OFFICE varchar(1),CAND_OFFICE_DISTRICT varchar(2),CAND_ICI varchar(1),CAND_STATUS varchar(1),CAND_PCC varchar(9),CAND_ST1 varchar(34),CAND_ST2 varchar(34),CAND_CITY varchar(30),CAND_ST varchar(2),CAND_ZIP varchar(9));" 
        # self.execute("exec", "DROP TABLE IF EXISTS `candidates`;")
        # self.execute("exec", query)

        # # Populate the candidates table
        # query = "INSERT INTO candidates (CAND_ID, CAND_NAME, CAND_PTY_AFFILIATION, CAND_ELECTION_YR, CAND_OFFICE_ST, CAND_OFFICE, CAND_OFFICE_DISTRICT, CAND_ICI, CAND_STATUS, CAND_PCC, CAND_ST1, CAND_ST2, CAND_CITY, CAND_ST, CAND_ZIP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        # self.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/cn.txt", query)

        # Create the individual expenditures table from itpas2.txt
        query = "CREATE TABLE individualexpenditures (CMTE_ID varchar(9) not null primary key,AMNDT_IND varchar(1),RPT_TP varchar(3),TRANSACTION_PGI varchar(5),IMAGE_NUM varchar(18),TRANSACTION_TP varchar(3),ENTITY_TP varchar(3),NAME varchar(200),CITY varchar(30),STATE varchar(2),ZIP_CODE varchar(9),EMPLOYER varchar(38),OCCUPATION varchar(38),TRANSACTION_DT varchar(8),TRANSACTION_AMT DOUBLE,OTHER_ID varchar(9),CAND_ID varchar(9),TRAN_ID varchar(32),FILE_NUM DOUBLE,MEMO_CD varchar(1),MEMO_TEXT varchar(100),SUB_ID DOUBLE);"
        self.execute("exec", 'DROP TABLE IF EXISTS `individualexpenditures`;')
        self.execute("exec", query)

        # Populate the individual expenditures table
        query = "INSERT INTO individualexpenditures (CMTE_ID, AMNDT_IND, RPT_TP, TRANSACTION_PGI, IMAGE_NUM, TRANSACTION_TP, ENTITY_TP, NAME, CITY, STATE, ZIP_CODE, EMPLOYER, OCCUPATION, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID, CAND_ID, TRAN_ID, FILE_NUM, MEMO_CD, MEMO_TEXT, SUB_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        db.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/itpas2.txt", query)
        print("itpas2")

        # query = "ALTER TABLE individualexpenditures add CONSTRAINT fk_CMTE_ID foreign key (CMTE_ID) references pacsummary(CMTE_ID);"
        # self.execute("exec", 'ALTER TABLE individualexpenditures add CONSTRAINT fk_CAND_ID foreign key (CAND_ID) references candidates(CAND_ID);')
        # self.execute("exec", query)

        # # Create the pac summary table from webk20.txt
        # query = "CREATE TABLE pacsummary (CMTE_ID varchar(9) not null PRIMARY KEY,CMTE_NM varchar(200),CMTE_TP varchar(1),CMTE_DSGN varchar(1),CMTE_FILING_FREQ varchar(1),TTL_RECEIPTS DOUBLE,TRANS_FROM_AFF DOUBLE,INDV_CONTRIB DOUBLE,OTHER_POL_CMTE_CONTRIB DOUBLE,CAND_CONTRIB DOUBLE,CAND_LOANS DOUBLE,TTL_LOANS_RECEIVED DOUBLE,TTL_DISB DOUBLE,TRANF_TO_AFF DOUBLE,INDV_REFUNDS DOUBLE,OTHER_POL_CMTE_REFUNDS DOUBLE,CAND_LOAN_REPAY DOUBLE,LOAN_REPAY DOUBLE,COH_BOP DOUBLE,COH_COP DOUBLE,DEBTS_OWED_BY DOUBLE,NONFED_TRANS_RECEIVED DOUBLE,CONTRIB_TO_OTHER_CMTE DOUBLE,IND_EXP DOUBLE,PTY_COORD_EXP DOUBLE,NONFED_SHARE_EXP DOUBLE,CVG_END_DT varchar(10));"
        # self.execute("exec", 'DROP TABLE IF EXISTS `pacsummary`;')
        # self.execute("exec", query)

        # # Populate the pac summary table
        # query = "INSERT INTO pacsummary (CMTE_ID, CMTE_NM, CMTE_TP, CMTE_DSGN, CMTE_FILING_FREQ, TTL_RECEIPTS, TRANS_FROM_AFF, INDV_CONTRIB, OTHER_POL_CMTE_CONTRIB, CAND_CONTRIB, CAND_LOANS, TTL_LOANS_RECEIVED, TTL_DISB, TRANF_TO_AFF, INDV_REFUNDS, OTHER_POL_CMTE_REFUNDS, CAND_LOAN_REPAY, LOAN_REPAY, COH_BOP, COH_COP, DEBTS_OWED_BY, NONFED_TRANS_RECEIVED, CONTRIB_TO_OTHER_CMTE, IND_EXP, PTY_COORD_EXP, NONFED_SHARE_EXP, CVG_END_DT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        # self.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/webk20.txt", query)
        # print("webk20")

        # Create the fips table from fips.txt
        # query = "CREATE TABLE fips (ID varchar(2) not null primary key, STATE_FULL_NAME varchar(40), STATE_ABBR varchar(2));"
        # self.execute("exec", 'DROP TABLE IF EXISTS `fips`;')
        # self.execute("exec", query)

        # # Populate the fips table
        # query = "INSERT INTO fips (ID, STATE_FULL_NAME, STATE_ABBR) VALUES (%s, %s, %s);"
        # self.parse_data("/Users/derekli/Desktop/School/HackRPI 2020/data/fips.txt", query)
        # print("fips")

    def parse_data(self, filename, query):
        data = []
        for line in open(filename, "r"):
            data.append([ele.strip("\n") if ele != "" else None for ele in line.split("|") ])
        for i in range(0, len(data), 7000):
            self.cursor.executemany(query, data[i:i+7000])
            self.cnxn.commit()

    def showTable(self, table, limit):
        print("%s:"% table)
        self.cursor.execute("SELECT * FROM %s LIMIT %s;"% (table, limit))
        out = self.cursor.fetchall()
        for row in out:
            print(row)

    def execute(self, type, query):
        self.cursor.execute(query)
        if type == "exec":
            self.cnxn.commit()
        if type == "select":
            out = self.cursor.fetchall()
            return out
            
    def close(self):
        self.cnxn.close()

import time

if __name__ == "__main__":
    db = DB()

    db.loadDB()

    query = 'select ie.CMTE_ID, c.ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total, ie.TRANSACTION_TP from (select cs.CAND_ID, f.ID from candidates cs, fips f where f.STATE_ABBR = cs.CAND_OFFICE_ST) c inner join individualexpenditures ie on ie.CAND_ID = c.CAND_ID group by ie.CMTE_ID, c.ID, ie.TRANSACTION_TP';
    exectype = 'select'
    query = "select * from individualexpenditures where CAND_ID is null limit 5;"
    start_time = time.time()
    # db.execute(exectype, query)
    print("--- %s seconds ---" % (time.time() - start_time))

    db.close()