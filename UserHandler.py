import DAL

class UserHandler:
    def register(username, email, password):
        users = DAL.DAL.getUsers()
        for user in users:
            if(user.get('username') == username):
                print("Username already taken")
                return False
            if(user.get('email') == email):
                print("account already exists")
                return False
        return True
    def login(i, password):
        users = DAL.DAL.getUsers()
        for user in users:
            if user.get('username') == i or user.get('email') == i and user.get('password') == password:
                print(user.get('username'), ":", user.get('email'), ":", i)
                print(True)
                return user
            else:
                print(user.get('username'), ":", user.get('email'), ":", i)
                print(False)
        return {}