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
        df = pd.read_excel(arquivo,usecols=[6,7,9,11,12,15,16,18,21,25,26])
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
    "SLA Sem Outliers",
    "SLA Com Outliers",
    "Tempo De Soma Por Tipo De Tarefa",
    "Tempo Medio Por Tipo De Tarefa"
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

    
def filtroTipoTarefas():
  filtroTipoTarefa = sorted(df['Tipo de tarefa'].dropna().unique().tolist())
  filtroTipoTarefaSelectBox = st.sidebar.selectbox("Filtrar Por Tipo De Tarefa",["(todas)"] + filtroTipoTarefa)
  colunasExibir = ["ID da Tarefa", "Tarefa", "Tipo de tarefa", "Já registradas h"]
  colunasMostrar = [coluna for coluna in colunasExibir if coluna in df.columns]
  if filtroTipoTarefaSelectBox == "(todas)":
    tipoTarefa = df[colunasMostrar].copy()
    tipoTarefa = tipoTarefa.sort_values("Já registradas h", ascending=False)
  else:
    tipoTarefa = df[df["Tipo de tarefa"] == filtroTipoTarefaSelectBox].copy()
    tipoTarefa = tipoTarefa[colunasMostrar].sort_values("Já registradas h", ascending=False)
    
  return tipoTarefa 

