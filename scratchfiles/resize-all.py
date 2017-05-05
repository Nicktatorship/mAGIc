import os, sys
from PIL import Image

target_type = 'jpg'
resize_method = 'auto'

input_dir = '/img/'
output_dir = '/imgout/'

for file in os.listdir(input_dir):
    multiplier = 1
    target_width = 450
    target_height = 200
    
    filename = file.split('.')[0].lower()
    filetype = file.split('.')[1].lower()

    is_image = (filetype == 'jpg' or filetype == 'jpeg' or filetype == 'png' or filetype == 'gif')

    if is_image:    
        if filename.rfind('resized') == -1:
            file_path = input_dir + file
            img = Image.open(file_path)

            file_width = img.size[0]
            file_height = img.size[1]

            if file_height > target_height:
                resize_method = 'height'
            else:
                resize_method = 'width'

            if resize_method == 'height' or (resize_method == 'auto' and file_height > target_height):
                # do this by height
                if file_height > target_height:
                    multiplier =  target_height / float(file_height)
                    target_width = int(file_width * multiplier)
            elif resize_method == 'width' or (resize_method == 'auto' and file_width > target_width):
                # do this by width
                if file_width > target_width:
                    multiplier = target_width / float(file_width)
                    target_height = int(file_height * multiplier)

            if multiplier != 1:
                if file_width > (target_width * 2) and file_height > (target_height * 2):
                    img = img.resize(((target_width * 2), (target_height * 2)))

                img = img.resize((target_width, target_height), Image.ANTIALIAS)
            target_file = output_dir + filename + '-resized' + '.' + target_type
            img.save(target_file, quality=90, subsampling=0, optimise=True, progressive=True)


