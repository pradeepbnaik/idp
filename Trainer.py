#Import the required Libraries 
from datetime import datetime
from msilib.schema import Class
from tkinter import *
from tkinter import ttk 
from PIL import Image,ImageTk
import glob
import pytesseract
import json
import os

glob.crop_text = ""
glob.x_max,glob.x_min,glob.y_max,glob.y_min = NONE
glob.org_image_width = glob.org_image_height = NONE
glob.bbox = NONE
glob.current_doc =  "SLK_Resume"
extraction_template_path = r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Extraction Templates"
image_path = "Resume.png"

doc_template = {
      "template" : "template",
      "image": "path",
      "bbox": []
}



def read_image(image_path):
        image = Image.open(image_path)
        return image,image.width,image.height


def create_fields(window,taxonomy,doc_type,labels=NONE,entries=NONE,buttons=NONE):
        
        fields =  get_fields(taxonomy,doc_type)

        if(labels == NONE):
                labels = [None]*len(fields)
                entries = [None]*len(fields)
                buttons = [None]*len(fields)
        else:
                for i in range(len(labels)):
                #for label,entry,button in labels,entries,buttons:
                        labels[i].destroy()
                        entries[i].destroy()
                        buttons[i].destroy()
        

        for idx,field in enumerate(fields):
                labels[idx] =  Label(window, text = field["FieldName"],font=("Ariel", 15))
                labels[idx].grid(row = idx+1, column = 0, sticky = W,padx = 10, pady = 6)

                entries[idx] = Entry(window,font=("Ariel", 15))
                entries[idx].grid(row = idx+1, column = 1, sticky = W,padx = 10, pady = 6)

                buttons[idx] = Button(window,text = "Capture Field",font=("Ariel", 15), command= lambda field= [idx,field["FieldName"]]: capture(field))
                buttons[idx].grid(row = idx+1, column = 2, sticky = W,padx = 10, pady = 6)

        #window.update()
        return labels,entries,buttons    

        

with open("Taxonomy.json") as json_file:
        taxonomy = json.load(json_file)
        json_file.close()


def get_doc_types(taxonomy):
        doc_types = []

        for doc_type_taxonomy in taxonomy["DocumentTypes"]:
            doc_types.append(doc_type_taxonomy["DocumentType"])
        
        return doc_types


def get_fields(taxonomy,doc_type):
    field_array = None
    for Doc in taxonomy["DocumentTypes"]:
        if Doc["DocumentType"] == doc_type:
            field_array = Doc["Fields"]
    return field_array

def capture(field):
        field_template = {
          "x": 0,
          "y": 0,
          "width": 0,
          "height": 0,
          "label": "label_temp",
          "value":"value_temp",
          "original_width": 1700,
          "original_height": 2200
        }
        entries[field[0]].delete(0,END)
        entries[field[0]].insert(END,glob.crop_text)
        field_template["x"],field_template["y"],field_template["width"],field_template["height"] = glob.x_min,glob.y_min,glob.x_max-glob.x_min,glob.y_max-glob.y_min
        field_template["label"] = field[1]
        field_template["value"] = glob.crop_text
        field_template["original_width"] = glob.org_image_width
        field_template["original_height"] = glob.org_image_height
        glob.bbox[field[0]] = field_template
        print(field_template)

def submit():
        doc_template["image"] = str(image_path).split('\\')[-1:][0]
        doc_template["template"] = glob.current_doc 
        doc_template["bbox"] = glob.bbox
        print(doc_template)
        
        path = os.path.join(extraction_template_path,glob.current_doc+"_"+''.join(i for i in str(datetime.now()) if i.isdigit()))
        os.mkdir(path)

        with open(path+"\\Extraction Template.json", "w") as outfile:
                outfile.write(json.dumps(doc_template,indent=4))

        with open(path+"\\Taxonomy.json", "w") as outfile:
                outfile.write(json.dumps(taxonomy,indent=4))

        glob.org_img.save(path+"\\"+str(image_path).split('\\')[-1:][0])

        print("Submitted")


def get_coordinates(org_width,org_height,x,y,width,height):
    l = int(x * org_width / 100)
    r = int((x + width) * org_width / 100)
    t = int(y * org_height /100)
    b = int((y + height) * org_height / 100)

    return l , r , t , b

