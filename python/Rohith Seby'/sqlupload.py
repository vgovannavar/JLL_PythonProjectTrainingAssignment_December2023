from tqdm import tqdm
import pandas as pd
import sqlalchemy as sa


class SQL:
    def __init__(self, dbuser, dbpass, dbhost, database, conn=False):
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbhost = dbhost
        self.database = database
        self.connection_string = f"mssql+pyodbc://{self.dbuser}:{self.dbpass}@{self.dbhost}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
        self.engine = sa.create_engine(self.connection_string, fast_executemany=True)
        self.conn = self.engine.connect()

    def __repr__(self):
        return f"SQL CRUD Object for\nServer: {self.dbhost}\nDatabase: {self.database}"

    def read_query(self, query, save=None, path=None, chunksize=None):
        if chunksize == None:
            return pd.read_sql_query(sa.text(query), con=self.conn)
        else:
            dfs = pd.read_sql_query(sa.text(query), con=self.conn, chunksize=chunksize)
            frames = []
            [frames.append(df) for df in tqdm(dfs)]
            return pd.concat(frames)

    def execute_query(self, query):
        self.conn.execute(sa.text(query))
        self.conn.execute(sa.text("COMMIT;"))

    def upload_df(
        self,
        df,
        table,
        schema,
        dtype=None,
        if_exists="replace",
        chunksize=25000,
        step=100,
    ):
        df_len = len(df)

        if df_len == 0:
            print("Dataframe has no rows")
        else:
            end_index = None

            print(f"---> Uploading dataframe to table: {schema}.{table}")

            for start_index in tqdm(
                range(0, df_len, step), desc="Dataframe upload progress"
            ):
                end_index = (
                    df_len if start_index + step > df_len else start_index + step
                )

                if_exists = if_exists if start_index == 0 else "append"

                df.iloc[start_index:end_index].to_sql(
                    name=table,
                    schema=schema,
                    con=self.engine,
                    if_exists=if_exists,
                    dtype=dtype,
                    index=False,
                    chunksize=chunksize,
                )
