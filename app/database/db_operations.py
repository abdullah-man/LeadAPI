import psycopg2
import pickle

class DbOperation:
    """
    Contains methods for performing operations on the database : data insertion, data fetching
    """

    def insert_data_db(self, conn_info : dict, sql : str, values : tuple) -> None:
        """
        Inserts a record into the database
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

            # query the db - inserting record
            cursor.execute(sql, values)

            conn.commit() # to persist/permanently saving record into table
            cursor.close()

        except (Exception, psycopg2.DatabaseError) as e:
            print(e)

        finally:
            if conn is not None:
                conn.close()
        return None


    def fetch_data(self, conn_info : dict, sql : str) -> list:
        """
        Fetches data of leads from the database and returns it
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

            # query the db - fetching record
            cursor.execute(sql)
            records = cursor.fetchall()
            
            cursor.close()
            if conn is not None:
                conn.close()

            return records
        
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)   
        

    def save_model(self, conn_info : dict, sql : str, values : tuple) -> None:
        """
        Saves a trained ML Model into database 
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

            # query the db - inserting the model
            cursor.execute(sql, values)
            conn.commit() # permanently saving record into table
            cursor.close()

        except (Exception, psycopg2.DatabaseError) as e:
            print(e)

        finally:
            if conn is not None:
                conn.close()
        
        return None

    
    def fetch_model(self, conn_info : dict, sql : str, value : tuple) -> object:
        """
        Fetches a trained ML Model from database 
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

            # query the db - fetching model
            cursor.execute(sql, value)
            model_file = cursor.fetchone()[0]
            
            # # Deserializing the fetched model file
            # model = pickle.load(open(model_file, 'rb'))

            cursor.close()
            if conn is not None:
                conn.close()
            
            # return model
            return model_file

        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
        
        
    def delete_model(self, conn_info : dict, sql : str, value : tuple) -> object:
        """
        Deletes a record of ML Model from database 
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

        
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
        
    
    def update_model(self, conn_info : dict, sql : str, value : tuple) -> object:
        """
        Update a record of ML Model from database 
        """
        conn = None
        try: 
            # connect to the existing db
            conn = psycopg2.connect(
                database = conn_info['database'],
                user = conn_info['user'],
                password = conn_info['password'],
                host = conn_info['host'],
                port = conn_info['port']
            )

            # open cursor to perform db operations
            cursor = conn.cursor()

        
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)




# sql = "INSERT INTO models (id, name, model) VALUES (%s, %s, %s)"
# values = (1, 'iris-classifier', model_bytes)

# model_fetch = "SELECT model FROM models WHERE name = %s", ('iris-classifier',)