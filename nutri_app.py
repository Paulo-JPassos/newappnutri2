import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import os

def inicializar_banco():
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        idade INTEGER,
        sexo TEXT,
        peso REAL,
        altura REAL,
        imc REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clinica (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        historico_doencas TEXT,
        alergias TEXT,
        medicamentos TEXT,
        objetivo_clinico TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS esportiva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        esporte TEXT,
        frequencia TEXT,
        suplementos TEXT,
        objetivo_esportivo TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS infantil (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        idade_gestacional TEXT,
        amamentacao TEXT,
        introducao_alimentar TEXT,
        objetivo_infantil TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    conexao.commit()
    conexao.close()

def salvar_paciente(nome, idade, sexo, peso, altura, imc):
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO pacientes (nome, idade, sexo, peso, altura, imc) VALUES (?, ?, ?, ?, ?, ?)',
                   (nome, idade, sexo, peso, altura, imc))
    paciente_id = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return paciente_id

def salvar_clinica(paciente_id, historico, alergias, medicamentos, objetivo):
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM clinica WHERE paciente_id = ?', (paciente_id,))
    cursor.execute('INSERT INTO clinica (paciente_id, historico_doencas, alergias, medicamentos, objetivo_clinico) VALUES (?, ?, ?, ?, ?)',
                   (paciente_id, historico, alergias, medicamentos, objetivo))
    conexao.commit()
    conexao.close()

def salvar_esportiva(paciente_id, esporte, frequencia, suplementos, objetivo):
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM esportiva WHERE paciente_id = ?', (paciente_id,))
    cursor.execute('INSERT INTO esportiva (paciente_id, esporte, frequencia, suplementos, objetivo_esportivo) VALUES (?, ?, ?, ?, ?)',
                   (paciente_id, esporte, frequencia, suplementos, objetivo))
    conexao.commit()
    conexao.close()

def salvar_infantil(paciente_id, gestacao, amamentacao, introducao, objetivo):
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM infantil WHERE paciente_id = ?', (paciente_id,))
    cursor.execute('INSERT INTO infantil (paciente_id, idade_gestacional, amamentacao, introducao_alimentar, objetivo_infantil) VALUES (?, ?, ?, ?, ?)',
                   (paciente_id, gestacao, amamentacao, introducao, objetivo))
    conexao.commit()
    conexao.close()

def listar_pacientes():
    conexao = sqlite3.connect('nutricao.db')
    df = pd.read_sql_query('SELECT * FROM pacientes', conexao)
    conexao.close()
    return df

def excluir_paciente(id_paciente):
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM clinica WHERE paciente_id = ?', (id_paciente,))
    cursor.execute('DELETE FROM esportiva WHERE paciente_id = ?', (id_paciente,))
    cursor.execute('DELETE FROM infantil WHERE paciente_id = ?', (id_paciente,))
    cursor.execute('DELETE FROM pacientes WHERE id = ?', (id_paciente,))
    conexao.commit()
    conexao.close()

def obter_dados_relatorio(id_paciente):
    conexao = sqlite3.connect('nutricao.db')
    paciente = pd.read_sql_query(f'SELECT * FROM pacientes WHERE id = {id_paciente}', conexao).iloc[0]
    clinica = pd.read_sql_query(f'SELECT * FROM clinica WHERE paciente_id = {id_paciente}', conexao)
    esportiva = pd.read_sql_query(f'SELECT * FROM esportiva WHERE paciente_id = {id_paciente}', conexao)
    infantil = pd.read_sql_query(f'SELECT * FROM infantil WHERE paciente_id = {id_paciente}', conexao)
    conexao.close()
    return paciente, clinica, esportiva, infantil

class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('helvetica', 'B', 20)
        self.cell(80)
        self.cell(30, 10, 'Relatório Nutricional', 0, 1, 'C')
        self.ln(20)

def gerar_pdf(paciente, clinica, esportiva, infantil):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('helvetica', '', 12)
    
    pdf.set_fill_color(220, 235, 255)
    pdf.cell(0, 10, 'Dados Básicos do Paciente', 0, 1, 'L', 1)
    pdf.cell(0, 10, f'Nome: {paciente["nome"]}', 0, 1)
    pdf.cell(0, 10, f'Idade: {paciente["idade"]} anos | Sexo: {paciente["sexo"]}', 0, 1)
    pdf.cell(0, 10, f'Peso: {paciente["peso"]}kg | Altura: {paciente["altura"]}m', 0, 1)
    pdf.cell(0, 10, f'IMC: {paciente["imc"]:.2f}', 0, 1)
    pdf.ln(5)

    sugestoes = []
    
    if not clinica.empty:
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, 'Avaliação Clínica', 0, 1, 'L', 1)
        pdf.multi_cell(0, 10, f'Histórico: {clinica.iloc[0]["historico_doencas"]}')
        pdf.multi_cell(0, 10, f'Alergias: {clinica.iloc[0]["alergias"]}')
        pdf.multi_cell(0, 10, f'Medicamentos: {clinica.iloc[0]["medicamentos"]}')
        pdf.multi_cell(0, 10, f'Objetivo: {clinica.iloc[0]["objetivo_clinico"]}')
        
        # IA Clínica
        sug_cli = []
        obj = str(clinica.iloc[0]["objetivo_clinico"]).lower()
        hist = str(clinica.iloc[0]["historico_doencas"]).lower()
        
        if 'emagrec' in obj or 'perder' in obj or 'peso' in obj:
            sug_cli.append("- [IA Clínica] Foco em déficit calórico e saciedade via fibras.")
        elif 'diabetes' in obj or 'glicose' in obj:
            sug_cli.append("- [IA Clínica] Controle de carga glicêmica em todas as refeições.")
        else:
            sug_cli.append("- [IA Clínica] Manter constância no plano alimentar para equilíbrio metabólico.")
            
        if 'cansaço' in hist or 'fadiga' in hist:
            sug_cli.append("- [IA Clínica] Avaliar deficiência de B12/Ferro e aporte hídrico.")
        
        pdf.set_font('helvetica', 'I', 10)
        pdf.set_text_color(40, 40, 150)
        for s in sug_cli:
            pdf.multi_cell(0, 7, s)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('helvetica', '', 12)
        pdf.ln(5)

    if not esportiva.empty:
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, 'Avaliação Esportiva', 0, 1, 'L', 1)
        pdf.multi_cell(0, 10, f'Atividade: {esportiva.iloc[0]["esporte"]} ({esportiva.iloc[0]["frequencia"]})')
        pdf.multi_cell(0, 10, f'Suplementação: {esportiva.iloc[0]["suplementos"]}')
        pdf.multi_cell(0, 10, f'Objetivo: {esportiva.iloc[0]["objetivo_esportivo"]}')
        
        # IA Esportiva
        sug_esp = []
        obj_e = str(esportiva.iloc[0]["objetivo_esportivo"]).lower()
        sup = str(esportiva.iloc[0]["suplementos"]).lower()
        
        if 'hipertrofia' in obj_e or 'massa' in obj_e or 'músculo' in obj_e:
            sug_esp.append("- [IA Esportiva] Proteína ideal: 2.0-2.2g/kg distribuída em 4-5 doses.")
            if 'creatina' not in sup:
                sug_esp.append("- [IA Esportiva] Info: Avaliar introdução de Creatina para performance.")
        elif 'performance' in obj_e or 'rendimento' in obj_e or 'treino' in obj_e:
            sug_esp.append("- [IA Esportiva] Periodização de carboidratos conforme carga de treino.")
        else:
            sug_esp.append("- [IA Esportiva] Ajustar aporte energético para suprir a demanda da atividade física.")
            
        pdf.set_font('helvetica', 'I', 10)
        pdf.set_text_color(40, 110, 40)
        for s in sug_esp:
            pdf.multi_cell(0, 7, s)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('helvetica', '', 12)
        pdf.ln(5)

    if not infantil.empty:
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, 'Avaliação Infantil', 0, 1, 'L', 1)
        pdf.multi_cell(0, 10, f'Gestação: {infantil.iloc[0]["idade_gestacional"]}')
        pdf.multi_cell(0, 10, f'Amamentação: {infantil.iloc[0]["amamentacao"]}')
        pdf.multi_cell(0, 10, f'Introdução Alimentar: {infantil.iloc[0]["introducao_alimentar"]}')
        pdf.multi_cell(0, 10, f'Objetivo: {infantil.iloc[0]["objetivo_infantil"]}')
        
        # IA Infantil
        sug_inf = []
        obj_i = str(infantil.iloc[0]["objetivo_infantil"]).lower()
        
        if 'introdução' in obj_i or 'comer' in obj_i or 'alimento' in obj_i:
            sug_inf.append("- [IA Infantil] Estímulo sensorial: variedade de cores e texturas naturais.")
        elif 'crescer' in obj_i or 'peso' in obj_i:
            sug_inf.append("- [IA Infantil] Atenção ao aporte de micronutrientes e gorduras saudáveis.")
        else:
            sug_inf.append("- [IA Infantil] Fomentar hábitos saudáveis e variedade alimentar lúdica.")

        pdf.set_font('helvetica', 'I', 10)
        pdf.set_text_color(150, 40, 40)
        for s in sug_inf:
            pdf.multi_cell(0, 7, s)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('helvetica', '', 12)
        pdf.ln(5)

    return bytes(pdf.output())

