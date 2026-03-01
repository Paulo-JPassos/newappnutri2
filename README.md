# Aplicativo Nutricionista Modular

Este é um aplicativo profissional desenvolvido em Python para nutricionistas. Ele oferece uma estrutura modular para atendimento em áreas específicas (Clínica, Esportiva e Infantil), além de um sistema centralizado de cadastro de pacientes.

## 🚀 Funcionalidades

- **Cadastro de Pacientes**: Registro completo com Nome, Idade, Sexo, Peso e Altura.
- **Cálculo Automático de IMC**: O Índice de Massa Corporal é calculado em tempo real durante o cadastro.
- **Módulos Especializados**:
  - **Nutrição Clínica**: Foco em histórico de doenças, alergias e medicamentos.
  - **Nutrição Esportiva**: Foco no esporte praticado, frequência e suplementação.
  - **Nutrição Infantil**: Foco em história gestacional, amamentação e introdução alimentar.
- **Gerenciamento de Dados**: Listagem de pacientes com opção de exclusão.
- **Relatório Sugestivo (PDF)**: Geração de um documento profissional consolidando todas as informações coletadas para o paciente.

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem base do sistema.
- **Streamlit**: Framework para criação da interface web interativa.
- **SQLite**: Banco de dados relacional para armazenamento local e persistente.
- **FPDF2**: Biblioteca para geração dinâmica de relatórios em PDF.
- **Pandas**: Manipulação e visualização de dados do banco.

## 📦 Como Executar

1. Certifique-se de ter o Python instalado.
2. Instale as dependências necessárias:
   ```bash
   pip install streamlit fpdf2 pandas
   ```
3. Execute o aplicativo:
   ```bash
   streamlit run nutri_app.py
   ```

## 📂 Estrutura do Banco de Dados

O aplicativo utiliza um arquivo local chamado `nutricao.db` com as seguintes tabelas:
- `pacientes`: Dados demográficos e biométricos.
- `clinica`: Dados de anamnese clínica.
- `esportiva`: Dados de performance esportiva.
- `infantil`: Dados de desenvolvimento pediátrico.

## 📝 Observações

- O código segue as melhores práticas de Clean Code, com nomes de variáveis e funções em Português (Brasil).
- O sistema de exclusão remove em cascata todos os dados de anamnese vinculados ao paciente.
