import TrainingUI
import Extract
import ExtractionUI

#app = TrainingUI.TrainerUI(image_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Resume.png",
#       taxonomy_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Taxonomy.json")
#app.current_doc = "Invoices"

#app.create_main_ui()
#app.rect = app.canvas.create_rectangle(200, 600,400,800 , outline="green")

#extracted_dict = Extract.Extract().extract()
#print(extracted_dict)

#for dict in extracted_dict:
        #print(extracted_dict[dict])

app = ExtractionUI.ExtractorUI(image_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Resume.png",
                                     taxonomy_path=r"C:\Users\PRADEEP\Documents\Python Codes\SamlpeGUI\Taxonomy.json")
app.create_main_ui()

