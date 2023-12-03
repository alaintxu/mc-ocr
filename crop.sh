#!/bin/bash

# @ToDo: Load all images from uncut folder or crate a nautilus script for vertical and another for horizontal images
# Load image
input_image='./base_brigada_enemigos.jpg'

# Get image width and height
image_width=$(identify -format "%w" $input_image)
image_height=$(identify -format "%h" $input_image)

card_width=744
card_height=1039

# Crop input image in multiple 750x1040 pixels images and name them base_brigada_enemigos_1x1.jpg, base_brigada_enemigos_1x2.jpg, etc.
h=0
while [ $h -lt $image_height ]
do
    w=0
    while [ $w -lt $image_width ]
    do
        output_file_name="base_brigada_enemigos_$(( $h / $card_height + 1 ))x$(( $w / $card_width + 1 )).jpg"
        convert $input_image -crop "$card_width"x$card_height+$w+$h $output_file_name
        # remove image if saller than 50kb
        if [ $(stat -c%s "$output_file_name") -lt 50000 ]; then
            rm $output_file_name
        fi
        w=$(( $w + $card_width ))
    done
    h=$(( $h + $card_height ))
done
