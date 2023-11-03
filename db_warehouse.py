from db_operations import DbOperation

def warehouse_dump(info_dict : dict, label : str, table_name : str) -> None:
    """
    Saves data to the warehouse
    """
    # query generation
    posted_on = info_dict['posted_on']
    category = info_dict['category']
    skills = info_dict['skills']
    country = info_dict['country']
    message = info_dict['message']
    hourly_from = info_dict['hourly_from']
    hourly_to = info_dict['hourly_to']
    budget = info_dict['budget']
    label = label # passed as arg

    table_name = table_name # passed as arg
    sql = f"""INSERT INTO {table_name}(posted_on, category, skills, country, message, hourly_from, hourly_to, budget, label) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    values = (posted_on, category, skills, country, message, hourly_from, hourly_to, budget, label)
    conn_info = {'database' : 'postgres', 'user' : 'postgres', 'password' : 'axiom123', 'host' : '0.0.0.0', 'port' : '5432'}

    # writing to db
    db_op = DbOperation()
    db_op.insert_data_db(sql=sql, conn_info=conn_info, values=values)

