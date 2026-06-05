import os
import uuid
from mcp.server.fastmcp import FastMCP
from http.server import SimpleHTTPRequestHandler
from threading import Thread
import socketserver
import json

mcp = FastMCP("VisualClaw_Pro")

@mcp.tool()
def generar_dashboard_completo(
    titulo: str, 
    kpi_nombre: str, kpi_valor: str,
    linea_x: list, linea_y: list,
    barras_x: list, barras_y: list,
    pie_labels: list, pie_values: list,
    conclusiones_texto: str
) -> str:
    """
    Genera un Dashboard nativo en Chart.js para evitar bloqueos de carga ("Cargando...").
    """
    
    # Aseguramos que las listas pasen correctamente como JSON seguro para JavaScript
    linea_x_json = json.dumps(linea_x)
    linea_y_json = json.dumps(linea_y)
    barras_x_json = json.dumps(barras_x)
    barras_y_json = json.dumps(barras_y)
    pie_labels_json = json.dumps(pie_labels)
    pie_values_json = json.dumps(pie_values)

    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background-color: #0b0f19; color: #f8fafc; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
            .card {{ background-color: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; }}
            .kpi-card {{ background-color: #1e293b; text-align: center; padding: 40px; border-radius: 12px; }}
            .conclusiones-box {{ background-color: #1e293b; border-left: 6px solid #3b82f6; padding: 20px; border-radius: 8px; margin-top: 25px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h2>📊 {titulo}</h2>
                <p style="color: #94a3b8;">Reporte Maestro Sincronizado</p>
            </div>
            
            <div class="grid">
                <div class="kpi-card">
                    <h3 style="color: #94a3b8; margin:0;">{kpi_nombre}</h3>
                    <h1 style="font-size: 42px; margin: 10px 0;">{kpi_valor}</h1>
                </div>
                
                <div class="card">
                    <h3>Tendencia Temporal</h3>
                    <canvas id="chartLineas"></canvas>
                </div>
                
                <div class="card">
                    <h3>Pareto / Comparativa de Ventas</h3>
                    <canvas id="chartBarras"></canvas>
                </div>
                
                <div class="card">
                    <h3>Mix de Portafolio</h3>
                    <canvas id="chartPie"></canvas>
                </div>
            </div>
            
            <div class="conclusiones-box">
                <h3 style="margin-top:0; color:#3b82f6;">📝 Conclusiones Ejecutivas</h3>
                <p style="color:#cbd5e1; line-height:1.6;">{conclusiones_texto.replace('\n', '<br>')}</p>
            </div>
        </div>

        <script>
            // Renderizado forzado inmediato al cargar la página
            new Chart(document.getElementById('chartLineas'), {{
                type: 'line',
                data: {{ labels: {linea_x_json}, datasets: [{{ label: 'Ventas', data: {linea_y_json}, borderColor: '#11caa0', tension: 0.1 }}] }},
                options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
            }});

            new Chart(document.getElementById('chartBarras'), {{
                type: 'bar',
                data: {{ labels: {barras_x_json}, datasets: [{{ label: 'Monto', data: {barras_y_json}, backgroundColor: '#3b82f6' }}] }},
                options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
            }});

            new Chart(document.getElementById('chartPie'), {{
                type: 'doughnut',
                data: {{ labels: {pie_labels_json}, datasets: [{{ data: {pie_values_json}, backgroundColor: ['#3b82f6', '#11caa0', '#f59e0b'] }}] }},
                options: {{ responsive: true }}
            }});
        </script>
    </body>
    </html>
    """

    os.makedirs("public", exist_ok=True)
    nombre_archivo = f"dashboard_bi_{uuid.uuid4().hex[:6]}.html"
    
    with open(f"public/{nombre_archivo}", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    dominio = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8080")
    return f"URL_DIRECTA: {dominio}/public/{nombre_archivo}"

def levantar_servidor_web():
    PORT = int(os.getenv("PORT", 8080))
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=levantar_servidor_web, daemon=True).start()
    mcp.run()
