import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="InovaSUS Connect",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed", # Inicia recolhida (e ocultada via CSS)
)

# ---------------------------------------------------------
# 1. ESTILO CSS CUSTOMIZADO (Tema Teal/Mint Escuro)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Ocultar completamente a barra lateral e o botão de expandir */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Estilização dos Cards e Hero */
    .hero {
        background: linear-gradient(135deg, #0e4146 0%, #166461 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(14, 65, 70, 0.2);
    }
    .brand-mark {
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.85rem;
        color: #7be7c3;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .tag {
        display: inline-block;
        background-color: #d9f6eb;
        color: #0e4146;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 0.4rem;
        margin-bottom: 0.5rem;
    }
    .tag-alert {
        background-color: #ffebee;
        color: #c62828;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

USER_NAME = "Rejane"
USER_ROLE = "Enfermeira · APS"

# Conexão com o Supabase usando o secrets.toml
@st.cache_resource
def init_supabase() -> Client:
    url: str = st.secrets["SUPABASE_URL"].rstrip("/").replace("/rest/v1", "")
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Busca os desafios reais cadastrados na tabela 'desafios'
def get_challenges():
    try:
        response = supabase.table("desafios").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao carregar desafios do Supabase: {e}")
        return []

# ---------------------------------------------------------
# FUNÇÕES DE AUTENTICAÇÃO E LOGIN
# ---------------------------------------------------------
def render_auth_page(key_prefix: str = "main"):
    # Cabeçalho de Login padronizado com o novo tema
    st.markdown(
        """
        <div class="hero" style="text-align: center; padding: 2.5rem 1rem;">
            <div class="brand-mark">InovaSUS Connect</div>
            <h1 style="margin: 0; font-size: 2rem;">Conectando conhecimento, transformando o SUS</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    tab_login, tab_signup = st.tabs(["Entrar", "Criar Conta"])
    
    # --- TAB LOGIN ---
    with tab_login:
        with st.form(f"{key_prefix}_login_form"):
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            
            if submit:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    user_id = res.user.id
                    
                    profile_res = supabase.table("profiles").select("*").eq("id", user_id).execute()
                    if profile_res.data:
                        st.session_state.user = res.user
                        st.session_state.profile = profile_res.data[0]
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Perfil de usuário não localizado.")
                except Exception as e:
                    st.error(f"Erro ao fazer login: {e}")

    # --- TAB CADASTRO ---
    with tab_signup:
        with st.form(f"{key_prefix}_signup_form"):
            name = st.text_input("Nome Completo*")
            email = st.text_input("E-mail*")
            password = st.text_input("Senha (mínimo 6 caracteres)*", type="password")
            user_type = st.selectbox("Tipo de Perfil*", ["Profissional de Saúde", "Gestor de Saúde"])
            ubs = st.text_input("Unidade / Secretaria de Saúde", placeholder="Ex: UBS Centro")

            submit_signup = st.form_submit_button("Cadastrar", type="primary")

        if submit_signup:
            if not name or not email or not password:
                st.error("Preencha todos os campos obrigatórios (*).")
            else:
                try:
                    role_value = "gestor" if user_type == "Gestor de Saúde" else "profissional"

                    auth_res = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                "name": name,
                                "role": role_value,
                                "ubs": ubs
                            }
                        }
                    })

                    st.success("✔ Conta criada com sucesso! Faça login.")
                except Exception as e:
                    st.error(f"Erro ao criar conta: {e}")

def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None
    st.session_state.profile = None
    st.rerun()

ACTIVE_PROJECTS = [
    {
        "title": "Fluxo Vivo — Triagem Inteligente",
        "phase": "Prototipação",
        "progress": 68,
        "ubs": "UBS Jardim das Acácias",
        "squad": "4 pessoas",
    },
    {
        "title": "Plantão Conectado",
        "phase": "Ideação",
        "progress": 35,
        "ubs": "UBS Centro Integrado",
        "squad": "3 pessoas",
    },
]

def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            :root {
                --primary: #0e4146;
                --primary-light: #166461;
                --accent: #7be7c3;
                --accent-text: #092c2f;
                --bg: #f4f8f7;
                --card: #ffffff;
                --muted: #5b7394;
            }

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            .stApp {
                background: linear-gradient(180deg, #f0f7f6 0%, #ffffff 40%, #eef5f4 100%);
            }

            [data-testid="stHeader"] { background: transparent; }

            /* Sobrescreve os botões "Primary" com a cor Menta/Teal do layout */
            .stButton > button[kind="primary"] {
                background: var(--accent) !important;
                border: 0 !important;
                color: var(--accent-text) !important;
                font-weight: 800 !important;
                box-shadow: 0 4px 10px rgba(123, 231, 195, 0.3);
            }
            .stButton > button[kind="primary"]:hover {
                background: #5cdbae !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "nav_page": "Página Principal",
        "accepted": [],
        "ratings": {},
        "current_challenge": None,
        "proposed_solutions": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def page_dashboard() -> None:
    profile = st.session_state.get("profile", {})
    user_name = profile.get("name", USER_NAME)

    # NOVO CABEÇALHO (Com o texto exato da imagem)
    st.markdown(
        f"""
        <div class="hero">
            <div class="brand-mark">INOVAÇÃO • CONHECIMENTO • IMPACTO</div>
            <h1 style="font-size: 2.8rem; font-weight: 800; line-height: 1.1; margin: 1rem 0;">
                Ideias que transformam.<br>Conexões que fazem<br>o SUS avançar.
            </h1>
            <p style="font-size: 1.15rem; line-height: 1.6; max-width: 650px; opacity: 0.95; margin-bottom: 0;">
                Uma rede colaborativa que aproxima os desafios reais dos serviços públicos de saúde do conhecimento acadêmico e da inovação social.
            </p>
        </div>
        <p style="color: #0e4146; font-size: 1.1rem; font-weight: 600;">Bem-vindo(a) de volta, {user_name}!</p>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Impactômetro")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Horas dedicadas", "128 h", "+12 h este mês")
    m2.metric("Desafios resolvidos", "7", "+2 no trimestre")
    m3.metric("Projetos ativos", str(len(ACTIVE_PROJECTS)), "em andamento")
    m4.metric("Impacto estimado", "2.4k usuários", "+18%")

    st.subheader("Ações rápidas")
    a1, a2, a3 = st.columns(3)
    if a1.button("Novo desafio", key="btn_dash_novo", use_container_width=True, type="primary"):
        st.session_state["go_mural"] = True
        st.rerun()
    if a2.button("Abrir trilha / Desafio Atual", key="btn_dash_trilha", use_container_width=True):
        st.session_state.nav_page = "Desafio em Andamento"
        st.rerun()
    if a3.button("Ver vitrine", key="btn_dash_vitrine", use_container_width=True):
        st.session_state.nav_page = "Vitrine de Soluções"
        st.rerun()

    st.subheader("Projetos ativos")
    cols = st.columns(3)
    for i, project in enumerate(ACTIVE_PROJECTS):
        col_idx = i % 3
        title = project.get("title") or "Projeto sem título"
        phase = project.get("phase") or "Em andamento"
        ubs = project.get("ubs") or "Unidade de Saúde"
        squad = project.get("squad") or "Equipe"
        progress = project.get("progress", 0)

        with cols[col_idx]:
            st.markdown(
                f"""
                <div class="card">
                    <span class="tag">{phase}</span>
                    <h4 style="margin:0.45rem 0 0.2rem 0;color:#0e4146;">{title}</h4>
                    <p style="color:#5b7394;font-size:0.9rem;">{ubs} · {squad}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(progress / 100 if progress <= 100 else 1.0, text=f"{progress}% concluído")


def page_challenges() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Mural de Desafios</div>
            <h1>Problemas Reais dos Serviços</h1>
            <p>Encontre um desafio de unidade, veja detalhes do problema e aceite com o seu grupo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("➕ Cadastrar Novo Desafio do SUS", expanded=False):
        with st.form("new_challenge_form", clear_on_submit=True):
            st.subheader("Registrar Nova Dor da Unidade")
            f_title = st.text_input("Título do Desafio*", placeholder="Ex: Demora na entrega de exames laboratoriais")
            
            col_a, col_b = st.columns(2)
            with col_a:
                f_ubs = st.text_input("Unidade de Saúde (UBS)*", placeholder="Ex: UBS Vila Maria")
            with col_b:
                f_city = st.text_input("Cidade/UF*", placeholder="Ex: Recife/PE")
            
            col_c, col_d = st.columns(2)
            with col_c:
                f_areas = st.multiselect(
                    "Áreas Afetadas*",
                    ["Triagem", "Gestão", "Comunicação", "Atenção Materna", "Atendimento", "Insumos", "Farmácia"],
                    default=["Gestão"]
                )
            with col_d:
                f_priority = st.selectbox("Prioridade*", ["Média", "Alta", "Baixa"])

            f_pain = st.text_area("Detalhamento da Dor (O que acontece hoje?)*", placeholder="Descreva o problema observado na rotina da unidade...")

            submitted = st.form_submit_button("Enviar Desafio para o Mural", type="primary", use_container_width=True)

            if submitted:
                if not f_title or not f_ubs or not f_city or not f_pain:
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    try:
                        new_data = {
                            "title": f_title,
                            "ubs": f_ubs,
                            "city": f_city,
                            "area": f_areas,
                            "pain": f_pain,
                            "priority": f_priority,
                        }
                        supabase.table("desafios").insert(new_data).execute()
                        st.success("✅ Desafio cadastrado com sucesso no Supabase!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar desafio no Supabase: {e}")

    st.markdown("---")

    challenges_list = get_challenges()
    search = st.text_input("Pesquisar desafio, UBS ou cidade")
    f1, f2 = st.columns(2)

    units = sorted({item["ubs"] for item in challenges_list if "ubs" in item and item["ubs"]})
    areas = sorted({
        tag for item in challenges_list if "area" in item and isinstance(item["area"], list) 
        for tag in item["area"]
    })

    unit_filter = f1.selectbox("Unidade de Saúde", ["Todas"] + units)
    area_filter = f2.multiselect("Área", areas, default=[])

    filtered = []
    query = search.strip().lower()
    for item in challenges_list:
        title = item.get("title", "")
        ubs = item.get("ubs", "")
        city = item.get("city", "")
        item_areas = item.get("area", [])
        
        text = f"{title} {ubs} {city}".lower()
        if query and query not in text:
            continue
        if unit_filter != "Todas" and ubs != unit_filter:
            continue
        if area_filter and not set(area_filter).intersection(item_areas):
            continue
        filtered.append(item)

    if not filtered:
        st.info("Nenhum desafio encontrado com esses filtros.")
        return

    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for col, item in zip(cols, filtered[i : i + 2]):
            with col:
                item_id = str(item.get("id", i))
                item_title = item.get("title", "Sem título")
                item_ubs = item.get("ubs", "N/A")
                item_city = item.get("city", "N/A")
                item_pain = item.get("pain", "Sem detalhamento disponível.")
                item_priority = item.get("priority", "Média")
                item_areas = item.get("area", [])
                
                if isinstance(item_areas, str):
                    item_areas = [item_areas]

                tags = "".join(f'<span class="tag">{tag}</span>' for tag in item_areas)
                alert = '<span class="tag tag-alert">Prioridade alta</span>' if item_priority == "Alta" else ""
                accepted = item_id in st.session_state.get("accepted", [])

                st.markdown(
                    f"""
                    <div class="card">
                        {tags}{alert}
                        <h4 style="color:#0e4146;margin:0.6rem 0 0.2rem 0;">{item_title}</h4>
                        <p style="color:#5b7394;font-size:0.9rem;">{item_ubs} · {item_city}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns(2)
                if b1.button("Detalhar Dor", key=f"pain_{item_id}", use_container_width=True):
                    st.info(item_pain)
                label = "Desafio aceito" if accepted else "Aceitar Desafio"
                if b2.button(label, key=f"accept_{item_id}", use_container_width=True, type="primary"):
                    if "accepted" not in st.session_state:
                        st.session_state.accepted = []
                    if item_id not in st.session_state.accepted:
                        st.session_state.accepted.append(item_id)
                    
                    st.session_state.current_challenge = item
                    st.session_state.nav_page = "Desafio em Andamento"
                    st.rerun()


# ---------------------------------------------------------
# PÁGINA: DESAFIO EM ANDAMENTO
# ---------------------------------------------------------
def page_active_challenge() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Desafio em Andamento</div>
            <h1>Seu Projeto Atual</h1>
            <p>Acompanhe o desafio selecionado, detalhe sua proposta e envie a solução final.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    challenge = st.session_state.get("current_challenge")
    
    if not challenge:
        st.info("⚠️ Você ainda não aceitou nenhum desafio. Vá ao Mural de Desafios para começar.")
        if st.button("Ir para o Mural de Desafios", type="primary"):
            st.session_state.nav_page = "Mural de Desafios"
            st.rerun()
        return

    st.markdown(f"### Desafio: {challenge.get('title', 'Sem Título')}")
    st.markdown(f"**📍 Unidade:** {challenge.get('ubs', 'Não informada')} · {challenge.get('city', '')}")
    st.markdown(f"**🔴 Dor Mapeada:** {challenge.get('pain', 'Sem detalhamento.')}")
    st.markdown("---")
    
    st.subheader("💡 Cadastrar Solução Proposta")
    st.write("Tem uma ideia para resolver este problema? Detalhe a sua solução e anexe o projeto da sua equipe.")
    
    with st.form("solution_proposal_form", clear_on_submit=True):
        sol_title = st.text_input("Nome da Solução*", placeholder="Dê um nome criativo e claro para a sua solução")
        sol_desc = st.text_area("Detalhamento da Solução*", placeholder="Como a sua solução resolve o problema apontado na dor mapeada?", height=120)
        
        sol_file = st.file_uploader("Anexar Arquivo do Projeto (Apresentação, PDF, Zip, etc)")
        
        submit_btn = st.form_submit_button("Enviar Solução para a Vitrine", type="primary")
        
        if submit_btn:
            if not sol_title or not sol_desc:
                st.error("Preencha o nome e o detalhamento da solução antes de enviar.")
            else:
                file_data = None
                file_name = None
                if sol_file is not None:
                    file_data = sol_file.getvalue()
                    file_name = sol_file.name

                author_name = st.session_state.get("profile", {}).get("name", "Equipe InovaSUS")
                
                new_solution = {
                    "title": sol_title,
                    "category": challenge.get("area", ["Solução Inovadora"])[0] if challenge.get("area") else "Inovação",
                    "author": author_name,
                    "challenge_title": challenge.get('title', ''),
                    "desc": sol_desc,
                    "impact": "Projeto Submetido (Em avaliação)",
                    "status": "Em Avaliação",
                    "file_data": file_data,
                    "file_name": file_name
                }
                
                st.session_state.proposed_solutions.append(new_solution)
                st.success("✅ Solução cadastrada com sucesso! Ela já está disponível na Vitrine.")


def page_solutions() -> None:
    # CABEÇALHO PADRONIZADO DA VITRINE
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Vitrine de Soluções</div>
            <h1 style="margin: 0 0 0.5rem 0;">Vitrine de Soluções</h1>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.95;">
                Explore as soluções e inovações aplicadas para transformar os serviços de saúde.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    base_solutions = [
        {
            "title": "Triagem Digital SUS",
            "category": "Atendimento & Triagem",
            "author": "Dr. Carlos Eduardo (SMS Mossoró)",
            "impact": "Redução de 35% no tempo de espera",
            "desc": "Sistema interativo para pré-classificação de risco antes do atendimento presencial nas UBSs.",
            "status": "Em Produção"
        },
        {
            "title": "Gestor de Estoque de Insumos",
            "category": "Logística & Farmácia",
            "author": "Maria Lúcia (Enfermeira)",
            "impact": "Zera desperdício por validade em 6 meses",
            "desc": "Painel de alertas para controle de validade e transferência de medicação entre unidades da rede.",
            "status": "Piloto Ativo"
        }
    ]

    user_proposed = st.session_state.get("proposed_solutions", [])
    all_solutions = base_solutions + user_proposed

    categories = ["Todas"] + list(set(s["category"] for s in all_solutions))
    selected_cat = st.selectbox("Filtrar por Categoria:", categories)

    if selected_cat != "Todas":
        filtered_solutions = [s for s in all_solutions if s["category"] == selected_cat]
    else:
        filtered_solutions = all_solutions

    st.markdown("---")

    if not filtered_solutions:
        st.info("Nenhuma solução encontrada nesta categoria.")
        return

    cols = st.columns(2)
    for index, sol in enumerate(filtered_solutions):
        col_idx = index % 2
        with cols[col_idx]:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 5px solid #166461; box-shadow: 0 4px 10px rgba(0,0,0,0.04); margin-bottom: 20px;">
                        <span style="background-color: #d9f6eb; color: #0e4146; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px;">{sol['category']}</span>
                        <h3 style="margin-top: 10px; margin-bottom: 5px; color: #0e4146;">{sol['title']}</h3>
                        <p style="font-size: 13px; color: #64748b; margin-bottom: 5px;">👥 <b>Equipe/Responsável:</b> {sol['author']}</p>
                        <p style="font-size: 14px; color: #334155; margin-bottom: 10px;">{sol['desc']}</p>
                        <div style="background-color: #f8fafc; padding: 8px 12px; border-radius: 8px; margin-top: 10px;">
                            <span style="font-size: 13px; color: #16a34a; font-weight: bold;">📈 Impacto: {sol['impact']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                with st.expander("🔍 Ver detalhes da solução"):
                    st.write(f"**Status atual:** {sol['status']}")
                    if sol.get("challenge_title"):
                        st.write(f"**Resolve o Desafio:** {sol['challenge_title']}")
                    
                    st.button("Entrar em contato com o autor", key=f"btn_sol_{index}")
                    
                    if sol.get("file_data") and sol.get("file_name"):
                        st.download_button(
                            label=f"⬇️ Baixar Arquivo ({sol['file_name']})",
                            data=sol["file_data"],
                            file_name=sol["file_name"],
                            key=f"download_file_{index}"
                        )

def render_ranking_page():
    st.header("🏆 Ranking de Soluções dos Alunos")
    try:
        res = supabase.table("ranking_alunos").select("*").execute()
        if res.data:
            st.dataframe(
                res.data,
                column_config={
                    "nome_aluno": "Aluno / Squad",
                    "instituicao": "Unidade / UBS",
                    "total_votos": "Total de Avaliações",
                    "media_nota": st.column_config.NumberColumn("Média", format="%.1f"),
                    "pontuacao_total": "Pontuação Total",
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("Nenhum dado cadastrado no ranking.")
    except Exception:
        st.info("Ranking de soluções em processamento.")

# ---------------------------------------------------------
# PÁGINA: EDITAR PERFIL
# ---------------------------------------------------------
def page_edit_profile():
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Configurações</div>
            <h1>Editar Perfil</h1>
            <p>Mantenha seus dados atualizados para facilitar o contato com outros profissionais.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    profile = st.session_state.get("profile", {})
    
    with st.form("form_edit_profile"):
        st.subheader("Seus Dados")
        new_name = st.text_input("Nome Completo", value=profile.get("name", ""))
        new_ubs = st.text_input("Unidade / Secretaria de Saúde", value=profile.get("ubs", ""))
        
        submit = st.form_submit_button("Salvar Alterações", type="primary")
        
        if submit:
            try:
                user_id = st.session_state.user.id
                supabase.table("profiles").update({
                    "name": new_name,
                    "ubs": new_ubs
                }).eq("id", user_id).execute()
                
                st.session_state.profile["name"] = new_name
                st.session_state.profile["ubs"] = new_ubs
                st.success("Perfil atualizado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao atualizar perfil: {e}")
                
    st.write("")
    if st.button("⬅ Voltar para o Início"):
        st.session_state.nav_page = "Página Principal"
        st.rerun()

# ==========================================
# FUNÇÃO PRINCIPAL (MAIN) E NAVEGAÇÃO
# ==========================================

def main():
    inject_styles()
    init_state()

    # Se não estiver logado, exibe a tela de login
    if "user" not in st.session_state or st.session_state.user is None:
        render_auth_page()
        return

    profile = st.session_state.get("profile", {})
    user_name = profile.get("name", "Usuário")

    # ---------------------------------------------------------
    # CABEÇALHO SUPERIOR (Navegação + Perfil)
    # ---------------------------------------------------------
    pages_list = [
        "Página Principal", 
        "Mural de Desafios", 
        "Desafio em Andamento", 
        "Vitrine de Soluções", 
        "🏆 Ranking"
    ]

    col_nav, col_profile = st.columns([5, 1])
    
    with col_profile:
        with st.popover(f"👤 {user_name}"):
            if st.button("✏️ Editar Perfil", use_container_width=True):
                st.session_state.nav_page = "Editar Perfil"
                st.rerun()
            if st.button("🚪 Sair", use_container_width=True):
                logout()

    with col_nav:
        if st.session_state.get("go_mural"):
            st.session_state.nav_page = "Mural de Desafios"
            st.session_state.go_mural = False
            
        current_nav = st.session_state.get("nav_page", "Página Principal")

        if current_nav != "Editar Perfil":
            idx = pages_list.index(current_nav) if current_nav in pages_list else 0
            
            selected_page = st.radio(
                "Navegação Principal", 
                pages_list, 
                index=idx, 
                horizontal=True, 
                label_visibility="collapsed"
            )
            
            st.session_state.nav_page = selected_page
        else:
            selected_page = "Editar Perfil"

    st.markdown("---")

    # ---------------------------------------------------------
    # ROTEAMENTO DE PÁGINAS
    # ---------------------------------------------------------
    if selected_page == "Página Principal":
        page_dashboard()
    elif selected_page == "Mural de Desafios":
        page_challenges()
    elif selected_page == "Desafio em Andamento":
        page_active_challenge()
    elif selected_page == "Vitrine de Soluções":
        page_solutions()
    elif selected_page == "🏆 Ranking":
        render_ranking_page()
    elif selected_page == "Editar Perfil":
        page_edit_profile()


if __name__ == "__main__":
    main()