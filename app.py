import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="InovaSUS Connect",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 1. ESTILO CSS CUSTOMIZADO (Cores Azuis e Cards)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
/* Estilização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #0b3d91 !important;
    }

    /* Força TODOS os textos da barra lateral a ficarem em BRANCO visível */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }

    /* APENAS o Botão de Logout fica com fundo azul escuro */
    div[data-testid="stSidebar"] div.stButton > button {
        background-color: #051937 !important;
        color: #ffffff !important;
        border: 1px solid #004d7a !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #004d7a !important;
        color: #ffffff !important;
    }

    /* Estilização dos Cards e Hero */
    .hero {
        background: linear-gradient(135deg, #0b3d91 0%, #1e5bb8 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .brand-mark {
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    .card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #0b3d91;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
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
# FUNÇÕES DE AUTENTICAÇÃO E LOGIN (Insira a partir daqui)
# ---------------------------------------------------------
def render_auth_page(key_prefix: str = "main"):
    st.markdown("## 🩺 InovaSUS Connect - Acesso")
    
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
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.profile = None
    st.rerun()

ACTIVE_PROJECTS = [
    {
        "name": "Fluxo Vivo — Triagem Inteligente",
        "phase": "Prototipação",
        "progress": 68,
        "ubs": "UBS Jardim das Acácias",
        "squad": "4 pessoas",
    },
    {
        "name": "Plantão Conectado",
        "phase": "Ideação",
        "progress": 35,
        "ubs": "UBS Centro Integrado",
        "squad": "3 pessoas",
    },
    {
        "name": "Cuidar+",
        "phase": "Validação",
        "progress": 82,
        "ubs": "UBS Nova Esperança",
        "squad": "5 pessoas",
    },
]

TALENTS = [
    {
        "name": "Dr. Lucas Mendes",
        "role": "Médico de Família",
        "skills": ["Triagem", "Protocolos", "Mentoria"],
        "unit": "UBS Centro Integrado",
        "match": 94,
    },
    {
        "name": "Marina Costa",
        "role": "Designer de Serviço",
        "skills": ["UX em Saúde", "Prototipação", "Facilitação"],
        "unit": "Núcleo de Inovação SES",
        "match": 91,
    },
    {
        "name": "Paulo Henrique",
        "role": "Analista de Dados SUS",
        "skills": ["Indicadores", "Python", "Gestão"],
        "unit": "SMS Recife",
        "match": 88,
    },
    {
        "name": "Dra. Camila Rocha",
        "role": "Enfermeira Obstetra",
        "skills": ["Atenção Materna", "Acolhimento", "Validação"],
        "unit": "UBS Nova Esperança",
        "match": 86,
    },
]

OPEN_VACANCIES = [
    {"team": "Fluxo Vivo", "role": "Facilitador clínico", "need": "Empatia + protocolos de Manchester"},
    {"team": "Plantão Conectado", "role": "Dev front-end", "need": "Protótipo web de handover"},
    {"team": "Cuidar+", "role": "Agente comunitário", "need": "Validação em território"},
]

TRAIL_PHASES = [
    {
        "name": "Empatia",
        "number": 1,
        "status": "Concluída",
        "desc": "Imersão na unidade, escuta da equipe e mapeamento da jornada do paciente.",
    },
    {
        "name": "Ideação",
        "number": 2,
        "status": "Concluída",
        "desc": "Geração de ideias com o squad e priorização das apostas de maior impacto.",
    },
    {
        "name": "Prototipação",
        "number": 3,
        "status": "Em andamento",
        "desc": "Construção do Canvas Clínico e teste rápido de fluxos na UBS.",
    },
    {
        "name": "Validação",
        "number": 4,
        "status": "Próxima",
        "desc": "Piloto assistido, indicadores de impacto e decisão de escala.",
    },
]

SOLUTIONS = [
    {
        "title": "Pulseira de Prioridade Visual",
        "ubs": "UBS Jardim das Acácias",
        "summary": "Sistema de pulseiras coloridas + painel de espera que reduz o tempo até a classificação de risco e deixa o fluxo transparente para o usuário.",
        "impact": "−38% no tempo de espera da triagem",
        "video": "https://www.w3schools.com/html/mov_bbb.mp4",
    },
    {
        "title": "Handover 360",
        "ubs": "UBS Centro Integrado",
        "summary": "Checklist digital de passagem de plantão com alertas de condutas críticas e histórico de 24h da unidade.",
        "impact": "−62% de falhas de comunicação entre turnos",
        "video": "https://www.w3schools.com/html/movie.mp4",
    },
    {
        "title": "Gestante Presente",
        "ubs": "UBS Nova Esperança",
        "summary": "Roteiro de reengajamento para faltosas de alto risco, com ACS, WhatsApp institucional e agenda protegida.",
        "impact": "+27% de adesão ao pré-natal de alto risco",
        "video": "https://www.w3schools.com/html/mov_bbb.mp4",
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            :root {
                --navy: #0b3d91;
                --blue: #1565c0;
                --sky: #1e88e5;
                --ice: #eef5ff;
                --card: #ffffff;
                --ink: #123056;
                --muted: #5b7394;
            }

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            .stApp {
                background: linear-gradient(180deg, #f4f8ff 0%, #ffffff 38%, #eaf2ff 100%);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0b3d91 0%, #1457c7 58%, #1e88e5 100%);
            }

            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                color: #ffffff !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                background: rgba(255, 255, 255, 0.12) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
                text-align: left;
                justify-content: flex-start;
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background: #ffffff !important;
                color: #0b3d91 !important;
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"] p,
            [data-testid="stSidebar"] .stButton > button[kind="primary"] span {
                color: #0b3d91 !important;
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            .hero {
                background: linear-gradient(135deg, #0b3d91 0%, #1565c0 52%, #42a5f5 100%);
                color: #fff;
                padding: 1.6rem 1.8rem;
                border-radius: 22px;
                margin-bottom: 1.2rem;
                box-shadow: 0 16px 40px rgba(11, 61, 145, 0.22);
            }

            .hero h1 {
                margin: 0 0 0.35rem 0;
                font-size: 1.85rem;
                letter-spacing: -0.03em;
            }

            .hero p {
                margin: 0;
                opacity: 0.92;
            }

            .brand-mark {
                font-size: 0.78rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }

            .card {
                background: var(--card);
                border: 1px solid #d7e6fb;
                border-radius: 18px;
                padding: 1.15rem 1.2rem;
                box-shadow: 0 8px 24px rgba(21, 101, 192, 0.08);
                height: 100%;
            }

            .tag {
                display: inline-block;
                background: #e3f0ff;
                color: #0b3d91;
                border-radius: 999px;
                padding: 0.18rem 0.7rem;
                font-size: 0.75rem;
                font-weight: 700;
                margin-right: 0.35rem;
                margin-bottom: 0.25rem;
            }

            .tag-alert {
                background: #ffe8e8;
                color: #b42318;
            }

            .muted {
                color: var(--muted);
                font-size: 0.9rem;
            }

            .progress-wrap {
                display: flex;
                gap: 0.6rem;
                margin: 1rem 0 1.4rem 0;
            }

            .phase {
                flex: 1;
                background: #fff;
                border: 2px solid #c9ddf8;
                border-radius: 16px;
                padding: 0.9rem;
                text-align: center;
            }

            .phase.done {
                background: #0b3d91;
                color: #fff;
                border-color: #0b3d91;
            }

            .phase.current {
                background: #e8f3ff;
                border-color: #1565c0;
            }

            .phase .num {
                font-weight: 800;
                font-size: 1.2rem;
            }

            .vacancy {
                background: #f7fbff;
                border-left: 4px solid #1565c0;
                padding: 0.85rem 1rem;
                border-radius: 12px;
                margin-bottom: 0.7rem;
            }

            div[data-testid="stMetric"] {
                background: #fff;
                border: 1px solid #d7e6fb;
                border-radius: 18px;
                padding: 0.9rem 1rem;
                box-shadow: 0 8px 24px rgba(21, 101, 192, 0.08);
            }

            .stButton > button {
                border-radius: 12px;
                font-weight: 700;
                border: 1px solid #1565c0;
            }

            .stButton > button[kind="primary"] {
                background: linear-gradient(90deg, #0b3d91, #1e88e5);
                border: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "page": "Dashboard Principal",
        "accepted": [],
        "invites": [],
        "ratings": {},
        "pilots": [],
        "mentoria": False,
        "canvas": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sidebar_nav() -> str:
    # 1. Se o usuário não estiver logado, oculta a sidebar completamente
    if not st.session_state.get("user"):
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)
        return ""

    # 2. Se o usuário estiver logado, desenha a barra lateral
    with st.sidebar:
        st.markdown("### InovaSUS Connect")
        
        user_name = st.session_state.get("profile", {}).get("name", "Usuário")
        user_role = st.session_state.get("profile", {}).get("role", "Profissional de Saúde")
        
        st.markdown(f"**Bem-vindo(a), {user_name}!**")
        st.caption(f"📌 {user_role}")
        st.markdown("---")

        st.markdown("**Navegação**")

        pages = [
            "Dashboard Principal",
            "Mural de Desafios",
            "Radar de Talentos",
            "Workspace da Trilha",
            "Vitrine de Soluções",
            "🏆 Ranking"
        ]

        if "page" not in st.session_state:
            st.session_state.page = "Mural de Desafios"

        selected_page = st.radio(
            "Navegação",
            pages,
            index=pages.index(st.session_state.page) if st.session_state.page in pages else 1,
            label_visibility="collapsed"
        )
        st.session_state.page = selected_page

        st.markdown("---")

        # Botão de Sair escuro nativo do Streamlit (type="primary")
        if st.button("🚪 Sair (Logout)", key="btn_logout_sidebar", use_container_width=True, type="primary"):
            logout()

    return st.session_state.page
def page_dashboard() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="brand-mark">InovaSUS Connect</div>
            <h1>Olá, {USER_NAME}</h1>
            <p>Sua rede de inovação na Atenção Primária está ativa. Continue gerando impacto clínico com o seu squad.</p>
        </div>
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
    a1, a2, a3, a4 = st.columns(4)
    if a1.button("Novo desafio", use_container_width=True, type="primary"):
        st.session_state["go_mural"] = True
        st.toast("Abra o Mural de Desafios na barra lateral para publicar ou aceitar.")
    if a2.button("Montar squad", use_container_width=True):
        st.toast("Use o Radar de Talentos para convidar colegas.")
    if a3.button("Abrir trilha", use_container_width=True):
        st.toast("A trilha está na fase de Prototipação.")
    if a4.button("Ver vitrine", use_container_width=True):
        st.toast("Confira soluções prontas para piloto.")

    st.subheader("Projetos ativos")
    cols = st.columns(3)
    for i, project in enumerate(ACTIVE_PROJECTS):
        with cols[i]:
            st.markdown(
                f"""
                <div class="card">
                    <span class="tag">{project['phase']}</span>
                    <h4 style="margin:0.45rem 0 0.2rem 0;color:#0b3d91;">{project['name']}</h4>
                    <p class="muted">{project['ubs']} · {project['squad']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(project["progress"] / 100, text=f"{project['progress']}% da trilha")

def page_challenges() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Mural de Desafios</div>
            <h1>Problemas Reais dos Serviços</h1>
            <p>Encontre um desafio de unidade, detalhe a dor e aceite com o seu squad.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # FORMULÁRIO DE CADASTRO DE NOVO DESAFIO (SUPABASE)
    # ---------------------------------------------------------
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
                        # Prepara os dados para inserir na tabela 'desafios' do Supabase
                        new_data = {
                            "title": f_title,
                            "ubs": f_ubs,
                            "city": f_city,
                            "area": f_areas,
                            "pain": f_pain,
                            "priority": f_priority,
                        }
                        # Executa o INSERT
                        supabase.table("desafios").insert(new_data).execute()
                        st.success("✅ Desafio cadastrado com sucesso no Supabase!")
                        st.rerun()  # Recarrega a página para exibir o novo card imediatamente
                    except Exception as e:
                        st.error(f"Erro ao cadastrar desafio no Supabase: {e}")

    st.markdown("---")

    # ---------------------------------------------------------
    # CONSULTA E EXIBIÇÃO DOS DESAFIOS (SUPABASE)
    # ---------------------------------------------------------
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

    # Renderização dos Cards
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
                        <h4 style="color:#0b3d91;margin:0.6rem 0 0.25rem 0;">{item_title}</h4>
                        <p class="muted">{item_ubs} · {item_city}</p>
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
                        st.session_state.accepted = [*st.session_state.accepted, item_id]
                    st.success(f"Você aceitou o desafio de {item_ubs}.")

def page_talents() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Radar de Talentos</div>
            <h1>Conecte quem resolve</h1>
            <p>Busque habilidades, convide para o squad e acompanhe vagas abertas nas equipes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    skill_options = sorted({skill for person in TALENTS for skill in person["skills"]})
    selected_skills = st.multiselect("Buscar por habilidades", skill_options)
    name_query = st.text_input("Buscar por nome ou unidade")

    suggested = []
    q = name_query.strip().lower()
    for person in TALENTS:
        haystack = f"{person['name']} {person['role']} {person['unit']}".lower()
        if q and q not in haystack:
            continue
        if selected_skills and not set(selected_skills).intersection(person["skills"]):
            continue
        suggested.append(person)

    st.subheader("Perfis sugeridos")
    cols = st.columns(2)
    for i, person in enumerate(suggested):
        with cols[i % 2]:
            tags = "".join(f'<span class="tag">{skill}</span>' for skill in person["skills"])
            invited = person["name"] in st.session_state.invites
            st.markdown(
                f"""
                <div class="card">
                    <p class="muted" style="margin:0;">Match {person['match']}%</p>
                    <h4 style="color:#0b3d91;margin:0.2rem 0;">{person['name']}</h4>
                    <p class="muted">{person['role']} · {person['unit']}</p>
                    {tags}
                </div>
                """,
                unsafe_allow_html=True,
            )
            label = "Convite enviado" if invited else "Convidar para o Squad"
            if st.button(label, key=f"invite_{i}", use_container_width=True, type="primary"):
                if person["name"] not in st.session_state.invites:
                    st.session_state.invites = [*st.session_state.invites, person["name"]]
                st.success(f"Convite enviado para {person['name']}.")

    if not suggested:
        st.info("Nenhum perfil encontrado. Amplie as habilidades da busca.")

    st.subheader("Vagas em Equipes")
    for vacancy in OPEN_VACANCIES:
        st.markdown(
            f"""
            <div class="vacancy">
                <strong>{vacancy['team']}</strong> · {vacancy['role']}<br>
                <span class="muted">{vacancy['need']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_workspace() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Workspace da Trilha</div>
            <h1>Fluxo Vivo — Triagem Inteligente</h1>
            <p>Trilha de inovação em 4 fases, do olhar da ponta até a validação clínica.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    phase_html = '<div class="progress-wrap">'
    for phase in TRAIL_PHASES:
        css = "phase"
        if phase["status"] == "Concluída":
            css += " done"
        elif phase["status"] == "Em andamento":
            css += " current"
        phase_html += (
            f'<div class="{css}">'
            f'<div class="num">{phase["number"]}</div>'
            f'<div>{phase["name"]}</div>'
            f'<small>{phase["status"]}</small>'
            "</div>"
        )
    phase_html += "</div>"
    st.markdown(phase_html, unsafe_allow_html=True)
    st.progress(0.68, text="68% da trilha concluída")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Abrir Canvas Clínico", use_container_width=True, type="primary"):
            st.session_state.canvas = True
        if st.session_state.canvas:
            st.markdown(
                """
                <div class="card">
                    <h4 style="color:#0b3d91;margin-top:0;">Canvas Clínico</h4>
                    <p><strong>Usuário:</strong> paciente da triagem matutina</p>
                    <p><strong>Dor:</strong> espera longa e opaca</p>
                    <p><strong>Aposta:</strong> sinalização visual + protocolo de priorização</p>
                    <p><strong>Prova:</strong> tempo até classificação e NPS da recepção</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with c2:
        if st.button("Agendar Mentoria", use_container_width=True):
            st.session_state.mentoria = True
        if st.session_state.mentoria:
            date = st.date_input("Data da mentoria")
            slot = st.selectbox("Horário", ["09:00", "11:00", "14:00", "16:30"])
            if st.button("Confirmar mentoria", type="primary"):
                st.success(f"Mentoria confirmada em {date.strftime('%d/%m/%Y')} às {slot}.")

    st.subheader("Fases da trilha")
    for phase in TRAIL_PHASES:
        with st.expander(f"{phase['number']}. {phase['name']} — {phase['status']}"):
            st.write(phase["desc"])


def page_showcase() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="brand-mark">Vitrine de Soluções</div>
            <h1>O que já funciona na rede</h1>
            <p>Assista ao pitch, avalie a solução e solicite um piloto para a sua unidade.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, solution in enumerate(SOLUTIONS):
        with st.container():
            col_video, col_info = st.columns([1.1, 1])
            with col_video:
                st.video(solution["video"])
            with col_info:
                st.markdown(
                    f"""
                    <div class="card">
                        <span class="tag">Solução validada</span>
                        <h3 style="color:#0b3d91;margin:0.4rem 0;">{solution['title']}</h3>
                        <p class="muted">{solution['ubs']}</p>
                        <p>{solution['summary']}</p>
                        <p><strong>Impacto:</strong> {solution['impact']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                rating = st.slider(
                    "Avaliação por estrelas",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.ratings.get(solution["title"], 4),
                    key=f"rate_{i}",
                    help="1 estrela = pouco útil · 5 estrelas = pronta para escala",
                )
                st.session_state.ratings[solution["title"]] = rating
                st.caption("★" * rating + "☆" * (5 - rating))
                requested = solution["title"] in st.session_state.pilots
                label = "Piloto solicitado" if requested else "Solicitar Piloto"
                if st.button(label, key=f"pilot_{i}", type="primary"):
                    if solution["title"] not in st.session_state.pilots:
                        st.session_state.pilots = [*st.session_state.pilots, solution["title"]]
                    st.success(f"Solicitação de piloto enviada para {solution['title']}.")
            st.divider()


def main():
    # Se não estiver logado, exibe apenas a tela de login/cadastro
    if "user" not in st.session_state or st.session_state.user is None:
        st.markdown("""
            <style>
                [data-testid="stSidebar"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)
        render_auth_page()
        return

    # USUÁRIO LOGADO: Renderiza a barra lateral
    profile = st.session_state.get("profile", {})
    user_name = profile.get("name", "Usuário")
    user_role = "Gestor" if profile.get("role") == "gestor" else "Profissional de Saúde"
    user_ubs = profile.get("ubs", "N/A")

    st.sidebar.markdown("### 🏥 InovaSUS Connect")
    st.sidebar.markdown(f"**Bem-vindo(a), {user_name}!**")
    st.sidebar.caption(f"📌 {user_role} · {user_ubs}")
    st.sidebar.markdown("---")

    # Dicionário com TODAS as páginas ativas da aplicação
    pages = {
        "Mural de Desafios": render_mural_desafios if "render_mural_desafios" in globals() else page_challenges,
        "Dashboard Principal": page_dashboard if "page_dashboard" in globals() else lambda: st.info("Dashboard em desenvolvimento"),
        "Radar de Talentos": page_talents if "page_talents" in globals() else lambda: st.info("Radar de Talentos em desenvolvimento"),
        "Workspace da Trilha": lambda: st.info("Workspace da Trilha em desenvolvimento"),
        "Vitrine de Soluções": page_management if "page_management" in globals() else lambda: st.info("Vitrine de Soluções em desenvolvimento"),
        "🏆 Ranking": render_ranking_page
    }

    # Navegação na Sidebar
    page_selected = st.sidebar.radio("Navegação", list(pages.keys()))

    st.sidebar.markdown("---")

    # Botão de Logout nativo no rodapé da sidebar
    if st.sidebar.button("🚪 Sair (Logout)", key="btn_logout_main", use_container_width=True, type="primary"):
        logout()

    # Executa a função da página selecionada
    pages[page_selected]()
    
if __name__ == "__main__":
    main()

    import streamlit as st

# Exemplo de exibição do Ranking
def render_ranking_page():
    st.header("🏆 Ranking de Soluções dos Alunos")
    
    # Busca os dados calculados da VIEW do Supabase
    res = supabase.table("ranking_alunos").select("*").execute()
    
    if res.data:
        # Exibe em formato de tabela elegante
        st.dataframe(
            res.data,
            column_config={
                "nome_aluno": "Aluno / Squad",
                "instituicao": "Unidade / UBS",
                "total_votos": "Total de Avaliações",
                "media_nota": st.column_config.NumberColumn("Média", format="%.1f ⭐"),
                "pontuacao_total": "Pontuação Total"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhuma avaliação registrada ainda.")

# Exemplo de componente de Votação (Apenas para Gestores)
def render_votacao_gestor(solution_id, aluno_id):
    user_role = st.session_state.get("profile", {}).get("role")
    
    if user_role == "gestor":
        st.subheader("⭐ Avaliar esta Solução")
        nota = st.slider("Nota da solução (1 a 5)", 1, 5, 5, key=f"score_{solution_id}")
        
        if st.button("Enviar Voto", key=f"btn_{solution_id}"):
            try:
                gestor_id = st.session_state.user.id
                
                # Insere ou atualiza o voto do gestor
                supabase.table("votes").upsert({
                    "gestor_id": gestor_id,
                    "solution_id": solution_id,
                    "aluno_id": aluno_id,
                    "score": nota
                }).execute()
                
                st.success("Voto registrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar voto: {e}")