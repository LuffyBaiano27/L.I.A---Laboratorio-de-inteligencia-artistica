# 🎨 L.I.A - Laboratório de Inteligência Artística

![Status](https://img.shields.io/badge/Status-Finalizado-success) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Framework](https://img.shields.io/badge/Framework-Flask-black) ![Deploy](https://img.shields.io/badge/Deploy-Online-green)

> Projeto online: https://luffybaiano27.pythonanywhere.com/

https://canva.link/dozmnmddrcco1zm ---

## 📖 Sobre o Projeto

O **L.I.A (Laboratório de Inteligência Artística)** é uma aplicação web *Full Stack* desenvolvida como projeto académico para o curso de Análise e Desenvolvimento de Sistemas (ADS).

O objetivo foi criar uma plataforma imersiva onde os utilizadores possam gerar artes únicas através de Inteligência Artificial, gerir os seus portefólios pessoais e expor as suas melhores criações num mural público. O diferencial do sistema é o foco na **Experiência do Utilizador (UX)** e na performance, apresentando uma interface responsiva baseada em *Glassmorphism*, sistema de paginação, prevenção de erros (Heurísticas de Nielsen) e tradução automática de *prompts*.

---

## 🛠️ Tecnologias e Ferramentas

**Backend**
* **Python:** Linguagem base.
* **Flask:** Microframework web para rotas e controlo de requisições.
* **SQLAlchemy (ORM):** Para manipulação da base de dados orientada a objetos.
* **Flask-Login:** Gestão de sessões de utilizadores e proteção de rotas privadas.
* **Requests:** Para consumo de APIs REST externas (Tradução e Geração de IA).

**Frontend**
* **HTML5 / CSS3:** Estrutura e Estilização avançada (*Glassmorphism*, Animações CSS, *Media Queries* para dispositivos móveis).
* **JavaScript Vanilla:** Manipulação de DOM, *Feedback* visual assíncrono, validação de cliques e *Clipboard API* (copiar *prompt*).
* **Jinja2:** Motor de *templates* para renderização dinâmica no servidor.

**Base de Dados**
* **SQLite:** Base de dados relacional *serverless* (ficheiro `lia_database.db`).

---

## ⚙️ Arquitetura e Fluxo de Dados

O sistema opera com um fluxo contínuo de "Criação e Gestão":

1. **Input e Enriquecimento:** O utilizador digita o conceito da arte. Pode utilizar a "Varinha Mágica", que consome uma API de tradução para converter o texto para Inglês de forma nativa, otimizando a compreensão da Rede Neural.
2. **Geração Neural:** O *Backend* processa o pedido e comunica com a API de geração de imagens.
3. **Persistência:** A URL da imagem gerada, juntamente com o *prompt* utilizado e o vínculo ao autor, são salvos na base de dados SQLite via SQLAlchemy.
4. **Gestão (*CRUD*):** O utilizador acede ao seu "Acervo Pessoal", onde pode processar artes em lote (publicar/privar/apagar), com navegação otimizada por um sistema robusto de paginação (10 a 12 itens por página).
5. **Visualização Otimizada:** As imagens são renderizadas com tecnologia *Lazy Loading* para poupar banda e garantir máxima performance em qualquer dispositivo.

---

## 🚀 Como correr o projeto localmente

Para testar o sistema na sua máquina, siga os passos abaixo:

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/LuffyBaiano27/LIA-Laboratorio-Inteligencia-Artistica.git](https://github.com/LuffyBaiano27/LIA-Laboratorio-Inteligencia-Artistica.git)```

2. **cd LIA-Laboratorio-Inteligencia-Artistica**

3. **python -m venv venv**
    ```venv\Scripts\activate```

4. **pip install -r requirements.txt**

5. O sistema estará disponível no seu navegador no endereço: http://127.0.0.1:5000/
***
### Último passo antes do Deploy: O `requirements.txt`
No guia acima, mencionámos o comando `pip install -r requirements.txt`. Este ficheiro é essencial para qualquer projeto em Python (e o PythonAnywhere vai exigir isso). 

Se ainda não o gerou na sua pasta, basta correr este comando no terminal do VS Code (com o seu ambiente virtual ativado):
```bash
pip freeze > requirements.txt 
