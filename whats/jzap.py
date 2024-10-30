import streamlit as st
import pandas as pd
import re
import urllib.parse

# Configuração inicial da página
st.set_page_config(page_title="Gerador de Links WhatsApp", layout="wide")

# Inicialização do session_state
if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'valid_numbers' not in st.session_state:
    st.session_state.valid_numbers = None

def validate_phone(phone):
    """Valida se o número de telefone está no formato correto."""
    phone = str(phone)
    phone_clean = re.sub(r'\D', '', phone)
    
    # Verifica o tamanho
    if len(phone_clean) != 11:
        return False, "Número deve ter 11 dígitos"
    
    # Verifica o DDD
    ddd = int(phone_clean[:2])
    if ddd < 11 or ddd > 99:
        return False, "DDD inválido"
    
    return True, "OK"

def format_phone(phone):
    """Formata o número para o padrão +5585989659006."""
    phone = str(phone)
    phone_clean = re.sub(r'\D', '', phone)
    
    if not phone_clean:
        return ""
    
    if len(phone_clean) >= 11:
        return f"+55{phone_clean[:2]}{phone_clean[2:11]}"
    
    return phone_clean

def create_whatsapp_link(phone, message):
    """Cria o link do WhatsApp com a mensagem."""
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded_message}"

def go_to_message_page():
    st.session_state.page = 'message'

def go_to_upload_page():
    st.session_state.page = 'upload'

# Página de Upload e Validação
if st.session_state.page == 'upload':
    st.title("📱 Validação de Números de Telefone")
    
    uploaded_file = st.file_uploader(
        "Carregue sua planilha Excel ou CSV com os números de telefone",
        type=['xlsx', 'csv']
    )
    
    if uploaded_file is not None:
        try:
            # Lê o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Verifica se existe a coluna 'telefone'
            if 'telefone' not in df.columns:
                st.error("❌ O arquivo deve conter uma coluna chamada 'telefone'")
            else:
                if st.button("Validar Números"):
                    # Processa os números
                    df['Telefone_Formatado'] = df['telefone'].apply(format_phone)
                    df['Válido'], df['Motivo'] = zip(*df['telefone'].apply(validate_phone))
                    
                    # Separa números válidos e inválidos
                    valid_phones = df[df['Válido']].copy()
                    invalid_phones = df[~df['Válido']].copy()
                    
                    # Mostra estatísticas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Números", len(df))
                    with col2:
                        st.metric("✅ Números Válidos", len(valid_phones))
                    with col3:
                        st.metric("❌ Números Inválidos", len(invalid_phones))
                    
                    # Mostra resultados em abas
                    tab1, tab2 = st.tabs(["✅ Números Válidos", "❌ Números Inválidos"])
                    
                    with tab1:
                        if not valid_phones.empty:
                            st.dataframe(valid_phones[['Telefone_Formatado']])
                            # Salva os números válidos no session_state
                            st.session_state.valid_numbers = valid_phones['Telefone_Formatado'].tolist()
                        else:
                            st.warning("Nenhum número válido encontrado")
                    
                    with tab2:
                        if not invalid_phones.empty:
                            st.dataframe(invalid_phones[['telefone', 'Motivo']])
                        else:
                            st.success("Nenhum número inválido encontrado")
                    
                    # Botão para próxima página só aparece se houver números válidos
                    if not valid_phones.empty:
                        st.button("Próximo Passo ➡️", on_click=go_to_message_page)
                    
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {str(e)}")

# Página de Mensagem e Geração de Links
elif st.session_state.page == 'message':
    st.title("💬 Geração de Links do WhatsApp")
    
    # Botão para voltar
    st.button("⬅️ Voltar", on_click=go_to_upload_page)
    
    if st.session_state.valid_numbers:
        # Campo para digitar a mensagem
        message = st.text_area(
            "Digite sua mensagem:",
            placeholder="Olá! Temos uma oferta especial para você..."
        )
        
        if message:
            if st.button("Gerar Links"):
                # Gera links para cada número
                links = []
                for phone in st.session_state.valid_numbers:
                    link = create_whatsapp_link(phone, message)
                    links.append({
                        'Telefone': phone,
                        'Link': link
                    })
                
                # Mostra os resultados
                df_links = pd.DataFrame(links)
                st.success(f"✅ {len(links)} links gerados com sucesso!")
                
                # Mostra os links em uma tabela expansível
                with st.expander("Ver Links Gerados", expanded=True):
                    st.dataframe(
                        df_links,
                        column_config={
                            "Link": st.column_config.LinkColumn()
                        }
                    )
    else:
        st.warning("Por favor, volte e carregue os números primeiro.")