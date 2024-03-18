import flask
from flask import session
from cryptography.fernet import Fernet
import random as r
import pandas as pd
from datetime import datetime as dt

JSON = "JSON"

class _ValueError(ValueError):
    pass

class User:
    def __init__(self, id, username, password, history, session, pandas, **values) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.values = values
        self.login_history = history
        self.session_id = session
        self.pandas = pandas
        self.pd_df=pd.DataFrame(pandas)

class Login:

    def __init__(
        self,
        app: flask.Flask,
        db_ret: list,
        database: str = None,
        DBtype: str = None,
        KEY: bytes = None,
        default_level=0,
        login_function = None,
        sign_up_function = None,
    ) -> None:
        self.app = app
        self.dbFile = database
        self.db_type = DBtype
        self.db_ret = db_ret
        self.level = default_level
        self.key=1


        if KEY == None:
            self.KEY = Fernet.generate_key()
        else:
            self.KEY = KEY

        self.fernet = Fernet(self.KEY)

        try:
            self.load()
        except:
            pass

        self.db = pd.DataFrame()

        if self.db_type == JSON:
            import json
            with open(database, "r") as f:
                j=json.loads(f.read())
                for i in j:
                    self.sign_up(**i)

        self.sessions = {}

    def login(self, **values):
        x = self.db
        for i in self.db_ret:
            x = x.loc[x[i] == str(values[i])]
        x = x.iloc[0]
        
        session_id = f"{dt.now().strftime("%d.%m.%y %H:%M:%S")}-{flask.request.remote_addr}-{r.randint(0, 10000000)}"
        self.sessions[session_id] = x.iloc[2]
        flask.session["session-key"] = str(session_id)
        user = User(x.iloc[2], x.iloc[0], x.iloc[1], [], session_id, x)
        self.user = user
        return user

    def save(self):
        if self.db_type == JSON:
            js = str(self.db.to_json()).encode()

            d = self.fernet.encrypt(js)
            with open("login.db", "wb") as f:
                f.write(d)


    def load(self, fernet, database):
        
        with open("login.db", "rb") as f:
            print(self.fernet.decrypt(f.read()).decode())

    def sign_up(self, **values):
        self.key += 1
        values["uuid"]=self.key
        values["level"]=values.get("level", self.level)
        self.db=pd.concat([self.db, pd.DataFrame(values, index=[0])], ignore_index=True)
        self.db.reset_index()
        
        return True
    

    def lock_page(self, index, value, refrence):
        try:
            sess = flask.session.get("session-key")
            uuid = self.sessions.get(sess)



            user = self.db.loc[self.db["uuid"] == uuid].iloc[0]
            types = ["g", "l", "e", "ge", "le"]
            if refrence in types:
                ref = refrence
                if ref == "g":
                    return user[index]>value
                if ref == "l":
                    return user[index]<value
                if ref == "e":
                    return user[index]==value
                if ref == "ge":
                    return user[index]>=value
                if ref == "le":
                    return user[index]<=value
                return False
            else:
                raise _ValueError(f"Refrerence {refrence} must be one of {types}")
        except _ValueError:
            raise
        except:
            return False
        
    def sign_out(self):
        s=session.pop("session-key")
        self.sessions.pop(s)
