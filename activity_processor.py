import json
import requests
from datetime import datetime

# Monday API
API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjM1NDg5MTEwOCwiYWFpIjoxMSwidWlkIjozNzM0ODA0MywiaWFkIjoiMjAyNC0wNS0wMlQxNjo1NDoxOC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTI2NTYzMzMsInJnbiI6InVzZTEifQ.27OtOtNCP7LWL8lQL2Pz2UhGYJM1C-L2GWaAjjEJE9U'
API_URL = 'https://api.monday.com/v2'

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': API_KEY,
    'API-Version': '2024-10'
}



def buscar_todos_os_itens(board_id):
    """Busca todos os itens de um board específico."""
    query = f'''
    {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            id
            name
            group {{
              id
              title
            }}
            column_values {{
              id
              text
              value
              column {{
                id
                title
                type
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    
    response = requests.post(API_URL, headers=HEADERS, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na API: {response.status_code}, {response.text}")
        return None
    

def filtrar_itens_parados(json_data):
    """Filtra itens com status 'Parado'."""
    itens_parados = []

    boards = json_data.get("data", {}).get("boards", [])
    for board in boards:
        items = board.get("items_page", {}).get("items", [])
        for item in items:
            for column in item.get("column_values", []):
                if column.get("id") == "status" and column.get("text") == "Parado":
                    itens_parados.append({
                        "id": item["id"],
                        "name": item["name"],
                        "group": item["group"]["title"]
                    })

    return itens_parados

def buscar_logs_de_atividade(board_id, pulse_id):
    """Busca os logs de atividade para um item específico (pulse_id)."""
    query = f'''
    {{
      boards(ids: {board_id}) {{
        items(ids: {pulse_id}) {{
          activity_logs {{
            id
            event
            data
            created_at
          }}
        }}
      }}
    }}
    '''
    
    response = requests.post(API_URL, headers=HEADERS, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar logs: {response.status_code}, {response.text}")
        return None


def processar_logs_para_status_parado(logs):
    """Processa os logs de atividades e encontra a data da mudança para 'Parado'."""
    for log in logs:
        if log["event"] == "update_column_value":
            data = json.loads(log["data"])
            # Verifica se o status foi alterado para "Parado"
            if data.get("value") == "Parado":
                return log["created_at"]
    return None

def main():
    board_id = 7446820469  # Substitua pelo ID do seu board

    # Passo 1: Buscar todos os itens
    print("Buscando todos os itens do board...")
    json_data = buscar_todos_os_itens(board_id)
    if not json_data:
        print("Falha ao buscar dados do Monday.")
        return

    # Passo 2: Filtrar os itens com status 'Parado'
    print("Filtrando itens com status 'Parado'...")
    itens_parados = filtrar_itens_parados(json_data)

    if itens_parados:
        print(f"{len(itens_parados)} itens encontrados no status 'Parado':")
        for item in itens_parados:
            print(f"ID: {item['id']}, Nome: {item['name']}, Grupo: {item['group']}")

            # Passo 3: Buscar logs de atividade para cada item
            print(f"Buscando logs de atividade para o item {item['name']}...")
            logs = buscar_logs_de_atividade(board_id, item['id'])
            if logs:
                # Passo 4: Processar logs para encontrar a data de mudança para 'Parado'
                data_mudanca = processar_logs_para_status_parado(logs.get("data", {}).get("boards", [])[0].get("items", [])[0].get("activity_logs", []))
                if data_mudanca:
                    print(f"Data de mudança para 'Parado': {data_mudanca}")
                else:
                    print("Nenhuma mudança encontrada para o status 'Parado'.")
            else:
                print("Erro ao buscar logs para o item.")
    else:
        print("Nenhum item encontrado com status 'Parado'.")

if __name__ == "__main__":
    main()
