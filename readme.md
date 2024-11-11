# PyCuller: a lightweight script/application to cull raw images
PyCuller is a python script I designed to provide a graphical interface for culling images, with features design for speed and convenience in mind. Currently, there are options like Select, or Photomechanic, but I don't like paying, and I also don't need all of their features.

PyCuller is relatively simple and easy to run, provided you have some preliminary understanding of Python. I will explain the remaining dependencies with the assumption that you have Python installed.

# Packages to Install
> pip install opencv-python
> 
> pip install PyQt6
> 
> pip install pillow
> 
> pip install rawpy

# How to use PyCuller
*DISCLAIMER: I have only tested this on Sony camera's proprietary .ARW file format. If you are using another system, I assume it should work but would not be surprised if thumbnail decoding breaks.*

## General Use
1. Begin by getting the pathname to your raw folder (this works with external drives or direct read on cards)
2. Paste the complete path into the **path/to/raws** input box, and fill out the file extension for your RAW filesin **Raw Extension** input.
3. Click the **Generate Thumbnails from Raws** button. You should see an output in the output box that gives the directory of the rendered thumbnails.
4. Take the thumbnail directory and paste it into **/path/to/images** and click **Submit**. Then, click **Render Images**.
5. Now, images should show up on the right hand side [you can adjust their size by moving the slider and then clicking render again].
6. Use **Next Image, Previous Image, and Delete Iamge** to cull images quickly.

## Using computer vision
*Computer vision features are largely experimental, and will take a while to run on a large set of raws, however they can be useful*
1. Select the method of choice (I recommend FFT)
2. Set the threshold for blurry images, such that a higher number means stricter for what is blurry. I find that for thumbnails, a threshold between 0-15 works best.
3. Click **Identify Blurry Images**, and then **Get Blurry Images**, which will then render the flagged images in the image display
