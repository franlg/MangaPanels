import requests
from bs4 import BeautifulSoup
import cfscrape
import numpy as np
import cv2
from imutils import contours
from PIL import Image, ImageOps

#TEST

scraper = cfscrape.create_scraper()
html_page = scraper.get('https://onepiecechapters.com/chapters/268/one-piece-chapter-1033')

soup = BeautifulSoup(html_page.content, 'html.parser')
images = soup.findAll('img', "fixed-ratio-content")
example = images[0]
n = 0
kernel = np.ones((5, 5), np.float32) / 25
for image in images:
    if n == 0 or n == 1:
        n = n + 1
        continue
    image_url = image.attrs['src']
    img_data = requests.get(image_url).content
    path = f'chapter_1033_{n}.png'
    with open(path, 'wb') as handler:
        handler.write(img_data)
        image = cv2.imread(path)

        im = Image.open(path)
        bordered = ImageOps.expand(im, border=5, fill=(0, 255, 255))
        bordered.save(path)

        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('output1', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # image = cv2.medianBlur(image, 1)
        # image = cv2.filter2D(image, -1, kernel)
        # _, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # blur = cv2.medianBlur(gray, 1)
        # image = cv2.filter2D(image, -1, kernel)
        ret, binary = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary = cv2.erode(binary,kernel,iterations = 2)
        # binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        # cv2.imshow('output2', binary)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # for contour in contours:
        #     if cv2.contourArea(contour) > 27000:
        #         cv2.drawContours(image, contour, -1, (0, 255, 0), 3)

        # cv2.imshow('output3', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        for i, c in enumerate(contours):
            if cv2.contourArea(contours[i]) > 27000:
                rect = cv2.boundingRect(c)
                x, y, w, h = rect
                # box = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cropped = image[y: y + h, x: x + w]
                # cv2.imshow("Show Boxes", cropped)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                cv2.imwrite(f"pagina{n}_panel{i}.png", cropped)

        # cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

    n = n + 1
