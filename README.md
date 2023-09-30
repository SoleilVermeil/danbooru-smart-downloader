# Danbooru Smart Downloader

The Danbooru Smart Downloader is a Python application that allows you to download images from Danbooru. Why is it smart?
1. It allows to download only certain images that match a specific tag.
2. Once an image is downloaded, it will not be downloaded again. Therefore, if you have a large collection of images you want to download, you can run the program multiple times and it will simply continue from there.
3. It stores the image, but also all the tags, and even all the available metadata, and stores everything in a comprehensive folder hierarchy.

## How to use

1. Install all dependencies: `pip install -r requirements.txt`.
2. Register on [Danbooru](https://danbooru.donmai.us/), go on your [profile](https://danbooru.donmai.us/profile) and generate an API key.
3. Run the script using `python danbooru_smart_downloader.py` and providing the needed arguments. For more infos, type `python danbooru_smart_downloader.py --help`.

All the images and corresponding informations are stored the following way:
```
images
|   <tag 1>
|   |   <id 1>_image.<jpg/png>
|   |   <id 1>_tags.txt
|   |   <id 1>_infos.json
|   |   ...
|   <tag 2>
|   |   ...
|   ...
```

## How it works

When using the application, it checks all the images you have already downloaded for the corresponding tag. It then looks for the image with the largest ID and only downloads images with an ID larger than that. Using the `--ignore_existing` flag, this behavior is disabled, and the app starts looking for all images again. This can be useful when you accidentally delete part of the data since it allows you to "fill the gaps".