class FullScreenApp(object):
        def __init__(self, master, **kwargs):
            self.master=master
            pad=3
            self._geom='200x200+0+0'
            master.geometry("{0}x{1}+0+0".format(
                master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
            master.bind('<Escape>',self.toggle_geom)            
        def toggle_geom(self,event):
            geom=self.master.winfo_geometry()
            print(geom,self._geom)
            self.master.geometry(self._geom)
            self._geom=geom

def callbackFunc(event):
        glob.current_doc = event.widget.get()  

        create_fields(win,taxonomy,glob.current_doc,labels,entries,buttons)       
        print(glob.current_doc)
            


def on_button_press(event):
        # save mouse drag start position
        glob.start_x = xscrol.get()[0]*glob.resized_image_width+event.x
        glob.start_y = yscrol.get()[0]*glob.resized_image_height+event.y
        glob.rect = canvas.create_rectangle(glob.start_x, glob.start_y,glob.start_x, glob.start_y , outline="red")

def on_move_press(event):
        curX, curY = (xscrol.get()[0]*glob.resized_image_width+event.x, yscrol.get()[0]*glob.resized_image_height+event.y)
        canvas.coords(glob.rect,glob.start_x, glob.start_y, curX, curY)

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

        print(str(x_start)+" , "+str(y_start)+" , "+str(x_end)+" , "+str(y_end))
        canvas.coords(glob.rect , x_start , y_start , x_end , y_end)

        glob.x_min = x_start/glob.resized_image_width*100
        glob.y_min = y_start/glob.resized_image_height*100

        glob.x_max = x_end/glob.resized_image_width*100
        glob.y_max = y_end/glob.resized_image_height*100



        '''print(x_min)
        print(y_min)
        print(x_max)
        print(y_max)
        print()'''

        l,r,t,b = get_coordinates(glob.org_image_width,glob.org_image_height, glob.x_min,glob.y_min,glob.x_max-glob.x_min,glob.y_max-glob.y_min)

        print(str(l)+" , "+str(t)+" , "+str(r)+" , "+str(b))
        crop_img = glob.org_img.crop((l,t,r,b))
        crop_img.save("crop_"+str(l)+".jpg")

        glob.crop_text = str.strip(pytesseract.image_to_string(crop_img))
        print("Extracted Text : " + glob.crop_text)

        pass

#Create an instance of tkinter frame
win = Tk()
win.title('Annotation')
app=FullScreenApp(win)

win.grid_columnconfigure(2, weight=1)

Label(win, text = "Document Type",font=("Ariel",15)).grid(row=0,column=0,sticky = W,padx = 10, pady = 6)

country = ttk.Combobox(win, textvariable = StringVar() ,font=("Ariel", 15)) 
  
# Adding combobox drop down list 
country["values"] = get_doc_types(taxonomy)
#country['values'] = ("SLK_Resume","Invoices","Tax Form")
country.set(glob.current_doc)  
country.grid(column = 1, row = 0,sticky = W,padx = 10, pady = 6) 
country.current()
country.bind("<<ComboboxSelected>>", callbackFunc)

labels,entries,buttons = create_fields(win,taxonomy,glob.current_doc)
glob.bbox = [None]*len(labels) 

submit_btn = Button(win, text = "Submit", font=("Ariel", 15),command = submit) 
submit_btn.grid(row = 19, column = 1, sticky = E,padx = 10, pady = 10)

glob.org_img , glob.org_image_width , glob.org_image_height = read_image(image_path)


print("Org Dimension : "+str(glob.org_image_width)+" - "+str(glob.org_image_height))

glob.resized_image= glob.org_img.resize((int(glob.org_img.width/2),int(glob.org_img.height/2)), Image.ANTIALIAS)
glob.resized_image_width = glob.resized_image.width
glob.resized_image_height = glob.resized_image.height
glob.photo_image= ImageTk.PhotoImage(glob.resized_image)



#Create a canvas
canvas= Canvas(win,bg="yellow",scrollregion=(0, 0,glob.resized_image_width, glob.resized_image_height))
canvas.place(x=650, y=10, width=600, height=750)
#canvas.grid(row = 0, column = 1)
canvas.bind("<ButtonPress-1>", on_button_press)
canvas.bind("<B1-Motion>", on_move_press)
canvas.bind("<ButtonRelease-1>", on_button_release)

xscrol = Scrollbar(canvas, orient=HORIZONTAL)
xscrol.pack(side=BOTTOM, fill=X)
xscrol.config(command=canvas.xview)
canvas.config(xscrollcommand=xscrol.set)

yscrol = Scrollbar(canvas, orient=VERTICAL)
yscrol.pack(side=RIGHT, fill=Y)
yscrol.config(command=canvas.yview)
canvas.config(yscrollcommand=yscrol.set)

canvas.create_image(0,0, anchor=NW, image=glob.photo_image)


#print(win.winfo_children())

win.mainloop()
