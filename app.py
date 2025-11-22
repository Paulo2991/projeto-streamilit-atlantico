import streamlit as st 
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="DashBoard De Tarefas",layout="wide")
st.title("Dashbord De Tarefas")

def card(title,value,icon = " 📄"):
    st.markdown(
           f"""
                    <div style="
                       background-color:#f5f7fa;padding:18px;border-radius:12px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;
                        border-left:5px solid #4a90e2;min-height:90px;"> 
                        <div style="font-size: 22px; font-weight: bold; color: #333;">{title}</div>
                        <div style="color:#555;font-size:15px;">{value}</div>
                        <div style="font-size:22px;font-weight:700;">{icon}</div>
                    </div>
                """,unsafe_allow_html=True,
                )


st.sidebar.header("📁 Carregar Arquivo")
arquivo = st.sidebar.file_uploader("Escolha uma planilha (.csv ou .xlsx)", type=['xlsx', 'xls','csv'])

if arquivo is not None:
    fileName = arquivo.name
    fileExtension = os.path.splitext(fileName)[1].lower()
    try:
     if fileExtension == '.csv':
         df = pd.read_csv(arquivo, sep=";")
         st.sidebar.success("Arquivo CSV carregado com sucesso!")
     elif fileExtension in ['.xlsx','.xls']:
        df = pd.read_excel(arquivo,usecols=[9, 11, 15,25, 26])
        st.sidebar.success("Arquivo Excel carregado com sucesso!")
     else:
         st.sidebar.error("Arquivo não suportado")
         st.stop()
    except Exception as e:
     st.sidebar.error(f"Erro ao ler o arquivo: {e}")
     st.stop()
else:
  st.sidebar.warning("Erro ao ler o arquivo, favor ler outro")
  st.stop()
    
st.sidebar.divider() 

def explodeResponsaveis(df):
    df = df.copy()
    df["Responsável"] = df["Responsável"].fillna("").astype(str)
    df["lista"] = df["Responsável"].apply(lambda x:[p.strip() for p in x.split(",") if p.strip()])
    df = df.explode("lista")
    df["Responsável"] = df["lista"]
    return df.drop(columns=["lista"])  


if st.sidebar.button("🔁 Analises Reabertas"):
    st.session_state.activate_analysis = "reabertas"


##Cards"""

col1, col2,col3 = st.columns(3)
totalTarefas = len(df)
tarefasEncerradas = df['Fase'].value_counts().get('Entregue',0)
menor = df["Criada em"].min()
maior = df["Criada em"].max()
# Quantidade de tarefas que foram reabertas

with col1: card("Total De Registros", totalTarefas, " 📄 ")
with col2: card("Tarefas Encerradas", tarefasEncerradas)
#with col2: card("Menor Data", menor.strftime("%d/%m/%Y") if pd.notnull(menor) else "-","📅")
with col3: card("Maior Data", maior.strftime("%d/%m/%Y") if pd.notnull(maior) else "-","📅")


relatorios = [
    "Percentual De Tarefas Reabertas",
    "Tarefas Por Responsável",
    "SLA"
]

selecoes = {}

st.sidebar.header("Selecione as opções para visualizar os relatorios")

comoboSelecionado = st.sidebar.selectbox(
    label="Relatórios",
    options=relatorios,
    index=None,
    placeholder="Selecione o relatório a ser visualizado"
)

st.sidebar.divider() 

    
if comoboSelecionado == "Percentual De Tarefas Reabertas":
 st.subheader("🔁 Analise De Tarefas Reabertas") 

 count = df["Reaberta?"].value_counts().reset_index()
 count.columns = ["Reaberta","Total"]

 fig = px.pie(count, names="Reaberta", values="Total", hole=0.4)
 st.plotly_chart(fig,use_container_width=True)
elif comoboSelecionado == "Tarefas Por Responsável":
  dfReabertadasSim = explodeResponsaveis(df[df["Reaberta?"] == "Sim"])
  
  dfResponsavel = dfReabertadasSim.groupby("Responsável").size().reset_index(name="Total").sort_values("Total")
 
  graficoReabertoResponsavel = px.bar(
    dfResponsavel,
    x="Total", y="Responsável",
    orientation="h", text="Total", height=800
     
 )
 
  graficoReabertoResponsavel.update_layout( xaxis=dict(showgrid=True, gridcolor="#cccccc", gridwidth=0.5),
        yaxis=dict(showgrid=False),)
  st.plotly_chart(graficoReabertoResponsavel, use_container_width=True)
  
  pessoa = sorted(dfReabertadasSim['Responsável'].unique())
  pessoaSelectBox = st.sidebar.selectbox("Filtrar Por Resposável",["(todas)"] + pessoa)
  criarSelectBox = dfReabertadasSim if pessoaSelectBox == "(todas)" else dfReabertadasSim[dfReabertadasSim["Responsável"] == pessoaSelectBox]
  
  st.dataframe(
        criarSelectBox[
            ["Tarefa", "Responsável", "Criada em", "Reaberta?"]
        ].sort_values("Criada em", ascending=False),
        use_container_width=True
    )
  
  
