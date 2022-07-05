from selenium import webdriver
from app import User, BlogPost
driver = webdriver.Firefox()
import time

def get_user_and_list_blogs(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, None
    # get all blog ids
    blog_ids = [blog.id for blog in BlogPost.query.filter_by(user_id=user_id, is_deleted=False).all()]
    return user.id, blog_ids

def check_if_blog_present(user_id):
    user_id, blog_ids = get_user_and_list_blogs(user_id)
    # if either user or blog is not present, return False
    if not user_id or not blog_ids:
        return False
    login_url = 'http://localhost:5002/login'
    driver.get(login_url)

    # for blog_id in blog_ids , get id and if present , check if it is table
    login_username = driver.find_element('id', 'login_username')
    login_username.send_keys('sasidhar')
    login_password = driver.find_element('id', 'login_password')
    login_password.send_keys('AaBb@123!@#')
    login_button = driver.find_element('id', 'login_button')
    login_button.click()
    time.sleep(2)
    url = f'http://localhost:5002/listBlogs/{user_id}'
    driver.get(url)
    validation_list = []
    for blog_id in blog_ids:
        id = f'table_{blog_id}'
        if driver.find_element('id', id):
            validation_list.append(True)
        else:
            validation_list.append(False)
    
    return all(validation_list)

        
users = User.query.all()
for user in users:
    if check_if_blog_present(user.id):
        print(f'Testing successfull for user {user.id}')
        driver.quit()
    else:
        print(f'Testing failed for user {user.id}')
        driver.quit()