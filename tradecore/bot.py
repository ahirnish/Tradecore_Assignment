import requests 
import json
import sys
import string, random

LIKE = 1
UNLIKE = 0

WORKING_EMAIL_ADDRESSES = ["vibhooti@planetganges.com", "parth@hiration.com", "ahirnish@gmail.com", "sonul@arista.com"]

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    """
    Generates a random string of interleaved lowercase ascii characters, uppercase ascii characters and numbers of given size.
    """
    return ''.join(random.choice(chars) for _ in range(size))

def content_string_generator(prefix="User"):
    """
    Generates a random string prefixed by given prefix string.
    """
    return prefix + "_" + random_string_generator()

def read_config_file( file_path ):
    """
    Reads config file containing integers for set up for bot.
    """
    number_of_users = 0
    max_posts_per_user = 0
    max_likes_per_user = 0
    try:
        file_obj = open(file_path, "r")
        line = file_obj.readline().strip().split(",")
        number_of_users = int(line[0])
        max_posts_per_user = int(line[1])
        max_likes_per_user = int(line[2])
    except FileNotFoundError:
        print("CONFIG_FILE: Please provide valid config file name.")
        sys.exit(1)
    except IndexError:
        print("CONFIG_FILE: Data is missing from config file. Please provide 3 integer values in comma-separated format for number of users, max posts per user and max likes per user resp.")
        sys.exit(1)
    else:
        file_obj.close()
        print("CONFIG_FILE: Users: {}, Max posts per user: {}, Max likes per user: {}".format(number_of_users, max_posts_per_user, max_likes_per_user))
        return(number_of_users, max_posts_per_user, max_likes_per_user)

