from db import db

def login(data):
    user_info = db.User.find_one({"userId": data.get("userId")})
    if user_info != None:
        user_info.pop('_id', None)
        return user_info
    else:
        create_new_user(data.get("userId"))
        create_new_level(data.get("userId"))
        new_user_info = db.User.find_one(data) 
        new_user_info.pop("_id", None)
        return new_user_info
def authenticate(userId):
    if db.User.find_one({"userId": userId}) != None:
        return True
    return False
def create_new_user(userId):
    new_user = {
    "userId": userId,
    }
    db.User.insert_one(new_user)
def create_new_level(userId):
    for c in ["classification", "ner"]:
        db.Level.insert_one({
            "userId": userId,
            "type": c,
            "level": 0,
            "levelPercentage": 10
        })
    return True