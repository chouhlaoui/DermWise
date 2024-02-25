from tkinter import *
import pandas as pd

chemin_fichier_excel = 'C:/Users/Chourouk/Desktop/AIdata.xlsx'

Products = pd.read_excel(chemin_fichier_excel, sheet_name='Produits')

routines={"Simple":['Cleanser','Traitement','Sunscreen'],
          "Moyen":['Eau micellaire','Cleanser','Tonic','Serum','Traitement','Créme hydratante','Sunscreen','Exfoliant'],
          "Compliqué":['Eau micellaire','Cleanser','Tonic','Traitement','Retinol','Serum','Créme hydratante','Eyecream','Lip Balm','Exfoliant','Masque']}

checked_responses = []
reponses = []
current_question = 0



def create_product_frame(txt, res):
    window.config(pady=50)
    product_frame = Frame(main_frame, bg='white')
    product_frame.pack(fill="both", expand=True)
    row_num = 2
    x = len(res)
    products_per_row = 2
    if x > 0:
        if x > 4:
            products_per_row = 4
        i=0
        for ind, row in res.iterrows():
            image_path = row['image_path']
            name = row['Nom']
            price = row['Prix']
            brand = row['Marque']

            image = PhotoImage(file=image_path).zoom(10).subsample(32)

            card = Label(
                product_frame,
                text=f"{name}\n{brand}\n{price} dt",
                image=image,
                compound='top',
                font=("Courier", 12),
                bg='white',
                fg='black',
                wraplength=200  
            )
            card.image = image  
            card.grid(row=row_num, column=i % products_per_row, padx=10, pady=10)

            if (i + 1) % products_per_row == 0:
                row_num += 1
            i+=1
        
    else:
        Label(product_frame, text=txt, bg='white').grid(row=0, column=0, columnspan=products_per_row)
questions = [
    ("Quel type de routine préférez-vous ?", ["Simple", "Moyen", "Compliqué"]),
    ("Quel est votre type de peau ?", ["Normale", "Sèche", "Mixte", "Grasse"]),
    ("À quel sous-type appartient votre peau ?", ["Normale", "Sensible", "Acnéique", "Atopique"]),
    ("Quels sont vos problèmes de peau majeurs ?", ["Aucun", "Acné", "Points noirs", "Pores dilatés", "Peau terne", "Tache brune", "Ride"]),
    ("Quels sont vos buts principaux pour cette routine ?", ["Aucun", "Moins d'imperfections", "Éclat", "Teint unifié", "Hydratation", "Moins de rides", "Peau plus lisse"]),
    ("Quel est votre âge ?", ["Moins de 30 ans", "Au-delà de 30 ans"]),
    ("Quel est votre budget pour les produits de soins ?", ["Moins de 80 dt", "Moins de 120 dt", "Moins de 200 dt", "Moins de 300 dt", "Peu importe"])
]

def filtering_prix(filtring3, budget):
    if not filtring3.empty :
     if budget != 0:
        result=pd.DataFrame([9999], columns=['Prix']) 
        i=0
        while (result['Prix'].sum() > budget*1.15 and i<70):
            role_sums = filtring3.groupby('Role')['Prix'].sum()
            filtered_products = []
            for role, role_sum in role_sums.items():
                role_products = filtring3[filtring3['Role'] == role]
                filtered_products.append(role_products.sample()) 
            result = pd.concat(filtered_products, ignore_index=True)
            i += 1
        if result['Prix'].sum() <= budget*1.15:
            return result
        else:
            return pd.DataFrame()  
     else:
        min_price_row = filtring3.loc[filtring3.groupby('Role')['Prix'].idxmin(), :]
        if not min_price_row.empty:
            return min_price_row

def filtering_peau(filtering2, type, sstype):
    type_p=filtering2['Type de peaux'].str.contains(type)
    tt_type=filtering2['Type de peaux'].str.contains('Tout type')
    sous_type=filtering2['Sous types'].str.contains(sstype)
    tt_sous_type=filtering2['Sous types'].str.contains('Tout type')
    filtering3 = filtering2.loc[type_p & sous_type, :]

    if filtering3.empty:
        filtering3 = filtering2.loc[tt_type & sous_type, :]

        if filtering3.empty:
            filtering3 = filtering2.loc[type_p & tt_sous_type, :]

    filtering3 = pd.concat([filtering3, filtering2.loc[tt_type & tt_sous_type, :]], ignore_index=True)
    return filtering3