def remover_duplicatas():
    conexao = sqlite3.connect('nutricao.db')
    cursor = conexao.cursor()
    
    cursor.execute('''
        DELETE FROM pacientes 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM pacientes 
            GROUP BY nome
        )
    ''')
    
    removidos = cursor.rowcount
    conexao.commit()
    conexao.close()
    return removidos

def main():
    st.set_page_config(page_title="Desenvolverdura Pro", page_icon="🥗", layout="wide")
    inicializar_banco()
    
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 20px;
            background-color: #28a745;
            color: white;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    
    st.sidebar.title("Desenvolverdura Pro")
    opcao = st.sidebar.radio("Navegação Principal", ["Cadastrar Paciente", "Módulo Clínico", "Módulo Esportivo", "Módulo Infantil", "Gerenciar Pacientes"])
    
    if opcao == "Cadastrar Paciente":
        st.title("📄 Novo Registro")
        with st.form("form_paciente"):
            nome = st.text_input("Nome Completo do Paciente")
            col1, col2 = st.columns(2)
            idade = col1.number_input("Idade", min_value=0, max_value=120, value=25)
            sexo = col2.selectbox("Sexo Biológico", ["Masculino", "Feminino", "Outro"])
            peso = col1.number_input("Peso Atual (kg)", min_value=0.0, value=70.0)
            altura = col2.number_input("Altura (m)", min_value=0.0, value=1.70)
            
            imc = 0.0
            if altura > 0:
                imc = peso / (altura ** 2)
            
            st.info(f"O IMC atual deste paciente é: {imc:.2f}")
            
            if st.form_submit_button("Confirmar Cadastro"):
                if nome:
                    pid = salvar_paciente(nome, idade, sexo, peso, altura, imc)
                    st.success(f"Paciente {nome} registrado com ID #{pid}")
                else:
                    st.error("O campo Nome é obrigatório.")
                    
    elif opcao == "Gerenciar Pacientes":
        st.title("📋 Base de Pacientes")
        
        if st.button("🧹 Limpar Pacientes Duplicados"):
            qtd = remover_duplicatas()
            st.success(f"Limpeza concluída! {qtd} registros duplicados removidos.")
            st.rerun()

        st.divider()
        
        pacientes = listar_pacientes()
        if not pacientes.empty:
            for _, row in pacientes.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.subheader(f"{row['nome']}")
                    c1.write(f"ID: {row['id']} | IMC: {row['imc']:.2f}")
                    
                    if c2.button(f"📥 Relatório", key=f"rel_{row['id']}"):
                        p, cl, es, inf = obter_dados_relatorio(row['id'])
                        try:
                            pdf_bytes = gerar_pdf(p, cl, es, inf)
                            st.download_button(label="Baixar Agora", data=pdf_bytes, file_name=f"relatorio_{row['nome']}.pdf", mime="application/pdf")
                        except Exception as e:
                            st.error(f"Erro ao gerar PDF: {e}")
                        
                    if c3.button(f"🗑️ Excluir", key=f"excluir_{row['id']}"):
                        excluir_paciente(row['id'])
                        st.warning("Registro removido.")
                        st.rerun()
        else:
            st.info("Nenhum registro encontrado no sistema.")

    elif opcao in ["Módulo Clínico", "Módulo Esportivo", "Módulo Infantil"]:
        pacientes = listar_pacientes()
        if pacientes.empty:
            st.warning("Realize primeiro o cadastro de um paciente.")
        else:
            paciente_selecionado = st.selectbox("Selecione o paciente para atendimento:", ["-- Selecione --"] + pacientes['nome'].tolist())
            
            if paciente_selecionado != "-- Selecione --":
                pid = pacientes[pacientes['nome'] == paciente_selecionado]['id'].values[0]
                st.divider()
                
                if "Clínico" in opcao:
                    st.title("🏥 Anamnese Clínica")
                    # Tentar carregar dados existentes
                    conexao = sqlite3.connect('nutricao.db')
                    dados_existentes = pd.read_sql_query(f'SELECT * FROM clinica WHERE paciente_id = {pid}', conexao)
                    conexao.close()
                    
                    hist_padrao = dados_existentes.iloc[0]['historico_doencas'] if not dados_existentes.empty else ""
                    aler_padrao = dados_existentes.iloc[0]['alergias'] if not dados_existentes.empty else ""
                    meds_padrao = dados_existentes.iloc[0]['medicamentos'] if not dados_existentes.empty else ""
                    obj_padrao = dados_existentes.iloc[0]['objetivo_clinico'] if not dados_existentes.empty else ""

                    historico = st.text_area("Histórico Clínico e Doenças Preexistentes", value=hist_padrao)
                    alergias = st.text_area("Alergias ou Intolerâncias Alimentares", value=aler_padrao)
                    medicamentos = st.text_area("Medicamentos e Fármacos em Uso", value=meds_padrao)
                    objetivo = st.text_area("Objetivo da Intervenção Clínica", value=obj_padrao)
                    if st.button("Gravar Avaliação Clínica"):
                        salvar_clinica(pid, historico, alergias, medicamentos, objetivo)
                        st.success("Dados clínicos atualizados!")
                        
                elif "Esportivo" in opcao:
                    st.title("🏋️ Anamnese Esportiva")
                    # Tentar carregar dados existentes
                    conexao = sqlite3.connect('nutricao.db')
                    dados_existentes = pd.read_sql_query(f'SELECT * FROM esportiva WHERE paciente_id = {pid}', conexao)
                    conexao.close()
                    
                    esp_padrao = dados_existentes.iloc[0]['esporte'] if not dados_existentes.empty else ""
                    freq_padrao = dados_existentes.iloc[0]['frequencia'] if not dados_existentes.empty else ""
                    sup_padrao = dados_existentes.iloc[0]['suplementos'] if not dados_existentes.empty else ""
                    obj_padrao = dados_existentes.iloc[0]['objetivo_esportivo'] if not dados_existentes.empty else ""

                    esporte = st.text_input("Modalidade Praticada", value=esp_padrao)
                    frequencia = st.text_input("Intensidade/Frequência Semanal", value=freq_padrao)
                    suplementos = st.text_area("Suplementação Utilizada", value=sup_padrao)
                    objetivo = st.text_area("Objetivo de Performance/Estético", value=obj_padrao)
                    if st.button("Gravar Avaliação Esportiva"):
                        salvar_esportiva(pid, esporte, frequencia, suplementos, objetivo)
                        st.success("Dados esportivos atualizados!")
                        
                elif "Infantil" in opcao:
                    st.title("👶 Anamnese Pediátrica")
                    # Tentar carregar dados existentes
                    conexao = sqlite3.connect('nutricao.db')
                    dados_existentes = pd.read_sql_query(f'SELECT * FROM infantil WHERE paciente_id = {pid}', conexao)
                    conexao.close()
                    
                    gest_padrao = dados_existentes.iloc[0]['idade_gestacional'] if not dados_existentes.empty else ""
                    amam_padrao = dados_existentes.iloc[0]['amamentacao'] if not dados_existentes.empty else ""
                    intr_padrao = dados_existentes.iloc[0]['introducao_alimentar'] if not dados_existentes.empty else ""
                    obj_padrao = dados_existentes.iloc[0]['objetivo_infantil'] if not dados_existentes.empty else ""

                    gestacao = st.text_input("Histórico Gestacional e Nascimento", value=gest_padrao)
                    amamentacao = st.text_input("Tempo de Amamentação", value=amam_padrao)
                    introducao = st.text_area("Histórico de Introdução Alimentar", value=intr_padrao)
                    objetivo = st.text_area("Objetivo Nutricional Infantil", value=obj_padrao)
                    if st.button("Gravar Avaliação Pediátrica"):
                        salvar_infantil(pid, gestacao, amamentacao, introducao, objetivo)
                        st.success("Dados pediátricos atualizados!")

if __name__ == "__main__":
    main()

