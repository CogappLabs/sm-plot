import os
import json
import requests

"""simple script to get all images from the Science Museum API and put them in input/images along with input/image_data.json"""

search_url = 'https://collection.sciencemuseumgroup.org.uk/search/image_license?page[number]='
zoom_path = 'https://zoom.sciencemuseumgroup.org.uk/iiif//s3-zooms/'
iiif_params = '/full/256,/0/default.jpg'

image_data = []
for i in range(10):
    print("getting page %s" % i)
    data_url = '%s%s' % (search_url, i)
    resp = requests.get(url=data_url, headers={'Accept': 'application/json'})

    data = resp.json()

    if resp.status_code != 200:
        print('BAD response %s' % data_url)
        continue

    if not 'data' in data:
        print('BAD data %s' % data)
        continue

    for d in data['data']:

        if 'zoom' in d['attributes']['multimedia'][0]['processed']:

            iiif = '%s%s' % (zoom_path, d['attributes']['multimedia'][0]['processed']['zoom']['location'])

            obj = {}
            obj['id'] = d['id']
            obj['name'] = d['attributes']['summary_title']
            obj['iiif'] = iiif

            image_data.append(obj)


print(image_data)

# Write out files
if not os.path.exists('../input'):
    os.makedirs('../input')

if not os.path.exists('../input/images'):
    os.makedirs('../input/images')

# build up a whole new array to allow for image errors
new_image_data = {}

for img in image_data:
    # don't download if already exists
    file_path = '../input/images/%s.jpg' % img['id']
    if os.path.isfile(file_path):
        new_image_data[img['id']] = { 'name' : img['name'], 'iiif' : img['iiif'] }
    else:
        img_url = '%s%s' % (img['iiif'], iiif_params)
        print(img_url)
        r = requests.get(url=img_url, stream=True)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            new_image_data[img['id']] = {'name': img['name'], 'iiif': img['iiif']}
        else:
            print('BAD image %s' % img['id'])

with open('../input/image_data.json', 'w') as outfile:
    json.dump(new_image_data, outfile)

