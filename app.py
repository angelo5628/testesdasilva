from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'wellness_secret_key_2024'

cred = credentials.Certificate('firebase-config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).where('senha', '==', senha).stream()
        
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            break
        
        if user_data:
            session['user_id'] = user_data['id']
            session['user_name'] = user_data['nome']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Email ou senha inválidos')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        data_nascimento = request.form['data_nascimento']
        
        user_id = str(uuid.uuid4())
        user_data = {
            'nome': nome,
            'email': email,
            'senha': senha,
            'data_nascimento': data_nascimento,
            'data_criacao': datetime.now().isoformat(),
            'treinos': [],
            'medidas': [],
            'refeicoes': [],
            'objetivos': []
        }
        
        db.collection('users').document(user_id).set(user_data)
        session['user_id'] = user_id
        session['user_name'] = nome
        return redirect('/dashboard')
    
    return render_template('cadastro.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user_name=session['user_name'])

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    
    return render_template('perfil.html', user=user_data)

@app.route('/treino_registro', methods=['GET', 'POST'])
def treino_registro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        tipo_treino = request.form['tipo_treino']
        duracao = request.form['duracao']
        intensidade = request.form['intensidade']
        observacoes = request.form['observacoes']
        
        treino_data = {
            'id': str(uuid.uuid4()),
            'tipo_treino': tipo_treino,
            'duracao': duracao,
            'intensidade': intensidade,
            'observacoes': observacoes,
            'data': datetime.now().isoformat()
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        user_data['treinos'].append(treino_data)
        user_ref.set(user_data)
        
        return redirect('/treino_historico')
    
    return render_template('treino_registro.html')

@app.route('/treino_historico')
def treino_historico():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    treinos = user_data.get('treinos', [])
    
    return render_template('treino_historico.html', treinos=treinos)

@app.route('/exercicios_cadastro', methods=['GET', 'POST'])
def exercicios_cadastro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        nome = request.form['nome']
        grupo_muscular = request.form['grupo_muscular']
        descricao = request.form['descricao']
        
        exercicio_data = {
            'id': str(uuid.uuid4()),
            'nome': nome,
            'grupo_muscular': grupo_muscular,
            'descricao': descricao,
            'criado_por': session['user_id']
        }
        
        db.collection('exercicios').document(exercicio_data['id']).set(exercicio_data)
        return redirect('/exercicios_cadastro')
    
    exercicios_ref = db.collection('exercicios')
    exercicios = [doc.to_dict() for doc in exercicios_ref.stream()]
    
    return render_template('exercicios_cadastro.html', exercicios=exercicios)

@app.route('/medidas_registro', methods=['GET', 'POST'])
def medidas_registro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        peso = request.form['peso']
        altura = request.form['altura']
        braco_esquerdo = request.form['braco_esquerdo']
        braco_direito = request.form['braco_direito']
        cintura = request.form['cintura']
        quadril = request.form['quadril']
        
        medida_data = {
            'id': str(uuid.uuid4()),
            'peso': peso,
            'altura': altura,
            'braco_esquerdo': braco_esquerdo,
            'braco_direito': braco_direito,
            'cintura': cintura,
            'quadril': quadril,
            'data': datetime.now().isoformat()
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        user_data['medidas'].append(medida_data)
        user_ref.set(user_data)
        
        return redirect('/medidas_historico')
    
    return render_template('medidas_registro.html')

@app.route('/medidas_historico')
def medidas_historico():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    medidas = user_data.get('medidas', [])
    
    return render_template('medidas_historico.html', medidas=medidas)

@app.route('/refeicoes_registro', methods=['GET', 'POST'])
def refeicoes_registro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        tipo_refeicao = request.form['tipo_refeicao']
        alimentos = request.form['alimentos']
        calorias = request.form['calorias']
        observacoes = request.form['observacoes']
        
        refeicao_data = {
            'id': str(uuid.uuid4()),
            'tipo_refeicao': tipo_refeicao,
            'alimentos': alimentos,
            'calorias': calorias,
            'observacoes': observacoes,
            'data': datetime.now().isoformat()
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        user_data['refeicoes'].append(refeicao_data)
        user_ref.set(user_data)
        
        return redirect('/diario_alimentar')
    
    return render_template('refeicoes_registro.html')

@app.route('/diario_alimentar')
def diario_alimentar():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    refeicoes = user_data.get('refeicoes', [])
    
    return render_template('diario_alimentar.html', refeicoes=refeicoes)

@app.route('/alimentos_cadastro', methods=['GET', 'POST'])
def alimentos_cadastro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        nome = request.form['nome']
        calorias = request.form['calorias']
        proteina = request.form['proteina']
        carboidratos = request.form['carboidratos']
        gorduras = request.form['gorduras']
        
        alimento_data = {
            'id': str(uuid.uuid4()),
            'nome': nome,
            'calorias': calorias,
            'proteina': proteina,
            'carboidratos': carboidratos,
            'gorduras': gorduras,
            'criado_por': session['user_id']
        }
        
        db.collection('alimentos').document(alimento_data['id']).set(alimento_data)
        return redirect('/alimentos_cadastro')
    
    alimentos_ref = db.collection('alimentos')
    alimentos = [doc.to_dict() for doc in alimentos_ref.stream()]
    
    return render_template('alimentos_cadastro.html', alimentos=alimentos)

@app.route('/sono_registro', methods=['GET', 'POST'])
def sono_registro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        horas_sono = request.form['horas_sono']
        qualidade = request.form['qualidade']
        data_sono = request.form['data_sono']
        
        sono_data = {
            'id': str(uuid.uuid4()),
            'horas_sono': horas_sono,
            'qualidade': qualidade,
            'data_sono': data_sono,
            'data_registro': datetime.now().isoformat()
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        if 'sono' not in user_data:
            user_data['sono'] = []
        user_data['sono'].append(sono_data)
        user_ref.set(user_data)
        
        return redirect('/dashboard')
    
    return render_template('sono_registro.html')

@app.route('/agua_registro', methods=['GET', 'POST'])
def agua_registro():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        quantidade_ml = request.form['quantidade_ml']
        data_agua = request.form['data_agua']
        
        agua_data = {
            'id': str(uuid.uuid4()),
            'quantidade_ml': quantidade_ml,
            'data_agua': data_agua,
            'data_registro': datetime.now().isoformat()
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        if 'agua' not in user_data:
            user_data['agua'] = []
        user_data['agua'].append(agua_data)
        user_ref.set(user_data)
        
        return redirect('/dashboard')
    
    return render_template('agua_registro.html')

@app.route('/objetivos', methods=['GET', 'POST'])
def objetivos():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        descricao = request.form['descricao']
        tipo_objetivo = request.form['tipo_objetivo']
        data_limite = request.form['data_limite']
        
        objetivo_data = {
            'id': str(uuid.uuid4()),
            'descricao': descricao,
            'tipo_objetivo': tipo_objetivo,
            'data_limite': data_limite,
            'data_criacao': datetime.now().isoformat(),
            'concluido': False
        }
        
        user_ref = db.collection('users').document(session['user_id'])
        user_data = user_ref.get().to_dict()
        user_data['objetivos'].append(objetivo_data)
        user_ref.set(user_data)
        
        return redirect('/objetivos')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    objetivos = user_data.get('objetivos', [])
    
    return render_template('objetivos.html', objetivos=objetivos)

@app.route('/relatorios')
def relatorios():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_ref = db.collection('users').document(session['user_id'])
    user_data = user_ref.get().to_dict()
    
    treinos = user_data.get('treinos', [])
    medidas = user_data.get('medidas', [])
    refeicoes = user_data.get('refeicoes', [])
    
    return render_template('relatorios.html', 
                         treinos=treinos, 
                         medidas=medidas, 
                         refeicoes=refeicoes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)