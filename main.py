import flask
from flask import session
from flask_sqlalchemy import SQLAlchemy as SQL
from flask_sqlalchemy import SQLAlchemy as SQL


class _ValueError(ValueError):
    pass

def get_database(db):  
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.Text, nullable = False)
        password = db.Column(db.Text, nullable=False)
        login_history = db.Column(db.PickleType, nullable=False)

    return User

class Login:

    def __init__(
        self,
        app: flask.Flask,
        db:SQL = SQL(),
        KEY: bytes = None,
        database = None,
        default_level=0,
    ) -> None:
        self.app = app
        self.level = default_level
        self.key=1
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
        self.db = db
        if not database:
            self.database=get_database(db)


    def login(self, **values):
        x = self.database
        user = x.query.filter(**values)[0]
        #app=flask.current_app
        flask.session["user"] = user
        return user

    def sign_up(self, **values):
        user=self.database(**values)
        self.db.session.add(user)
        self.db.session.commit()
        return True
    

    def lock_page(self, index, value, refrence):
        try:
            user = flask.session.get("user")
            types = ["g", "l", "e", "ge", "le"]
            if refrence in types:
                ref = refrence
                if ref == "g":
                    return user.__dict__[index]>value
                if ref == "l":
                    return user.__dict__[index]<value
                if ref == "e":
                    return user.__dict__[index]==value
                if ref == "ge":
                    return user.__dict__[index]>=value
                if ref == "le":
                    return user.__dict__[index]<=value
                return False
            else:
                raise _ValueError(f"Refrerence {refrence} must be one of {types}")
        except _ValueError:
            raise
        except:
            return False
        
    def sign_out(self):
        try:
            u=session.pop("user")
            return u, True
        except:
            return False

    def delete_user(self) -> bool:
        try:
            user = flask.session.get("user")
            if not user:
                return False
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        except:
            return False
        
    def login_required(self):
        user = flask.session.get("user")
        if user:
            return True
        else:
            return False
