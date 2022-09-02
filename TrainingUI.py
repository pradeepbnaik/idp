#Import the required Libraries 
from datetime import datetime
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import pytesseract
import json
import os



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


class TrainerUI:

    def __init__(self,image_path,taxonomy_path):

        self.labels=self.entries=self.buttons =self.evidence_entry= NONE
        self.image_path = image_path
        self.taxonomy_path = taxonomy_path
        self.current_doc = "SLK_Resume"
        self.x = self.y = 0
        self.rect = None
        self.start_x = None
        self.start_y = None
        
        self.doc_template = {
            "template" : "template",
            "image": "path",
            "evidences" : [],
            "bbox": []
            }
        self.canvas_width = 600
        self.canvas_height = 750
        self.crop_text = ""
        self.bboxs = NONE
        self.extraction_template_path = r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Extraction Templates"

        self.window = Tk()
        self.window.title('Annotation')
        self.app=FullScreenApp(self.window)
        self.window.grid_columnconfigure(4, weight=1)

    def resize_factor(self,screen_size,pic_size):
        return screen_size/pic_size

    def read_image(self):
        self.org_image = Image.open(self.image_path)

    def resize_image(self):
        self.resized_image= self.org_image.resize((int(self.org_image.width/self.resize_factor(self.org_image.height,self.canvas_height)),
                                                    int(self.org_image.height/self.resize_factor(self.org_image.height,self.canvas_height))), Image.ANTIALIAS)
        self.resized_image_width = self.resized_image.width
        self.resized_image_height = self.resized_image.height
        self.photo_image= ImageTk.PhotoImage(self.resized_image)

        self.canvas_width = self.resized_image_width

    def get_coordinates(self,org_width,org_height,x,y,width,height):
        l = int(x * org_width / 100)
        r = int((x + width) * org_width / 100)
        t = int(y * org_height /100)
        b = int((y + height) * org_height / 100)
        return l , r , t , b

    def read_json(self,file_path):
        with open(file_path) as json_file:
            json_coontent = json.load(json_file)
            json_file.close()
        return json_coontent

    def get_doc_types(self,taxonomy):
        doc_types = []
        for doc_type_taxonomy in taxonomy["DocumentTypes"]:
            doc_types.append(doc_type_taxonomy["DocumentType"])
        
        return doc_types


    def get_fields(self,taxonomy,doc_type):   
        for Doc in taxonomy["DocumentTypes"]:
            if Doc["DocumentType"] == doc_type:
                field_array = Doc["Fields"]

        return field_array

        
    def create_fields(self):
        
        fields =  self.get_fields(self.taxonomy,self.current_doc)

        if(self.labels == NONE):
                self.labels = [None]*len(fields)
                self.entries = [None]*len(fields)
                self.buttons = [None]*len(fields)
        else:
                for i in range(len(self.labels)):
                        self.labels[i].destroy()
                        self.entries[i].destroy()
                        self.buttons[i].destroy()
        

        for idx,field in enumerate(fields):
                self.labels[idx] =  Label(self.window, text = field["FieldName"],font=("Ariel", 15))
                self.labels[idx].grid(row = idx+3, column = 0, sticky = W,padx = 10, pady = 6)

                self.entries[idx] = Entry(self.window,font=("Ariel", 15))
                self.entries[idx].grid(row = idx+3, column = 1, sticky = W,padx = 10, pady = 6)

                self.buttons[idx] = Button(self.window,text = "Capture Field",font=("Ariel", 15), command= lambda field= [idx,field["FieldName"]]: self.capture(field))
                self.buttons[idx].grid(row = idx+3, column = 2, sticky = W,padx = 10, pady = 6)

    def callbackFun(self,event):
        self.current_doc = event.widget.get()  
        self.create_fields()    
        print(self.current_doc)
    
    def capture(self,field):
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
        self.entries[field[0]].delete(0,END)
        self.entries[field[0]].insert(END,self.crop_text)
        field_template["x"],field_template["y"],field_template["width"],field_template["height"] = self.x_min,self.y_min,self.x_max-self.x_min,self.y_max-self.y_min
        field_template["label"] = field[1]
        field_template["value"] = self.crop_text
        field_template["original_width"] = self.org_image.width
        field_template["original_height"] = self.org_image.height
        self.bboxs[field[0]] = field_template
        print(field_template)
    
    def submit(self):
        self.doc_template["image"] = str(self.image_path).split('\\')[-1:][0]
        self.doc_template["template"] = self.current_doc 
        self.doc_template["bbox"] = self.bboxs
        print(self.doc_template)
        
        template_path = self.extraction_template_path+"\\"+self.current_doc
        if os.path.isdir(template_path) == False:
            os.mkdir(template_path)
        spcific_template_path = template_path+"\\"+self.current_doc+"_"+''.join(i for i in str(datetime.now()) if i.isdigit())
        os.mkdir(spcific_template_path)

        with open(spcific_template_path+"\\Extraction Template.json", "w") as outfile:
                outfile.write(json.dumps(self.doc_template,indent=4))

        with open(spcific_template_path+"\\Taxonomy.json", "w") as outfile:
                outfile.write(json.dumps(self.taxonomy,indent=4))

        self.org_image.save(spcific_template_path+"\\"+str(self.image_path).split('\\')[-1:][0])

        print("Submitted")



    def callbackFunc(self,event):
        self.current_doc = event.widget.get()  
        self.create_fields()       
        print(self.current_doc)
            


    def on_button_press(self,event):
            # save mouse drag start position
            self.start_x = self.xscrol.get()[0]*self.resized_image_width+event.x
            self.start_y = self.yscrol.get()[0]*self.resized_image_height+event.y
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y,self.start_x, self.start_y , outline="red")

    def on_move_press(self,event):
            curX, curY = (self.xscrol.get()[0]*self.resized_image_width+event.x, self.yscrol.get()[0]*self.resized_image_height+event.y)
            self.canvas.coords(self.rect,self.start_x, self.start_y, curX, curY)

    def on_button_release(self,event):

            x_start = self.start_x
            x_end = self.xscrol.get()[0]*self.resized_image_width+event.x
            y_start = self.start_y
            y_end = self.yscrol.get()[0]*self.resized_image_height+event.y

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

            if x_end > self.resized_image_width :
                    x_end = self.resized_image_width

            if y_end > self.resized_image_height :
                    y_end = self.resized_image_height 

            print(str(x_start)+" , "+str(y_start)+" , "+str(x_end)+" , "+str(y_end))
            self.canvas.coords(self.rect , x_start , y_start , x_end , y_end)

            self.x_min = x_start/self.resized_image_width*100
            self.y_min = y_start/self.resized_image_height*100

            self.x_max = x_end/self.resized_image_width*100
            self.y_max = y_end/self.resized_image_height*100



            '''print(x_min)
            print(y_min)
            print(x_max)
            print(y_max)
            print()'''

            l,r,t,b = self.get_coordinates(self.org_image.width,self.org_image.height, self.x_min,self.y_min,self.x_max-self.x_min,self.y_max-self.y_min)

            print(str(l)+" , "+str(t)+" , "+str(r)+" , "+str(b))
            crop_img = self.org_image.crop((l,t,r,b))
            #crop_img.save("crop_"+str(l)+".jpg")

            self.crop_text = str.strip(pytesseract.image_to_string(crop_img)).replace("\n"," ").replace("  "," ")
            print("Extracted Text : " + self.crop_text)

            pass

    def add_evidence(self):
        evidence_temp={
                "value" : "",
                "x":"0",
                "y":"0",
                "width":"0",
                "height":"0"
             }
        evidence_temp["value"] = self.crop_text
        evidence_temp["x"]= self.x_min
        evidence_temp["y"]=self.y_min
        evidence_temp["width"]=self.x_max-self.x_min
        evidence_temp["height"]=self.y_max-self.y_min

        self.doc_template["evidences"].append(evidence_temp)

        self.evidence_entry.insert(END,"\""+self.crop_text+"\" ")


    def clear_evidence(self):
        self.doc_template["evidences"] = []
        self.evidence_entry.delete(0, END)

    def create_main_ui(self):

        self.taxonomy = self.read_json(self.taxonomy_path)

        Label(self.window, text = "Document Type",font=("Ariel",15)).grid(row=0,column=0,sticky = W,padx = 10, pady = 6)

        country = ttk.Combobox(self.window, textvariable = StringVar() ,font=("Ariel", 15)) 
  
        # Adding combobox drop down list 
        country["values"] = self.get_doc_types(self.taxonomy)
        #country['values'] = ("SLK_Resume","Invoices","Tax Form")
        country.set(self.current_doc)  
        country.grid(column = 1, row = 0 , sticky = W , padx = 10 , pady = 6) 
        country.current()
        country.bind("<<ComboboxSelected>>", self.callbackFun)

        Label(self.window, text = "Evidence",font=("Ariel",15)).grid(row=1,column=0,sticky = W,padx = 10, pady = 6)
        self.evidence_entry = Entry(self.window,font=("Ariel", 15))
        self.evidence_entry.grid(row =1, column = 1, sticky = W,padx = 10, pady = 6)

        Button(self.window,text = "Add",font=("Ariel", 15), command= self.add_evidence).grid(row = 1, column = 2, sticky = W,padx = 10, pady = 6)
        Button(self.window,text = "Clear",font=("Ariel", 15), command= self.clear_evidence).grid(row = 1, column = 3, sticky = W,padx = 10, pady = 6)
        
        Label(self.window,text = "",font=("Ariel", 15)).grid(row = 2, column = 0, sticky = W,padx = 10, pady = 6)

        self.create_fields()
        self.bboxs = [None]*len(self.labels) 

        self.submit_btn = Button(self.window, text = "Submit", font=("Ariel", 15),command = self.submit) 
        self.submit_btn.grid(row = 19, column = 1, sticky = E,padx = 10, pady = 10)

        self.read_image()



        self.resize_image()

        #self.resized_image.save("pric.jpg")
    
        #Create a canvas
        self.canvas= Canvas(self.window,bg="yellow",scrollregion=(0, 0,self.resized_image_width, self.resized_image_height))
        self.canvas.place(x=760, y=10, width=self.canvas_width, height=self.canvas_height)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.xscrol = Scrollbar(self.canvas, orient=HORIZONTAL)
        self.xscrol.pack(side=BOTTOM, fill=X)
        self.xscrol.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.xscrol.set)

        self.yscrol = Scrollbar(self.canvas, orient=VERTICAL)
        self.yscrol.pack(side=RIGHT, fill=Y)
        self.yscrol.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.yscrol.set)

        self.canvas.create_image(0,0, anchor=NW, image=self.photo_image)

        self.window.mainloop()

app = TrainerUI(image_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Resume_3.jpg",
       taxonomy_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Taxonomy.json")
#app.current_doc = "Invoices"

app.create_main_ui()