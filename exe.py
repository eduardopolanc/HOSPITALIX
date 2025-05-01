import sys
from streamlit import cli as stcli 

# Cette fonction permet d'appeler le scritp app.py pour executer les streamlit

if __name__ == '__main__': 
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())