def signup_users(no_of_users):
    """
    Sign up given no. of users by providing necessary details about each user and saving necessary client-side detail about each user in a dictionary.
    """
    url = "http://localhost:8000/api/auth/register/"
    headers = {"content-type": "application/json"}
    user_data_list = {}
    for i in range(no_of_users):
        first_name = content_string_generator(prefix="first_name")
        last_name = content_string_generator(prefix="last_name")
        username = content_string_generator(prefix="username")
        password = content_string_generator(prefix="password")
        email = random.choice(WORKING_EMAIL_ADDRESSES)
        payload = {"first_name": first_name, "last_name": last_name, "username": username, "password": password, "email": email}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e:
            if "Failed to establish a new connection" in e.args[0].__str__():
                print("Server not running. Please run Django server.")
            else:
                print(e)
            sys.exit(1)
        expected_status_code = 201
        if response.status_code != expected_status_code:
            print("SIGNUP: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
            print(response.text)
            sys.exit(1)
        user_dict = {}
        user_dict["username"] = response.json()["username"]
        user_dict["password"] = password
        user_dict["token"] = None
        user_data_list[response.json()["id"]] = user_dict
        print("SIGNUP_USERS: user id: {} with username: {} signed up".format(response.json()["id"], response.json()["username"]))
    print(user_data_list)
    return user_data_list

def login_users(user_data_list):
    """
    Logging in each user by providing username and password and saving JWT token from response for each user. 
    """
    url = "http://localhost:8000/api/auth/login/"
    headers = {"content-type": "application/json"}
    for user_data in user_data_list.values():
        payload = {"username": user_data["username"], "password": user_data["password"]}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e:
            if "Failed to establish a new connection" in e.args[0].__str__():
                print("Server not running. Please run Django server.")
            else:
                print(e)
            sys.exit(1)
        expected_status_code = 200
        if response.status_code != expected_status_code:
            print("LOGIN: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
            print(response.text)
            sys.exit(1)
        user_data["token"] = "Bearer " + response.json()["token"]
        print("LOGIN_USERS: username: {} logged in".format(user_data["username"]))
    print(user_data_list)

def logout_users(user_data_list):
    """
    Logging out each user.
    """
    url = "http://localhost:8000/api/auth/logout/"
    headers = {"content-type": "application/json", "Authorization": None}
    for user_data in user_data_list.values():
        headers["Authorization"] = user_data["token"]
        try:
            response = requests.get(url, headers=headers, allow_redirects=False)
        except requests.exceptions.RequestException as e:
            if "Failed to establish a new connection" in e.args[0].__str__():
                print("Server not running. Please run Django server.")
            else:
                print(e)
            sys.exit(1)
        expected_status_code = 302
        if response.status_code != expected_status_code:
            print("LOGOUT: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
            print(response.text)
            sys.exit(1)
        print("LOGOUT_USERS: username: {} logged out".format(user_data["username"]))

def write_post_users(user_data_list, max_posts_per_user):
    """
    Writing a random number(max: max_posts_per_user) of posts by each user.
    """
    url = "http://localhost:8000/api/post/"
    headers = {"content-type": "application/json", "Authorization": None}
    for user_data in user_data_list.values():
        posts_per_user = random.randint(0, max_posts_per_user)
        print("WRITE_POST: number of posts: {} for user: {}".format(posts_per_user, user_data["username"]))
        headers["Authorization"] = user_data["token"]
        for _ in range(posts_per_user):
            content = content_string_generator(prefix="post")
            payload = {"content": content}
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
            except requests.exceptions.RequestException as e:
                if "Failed to establish a new connection" in e.args[0].__str__():
                    print("Server not running. Please run Django server.")
                else:
                    print(e)
                sys.exit(1)
            expected_status_code = 201
            if response.status_code != expected_status_code:
                print("WRITE_POST: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
                print(response.text)
                sys.exit(1)
            print("WRITE_POST: post id:{} with content: {} created by user: {}".format(response.json()["id"],content, user_data["username"]))

def create_preference_for_post(post_id, user_data, pref_value=LIKE):
    """
    Creating LIKE or UNLIKE preference on a given post by a given user.
    """
    print("CREATE_PREFERENCE: preference: {} to be set for post_id: {} by user: {}".format(pref_value, post_id, user_data["username"]))
    url = "http://localhost:8000/api/preference/{}/".format(post_id)
    headers = {"content-type": "application/json", "Authorization": user_data["token"]}
    payload = {"pref_value": pref_value}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.RequestException as e:
        if "Failed to establish a new connection" in e.args[0].__str__():
            print("Server not running. Please run Django server.")
        else:
            print(e)
        sys.exit(1)
    expected_status_code = 201
    if response.status_code != expected_status_code:
        if response.status_code == 400:
            return response
        else:
            print("CREATE_PREFERENCE: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
            print(response.text)
            sys.exit(1)
    print("CREATE_PREFERENCE: preference: {} set for post_id: {} by user: {}".format(pref_value, post_id, user_data["username"]))
    return response

def no_of_posts_by_user(user_data):
    """
    Returns numbers of posts and detail of each post written by a given user.
    """
    url = "http://localhost:8000/api/post/all/{}/".format(user_data["username"])
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        if "Failed to establish a new connection" in e.args[0].__str__():
            print("Server not running. Please run Django server.")
        else:
            print(e)
        sys.exit(1)
    expected_status_code = 200
    if response.status_code != expected_status_code:
         print("GET_POSTS_BY_USER: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
         print(user_data)
         print(response.text)
         sys.exit(1)
    return (len(response.json()), response.json())

def no_of_posts_by_all_users(user_data_list):
    """
    Returns a dictionary containing number of posts written by each user.
    """
    users_with_posts = {}
    for(user_id, user_data) in user_data_list.items():
        no_of_posts, _ = no_of_posts_by_user(user_data)
        users_with_posts[user_id] = no_of_posts
    return users_with_posts

def find_current_user_id(users_with_posts, exclude_list_users_id):
    """
    Returns user id of user to  start liking/disliking activity based on pre-defined conditions.
    """
    current_user_id = None
    max_posts = -1
    for(user_id, no_of_posts) in users_with_posts.items():
        if no_of_posts > max_posts and user_id not in exclude_list_users_id:
            current_user_id = user_id
            max_posts = no_of_posts
    return current_user_id

def valid_posts_for_user(current_user_id, user_data_list):
    """
    Returns list of valid post id-s which can be liked/disliked by given user.
    """
    valid_post_ids = []
    for (user_id, user_data) in user_data_list.items():
        valid_user = False
        if user_id != current_user_id:
            _, posts_by_user = no_of_posts_by_user(user_data)
            for post in posts_by_user:
                if post["likes"] == 0:
                    valid_user = True
            if valid_user:
                for post in posts_by_user:
                    valid_post_ids.append(post["id"])
    return valid_post_ids

def liking_activity(user_data_list, max_likes_per_user):
    """
    Bot performing liking activity.
    """
    exclude_list_users_id = []
    users_with_posts = no_of_posts_by_all_users(user_data_list)
    while(1):
        current_user_id = find_current_user_id(users_with_posts, exclude_list_users_id)
        if not current_user_id:
            break
        print("BOT_LIKE_ACTIVITY: Current user is user_id: {} username: {}".format(current_user_id, user_data_list[current_user_id]["username"]))
        for _ in range(max_likes_per_user):
            valid_post_ids = valid_posts_for_user(current_user_id, user_data_list)
            print("BOT_LIKE_ACTIVITY: valid post ids:", valid_post_ids)
            if not valid_post_ids:
                break
            while(1):
                random_post_id = random.choice(valid_post_ids)
                response = create_preference_for_post(random_post_id, user_data_list[current_user_id])
                if response.status_code == 201:
                    break
        exclude_list_users_id.append(current_user_id)

def delete_users(user_data_list):
    """
    Delete users data and tearing down the data setup.
    """
    for (user_id, user_data) in user_data_list.items(): 
        url = "http://localhost:8000/api/user/{}/".format(user_id)
        headers = {"content-type": "application/json", "Authorization": user_data["token"]}
        try:
            response = requests.delete(url, headers=headers)
        except requests.exceptions.RequestException as e:
            if "Failed to establish a new connection" in e.args[0].__str__():
                print("Server not running. Please run Django server.")
            else:
                print(e)
            sys.exit(1)
        expected_status_code = 204
        if response.status_code != expected_status_code:
            print("DELETE_USER: Please check status code of response. Expected: {}, Obtained: {}".format(expected_status_code, response.status_code))
            print(user_data)
            print(response.text)
            sys.exit(1)
        print("DELETE_USER: username: {} deleted".format(user_data["username"]))
        
def main(config_file_path):
    number_of_users, max_posts_per_user, max_likes_per_user = read_config_file(config_file_path)
    user_data_list = signup_users(number_of_users)
    login_users(user_data_list)
    write_post_users(user_data_list, max_posts_per_user)
    liking_activity(user_data_list, max_likes_per_user)
    logout_users(user_data_list)
#    delete_users(user_data_list) # uncomment this line if you want data to be deleted after bot has finished.

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Too many arguments.")
        print("Usage: python bot.py <CONFIG_FILE_PATH>")
        sys.exit(1)
        
    if len(sys.argv) != 2:
        print("Usage: python bot.py <CONFIG_FILE_PATH>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    main(file_path)
