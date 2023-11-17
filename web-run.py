from flask import Flask, render_template, request, redirect, url_for
import os
import openpyxl
import requests
from urllib.parse import urljoin

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_to_consul(ip, port, service_name):
    # Consul API endpoint
    consul_url = "http://192.168.137.111:8500/v1/agent/service/register"

    # 构建注册信息
    registration_payload = {
        "id": f"node_exporter-{ip}",
        "name": service_name,
        "address": ip,
        "port": int(port),
        # 根据需要添加其他注册参数
    }

    # 发送注册请求到Consul
    response = requests.put(consul_url, json=registration_payload)

    if response.status_code == 200:
        return f"成功注册 {ip}:{port} 到 Consul."
    else:
        return f"无法注册 {ip}:{port} 到 Consul. 状态码: {response.status_code}"

def process_excel_file(file_path, service_name):
    try:
        # 打开Excel文件
        workbook = openpyxl.load_workbook(file_path)

        # 假设IP地址和端口在第一个表格中
        sheet = workbook.active

        # 遍历每一行并注册到Consul
        for row in sheet.iter_rows(min_row=2, values_only=True):
            ip_port = row[0]
            ip, port = ip_port.split(':')
            result = register_to_consul(ip, port, service_name)
            print(result)

    except Exception as e:
        print(f"处理Excel文件时出错: {e}")
    finally:
        if workbook:
            workbook.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        service_name = request.form.get("service_name")

        if not file or not service_name or not allowed_file(file.filename):
            return "请提供正确的Excel文件和服务名."

        # 保存上传的文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        process_excel_file(file_path, service_name)
        return "注册完成."

    return render_template("index.html")

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)