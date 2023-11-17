from flask import Flask, render_template, request
import pandas as pd
import requests

app = Flask(__name__)

def register_to_consul(ip, port, service_name):
    # 替换为你的 Consul 服务器的 IP 地址
    consul_url = "http://192.168.137.113:8500/v1/agent/service/register"
    
    service_id = f"node_exporter-{ip.replace('.', '-')}"
    # 使用用户输入的服务名，如果未提供则使用默认值
    service_name = service_name or "node-exporter-group"

    payload = {
        "ID": service_id,
        "Name": service_name,
        "Address": ip,
        "Port": port,
        # Add other necessary parameters
    }

    response = requests.put(consul_url, json=payload)

    if response.status_code == 200:
        return f"Service {service_id} registered successfully."
    else:
        return f"Failed to register service {service_id}. Status code: {response.status_code}"



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            try:
                df = pd.read_excel(file)
                results = []
                for index, row in df.iterrows():
                    ip, port = row['IP'], row['Port']
                    result = register_to_consul(ip, port)
                    results.append(result)
                return render_template('index.html', results=results)
            except Exception as e:
                error_message = f"Error reading Excel file: {e}"
                return render_template('index.html', error_message=error_message)
        else:
            error_message = "Please upload a valid Excel file."
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
