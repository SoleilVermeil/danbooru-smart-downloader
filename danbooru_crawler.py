import os
import requests
import json
import argparse
import glob
import math

def login(username: str, api_key: str) -> None:
    login_url = f"{base_url}/profile.json?login={parser.parse_args().username}&api_key={parser.parse_args().api_key}"
    response = requests.get(login_url)

def get_largest_id(tag: str) -> int:
    files = glob.glob(f"images/{tag}/*/*_infos.json", recursive=True)
    ids = [int(os.path.basename(f).split("_")[0]) for f in files]
    if len(ids) > 0:
        id_max = max(ids)
    else:
        id_max = 0
    return id_max


def download_image(tag: str, infos: dict) -> None:
    
    id = infos['id']
    image_url = infos['file_url']
    ext = infos['file_ext']
    tags = infos['tag_string']
    rating = infos['rating']
    
    if ext in ["mp4"]:
        print("ignored (video)")
        return
    
    # Save the image
    try:
        image_response = requests.get(image_url)
        image_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("failed")
        return

    image_data = image_response.content
    
    path = f"images/{tag}/{rating}"
    imagepath = f"{path}/{id}_image.{ext}"
    tagspath = f"{path}/{id}_tags.txt"
    jsonpath = f"{path}/{id}_infos.json"
    
    if not os.path.exists(path):
        os.makedirs(path)
            
    with open(imagepath, "wb") as f:
        f.write(image_data)
        
    with open(tagspath, "w") as f:
        f.write("\n".join(tags.split(" ")))
        
    with open(jsonpath, "w") as f:
        json.dump(image, f, indent=4)
    
    print("done")


def get_images_infos(tag: str, limit: int, id_max: int) -> list[dict]:
    
    result = []
    results_per_page_max = 200
    page_limit = math.ceil(limit / results_per_page_max)
    for page in range(1, page_limit + 1):
        results_per_page_current = results_per_page_max
        if page == page_limit:
            results_per_page_current = limit - results_per_page_max * (page_limit - 1)
        images_url = f"{base_url}/posts.json?tags={tag}+order:id+id:>{id_max}&limit={results_per_page_current}&page={page}"
        try:
            response = requests.get(images_url)
            response.raise_for_status()
            images_data = response.json()
            if not images_data:
                print("All images have been downloaded.")
                return
            result += images_data
        except requests.exceptions.RequestException as e:
            print(f"An error occured while trying to access {images_url}.")
            continue
    print("Done!")

if __name__ == "__main__":
    
    # Configuring the commands

    parser = argparse.ArgumentParser(description='Downloads images from danbooru')
    parser.add_argument('--username', type=str, help='username to login with', required=True)
    parser.add_argument('--apikey', type=str, help='api key to login with', required=True)
    parser.add_argument('--tag', type=str, help='tag to search for', required=True)
    parser.add_argument('--limit', type=int, help='maximum number of images to download', required=True)
    parser.add_argument('--test', action='store_true', help='use testbooru instead of danbooru', required=False)

    # Setting the base URL

    url_danbooru = "https://danbooru.donmai.us"
    url_testbooru = "https://testbooru.donmai.us"
    base_url = url_danbooru if not parser.parse_args().test else url_testbooru
    
    # Connect
    
    login(parser.parse_args().username, parser.parse_args().api_key)
    
    tag = parser.parse_args().tag
    
    get_image_infos