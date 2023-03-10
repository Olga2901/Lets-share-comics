from dotenv import load_dotenv
import requests
import os
from random import randint
import logging
from urllib.error import HTTPError


class VkApiError(Exception):
    pass
    
    
def check_for_error_in_response(response):
    response.raise_for_status()
    answer = response.json()
    if "error" in answer:
        raise VkApiError("Invalid access token")


def get_total_comics():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return int(response.json()["num"])


def download_random_comic(total_comics):
    randon_num = randint(1, total_comics)
    xkcd_url = f"https://xkcd.com/{randon_num}/info.0.json"
    response = requests.get(xkcd_url)
    response.raise_for_status()
    response = response.json()
    comic_url_response = requests.get(response["img"])
    comic_url_response.raise_for_status()
    with open("image.png", 'wb') as file:
        file.write(comic_url_response.content)
    return response["alt"]


def get_address_for_upload_img(vk_token, vk_group_id):
    photos_wall_url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": vk_token,
        "v": "5.131",
        "group_id": vk_group_id,
    }
    response = requests.get(photos_wall_url, params=params)
    response.raise_for_status()
    check_for_error_in_response(response)
    return response.json()["response"]["upload_url"]


def upload_img_to_server(upload_url):
    with open("image.png", "rb") as img_path:
        files = {"photo": img_path}
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    check_for_error_in_response(response)
    upload_url_response = response.json()
    return upload_url_response["server"], upload_url_response["photo"], upload_url_response["hash"] 


def save_img_to_vk(vk_token, vk_group_id, server, photo_url, img_hash):
    photos_save_url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": vk_token,
        "v": "5.131",
        "group_id": vk_group_id,
        "photo": photo_url,
        "server": server,
        "hash": img_hash,
    }
    response = requests.post(photos_save_url, params=params)
    response.raise_for_status()
    check_for_error_in_response(response)
    save_photos_response = response.json()    
    return save_photos_response["response"][0]["owner_id"], save_photos_response["response"][0]["id"]


def make_wall_post_vk(vk_token, vk_group_id, owner_id, photo_id, comic_commentary):
    wall_post_url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": vk_token,
        "v": "5.131",
        "owner_id": f"-{vk_group_id}",
        "from_group": 1,
        "message": comic_commentary, 
        "attachments": f"photo{owner_id}_{photo_id}",
    }
    response = requests.post(wall_post_url, params=params)
    response.raise_for_status()
    check_for_error_in_response(response)
    return response.json()["response"]["post_id"]
    

def main():
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")
    total_comics = get_total_comics()
    comic_commentary = download_random_comic(total_comics)
    try:
        upload_url = get_address_for_upload_img(vk_token, vk_group_id)
        server, photo_url, img_hash = upload_img_to_server(upload_url)
        owner_id, photo_id = save_img_to_vk(vk_token, vk_group_id, server, photo_url, img_hash)
        make_wall_post_vk(vk_token, vk_group_id, owner_id, photo_id, comic_commentary)
    except (VkApiError, HTTPError, ConnectionError) as err:
        logging.error(err, exc_info=True)
    finally:
        os.remove("image.png")


if __name__ == "__main__":
    main()