def filtering_age(f,age):
  age_filter=f['Age'].str.contains(age)
  f1=f.loc[age_filter, :]
  if not f1.empty:
    return f1
  else:
    return f.loc[f['Age'].str.contains('Tout age'), :]

def filtering_bp(filtering1,L1, L2):
    any_prob=filtering1['Probleme majeure'].str.contains('')
    no_prob=filtering1['Probleme majeure'].str.contains('Rien')
    no_but=filtering1['But principal'].str.contains('Rien')
    any_but=filtering1['But principal'].str.contains('')
    problems=[]
    for p in L1:
        problems.append(filtering1['Probleme majeure'].str.contains(p))
    buts=[]
    for b in L2:
        buts.append(filtering1['But principal'].str.contains(b))
    filtering2 = pd.DataFrame()
    # se concentrer sur but et problem
    for p in problems:
        for b in buts:
            aux = filtering1.loc[p & b, :]
            if not aux.empty:
                filtering2 = pd.concat([filtering2, aux], ignore_index=True)

    if filtering2.empty:
        # se concentrer sur but
        for b in buts:
            aux = filtering1.loc[any_prob & b, :]
            if not aux.empty:
                filtering2 = pd.concat([filtering2, aux], ignore_index=True)


        if filtering2.empty:
          # se concentrer sur but et problem
          for p in problems:
            aux = filtering1.loc[p & any_but, :]
            if not aux.empty:
                filtering2 = pd.concat([filtering2, aux], ignore_index=True)

          if filtering2.empty:
            # se concentrer sur pas de but et pas de problem
            aux = filtering1.loc[no_prob & no_but, :]
            filtering2 = pd.concat([filtering2, aux], ignore_index=True)

            if filtering2.empty:
              # se concentrer sur pas de but et pas de problem
              aux = filtering1.loc[any_prob & any_but, :]
              filtering2 = pd.concat([filtering2, aux], ignore_index=True)

    return filtering2

def filtering_off_budget(responses):
    routine = routines.get(responses[0])

    mask = Products['Role'].isin(routine)
    filter_products = Products[mask]
    filter0 = filter_products['Sous types'].str.contains(responses[2])
    filter4 = filter_products['Sous types'].str.contains('Tout type')
    print(filter0)
    filter1 = filter_products['Type de peaux'].str.contains(responses[1])
    filter2 = filter_products['Type de peaux'].str.contains('Tout type')
    dataframe_filtre = filter_products[(filter0 | filter4) & (filter1 | filter2)]
    if (responses[len(responses)-1]!="Peu importe"):
        budget = float((responses[len(responses)-1].split())[2])
    else:
        budget=0
    
    X = filtering_prix(dataframe_filtre,budget)
    return X
    
def Traitement(responses):
    routine=routines.get(responses[0])

    if responses[5]=='Moins de 30 ans':
        age= 'Tout age'
    else:
        age='Plus 30'
    
    responses[3] = [elem.replace('Aucun','Rien') for elem in responses[3]]
    responses[4] = [elem.replace('Aucun','Rien') for elem in responses[4]]

    if (responses[len(responses)-1]!="Peu importe"):
        budget = float((responses[len(responses)-1].split())[2])
    else:
        budget=0
    
    t_peau=['Grasse','Mixte']
    if responses[0] == "Simple":
        if(responses[1] in t_peau):
            routine.append('Tonic')
        else:
            routine.append('Créme hydratante')
    
    result = pd.DataFrame()
    for r in routine:
        print(r)
        role = Products['Role'].str.contains(r)
        filtering1=Products[role]

        if(len(responses[3])==len(responses[4])==1 and responses[3][0]==responses[4][0]=='Rien'):
            print("1 er cas ")
            f1=filtering_peau(filtering1,responses[1],responses[2])
            f2=filtering_age(f1,age)
            result=pd.concat([result,f2], ignore_index=True)
        else:
            print("2 eme cas ")
            filtering2 = filtering_bp(filtering1,responses[3],responses[4])
            if len(filtering2) == 1:
                result = pd.concat([result, filtering2], ignore_index=True)
            else:
                filtering3=filtering_peau(filtering2,responses[1],responses[2])
                f4=filtering_age(filtering3,age)
                result = pd.concat([result, f4], ignore_index=True)
    
    Result_final = filtering_prix(result,budget)

    if(Result_final.empty):
        Result_final = filtering_off_budget(responses)

    return Result_final