match comoboSelecionado:   
    case "Percentual De Tarefas Reabertas":
        st.subheader("🔁 Analise De Tarefas Reabertas") 
        dfReabertadasSim = explodeResponsaveis(df[df["Reaberta?"] == "Sim"])

        count = df["Reaberta?"].value_counts().reset_index()
        count.columns = ["Reaberta","Total"]

        fig = px.pie(count, names="Reaberta", values="Total", hole=0.4)
        st.plotly_chart(fig,use_container_width=True)
        
        pessoa = sorted(dfReabertadasSim['Tipo de tarefa'].dropna().unique())
        pessoaSelectBox = st.sidebar.selectbox("Filtrar Por Resposável",["(todas)"] + pessoa)
        criarSelectBox = dfReabertadasSim if pessoaSelectBox == "(todas)" else dfReabertadasSim[dfReabertadasSim["Responsável"] == pessoaSelectBox]
  
        st.dataframe(
            criarSelectBox[
                ["Tipo de tarefa", "Responsável", "Criada em", "Reaberta?"]
            ].sort_values("Criada em", ascending=False),
            use_container_width=True
        )
    case "Tarefas Por Responsável":
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
  
        pessoa = sorted(dfReabertadasSim['Responsável'].dropna().unique())
        pessoaSelectBox = st.sidebar.selectbox("Filtrar Por Resposável",["(todas)"] + pessoa)
        criarSelectBox = dfReabertadasSim if pessoaSelectBox == "(todas)" else dfReabertadasSim[dfReabertadasSim["Responsável"] == pessoaSelectBox]
  
        st.dataframe(
            criarSelectBox[
                ["Tarefa", "Responsável", "Criada em", "Reaberta?"]
            ].sort_values("Criada em", ascending=False),
            use_container_width=True
        )
  
    case "SLA Sem Outliers":
        st.subheader(":blue[📈 Análise SLA]")
    ##----------------Informe os dados que estão vazios-------------------------
        df["Entrega desejada"] = df["Entrega desejada"].fillna("Não Informado")
        df["Fechada em"] = df["Fechada em"].fillna("Não Informado")
        df['Entrega desejada'] = pd.to_datetime(df['Entrega desejada'], errors='coerce')
        df['Fechada em'] = pd.to_datetime(df['Fechada em'], errors='coerce')
    ##--- Faz o calculo da diferencia entre a entrega fechada e a desejada
        df['diferencaHoras'] = (df['Fechada em'] - df['Entrega desejada']) / pd.Timedelta(days=1) * 24 * -1
        Q1 = df["diferencaHoras"].quantile(0.25)
        Q3 = df["diferencaHoras"].quantile(0.75)
        IQR = Q3 - Q1
        limiteInferior = Q1 - 1.5 * IQR
        limiteSuperior = Q3 + 1.5 * IQR
        diferencaSemOutlires = df[(df["diferencaHoras"] >= limiteInferior) & (df["diferencaHoras"] <= limiteSuperior)]
        dfSlaTarefaMedio = diferencaSemOutlires.groupby("Tipo de tarefa")["diferencaHoras"].mean().reset_index().sort_values("diferencaHoras",ascending=True)

    
        fig1 = px.bar(dfSlaTarefaMedio,
                x='diferencaHoras',
                y='Tipo de tarefa',
                orientation='h',
                color='Tipo de tarefa',
                color_continuous_scale='RdYlGn',
                labels={'diferenciaHoras': 'Média da Diferença de Horas (SLA)', 'Tipo de tarefa': 'Tipo de Tarefa'},
                title='Tempo Médio (SLA) entre Entrega Desejada e Fechada por Tipo de Tarefa (Sem Outliers)',
                height=900) 

    # Ajusta o layout para melhor legibilidade
        fig1.update_layout(
            title_font_size=20,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            xaxis_tickfont_size=10,
            yaxis_tickfont_size=10,
            yaxis_categoryorder='total ascending' # Garante a ordem das barras
    )

        st.plotly_chart(fig1, use_container_width=True)
    
    ## -----Tempo Medio Por Tipo De Tarefa
    case "Tempo De Soma Por Tipo De Tarefa":
     st.markdown("## 🧮 Análise de Tempo Total e Soma por Tipo de Tarefa")
     dfFechado = df[df['Fechada em'].notna()]
     tempoTotalTarefa = (
         dfFechado.groupby("Tipo de tarefa")["Já registradas h"]
         .sum()
         .reset_index()
         .sort_values("Já registradas h",ascending=False)
    )
     st.markdown("### 📊 Tempo Total Registrado por Tarefa")
     tempoTotalTarefa["Já registradas h"] = tempoTotalTarefa["Já registradas h"].round(2)
     figTempoTotalTarefa = px.bar(
         tempoTotalTarefa,
         x='Tipo de tarefa',
         y='Já registradas h',
         color='Tipo de tarefa',
         color_continuous_scale='RdYlGn',
         labels={'Já registradas h': 'Tempo Total', 'Tipo de tarefa': 'Tipo de Tarefa'},
         height=500)
     figTempoTotalTarefa.update_traces(textposition="outside")
     figTempoTotalTarefa.update_layout(xaxis_tickangle=-45)
     st.plotly_chart(figTempoTotalTarefa, use_container_width=True)
     
     st.dataframe(
            filtroTipoTarefas(),
            use_container_width=True
        )
  
    case "Tempo Medio Por Tipo De Tarefa":
        st.markdown("## 🧮 Análise de Tempo Total e Medio por Tipo de Tarefa")
        dfFechado = df[df['Fechada em'].notna()]
        tempoTotalTarefa = (
         dfFechado.groupby("Tipo de tarefa")["Já registradas h"]
         .mean()
         .reset_index()
         .sort_values("Já registradas h",ascending=False)
    )
        tempoTotalTarefa["Já registradas h"] = tempoTotalTarefa["Já registradas h"].round(2)
        st.markdown("### 📊 Tempo Médio Registrado por Tarefa")
        figTempoTotalTarefa = px.bar(
         tempoTotalTarefa,
         x='Tipo de tarefa',
         y='Já registradas h',
         color='Tipo de tarefa',
         color_continuous_scale='RdYlGn',
         labels={'Já registradas h': 'Tempo Medio', 'Tipo de tarefa': 'Tipo de Tarefa'},
         height=500)
        figTempoTotalTarefa.update_traces(textposition="outside")
        figTempoTotalTarefa.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(figTempoTotalTarefa, use_container_width=True)
        filtro = filtroTipoTarefas()
        st.dataframe(
            filtro,
            use_container_width=True
        )
    
  
