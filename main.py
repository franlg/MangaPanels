import requests
from bs4 import BeautifulSoup
import cfscrape
import numpy as np
import cv2
from imutils import contours
from PIL import Image, ImageOps
import os
import time

# TEST


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


def process_image(image):

    # Probar si añadiendo el borde va mejor o no
    # De momento parece que no
    # border = 10
    # bordered = cv2.copyMakeBorder(image, border, border, border, border, cv2.BORDER_CONSTANT)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # ret, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ret, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV)
    # binary = cv2.erode(binary, kernel, iterations=2)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        hull = cv2.convexHull(contour)
        cv2.drawContours(gray, [hull], -1, 0, -1)


    ret, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, heirarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        cv2.drawContours(gray, [contour], -1, (0, 255, 0), 3)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    crop_contours_from_image(image, contours)


def crop_contours_from_image(image, contours):

    for i, c in enumerate(contours):
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        if w > 150 and h > 150:
            cropped = image[y: y + h, x: x + w]
            cv2.imwrite(f"images/pagina{n}_panel{i}.png", cropped)
        # if cv2.contourArea(contours[i]) > 20000:
        #     rect = cv2.boundingRect(c)
        #     x, y, w, h = rect
        #     cropped = image[y: y + h, x: x + w]
        #     cv2.imwrite(f"images/pagina{n}_panel{i}.png", cropped)


if __name__ == '__main__':

    web_url = 'https://onepiecechapters.com/chapters/268/one-piece-chapter-1033'
    file_name = web_url.split("/")[-1]
    images = scrape_web_for_images(web_url)
    n = 0
    kernel = np.ones((5, 5), np.float32) / 25

    for image in images:

        # skip cover and ad
        if n == 0 or n == 1:
            n = n + 1
            continue

        path = f'images/{file_name}-page-{n}.png'
        save_image_on_path(image, path)
        image = cv2.imread(path)
        process_image(image)

        n = n + 1
