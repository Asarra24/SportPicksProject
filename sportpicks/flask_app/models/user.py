from flask_app.config.mysqlconnection import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash
from flask_app.models.pick import Pick

class User:
    db = "sportpicks"
    def __init__(self,data):
        self.id = data['id']
        self. first_name= data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.picks = []

    def fullName(self):
        return f'{self.first_name} {self.last_name}'
    
    @classmethod
    def save(cls,data):
        query = """
        INSERT INTO users(first_name,last_name,email,password) 
        VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s)
        ;"""
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def get_all(cls):
        query = """
        SELECT * FROM users
        ;"""
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for row in results:
            users.append( cls(row))
        return users
    
    @classmethod
    def get_by_id(cls,data):
        query = """
        SELECT * FROM users LEFT JOIN picks ON users.id = picks.user_id WHERE users.id = %(id)s
        ;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        this_user = cls(results[0])
        for i_picks in results:
            data = {
                'id' : i_picks['id'],
                'name': i_picks['name'],
                'number': i_picks['number'],
                'bet': i_picks['bet'],
                'record': i_picks['record'],
                'date' : i_picks['date'],
                'created_at': i_picks['created_at'],
                'updated_at': i_picks['updated_at'],
                'user_id': i_picks['user_id'],
            }
            this_user.picks.append(Pick(data))
        return (this_user)
    
    @classmethod
    def get_by_email(cls, data):
        query = """
        SELECT * FROM users WHERE email = %(email)s
        ;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(User.db).query_db(query,user)
        if len(results) >= 1:
            flash("Email already taken.","register")
            is_valid=False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid Email!","register")
            is_valid=False
        if len(user['first_name']) < 3:
            flash("First name must be at least 3 characters","register")
            is_valid= False
        if len(user['last_name']) < 3:
            flash("Last name must be at least 3 characters","register")
            is_valid= False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters","register")
            is_valid= False
        if user['password'] != user['confirm']:
            isValid = False
            flash("Passwords don't match","register")
        return is_valid