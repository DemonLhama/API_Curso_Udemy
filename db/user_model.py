from sql_alchemy import db


class UserTable(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40))
    password = db.Column(db.String(40))


    def __init__(self, login, password ):
        self.login = login
        self.password = password
        

    def json(self):
        return {
            "user_id": self.user_id,
            "login": self.login, 
        }
    
    
    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user:
            return user
        return None

    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None



    def save_user(self):
        db.session.add(self)
        db.session.commit()


    def delete_user(self):
        db.session.delete(self)
        db.session.commit()
