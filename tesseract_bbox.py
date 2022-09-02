from typing import NoReturn
import pytesseract
from pytesseract import Output
from PIL import Image,ImageTk

image = Image.open("Resume.png")
image_data =pytesseract.image_to_data(image,output_type=Output.DATAFRAME)#,output_type=Output.DICT)
columns = image_data.columns

arr = image_data.to_numpy()

x = 34.97164461247637
y =  8.933333333333334
width = 61.4366729678639
height = 7.733333333333331

def get_coordinates(org_width,org_height,x,y,width,height):
        l = int(x * org_width / 100)
        r = int((x + width) * org_width / 100)
        t = int(y * org_height /100)
        b = int((y + height) * org_height / 100)
        return l , r , t , b

def get_all_bboxes(image_data,l,t,r,b):
    bboxs = []


l,r,t,b = get_coordinates(image.width,image.height,x,y,width,height)

not_required = ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num','conf']
image_data = image_data.drop(not_required,axis=1)
image_data["right"] = image_data["left"]+image_data["width"]
image_data["bottom"] = image_data["top"]+image_data["height"]
print(image_data)
print(len(image_data.index))
image_data = image_data[image_data['text'].notna()]
print(len(image_data.index))

image_data = image_data.loc[image_data['left'] >= l]  
image_data = image_data.loc[image_data["top"]>=t]  
image_data = image_data.loc[image_data['right']<=r]
image_data = image_data.loc[image_data['bottom']<=b]


print(image_data)
print(len(image_data.index))

print(str(l)+" - "+str(t)+" - "+str(r)+" - "+str(b))