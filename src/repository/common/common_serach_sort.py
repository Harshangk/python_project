from orm.common.common import (
    mstbranch,
    mstbroker,
    mstcity,
    mstmake,
    mstmodel,
    mstsource,
    mststate,
    mstyear,
    tblbank,
    tblinsurance_company,
)

MAKE_SEARCHABLE_COLUMNS = {
    "make": mstmake.c.make,
    "is_premium": mstmake.c.is_premium,
}

MAKE_SORTABLE_COLUMNS = {
    "id": mstmake.c.id,
    "make": mstmake.c.make,
    "is_premium": mstmake.c.is_premium,
}

MODEL_SEARCHABLE_COLUMNS = {
    "make_id": mstmodel.c.make_id,
    "model": mstmodel.c.model,
}

MODEL_SORTABLE_COLUMNS = {
    "id": mstmodel.c.id,
    "make_id": mstmodel.c.make_id,
    "model": mstmodel.c.model,
}

BRANCH_SEARCHABLE_COLUMNS = {
    "branch": mstbranch.c.branch,
}

BRANCH_SORTABLE_COLUMNS = {
    "id": mstbranch.c.id,
    "branch": mstbranch.c.branch,
}

SOURCE_SEARCHABLE_COLUMNS = {
    "source": mstsource.c.source,
}

SOURCE_SORTABLE_COLUMNS = {
    "id": mstsource.c.id,
    "source": mstsource.c.source,
}

YEAR_SEARCHABLE_COLUMNS = {
    "year": mstyear.c.year,
}

BROKER_SEARCHABLE_COLUMNS = {
    "broker": mstbroker.c.broker,
}

BROKER_SORTABLE_COLUMNS = {
    "id": mstbroker.c.id,
    "broker": mstbroker.c.broker,
}

STATE_SEARCHABLE_COLUMNS = {
    "state": mststate.c.state,
}

STATE_SORTABLE_COLUMNS = {
    "id": mststate.c.id,
    "state": mststate.c.state,
}

CITY_SEARCHABLE_COLUMNS = {
    "city_id": mstcity.c.state_id,
    "city": mstcity.c.city,
}

CITY_SORTABLE_COLUMNS = {
    "id": mstcity.c.id,
    "state_id": mstcity.c.state_id,
    "city": mstcity.c.city,
}

BANK_SEARCHABLE_COLUMNS = {
    "bank_name": tblbank.c.bank_name,
}

BANK_SORTABLE_COLUMNS = {
    "id": tblbank.c.id,
    "bank_name": tblbank.c.bank_name,
}

INSURANCE_COMPANY_SEARCHABLE_COLUMNS = {
    "insurance_company_name": tblinsurance_company.c.insurance_company_name,
}

INSURANCE_COMPANY_SORTABLE_COLUMNS = {
    "id": tblinsurance_company.c.id,
    "insurance_company_name": tblinsurance_company.c.insurance_company_name,
}
