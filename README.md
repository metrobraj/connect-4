# connect-4

Connect-4 is a web-based game that features a Minimax AI embedded with alpha-beta pruning.
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask-000000?style=flat-square&logo=flask)
![Frontend](https://img.shields.io/badge/UI-Liquid%20Glass-7b83a7?style=flat-square)

---

## features

- **minimax AI engine:** uses negamax search with Alpha-Beta Pruning and optimal move ordering (center-outwards search) for optimized working.
- **responsive web interface:** zero external frontend frameworks—built with pure HTML, CSS, and vanilla JavaScript.
- **inclusive dev tools:** Hidden developer metrics panel tracking search depth, evaluated positions, pruned branches, and decision latency in real time.

---

## project directory

```text
connect-4/
├── static/
│   ├── index.html        
│   └── blue.gif          
├── app.py                # Flask API routes & game state management
├── game.py               # Connect 4 rules + Minimax AI search engine
├── requirements.txt      # required python dependencies
└── README.md

```
---

## how to run?

1. open terminal in your ide and install required dependencies if not done already

pip install -r requirements.txt

2. run command: 

python app.py (or) python3 app.py

3. open 

http://127.0.0.1:5000
