import os
import random
import urllib.parse
import requests  
import time      
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lia_projeto_ads_2024' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lia_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# PASTA PARA FUNDOS
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# PASTA PARA FOTOS DE PERFIL
PROFILE_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
os.makedirs(PROFILE_FOLDER, exist_ok=True)
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER

# PASTA PARA ARTES GERADAS DA IA
ARTES_FOLDER = os.path.join(app.root_path, 'static', 'artes_geradas')
os.makedirs(ARTES_FOLDER, exist_ok=True)
app.config['ARTES_FOLDER'] = ARTES_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Acesso restrito. Por favor, identifique-se.'
login_manager.login_message_category = 'danger'

# ==========================================
# EXTENSÕES PERMITIDAS PARA UPLOADS
# ==========================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# TABELA DE ASSOCIAÇÃO (CURTIDAS)
# ==========================================
favoritos = db.Table('favoritos',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('wallpaper_id', db.Integer, db.ForeignKey('wallpaper.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    termos = db.Column(db.Boolean, default=False)
    
    background_file = db.Column(db.String(300), default='videos/shadow-crown.mp4')
    bio = db.Column(db.String(500), default="Explorador de arte na L.I.A.")
    profile_pic = db.Column(db.String(300), default='images/cyberpunk.jpg') 
    
    wallpapers = db.relationship('Wallpaper', backref='author', lazy=True)
    curtidas = db.relationship('Wallpaper', secondary=favoritos, backref=db.backref('curtido_por', lazy='dynamic'))

class Wallpaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    prompt_usado = db.Column(db.String(300), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    publica = db.Column(db.Boolean, default=True)
    
    def total_curtidas(self):
        return self.curtido_por.count()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Credenciais incorretas.', 'danger')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        data_str = request.form.get('data_nascimento')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Usuário ou e-mail já em uso.', 'danger')
            return redirect(url_for('cadastro'))
            
        data_nascimento = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None
        hashed_password = generate_password_hash(password, method='scrypt')
        
        # --- A MÁGICA ENTRA AQUI ---
        # Defina o link direto do Imgur que será o fundo padrão da L.I.A.
        fundo_padrao = "https://i.imgur.com/P2UU3l4.mp4" 
        
        # Adicione o background_file na criação do usuário
        new_user = User(
            username=username, 
            email=email, 
            password=hashed_password, 
            data_nascimento=data_nascimento, 
            termos=True,
            background_file=fundo_padrao # <-- O usuário já nasce com o fundo no banco
        )
        # ---------------------------
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada! Bem-vindo ao L.I.A.', 'success')
        return redirect(url_for('login'))
        
    return render_template('cadastro.html')
@app.route('/dashboard')
@login_required
def dashboard():
    from sqlalchemy import func
    total = Wallpaper.query.filter_by(user_id=current_user.id).count()
    recentes = Wallpaper.query.filter_by(user_id=current_user.id).order_by(Wallpaper.id.desc()).limit(3).all()
    
    top_artes = db.session.query(Wallpaper)\
        .filter_by(publica=True)\
        .outerjoin(favoritos)\
        .group_by(Wallpaper.id)\
        .order_by(func.count(favoritos.c.user_id).desc(), Wallpaper.id.desc())\
        .limit(3).all()
        
    stats = {'total_artes': total, 'prompts_usados': total, 'status': 'Online'}
    return render_template('dashboard.html', stats=stats, artes_recentes=recentes, top_artes=top_artes)

@app.route('/estudio', methods=['GET', 'POST'])
@login_required
def estudio():
    if request.method == 'POST':
        prompt_br = request.form['prompt']
        
        constraints = (
            "masterpiece, best quality, ultra-detailed photography, "
            "realistic anime cosplay, accurate character design, "
            "cinematic lighting, highly detailed face, 8k resolution"
        )
        
        prompt_final = f"{prompt_br}, {constraints}"
        prompt_codificado = urllib.parse.quote(prompt_final)
        seed = random.randint(1, 999999)
        
        url_ia = f"https://image.pollinations.ai/prompt/{prompt_codificado}?width=1024&height=768&nologo=true&seed={seed}&model=flux"
            
        nova_arte = Wallpaper(
            title=f"Criação #{random.randint(100, 999)}", 
            prompt_usado=prompt_br, 
            image_url=url_ia, 
            user_id=current_user.id,
            publica=True 
        )
        db.session.add(nova_arte)
        db.session.commit()
        
        flash('Arte solicitada com sucesso!', 'success')
        return redirect(url_for('acervo'))
    
    return render_template('estudio.html', ref_prompt=request.args.get('ref_prompt', ''), ref_img=request.args.get('ref_img', ''))

@app.route('/acervo')
@login_required
def acervo():
    # Pega a página atual da URL (padrão é 1)
    page = request.args.get('page', 1, type=int)
    
    # Filtra apenas as artes do usuário logado e aplica a paginação (12 por página)
    artes_paginadas = Wallpaper.query.filter_by(user_id=current_user.id)\
        .order_by(Wallpaper.id.desc())\
        .paginate(page=page, per_page=10)
    
    # artes=artes_paginadas.items (a lista de artes daquela página)
    # artes_obj=artes_paginadas (o objeto completo com informações de navegação)
    return render_template('acervo.html', artes=artes_paginadas.items, artes_obj=artes_paginadas)

@app.route('/mural')
def mural():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'recentes')
    
    query = Wallpaper.query.filter_by(publica=True)
    
    if sort_by == 'curtidas':
        from sqlalchemy import func
        artes_paginadas = query.outerjoin(favoritos)\
            .group_by(Wallpaper.id)\
            .order_by(func.count(favoritos.c.user_id).desc(), Wallpaper.id.desc())\
            .paginate(page=page, per_page=10)
    else:
        artes_paginadas = query.order_by(Wallpaper.id.desc()).paginate(page=page, per_page=12)
        
    return render_template('mural.html', artes=artes_paginadas.items, artes_obj=artes_paginadas, sort_by=sort_by)

@app.route('/perfil/<username>')
def perfil_publico(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Pega a página atual da URL
    page = request.args.get('page', 1, type=int)
    
    # Paginação: 10 artes por página
    artes_paginadas = Wallpaper.query.filter_by(user_id=user.id, publica=True)\
        .order_by(Wallpaper.id.desc())\
        .paginate(page=page, per_page=12)
        
    return render_template('perfil.html', user=user, artes=artes_paginadas.items, artes_obj=artes_paginadas)

@app.route('/toggle_privacidade/<int:id>', methods=['POST'])
@login_required
def toggle_privacidade(id):
    arte = Wallpaper.query.get_or_404(id)
    if arte.user_id == current_user.id:
        arte.publica = not arte.publica
        db.session.commit()
        return jsonify({"status": "sucesso", "publica": arte.publica})
    return jsonify({"status": "erro"}), 403

@app.route('/acoes_em_lote', methods=['POST'])
@login_required
def acoes_em_lote():
    dados = request.get_json()
    ids = dados.get('ids', [])
    acao = dados.get('acao')
    
    if not ids:
        return jsonify({"status": "erro", "mensagem": "Nenhuma arte selecionada"}), 400
        
    artes = Wallpaper.query.filter(Wallpaper.id.in_(ids), Wallpaper.user_id == current_user.id).all()
    
    for arte in artes:
        if acao == 'deletar':
            db.session.delete(arte)
        elif acao == 'privar':
            arte.publica = False
        elif acao == 'publicar':
            arte.publica = True
            
    db.session.commit()
    return jsonify({"status": "sucesso", "count": len(artes)})

@app.route('/curtir/<int:id>', methods=['POST'])
@login_required
def curtir_arte(id):
    arte = Wallpaper.query.get_or_404(id)
    if arte in current_user.curtidas:
        current_user.curtidas.remove(arte)
        status = "removido"
    else:
        current_user.curtidas.append(arte)
        status = "adicionado"
    
    db.session.commit()
    return jsonify({"status": status, "count": arte.total_curtidas()})

@app.route('/editar_arte/<int:id>', methods=['POST'])
@login_required
def editar_arte(id):
    arte = Wallpaper.query.get_or_404(id)
    if arte.user_id == current_user.id:
        arte.title = request.form.get('novo_titulo')
        db.session.commit()
        flash('Título atualizado.', 'success')
    return redirect(url_for('acervo'))

@app.route('/deletar_arte/<int:id>', methods=['POST'])
@login_required
def deletar_arte(id):
    arte = Wallpaper.query.get_or_404(id)
    if arte.user_id == current_user.id:
        db.session.delete(arte)
        db.session.commit()
        flash('Arte removida.', 'success')
    return redirect(url_for('acervo'))

@app.route('/mudar_fundo', methods=['POST'])
@login_required
def mudar_fundo():
    if 'fundo' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
    
    file = request.files['fundo']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(request.referrer or url_for('dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        nome_unico = f"user_{current_user.id}_{filename}"
        caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_unico)
        
        file.save(caminho_completo)
        current_user.background_file = f"uploads/{nome_unico}"
        db.session.commit()
        flash('Plano de fundo atualizado com sucesso!', 'success')
    else:
        flash('Arquivo não suportado. Use apenas Imagens (JPG/PNG) ou Vídeos (MP4).', 'error')
        
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nova_bio = request.form.get('bio')
        foto = request.files.get('foto_perfil')
        
        # Captura o link do fundo que o usuário colou
        novo_link_fundo = request.form.get('background_url')
        
        if nova_bio and len(nova_bio) > 500:
            flash('A bio deve ter no máximo 500 caracteres.', 'danger')
            return redirect(url_for('editar_perfil'))
            
        current_user.bio = nova_bio
        
        # --- A MÁGICA DO FUNDO AQUI ---
        if novo_link_fundo:
            current_user.background_file = novo_link_fundo.strip()
        # ------------------------------
        
        if foto and foto.filename != '' and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            nome_foto = f"avatar_{current_user.id}_{filename}"
            caminho = os.path.join(app.config['PROFILE_FOLDER'], nome_foto)
            foto.save(caminho)
            current_user.profile_pic = f"uploads/profiles/{nome_foto}"
            
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil_publico', username=current_user.username))
        
    # Retorno padrão para quando a página for carregada via GET
    return render_template('editar_perfil.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão encerrada.', 'success')
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Erro: O arquivo é muito grande! O tamanho máximo permitido é 50MB.', 'danger')
    return redirect(request.referrer or url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=False)