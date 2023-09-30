import os
import requests
import json
import argparse
import glob
import math
from tqdm import tqdm

def login(username: str, api_key: str) -> None:
    print("Logging in...", end=" ")
    params = {
        'login': username,
        'api_key': api_key
    }
    response = requests.get(f"{base_url}/users.json", params=params)
    if response.status_code != 200:
        print(f"failed (status code: {response.status_code}).")
        print(response)
        exit(1)
    print("success!")

def get_largest_id(tag: str) -> int:
    files = glob.glob(f"images/{tag}/*/*_*.*", recursive=True)
    ids = [int(os.path.basename(f).split("_")[0]) for f in files]
    if len(ids) > 0:
        id_max = max(ids)
    else:
        id_max = 0
    return id_max

def download_image(tag: str, infos: dict, verbose: bool = True) -> None:
    if verbose: print("Reading image informations...", end=" ")
    try:
        id = infos['id']
        image_url = infos['file_url']
        extension = infos['file_ext']
        tags = infos['tag_string']
        rating = infos['rating']
    except KeyError:
        if verbose: print("ignored (wrong formatting).")
        return
    if verbose: print(f"trying to download image with id '{id}'...", end=" ")
    if extension in ["mp4"]:
        if verbose: print("ignored (video).")
        return
    image_response = requests.get(image_url)
    image_data = image_response.content
    path = f"images/{tag}/{rating}"
    imagepath = f"{path}/{id}_image.{extension}"
    tagspath = f"{path}/{id}_tags.txt"
    jsonpath = f"{path}/{id}_infos.json"
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(imagepath) and os.path.exists(tagspath) and os.path.exists(jsonpath):
        if verbose: print("ignored (already exists).")
        return
    with open(imagepath, "wb") as f:
        f.write(image_data)
    with open(tagspath, "w") as f:
        f.write("\n".join(tags.split(" ")))
    with open(jsonpath, "w") as f:
        json.dump(infos, f, indent=4)
    if verbose: print("done!")

def get_images_infos(base_url: str, tag: str, limit: int, skip_ids_below: int = 0) -> list[dict]:
    print("Requesting images infos...", end=" ")
    result = []
    max_items_per_page = 200
    page_limit = math.ceil(limit / max_items_per_page)
    for page in range(1, page_limit + 1):
        max_items_for_current_page = max_items_per_page
        if page == page_limit:
            max_items_for_current_page = limit - max_items_per_page * (page_limit - 1)
        # TODO: improve the following line using for example requests.get(..., params=params)
        # NOTE: requests.get() automatically encodes the parameters, which is not wanted since a lot of tags contain special characters
        images_url = f"{base_url}/posts.json?tags={tag}+id:>{skip_ids_below}+order:id&limit={max_items_for_current_page}&page={page}"
        response = requests.get(images_url)
        if response.status_code != 200:
            print(f"failed (status code: {response.status_code}).")
            continue
        items = response.json()
        if len(items) == 0:
            break
        result += items
    print(f"{len(result)} images found!")
    return result

if __name__ == "__main__":
    
    # Configuring the commands

    parser = argparse.ArgumentParser(description='Downloads images from danbooru')
    parser.add_argument('--username', type=str, help='username to login with', required=True)
    parser.add_argument('--api_key', type=str, help='api key to login with', required=True)
    parser.add_argument('--tag', type=str, help='tag to search for', required=True)
    parser.add_argument('--limit', type=int, help='maximum number of images to download', required=True)
    parser.add_argument('--test', action='store_true', help='use testbooru instead of danbooru', required=False)
    parser.add_argument('--ignore_existing', action='store_true', help='ignore existing images', required=False)
    
    # Setting the base URL

    url_danbooru = "https://danbooru.donmai.us"
    url_testbooru = "https://testbooru.donmai.us"
    base_url = url_danbooru if not parser.parse_args().test else url_testbooru
    
    # Connecting to the API
    
    login(parser.parse_args().username, parser.parse_args().api_key)
    
    # Requesting the images

    tag = parser.parse_args().tag
    
    if not parser.parse_args().ignore_existing:
        infos = get_images_infos(
            tag=tag,
            base_url=base_url,
            limit=parser.parse_args().limit,
            skip_ids_below=get_largest_id(tag)
        )
    else:
        infos = get_images_infos(
            tag=tag,
            base_url=base_url,
            limit=parser.parse_args().limit
        )

    # Downloading the images

    for info in tqdm(infos):
        download_image(tag, info, verbose=False)