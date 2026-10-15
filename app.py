import streamlit as st
import yaml
import json
from pathlib import Path
from datetime import datetime
import hashlib
import base64
import requests

# Paths
BASE_DIR = Path(__file__).parent
CONTENT_FILE = BASE_DIR / "content" / "modules.yaml"
PROGRESS_FILE = BASE_DIR / "content" / "progress.json"
ASSETS_DIR = BASE_DIR / "assets"

# GitHub persistence (for Streamlit Cloud)
def get_github_config():
    try:
        return {
            "token": st.secrets["GITHUB_TOKEN"],
            "repo": st.secrets.get("GITHUB_REPO", "yourusername/rooted-workbook"),
            "branch": st.secrets.get("GITHUB_BRANCH", "main"),
            "file_path": "content/modules.yaml"
        }
    except Exception:
        return None

def save_to_github(content_str, commit_message="Update Rooted workbook content"):
    config = get_github_config()
    if not config:
        return False, "GitHub not configured (running locally or secrets missing)"

    url = f"https://api.github.com/repos/{config['repo']}/contents/{config['file_path']}"
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get current file SHA
    r = requests.get(url, headers=headers, params={"ref": config["branch"]})
    if r.status_code != 200:
        return False, f"Could not read file from GitHub: {r.status_code}"

    sha = r.json()["sha"]
    encoded = base64.b64encode(content_str.encode()).decode()

    data = {
        "message": commit_message,
        "content": encoded,
        "sha": sha,
        "branch": config["branch"]
    }

    r = requests.put(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        return True, "Saved to GitHub successfully"
    else:
        return False, f"GitHub save failed: {r.status_code} - {r.text}"

# Load content
def load_modules():
    if CONTENT_FILE.exists():
        with open(CONTENT_FILE, "r") as f:
            return yaml.safe_load(f)
    return {"modules": []}

def save_modules(data):
    # Always try local save first
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    try:
        with open(CONTENT_FILE, "w") as f:
            f.write(yaml_str)
    except Exception as e:
        st.warning(f"Local save failed: {e}")

    # Try GitHub save if configured
    success, msg = save_to_github(yaml_str, f"Update modules via Admin Panel - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if success:
        st.success(msg)
    elif "not configured" not in msg:
        st.info(msg)

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Simple password hashing for demo (in production use proper auth)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Demo users (change these!)
USERS = {
    "admin": {
        "name": "Tiaan Steenkamp",
        "password": hash_password("rooted2026"),  # Change this
        "role": "admin"
    },
    "demo": {
        "name": "Demo User",
        "password": hash_password("demo123"),
        "role": "user"
    }
}

def check_password(username, password):
    user = USERS.get(username)
    if user and user["password"] == hash_password(password):
        return user
    return None

# Page config
st.set_page_config(
    page_title="Rooted | Life Church Waterfall",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
<style>
    :root {
        --sage: #8AB698;
        --sage-dark: #6B8E6B;
        --sage-light: #A8D5A8;
    }
    .stApp {
        background-color: #ffffff;
    }
    .main-header {
        color: #6B8E6B;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .module-card {
        border-left: 4px solid #8AB698;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8faf8;
        border-radius: 0 8px 8px 0;
    }
    .completed {
        border-left-color: #2E8B57;
        background: #f0fff0;
    }
    div[data-testid="stSidebar"] {
        background-color: #f5f8f5;
    }
    .stButton>button {
        background-color: #8AB698;
        color: white;
        border: none;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #6B8E6B;
        color: white;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f5f0;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8AB698 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_module" not in st.session_state:
    st.session_state.current_module = -1

# Login page (this is the Open / Home page)
if not st.session_state.logged_in:
    # Full-width banner
    st.image(str(ASSETS_DIR / "home_banner.jpg"), use_container_width=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #6B8E6B; margin-top: -10px;'>Rooted</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555;'>Life Church Waterfall<br>A clear path of discipleship for new believers</p>", unsafe_allow_html=True)
        st.divider()
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user = check_password(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.current_module = -1  # Go to Home page after login
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.caption("Demo credentials: **admin** / rooted2026  |  **demo** / demo123")
        st.caption("Change passwords in the code before going live.")
    
    st.stop()

# Main app after login
user = st.session_state.user
modules_data = load_modules()
modules = modules_data.get("modules", [])
progress = load_progress()
user_progress = progress.get(user["name"], {})

# Sidebar
with st.sidebar:
    st.image(str(ASSETS_DIR / "sidebar_logo.png"), use_container_width=True)
    st.markdown(f"**Welcome, {user['name']}**")
    st.caption(f"Role: {user['role'].title()}")
    st.divider()
    
    st.markdown("### Modules")
    for i, mod in enumerate(modules):
        completed = user_progress.get(str(mod["id"]), {}).get("completed", False)
        icon = "✅" if completed else "○"
        if st.button(f"{icon} {mod['id']}. {mod['title'][:30]}...", key=f"nav_{i}", use_container_width=True):
            st.session_state.current_module = i
            st.rerun()
    
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_module = -1
        st.rerun()
    
    if user["role"] == "admin":
        if st.button("⚙️ Admin Panel", use_container_width=True):
            st.session_state.current_module = -2
            st.rerun()
    
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# Main content area
if st.session_state.current_module == -1:
    # Home
    st.image(str(ASSETS_DIR / "home_banner.jpg"), use_container_width=True)
    st.markdown("<h1 class='main-header'>Rooted</h1>", unsafe_allow_html=True)
    st.markdown("### A clear path of discipleship")
    st.markdown("""
    Welcome to **Rooted** — Life Church Waterfall's discipleship pathway for new believers and new members.
    
    This is an original resource designed to help you understand the foundations of the Christian faith 
    and walk in a clear, biblical pathway of growth.
    
    **Vision:** Rooted in Christ • Renewed and Equipped • Released to make disciples that make disciples.
    """)
    
    st.subheader("Your Progress")
    completed_count = sum(1 for m in modules if user_progress.get(str(m["id"]), {}).get("completed"))
    st.progress(completed_count / len(modules) if modules else 0)
    st.caption(f"{completed_count} of {len(modules)} modules completed")
    
    st.subheader("Modules Overview")
    for mod in modules:
        completed = user_progress.get(str(mod["id"]), {}).get("completed", False)
        css_class = "module-card completed" if completed else "module-card"
        st.markdown(f"""
        <div class="{css_class}">
            <strong>Module {mod['id']}: {mod['title']}</strong><br>
            <small>{mod['subtitle']}</small>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_module == -2 and user["role"] == "admin":
    # Admin Panel
    st.title("⚙️ Admin Panel")
    st.markdown("Edit module content below. Changes are saved to the content file.")
    
    selected = st.selectbox("Select Module to Edit", options=range(len(modules)), 
                           format_func=lambda i: f"{modules[i]['id']}. {modules[i]['title']}")
    
    if selected is not None:
        mod = modules[selected]
        with st.form(f"edit_mod_{selected}"):
            mod["title"] = st.text_input("Title", mod["title"])
            mod["subtitle"] = st.text_input("Subtitle", mod.get("subtitle", ""))
            mod["description"] = st.text_area("Description", mod.get("description", ""), height=100)
            
            st.markdown("**Key Scriptures** (one per line)")
            scriptures = st.text_area("Scriptures", "\n".join(mod.get("key_scriptures", [])))
            mod["key_scriptures"] = [s.strip() for s in scriptures.split("\n") if s.strip()]
            
            st.markdown("---")
            st.markdown("**Sections**")
            for idx, section in enumerate(mod.get("sections", [])):
                st.markdown(f"**Section {idx+1}**")
                section["title"] = st.text_input(f"Section title {idx}", section.get("title", ""), key=f"st_{selected}_{idx}")
                section["content"] = st.text_area(f"Content {idx}", section.get("content", ""), height=150, key=f"sc_{selected}_{idx}")
                section["reflection"] = st.text_area(f"Reflection question {idx}", section.get("reflection", ""), key=f"sr_{selected}_{idx}")
            
            if st.form_submit_button("💾 Save Module"):
                modules[selected] = mod
                modules_data["modules"] = modules
                save_modules(modules_data)
                st.success("Module saved successfully!")
                st.rerun()
    
    st.divider()
    st.subheader("Export for Print")
    if st.button("Generate Printable Summary (Markdown)"):
        md = "# Rooted Workbook\n## Life Church Waterfall\n\n"
        for m in modules:
            md += f"## Module {m['id']}: {m['title']}\n\n"
            md += f"*{m.get('subtitle', '')}*\n\n"
            md += f"{m.get('description', '')}\n\n"
            md += "**Key Scriptures:** " + ", ".join(m.get("key_scriptures", [])) + "\n\n"
            for s in m.get("sections", []):
                md += f"### {s.get('title', '')}\n\n{s.get('content', '')}\n\n"
                md += f"**Reflection:** {s.get('reflection', '')}\n\n"
            md += "---\n\n"
        st.download_button("Download Markdown", md, "rooted_workbook.md", "text/markdown")

else:
    # Module view
    if 0 <= st.session_state.current_module < len(modules):
        mod = modules[st.session_state.current_module]
        mod_id = str(mod["id"])
        user_mod_progress = user_progress.get(mod_id, {"completed": False, "notes": "", "reflections": {}})
        
        st.markdown(f"<h1 class='main-header'>Module {mod['id']}: {mod['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"*{mod.get('subtitle', '')}*")
        st.markdown(mod.get("description", ""))
        
        if mod.get("key_scriptures"):
            st.markdown("**Key Scriptures:** " + " • ".join(mod["key_scriptures"]))
        
        st.divider()
        
        for idx, section in enumerate(mod.get("sections", [])):
            with st.expander(f"📖 {section.get('title', f'Section {idx+1}')}", expanded=True):
                st.markdown(section.get("content", "Content coming soon."))
                
                if section.get("reflection"):
                    st.markdown(f"**Reflection:** {section['reflection']}")
                    reflection_key = f"{mod_id}_{idx}"
                    existing = user_mod_progress.get("reflections", {}).get(str(idx), "")
                    response = st.text_area("Your response", existing, key=f"ref_{mod_id}_{idx}", height=100)
                    if response != existing:
                        if "reflections" not in user_mod_progress:
                            user_mod_progress["reflections"] = {}
                        user_mod_progress["reflections"][str(idx)] = response
        
        st.divider()
        notes = st.text_area("Personal notes for this module", user_mod_progress.get("notes", ""), height=100)
        user_mod_progress["notes"] = notes
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Mark Module Complete", type="primary"):
                user_mod_progress["completed"] = True
                user_mod_progress["completed_at"] = datetime.now().isoformat()
                st.success("Module marked complete!")
        with col2:
            if user_mod_progress.get("completed"):
                if st.button("↩️ Mark as Incomplete"):
                    user_mod_progress["completed"] = False
                    st.info("Marked as incomplete")
        
        # Save progress
        user_progress[mod_id] = user_mod_progress
        progress[user["name"]] = user_progress
        save_progress(progress)
        
        # Navigation
        st.divider()
        cols = st.columns([1, 1, 1])
        with cols[0]:
            if st.session_state.current_module > 0:
                if st.button("← Previous Module"):
                    st.session_state.current_module -= 1
                    st.rerun()
        with cols[2]:
            if st.session_state.current_module < len(modules) - 1:
                if st.button("Next Module →"):
                    st.session_state.current_module += 1
                    st.rerun()
    else:
        st.warning("Select a module from the sidebar.")

# Footer
st.divider()
st.caption("Rooted • Life Church Waterfall • Rooted in Christ, Renewed, Released")
