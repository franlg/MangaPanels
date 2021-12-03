import requests
from bs4 import BeautifulSoup
import cfscrape
import numpy as np
import cv2
from imutils import contours
from PIL import Image, ImageOps
import os
import time
import flask

# TEST


def main():
    web_url = 'https://onepiecechapters.com/chapters/268/one-piece-chapter-1033'
    file_name = web_url.split("/")[-1]
    images = scrape_web_for_images(web_url)
    n = 0
    for image_data in images:
        # skip cover and ad
        if n == 0 or n == 1:
            n = n + 1
            continue
        path = f'images/{file_name}-page-{n}'
        extension = '.png'
        save_image_on_path(image_data, path + extension)
        image = cv2.imread(path + extension)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        contours = get_panels_contours(blur)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        save_contour_from_image_on_path(contours, gray, path)
        n = n + 1


def scrape_web_for_images(web_url):
    scraper = cfscrape.create_scraper()
    html_page = scraper.get(web_url)
    soup = BeautifulSoup(html_page.content, 'html.parser')
    images = soup.findAll('img', "fixed-ratio-content")
    return images


def save_image_on_path(image, path):
    image_url = image.attrs['src']
    img_data = requests.get(image_url).content
    with open(path, 'wb') as handler:
        handler.write(img_data)


def show_image(image):
    cv2.imshow('output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_panels_contours(image):
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV)
    contours,_ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    draw_convex_hull_contours_on_image(contours, image)
    _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    contours,_ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours


def draw_convex_hull_contours_on_image(contours, image):
    for contour in contours:
        hull = cv2.convexHull(contour)
        cv2.drawContours(image, [hull], -1, 0, -1)


def save_contour_from_image_on_path(contours, image, path):
    for i, c in enumerate(contours):
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        if w > 150 and h > 150:
            cropped = image[y: y + h, x: x + w]
            cv2.imwrite(f"{path}-panel-{i}.png", cropped)


if __name__ == '__main__':
    main()
