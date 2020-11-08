

create table individualexpenditures (
    CMTE_ID varchar2(9) not null,
    AMNDT_IND varchar2(1),
    RPT_TP varchar2(3),
    TRANSACTION_PGI varchar2(5),
    IMAGE_NUM varchar2(18),
    TRANSACTION_TP varchar2(3),
    ENTITY_TP varchar2(3),
    NAME varchar2(200),
    CITY varchar2(30),
    STATE varchar2(2),
    ZIP_CODE varchar2(9),
    EMPLOYER varchar2(38),
    OCCUPATION varchar2(38),
    TRANSACTION_DT date,
    TRANSACTION_AMT	number(14,2),
    OTHER_ID varchar2(9),
    CAND_ID varchar2(9),
    TRAN_ID varchar2(32),
    FILE_NUM number(22),
    MEMO_CD varchar2(1),
    MEMO_TEXT varchar2(100),
    SUB_ID number(19)
)



create table candidates(
    CAND_ID varchar2(9) not null,
    CAND_NAME varchar2(200),
    CAND_PTY_AFFILATION varchar2(3),
    CAND_ELECTION_YR number(4),
    CAND_OFFICE_ST varchar2(2),
    CAND_OFFICE varchar2(1),
    CAND_OFFICE_DISTRICT varchar2(2),
    CAND_ICI varchar2(1),
    CAND_STATUS varchar2(1),
    CAND_PCC varchar2(9),
    CAND_ST1 varchar2(34),
    CAND_ST2 varchar2(34),
    CAND_CITY varchar2(30),
    CAND_ST varchar2(2),
    CAND_ZIP varchar2(9)
)

-- {
--   "payer": [
--     {"name": string, "id": string, "total_expenditure": number},
--     ...
--   ],
--   "payee": [
--     {"name": string, "id": string or number(fips for national), "total_expenditure": number},
--     ...
--   ],
--   "links": [
--     {"payer": pac_id, "payee": (fips for national), "expenditure": number, "type": "support" | "oppose"},
--     ...
--   ]
-- }

with c as 
    (select c.CAND_NAME, f.ID from candidates c inner join fips f on f.STATE_ABBR = c.CAND_OFFICE_ST)
select
    ie.CMTE_ID,
    f.ID,
    sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total,
    ie.TRANSACTION_TP
from
    individualexpenditures ie,
    c
on
    ie.CAND_ID = c.CAND_ID
group by
    c.CAND_NAME,
    f.ID,
    ie.TRANSACTION_TP;

select ie.CMTE_ID, f.ID, sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total, ie.TRANSACTION_TP from individualexpenditures ie inner join (select c.CAND_NAME, f.ID from candidates c inner join fips f on f.STATE_ABBR = c.CAND_OFFICE_ST) on ie.CAND_ID = c.CAND_ID group by c.CAND_NAME, f.ID, ie.TRANSACTION_TP;



select
    ps.CMTE_NM,
    ie.CMTE_ID,
    sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total
from
    individualexpenditures ie,
    pacsummary ps
where
    ps.CMTE_ID = ie.CMTE_ID
group by
    ps.CMTE_NM,
    ie.CMTE_ID
order by 
    total desc;

select
    c.CAND_NAME,
    f.ID,
    sum(CAST(ie.TRANSACTION_AMT as DECIMAL(14,2))) as total
from
    individualexpenditures ie,
    candidates c,
    fips f
where
    c.CAND_ID = ie.CAND_ID and
    f.STATE_ABBR = c.CAND_OFFICE_ST
group by
    c.CAND_NAME,
    f.ID;
