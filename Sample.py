from tkinter import *
from PIL import Image,ImageTk
import glob
import pytesseract
from pytesseract import Output

glob.crop_text = ""
glob.x_max,glob.x_min,glob.y_max,glob.y_min = NONE
glob.org_image_width = glob.org_image_height = NONE
glob.bbox = NONE

glob.resized_image_width = glob.resized_image_height = 0
glob.img = glob.resized_image = NONE
image_path = "Resume.png"

def next_page():
        a=10
def prev_page():
        a=10

def get_word_bboxes():
        a=10
        image_data =pytesseract.image_to_data(glob.img,output_type=Output.DATAFRAME)#,output_type=Output.DICT)
        not_required = ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num','conf']
        image_data = image_data.drop(not_required,axis=1)
        #image_data["right"] = image_data["left"]+image_data["width"]
        #image_data["bottom"] = image_data["top"]+image_data["height"]

        #image_data[""]
        print(image_data)
        #print(len(image_data.index))
        image_data = image_data[image_data['text'].notna()]
        #print(len(image_data.index))

        image_data["left"] = image_data["left"] / glob.img.width * 100
        image_data["top"] = image_data["top"] / glob.img.height * 100
        image_data["width"] = image_data["width"] / glob.img.width * 100
        image_data["height"] = image_data["height"] / glob.img.height * 100

        '''image_data = image_data.loc[image_data['left'] >= l]  
        image_data = image_data.loc[image_data["top"]>=t]  
        image_data = image_data.loc[image_data['right']<=r]
        image_data = image_data.loc[image_data['bottom']<=b]'''

        return image_data


def get_coordinates(org_width,org_height,x,y,width,height):
    l = int(x * org_width / 100)
    r = int((x + width) * org_width / 100)
    t = int(y * org_height /100)
    b = int((y + height) * org_height / 100)

    return l , r , t , b

def draw_rectangel(image_data,canvas):

        for index, row in image_data.iterrows():
                l,r,t,b = get_coordinates(glob.resized_image_width,glob.resized_image_height,row["left"],row["top"],row["width"],row["height"])
                fill = Tk().winfo_rgb("red") + (int(0.5 * 255),)
                canvas.create_rectangle(l, t, r, b,outline="",fill=fill,activeoutline="red")



glob.x = glob.y = 0
glob.rect = None
glob.start_x = None
glob.start_y = None

def on_button_press(event):

        can.delete(glob.rect)
        # save mouse drag start position
        glob.start_x = xscrol.get()[0]*glob.resized_image_width+event.x
        glob.start_y = yscrol.get()[0]*glob.resized_image_height+event.y
        glob.rect = can.create_rectangle(glob.start_x, glob.start_y,glob.start_x, glob.start_y ,outline="red")

        '''print("x : "+str(xscrol.get()))
        print("y : "+str(yscrol.get()))'''

def on_move_press(event):
        curX, curY = (xscrol.get()[0]*glob.resized_image_width+event.x, yscrol.get()[0]*glob.resized_image_height+event.y)
        can.coords(glob.rect,glob.start_x, glob.start_y, curX, curY)

