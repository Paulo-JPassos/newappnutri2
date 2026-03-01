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
    paciente = pd.read_sql_query(f'SELECT * FROM pacientes WHERE id = {id_paciente}', conexao)
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

def gerar_pdf(paciente, dados_modulo, modulo_alvo):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('helvetica', '', 12)
    
    # Cabeçalho de Identificação (Visual Premium)
    pdf.set_fill_color(0, 100, 0) # Verde Escuro
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, f'PARECER TÉCNICO NUTRICIONAL - DESENVOLVERDURA IA', 0, 1, 'C', 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Identificação do Paciente (Limpeza de Dados)
    try:
        p_peso = float(paciente.get('peso', 0)) if paciente.get('peso') else 0.0
        p_altura = float(paciente.get('altura', 0)) if paciente.get('altura') else 0.0
        p_imc = float(paciente.get('imc', 0)) if paciente.get('imc') else 0.0
    except:
        p_peso, p_altura, p_imc = 0.0, 0.0, 0.0

    pdf.set_fill_color(235, 245, 235)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f' Paciente: {paciente.get("nome", "N/A")}', 0, 1, 'L', True)
    pdf.set_font('helvetica', '', 11)
    pdf.cell(0, 8, f'  Ficha: #{paciente.get("id", "0")} | Idade: {paciente.get("idade", "0")} anos | Sexo: {paciente.get("sexo", "N/A")}', 0, 1)
    pdf.cell(0, 8, f'  Antropometria: {p_peso}kg | {p_altura}m | IMC: {p_imc:.2f}', 0, 1)
    pdf.ln(5)

    def imprimir_relato_ia(titulo, relato, cor_box):
        pdf.set_fill_color(*cor_box)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, f' {titulo}', 0, 1, 'L', True)
        pdf.set_font('helvetica', 'I', 10)
        pdf.multi_cell(0, 7, relato)
        pdf.ln(10)

    if modulo_alvo == "Clínico":
        hist = dados_modulo.get('historico', '')
        aler = dados_modulo.get('alergias', '')
        meds = dados_modulo.get('medicamentos', '')
        obj = dados_modulo.get('objetivo', '')

        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, 'Contexto Clínico Inicial:', 0, 1)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 7, f"Análise das queixas de {hist}. Medicamentos em uso: {meds}. Alergias: {aler}. Foco principal: {obj}.")
        pdf.ln(5)

        # Brain da IA Clínica - Relato Denso
        relato_ia = f"RELATO IA: Após análise sistêmica do perfil clínico de {paciente.get('nome','o paciente')}, observamos que a queixa principal ({obj}) exige uma manobra dietoterápica focada na homeostase metabólica. "
        if 'emagrec' in str(obj).lower() or 'peso' in str(obj).lower():
            relato_ia += "Propomos uma estratégia baseada em densidade nutricional elevada com restrição energética moderada. Sugere-se a modulação da carga glicêmica das refeições para controle do eixo insulina-glucagon, priorizando fibras solúveis que auxiliam na saciedade precoce. "
        if 'diabetes' in str(obj).lower() or 'glicose' in str(obj).lower():
            relato_ia += "O quadro exige rigoroso monitoramento do índice glicêmico. Recomenda-se a inclusão de gorduras monoinsaturadas e proteínas em todas as janelas de carboidrato para mitigar picos pós-prandiais e proteger a função pancreática. "
        
        calc_agua = p_peso * 35 if p_peso > 0 else 2000
        relato_ia += f"Quanto aos medicamentos ({meds}), é vital o acompanhamento da absorção de micronutrientes, mantendo a ingestão hídrica alvo de {calc_agua:.0f}ml/dia."
        
        imprimir_relato_ia("ANÁLISE AVANÇADA DE IA CLÍNICA", relato_ia, (230, 240, 255))

    elif modulo_alvo == "Esportivo":
        esp = dados_modulo.get('esporte', '')
        freq = dados_modulo.get('frequencia', '')
        sup = dados_modulo.get('suplementos', '')
        obj = dados_modulo.get('objetivo', '')

        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, 'Performance e Atividade Física:', 0, 1)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 7, f"Atividade Principal: {esp} ({freq}). Suplementação Reportada: {sup}. Objetivo: {obj}.")
        pdf.ln(5)

        # Brain da IA Esportiva
        relato_ia = f"RELATO IA: Para a modalidade {esp}, identificamos uma demanda bioenergética específica. "
        if 'hipertrofia' in str(obj).lower() or 'massa' in str(obj).lower() or 'músculo' in str(obj).lower():
            calc_prot = p_peso * 2.2 if p_peso > 0 else 150
            relato_ia += f"Para maximizar a hipertrofia muscular, o laudo projeta um superávit calórico progressivo. Sugere-se aporte proteico central de 2.2g/kg (aprox. {calc_prot:.1f}g/dia), fracionado para manter a síntese proteica elevada. "
            if 'creatina' not in str(sup).lower():
                relato_ia += "Considerando o perfil de força, a suplementação com Creatina Monoidratada (3-5g/dia) deve ser avaliada para otimizar os estoques de fosfocreatina. "
        if 'performance' in str(obj).lower() or 'rendimento' in str(obj).lower() or 'treino' in str(obj).lower():
            relato_ia += "A estratégia deve incluir periodização de carboidratos, ajustando o volume conforme a depleção de glicogênio nas sessões de alta intensidade."
        relato_ia += "A recuperação tecidual será otimizada via balanço nitrogenado positivo constante."

        imprimir_relato_ia("ANÁLISE DE PERFORMANCE ESPORTIVA IA", relato_ia, (230, 255, 230))

    elif modulo_alvo == "Infantil":
        gest = dados_modulo.get('gestacao', '')
        amam = dados_modulo.get('amamentacao', '')
        intr = dados_modulo.get('introducao', '')
        obj = dados_modulo.get('objetivo', '')

        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, 'Desenvolvimento Pediátrico:', 0, 1)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 7, f"Contexto: {gest}. Amamentação: {amam}. Introdução Alimentar: {intr}. Objetivo: {obj}.")
        pdf.ln(5)

        # Brain da IA Infantil
        relato_ia = f"RELATO IA: A janela de desenvolvimento pediátrico para {paciente.get('nome','a criança')} exige atenção à plasticidade sensorial. "
        if 'introdução' in str(intr).lower() or 'comer' in str(obj).lower():
            relato_ia += "Sugerimos a técnica de exposição repetida e variada a alimentos 'in natura'. O foco deve ser a exploração de texturas, cores e sabores para consolidar um paladar saudável e prevenir a neofobia alimentar. "
        relato_ia += "Deve-se garantir o aporte de ácidos graxos essenciais (ômega-3) e ferro heme, fundamentais para a mielinização neural e desenvolvimento cognitivo. A amamentação deve ser incentivada conforme a diretriz vigente."

        imprimir_relato_ia("PARECER PEDIÁTRICO DE IA", relato_ia, (255, 240, 240))

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
        .report-section {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    
    st.sidebar.title("Desenvolverdura Pro")
    opcao = st.sidebar.radio("Navegação Principal", ["Cadastrar Paciente", "Módulo Clínico", "Módulo Esportivo", "Módulo Infantil", "Base de Pacientes"])
    
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
                    
    elif opcao == "Base de Pacientes":
        st.title("📋 Gerenciamento de Dados")
        
        if st.button("🧹 Limpar Pacientes Duplicados"):
            qtd = remover_duplicatas()
            st.success(f"Limpeza concluída! {qtd} registros duplicados removidos.")
            st.rerun()

        st.divider()
        
        pacientes = listar_pacientes()
        if not pacientes.empty:
            for _, row in pacientes.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.subheader(f"{row['nome']}")
                    c1.write(f"ID: {row['id']} | Idade: {row['idade']} | IMC: {row['imc']:.2f}")
                                            
                    if c2.button(f"🗑️ Excluir", key=f"excluir_{row['id']}"):
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
                p_atual, c_atual, e_atual, i_atual = obter_dados_relatorio(pid)
                st.divider()
                
                if "Clínico" in opcao:
                    st.title("🏥 Atendimento Clínico")
                    hist_val = c_atual.iloc[0]['historico_doencas'] if not c_atual.empty else ""
                    aler_val = c_atual.iloc[0]['alergias'] if not c_atual.empty else ""
                    meds_val = c_atual.iloc[0]['medicamentos'] if not c_atual.empty else ""
                    obj_val = c_atual.iloc[0]['objetivo_clinico'] if not c_atual.empty else ""

                    historico = st.text_area("Histórico Clínico", value=hist_val)
                    alergias = st.text_area("Alergias", value=aler_val)
                    medicamentos = st.text_area("Medicamentos", value=meds_val)
                    objetivo = st.text_area("Objetivo Clínico", value=obj_val)
                    
                    dados_form = {'historico': historico, 'alergias': alergias, 'medicamentos': medicamentos, 'objetivo': objetivo}
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("💾 Gravar Dados"):
                        salvar_clinica(pid, historico, alergias, medicamentos, objetivo)
                        st.success("Dados salvos e sincronizados!")
                        st.rerun()
                    
                    # Relatório IA em Tempo Real
                    try:
                        paciente_dict = p_atual.to_dict('records')[0]
                        pdf_bytes = gerar_pdf(paciente_dict, dados_form, "Clínico")
                        col_btn2.download_button("📥 Gerar Relato IA (PDF)", data=pdf_bytes, file_name=f"relato_clinico_{paciente_selecionado}.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Erro ao preparar laudo: {e}")
                        
                elif "Esportivo" in opcao:
                    st.title("🏋️ Atendimento Esportivo")
                    esp_val = e_atual.iloc[0]['esporte'] if not e_atual.empty else ""
                    freq_val = e_atual.iloc[0]['frequencia'] if not e_atual.empty else ""
                    sup_val = e_atual.iloc[0]['suplementos'] if not e_atual.empty else ""
                    obj_val = e_atual.iloc[0]['objetivo_esportivo'] if not e_atual.empty else ""

                    esporte = st.text_input("Modalidade", value=esp_val)
                    frequencia = st.text_input("Frequência", value=freq_val)
                    suplementos = st.text_area("Suplementação", value=sup_val)
                    objetivo = st.text_area("Objetivo Esportivo", value=obj_val)
                    
                    dados_form = {'esporte': esporte, 'frequencia': frequencia, 'suplementos': suplementos, 'objetivo': objetivo}
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("💾 Gravar Dados"):
                        salvar_esportiva(pid, esporte, frequencia, suplementos, objetivo)
                        st.success("Performance gravada!")
                        st.rerun()
                    
                    # Relatório IA em Tempo Real
                    try:
                        paciente_dict = p_atual.to_dict('records')[0]
                        pdf_bytes = gerar_pdf(paciente_dict, dados_form, "Esportivo")
                        col_btn2.download_button("📥 Gerar Relato IA (PDF)", data=pdf_bytes, file_name=f"relato_esportivo_{paciente_selecionado}.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Erro ao preparar laudo: {e}")
                        
                elif "Infantil" in opcao:
                    st.title("👶 Atendimento Pediátrico")
                    gest_val = i_atual.iloc[0]['idade_gestacional'] if not i_atual.empty else ""
                    amam_val = i_atual.iloc[0]['amamentacao'] if not i_atual.empty else ""
                    intr_val = i_atual.iloc[0]['introducao_alimentar'] if not i_atual.empty else ""
                    obj_val = i_atual.iloc[0]['objetivo_infantil'] if not i_atual.empty else ""

                    gestacao = st.text_input("Gestação", value=gest_val)
                    amamentacao = st.text_input("Amamentação", value=amam_val)
                    introducao = st.text_area("Introdução Alimentar", value=intr_val)
                    objetivo = st.text_area("Objetivo Pediátrico", value=obj_val)
                    
                    dados_form = {'gestacao': gestacao, 'amamentacao': amamentacao, 'introducao': introducao, 'objetivo': objetivo}
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("💾 Gravar Dados"):
                        salvar_infantil(pid, gestacao, amamentacao, introducao, objetivo)
                        st.success("Dados infantis salvos!")
                        st.rerun()
                    
                    # Relatório IA em Tempo Real
                    try:
                        paciente_dict = p_atual.to_dict('records')[0]
                        pdf_bytes = gerar_pdf(paciente_dict, dados_form, "Infantil")
                        col_btn2.download_button("📥 Gerar Relato IA (PDF)", data=pdf_bytes, file_name=f"relato_infantil_{paciente_selecionado}.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Erro ao preparar laudo: {e}")

if __name__ == "__main__":
    main()
