#Import the required Libraries
import os
from tkinter import *
from PIL import Image
import pytesseract
import json

class Extract:
    def __init__(self,image_path,doc_type,extraction_template_path):
        self.bbox_dict = {}
        self.image_path = image_path
        self.read_image()
        self.extraction_template_path = extraction_template_path
        self.template = doc_type
        self.extraction_template = self.read_json(self.extraction_template_path)
        self.teamplate_dict = self.create_template_dict(self.extraction_template)

        pass

    def read_json(self,file_path):
        with open(file_path) as json_file:
            json_coontent = json.load(json_file)
            json_file.close()
        return json_coontent

    def read_image(self):
        self.image = Image.open(self.image_path)

    def create_template_dict(self,extraction_template) :

        for bbox in extraction_template["bbox"]:
            bbox_temp = {
                "x" : "",
                "y" : "",
                "width" : "",
                "height" : "",
                "value" : ""
            }
            bbox_temp["x"] = bbox["x"]
            bbox_temp["y"] = bbox["y"]
            bbox_temp["width"] = bbox["width"]
            bbox_temp["height"] = bbox["height"]
            self.bbox_dict[bbox["label"]] = bbox_temp

        return self.bbox_dict

    def get_coordinates(self,org_width,org_height,x,y,width,height):
        l = int(x * org_width / 100)
        r = int((x + width) * org_width / 100)
        t = int(y * org_height /100)
        b = int((y + height) * org_height / 100)

        return l , r , t , b

    def crop_and_extract(self,image,bbox):
        l,r,t,b = self.get_coordinates(self.image.width , self.image.height , bbox["x"] , bbox["y"] , bbox["width"] , bbox["height"])
        crop_img = image.crop((l,t,r,b))
        text = str.strip(pytesseract.image_to_string(crop_img))
        return text


    def extract_fields(self,image,template_dict):
        for template in template_dict:
            #print(template_dict[template])
            text = self.crop_and_extract(image,template_dict[template])
            self.teamplate_dict[template]["value"] = text
            #print(template_dict[template])
            #print(template+" : "+text)
        return self.teamplate_dict

    
    def extract(self):
        return self.extract_fields(self.image,self.teamplate_dict)


class ValidateTemplate:
    def __init__(self,image,doc_type:str,extraction_template_path:str):
        self.image = image
        self.doc_type = doc_type
        self.extraction_template_path = extraction_template_path

        self.templates_evidences =  self.read_templates(self.extraction_template_path,doc_type)
        self.template_confidences = self.get_template_confidences(self.templates_evidences,image)

        self.template = self.get_template(self.template_confidences)


    def read_json(self,file_path):
        with open(file_path) as json_file:
            json_coontent = json.load(json_file)
            json_file.close()
        return json_coontent

    def read_templates(self,extraction_template_path,doc_type):
        path = extraction_template_path+"\\"+doc_type
        templates = os.listdir(path)
        templates_evidences = []
        for template in templates:
            templates_evidences.append({"template":template,
                            "evidence":self.read_json(path+"\\"+template+"\\Extraction Template.json")["evidences"]})
        return templates_evidences

    def get_coordinates(self,image_width,image_height,x,y,width,height):
        l = int(x * image_width / 100)
        r = int((x + width) * image_width / 100)
        t = int(y * image_height /100)
        b = int((y + height) * image_height / 100)
        return l , r , t , b


    def compare_bbox_text(self,evidence):
        l,r,t,b = self.get_coordinates(self.image.width,self.image.height,evidence["x"],evidence["y"],evidence["width"],evidence["height"])
        crop_image = self.image.crop((l,t,r,b))
        crop_text = str.strip(pytesseract.image_to_string(crop_image)).replace("\n"," ").replace("  "," ")
        if(evidence["value"].upper() == crop_text.upper()):
            return 100
        else:
            return 10

    def get_template_confidences(self,templates_evidences,image):
        template_confidences = []
        for template in templates_evidences:
            confidences = []
            for evidence in template["evidence"]:
                confidences.append(self.compare_bbox_text(evidence))
            
            template_confidences.append({
                "template" : template["template"],
                "confidence" : sum(confidences)/(len(confidences)*100)
            })
        return template_confidences

    def get_template(self,template_confidences):
        max_conf = 0
        template = ""
        for template_confidence in template_confidences:
                if template_confidence["confidence"] > max_conf :
                    max_conf = template_confidence["confidence"]
                    template = template_confidence["template"]
        
        if max_conf > 0.65 :
            return template
        else:
            #return First Template
            return template_confidences[0]["template"]

    def identify_template(self):
        return self.template


vt = ValidateTemplate(Image.open("Resume_2.png"),"SLK_Resume",r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Extraction Templates")
temp = vt.identify_template()
print("Template :"+temp)