def action(var):
    global current_question
    global checked_responses
    if current_question in [3, 4]:
        if len(checked_responses) == 0:
            checked_responses.append("Aucun")
        reponses.append(checked_responses)
        checked_responses = []
    else:
        reponses.append(str(var.get()))

   
    if current_question <len(questions)-1:
        for widget in frame.winfo_children():
            widget.destroy()
        current_question += 1
        update_question()
    else:
        for widget in main_frame.winfo_children():
            widget.destroy()
        print(reponses)
        X = Traitement(reponses)
        if(X.empty):
            res = 'On n\'a pas pu trouvé un match pour vous vu votre budget limité et selection limité des produits tunisiens pour test'
            create_product_frame(res,X)
        elif(X.shape[0]<len(routines.get(reponses[0]))):
            res = 'On n\'a pas pu trouvé tout le routine pour vous vu votre choix très spécifique, mais voila les produits disponibles sur le marché pour commencer votre routine'
            print(X)
            create_product_frame(res,X)
        else:
            res = 'Votre routine est :'
            print(X)
            create_product_frame(res,X)

def update_question():

    label_question.config(text=questions[current_question][0])
    var = StringVar()
    options = questions[current_question][1]

    var.set(options[0])
    if current_question in [3, 4]:
        for index, option_text in enumerate(options, start=1): 
            checkbutton_var = BooleanVar()
            checkbutton = Checkbutton(frame, text=option_text, variable=checkbutton_var,bg='#F0CDD3',font=("Courrier", 10))
            checkbutton.grid(row=index, column=0, columnspan=2, sticky=W, pady=5)

            checkbutton.configure(command=lambda option=option_text, var=checkbutton_var: add_response(option, var))

    else: 
        if current_question == 6:
            if reponses[0] == "Moyen":
                options = options[2:]
                var.set(options[0])
            elif reponses[0] == "Compliqué":
                options = options[3:]
                var.set(options[0])
        for index, option_text in enumerate(options, start=1):
            radiobutton = Radiobutton(frame, text=option_text, variable=var, value=option_text, bg='#F0CDD3',font=("Courrier", 10))
            radiobutton.grid(row=index, column=0, columnspan=2, sticky=W, pady=5)
    next_button = Button(frame, text="Suivant", command=lambda: action(var), bg='#D87883', fg='white',font=("Courrier", 13))
    next_button.grid(row=len(questions)+1, column=1, sticky=E, pady=15, padx=200)

def add_response(option, var):
    if var.get():
        checked_responses.append(option)
    else:
        checked_responses.remove(option)


window = Tk()

window.title("DermWise")
window.geometry("1200x670")
window.minsize(1300, 700)
window.maxsize(1300, 700)
window.config(background='#D87883')

main_frame = Frame(window, bg='#D87883')
main_frame.pack(fill="both", expand=True)

frame1 = Frame(main_frame, bg='#D87883', padx=20, pady=20)
frame1.pack()

label_title = Label(frame1, text="Bienvenue dans notre système expert Conseillé Beauté", font=("Courrier", 25), bg='#D87883', fg='white')
label_title.pack(pady=20)

label_description = Label(frame1, text="Pour que nous puissions vous aider, merci de répondre à ces questions", font=("Courrier", 18), bg='#D87883', fg='white', pady=10)
label_description.pack()

frame2 = Frame(main_frame, bg='#F0CDD3', padx=20, pady=20, highlightbackground="white", highlightcolor="white", highlightthickness=10, width=400)
frame2.pack(padx=200,fill='both')

label_question = Label(frame2, text=questions[current_question][0], font=("Courrier", 15), bg='#F0CDD3', fg='black')
label_question.pack()

frame = Frame(frame2, bg='#F0CDD3')
frame.pack(padx=70,pady=20, fill='both')

update_question()


window.mainloop()



