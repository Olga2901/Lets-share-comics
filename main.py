from dotenv import load_dotenv
import requests
import os
from random import randint


def get_random_url_xkcd():
    randon_num = randint(1, 2719)
    xkcd_url = f"https://xkcd.com/{randon_num}/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    response = response.json()
    comic_url_response = requests.get(response["img"])
    comic_url_response.raise_for_status()
    with open("image.png", 'wb') as file:
        file.write(comic_url_response.content)
    return response["alt"]


def get_address_for_upload_img(access_token, group_id, user_id):
    photos_wall_url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": access_token,
        "v": "5.131",
        "user_id": user_id,
        "group_id": group_id,
    }
    response = requests.get(photos_wall_url, params=params)
    response.raise_for_status()
    return response.json()["response"]["upload_url"]


def upload_img_to_server(upload_url):
    with open("image.png","rb") as img_path:
        files = {"photo": img_path}
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    upload_url_response = response.json()
    return upload_url_response["server"], upload_url_response["photo"], upload_url_response["hash"] 


def save_img_to_vk(access_token, user_id, group_id, server, photo_url, hash):
    photos_save_url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": access_token,
        "v": "5.131",
        "user_id": user_id,
        "group_id": group_id,
        "photo": photo_url,
        "server": server,
        "hash": hash,
    }
    response = requests.post(photos_save_url, params=params)
    response.raise_for_status()
    save_photos_response = response.json()    
    return save_photos_response["response"][0]["owner_id"], save_photos_response["response"][0]["id"]


def make_wall_post_vk(access_token, group_id, owner_id, photo_id, comic_commentary):
    wall_post_url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": access_token,
        "v": "5.131",
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": comic_commentary, 
        "attachments": f"photo{owner_id}_{photo_id}",
    }
    response = requests.post(wall_post_url, params=params)
    return response.raise_for_status()
    

if __name__ == "__main__":
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    user_id = os.getenv("USER_ID")
    group_id = os.getenv("GROUP_ID")
    get_random_url_xkcd()
    comic_commentary = get_random_url_xkcd()
    get_address_for_upload_img(access_token, group_id, user_id)
    upload_url = get_address_for_upload_img(access_token, group_id, user_id)
    upload_img_to_server(upload_url)
    server, photo_url, hash = upload_img_to_server(upload_url)
    save_img_to_vk(access_token, user_id, group_id, server, photo_url, hash)
    owner_id, photo_id = save_img_to_vk(access_token, user_id, group_id, server, photo_url, hash)
    make_wall_post_vk(access_token, group_id, owner_id, photo_id, comic_commentary)
    os.remove("image.png")