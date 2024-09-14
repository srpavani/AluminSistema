import requests
import re
import json




def valorDolaBRL():
    URL = 'https://br.investing.com/currencies/usd-brl'
    response = requests.get(URL)
    if response.status_code == 200:
        html = response.text
        divDola = r'<div class="text-5xl/9 font-bold text-\[#232526\] md:text-\[42px\] md:leading-\[60px\]" data-test="instrument-price-last">([\d,]+)</div>'
        busca = re.search(divDola, html)
        if busca:
            valor = busca.group(1) # pega o segundo..
            result = {
                "moeda": "USD/BRL",
                "valor": valor
            }
            return json.dumps(result)
        else:
            return json.dumps({"error": "dolar não encontrado"})
    else:
        return json.dumps({"error": f"e ao acessar a página. status: {response.status_code}"})
    
    
    
    
def valorSMM():
    URL = 'https://www.metal.com/Aluminum/201102250311'
    response = requests.get(URL)
    if response.status_code == 200:
        html = response.text
        divDola = r'<div class="price___2mpJr">([\d,]+)</div>'
        busca = re.search(divDola, html)
        if busca:
            valor = busca.group(1) # pega o segundo..
            result = {
                "moeda": "CNY/mt",
                "valor": valor
            }
            return json.dumps(result)
        else:
            return json.dumps({"error": "CNY/mt não encontrado"})
    else:
        return json.dumps({"error": f"e ao acessar a página. status: {response.status_code}"})    
    
    

print(valorDolaBRL())
print(valorSMM())
