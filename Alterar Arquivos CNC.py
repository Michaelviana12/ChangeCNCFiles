import os
import sys
import tkinter as tk
import tkinter as tkk
import customtkinter
import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox, Tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


# Verica pelo padrão pra encontrar recortes
def verificar_linha_recorte(linha_anterior, linha_atual, linha_proxima):
    if 'G01' in linha_atual or 'G02' in linha_atual or 'G03' in linha_atual:
        if 'M20' in linha_anterior:
            if 'G01' in linha_proxima or 'G02' in linha_proxima or 'G03' in linha_proxima or var_m5 in linha_proxima:
                if not 'F' in linha_atual:
                    return True

# Função para perguntar ao usuário se ele deseja continuar
def caixa_sim_nao(mensagem):
    global root
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    resposta = messagebox.askyesno("Velocidade de Recorte", mensagem)
    return resposta

def botao():
    valor_digitado = entrada_velocidade.get()
    valor_formatado = "F" + valor_digitado + ","
    print("botao clicado")
    print("valor digitado", valor_digitado)
    #app.destroy()
    # Abre arquivo novamente pra alterar as velocidades
    with open(filepath, 'r+') as file:
            content = file.readlines()
            for i in range(len(content)):
                if 'F1234,' in content[i]:
                    content[i] = content[i].replace('F1234,', valor_formatado)
            file.seek(0)
            file.writelines(content)
    sys.exit()
    

# Função pra perguntar e alterar a velocidade
def altera_velocidade():
    mensagem = "Deseja alterar a velocidade de recorte?"
    resposta = caixa_sim_nao("Este arquivo possuia recortes!\nDeseja alterar a velocidade de corte?\nSe não o padrão será definido em F1234,")
    if resposta:
        print("aqui vamos alterar os recortes")
        global app
        global entrada_velocidade
        
        app = ctk.CTk()
        app.geometry("200x100")
        app.attributes('-topmost', True)
        app.protocol("WM_DELETE_WINDOW", lambda: None)
        app.title("Alterar velocidade de recortes.")

        # Entrada da Largura
        entrada_velocidade = ctk.CTkEntry(master=app, 
                                placeholder_text="Velocidade", 
                                width=300, height=15)
        entrada_velocidade.pack(pady=15, padx=10)

        # Botao de alterar
        button_1 = customtkinter.CTkButton(master=app, 
                                   width=300, 
                                   height=15, 
                                   text="Alterar Velocidade",
                                   command=botao)
        button_1.pack(pady=10, padx=10)
        app.mainloop()
    else:
        print("foi escolhido nao")

var_m5 = "M5G0Z5"
var_comentario = "(GTP AI PY)"
var_velocidade = "F1234,"
#filepath = "D:\Google Drive\MICHAEL-PC\Visual Studio Code\Alterar Arquivos CNC\Arquivos pra Teste/02.cnc"

filepath = askopenfilename(filetypes=[('Arquivos CNC', '*.cnc')])


if filepath.endswith(".cnc") or filepath.endswith(".CNC"):
    # Se o arquivo selecionar for .cnc le a primeira linha do arquivo
    with open(filepath, 'r') as file:
        first_line = file.readline().strip()

    if first_line == 'G70':
        # Se a primeira linha for G70 realiza as alterações no arquivo
        with open(filepath, 'r') as file:
            content = file.readlines()

        # Remover as 5 primeiras linhas
        content = content[5:]

        # Substituir a linha que contém "T0" por "G21"
        for i in range(len(content)):
            if 'T0' in content[i]:
                content[i] = content[i].replace('T0', 'G21')

        # Substituir todas as linhas que contém "M21" por "var_m5"
        m21_count = 0
        for i in range(len(content)):
            if 'M21' in content[i]:
                content[i] = content[i].replace('M21', var_m5)
                m21_count += 1

        # Substituir a última linha que contém "var_m5" por "M21"
        for i in range(len(content)-1, -1, -1):
            if var_m5 in content[i]:
                content[i] = content[i].replace(var_m5, 'M21')
                break
        
        # Verificar todas as linhas que começam com "G01", "G02" ou "G03" e adiciona "var_velocidade" se necessário
        global f_added
        f_added = False
        f_count = 0
        
        for i in range(1, len(content)-1):

            linha_atual = content[i]
            linha_anterior = content[i-1]
            linha_proxima = content[i+1]

            if verificar_linha_recorte(linha_anterior, linha_atual, linha_proxima):
                f_count += 1
                content[i] = f"{content[i].strip()}{var_velocidade}\n"
                f_added = True


        # Mensagem pra aparecer de acordo com o resultado da verificação acima
        if f_added:
            #altera_velocidade()
            message = f'Este código possuia recortes\nPrecisou ser adicionado {f_count} {var_velocidade}\n\n' 
        else:
            message = 'Nenhum recorte encontrado no arquivo.\n\n'

        # Exibir quantidade de "M21" substituídos
        message += f'Foram substituídos {m21_count} M21 no arquivo.\n\n'

        # Adicionar a sequência na primeira linha do arquivo
        content.insert(0, f'{var_comentario}\n')

        # Escrever as alterações no arquivo temporário
        temp_filepath = os.path.join(os.path.dirname(filepath), 'temp.cnc')
        with open(temp_filepath, 'w') as file:
            file.writelines(content)

        # diretório original
        directory = os.path.dirname(filepath)

        # extrai o nome e extensão do arquivo original
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        #excluir arquivo original
        os.remove(filepath)

        # Renomear o arquivo temporário com o nome do arquivo original e salva
        os.rename(temp_filepath, filepath)      

        #Exibe as mensagens do que foi feito
        message +=(f'O Arquivo modificado foi: {filename}\n')

        if f_added == False:
            print("valor de de f_added", f_added)
            sys.exit()
        else:
            altera_velocidade()

    
    elif first_line == 'G21':
        showerror('Arquivo Já Modificado', 'O arquivo .CNC foi modificado manualmente anteriormente.')
    elif first_line == 'g21':
        showerror('Arquivo Já Modificado', 'O arquivo .CNC foi modificado manualmente anteriormente.')
    elif first_line == var_comentario:
        showerror('Arquivo Já Modificado', 'O arquivo .CNC já foi modificado usando AI + Python')
    else:
        showerror("Arquivo Indefinido", "O arquivo pode ter sido modificado com comentario diferente ou ele não é um arquivo .cnc valido pra máquina.\n\nAbra o arquivo e verifique manualmente!")
else:
    showerror("Arquivo Inválido", "Arquivo não selecionado ou não possui a extensão .cnc.")     

    