def on_button_release(event):

        x_start = glob.start_x
        x_end = xscrol.get()[0]*glob.resized_image_width+event.x
        y_start = glob.start_y
        y_end = yscrol.get()[0]*glob.resized_image_height+event.y

        if x_start > x_end :
                temp = x_start
                x_start = x_end
                x_end = temp
        
        if y_start > y_end :
                temp = y_start
                y_start = y_end
                y_end = temp

        
        if x_start < 0 :
                x_start = 0
                
        if y_start < 0 :
               y_start = 0

        if x_end > glob.resized_image_width :
                x_end = glob.resized_image_width

        if y_end > glob.resized_image_height :
                y_end = glob.resized_image_height 

        #print(str(x_start)+" , "+str(y_start)+" , "+str(x_end)+" , "+str(y_end))
        can.coords(glob.rect , x_start , y_start , x_end , y_end)

        glob.x_min = x_start/glob.resized_image_width*100
        glob.y_min = y_start/glob.resized_image_height*100

        glob.x_max = x_end/glob.resized_image_width*100
        glob.y_max = y_end/glob.resized_image_height*100

        print("x : "+str(glob.resized_image_width))
        print("y : "+str(glob.resized_image_height))

        print("x1 : "+str(xscrol.get()[0]*glob.org_image_width+x_start))

        print(glob.x_min)
        print(glob.y_min)
        print(glob.x_max)
        print(glob.y_max)
        print()

        l,r,t,b = get_coordinates(glob.org_image_width,glob.org_image_height, glob.x_min,glob.y_min,glob.x_max-glob.x_min,glob.y_max-glob.y_min)

        #print(str(l)+" , "+str(t)+" , "+str(r)+" , "+str(b))
        crop_img = glob.img.crop((l,t,r,b))
        crop_img.save("crop_"+str(l)+".jpg")

        glob.crop_text = str.strip(pytesseract.image_to_string(crop_img))
        print("Extracted Text : " + glob.crop_text)

        pass

def zoom_in():
        
        glob.resized_image= glob.img.resize((int(glob.resized_image_width*1.5),int(glob.resized_image_height*1.5)), Image.ANTIALIAS)
        glob.resized_image_width = glob.resized_image.width
        glob.resized_image_height = glob.resized_image.height
        glob.ph_img = ImageTk.PhotoImage(glob.resized_image)

        can.config(scrollregion=(0, 0,glob.resized_image.width, glob.resized_image.height))

        can.create_image(0 , 0 , anchor=NW , image=glob.ph_img)

def zoom_out():
        
        glob.resized_image= glob.img.resize((int(glob.resized_image_width/1.5),int(glob.resized_image_height/1.5)), Image.ANTIALIAS)
        glob.resized_image_width = glob.resized_image.width
        glob.resized_image_height = glob.resized_image.height
        glob.ph_img = ImageTk.PhotoImage(glob.resized_image)

        can.config(scrollregion=(0, 0,glob.resized_image.width, glob.resized_image.height))

        can.create_image(0 , 0 , anchor=NW , image=glob.ph_img)

root = Tk()
root.title("Canvas Tutorial")
root.geometry('900x600')


glob.img = Image.open(image_path)
glob.org_image_width = glob.img.width
glob.org_image_height = glob.img.height

glob.resized_image= glob.img.resize((int(glob.img.width*2),int(glob.img.height*2)), Image.ANTIALIAS)
glob.resized_image_width = glob.resized_image.width
glob.resized_image_height = glob.resized_image.height
glob.ph_img = ImageTk.PhotoImage(glob.resized_image)

lbl_can = Label (root, text="Canvas Tutorial", font=("Ariel", 20)).place(x=100, y = 10) 
can = Canvas(root, bg='yellow', scrollregion=(0, 0,glob.resized_image.width, glob.resized_image.height))
can.place(x=100, y=100, width=600, height=400)
can.bind("<ButtonPress-1>", on_button_press)
can.bind("<B1-Motion>", on_move_press)
can.bind("<ButtonRelease-1>", on_button_release)

xscrol = Scrollbar(can, orient=HORIZONTAL)
xscrol.pack(side=BOTTOM, fill=X)
xscrol.config(command=can.xview)
can.config(xscrollcommand=xscrol.set)

yscrol = Scrollbar(can, orient=VERTICAL)
yscrol.pack(side=RIGHT, fill=Y)
yscrol.config(command=can.yview)
can.config(yscrollcommand=yscrol.set)

can_img = can.create_image(0 , 0 , anchor=NW , image=glob.ph_img)

image_data = get_word_bboxes()
draw_rectangel(image_data,can)

'''button = Button(root, text = "Zoom In", command = zoom_in).pack()

button2 = Button(root, text = "<<", command = prev_page).pack()


lbl_page = Label (root, text="Page 1 of 2", font=("Ariel", 20)).pack()

button3 = Button(root, text = ">>", command = next_page).pack()


button4 = Button(root, text = "Zoom Out", command = zoom_out).pack()'''

root.mainloop()