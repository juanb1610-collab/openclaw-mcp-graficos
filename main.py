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
    Genera un Dashboard Ejecutivo Premium con Chart.js.
    Diseño estilizado con paleta moderna, tipografía limpia y espaciados de alta fidelidad.
    """
    
    # Serialización limpia de datos
    linea_x_json = json.dumps([str(x) for x in linea_x])
    linea_y_json = json.dumps([float(str(y).replace('$', '').replace('.', '').replace(' COP', '').strip()) for y in linea_y])
    barras_x_json = json.dumps([str(x) for x in barras_x])
    barras_y_json = json.dumps([float(str(y).replace('$', '').replace('.', '').replace(' COP', '').strip()) for y in barras_y])
    pie_labels_json = json.dumps([str(l) for l in pie_labels])
    pie_values_json = json.dumps([float(str(v).replace('%', '').strip()) for v in pie_values])

    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{
                --bg-main: #0f172a;
                --bg-card: #1e293b;
                --border-color: #334155;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent: #3b82f6;
                --emerald: #10b981;
            }}
            body {{ 
                background-color: var(--bg-main); 
                color: var(--text-main); 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                padding: 30px;
                margin: 0;
            }}
            .container {{ max-width: 1440px; margin: 0 auto; }}
            
            /* Encabezado */
            .header {{ 
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                padding: 30px; 
                border-radius: 16px; 
                margin-bottom: 25px; 
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.025em; }}
            
            /* Grid de KPIs */
            .kpi-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
                gap: 20px; 
                margin-bottom: 25px; 
            }}
            .kpi-card {{ 
                background-color: var(--bg-card); 
                padding: 24px; 
                border-radius: 14px; 
                border: 1px solid var(--border-color);
                text-align: center;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
            }}
            .kpi-card h3 {{ color: var(--text-muted); font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }}
            .kpi-card .value {{ font-size: 32px; font-weight: 700; margin-top: 10px; color: var(--accent); }}
            
            /* Grid de Gráficos */
            .chart-grid {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 25px; 
                margin-bottom: 25px; 
            }}
            @media (max-width: 968px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
            
            .chart-card {{ 
                background-color: var(--bg-card); 
                padding: 24px; 
                border-radius: 16px; 
                border: 1px solid var(--border-color); 
                position: relative;
            }}
            .chart-card h3 {{ margin: 0 0 20px 0; font-size: 16px; font-weight: 600; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }}
            .chart-wrapper {{ position: relative; height: 320px; width: 100%; }}
            
            /* Conclusiones */
            .conclusiones-box {{ 
                background: linear-gradient(180deg, #1e293b 0%, #111827 100%); 
                border-top: 4px solid var(--accent); 
                padding: 25px; 
                border-radius: 14px; 
                border: 1px solid var(--border-color);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            }}
            .conclusiones-box h3 {{ color: var(--accent); margin-top: 0; font-size: 18px; display: flex; align-items: center; gap: 8px; }}
            .conclusiones-text {{ color: #cbd5e1; line-height: 1.7; font-size: 15px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 {titulo}</h1>
                <p style="color: var(--text-muted); margin: 6px 0 0 0; font-size: 14px;">Intelligence & Analytics Dashboard Suite • Sincronizado</p>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <h3>{kpi_nombre}</h3>
                    <div class="value">{kpi_valor}</div>
                </div>
                <div class="kpi-card">
                    <h3>Cumplimiento Objetivo</h3>
                    <div class="value" style="color: var(--emerald);">89.0%</div>
                </div>
                <div class="kpi-card">
                    <h3>Margen Bruto Promedio</h3>
                    <div class="value" style="color: #f59e0b;">59.7%</div>
                </div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Evolución de Ventas / Tendencia Temporal</h3>
                    <div class="chart-wrapper">
                        <canvas id="chartLineas"></canvas>
                    </div>
                </div>
                
                <div class="chart-card">
                    <h3>Pareto de Ventas por Segmento</h3>
                    <div class="chart-wrapper">
                        <canvas id="chartBarras"></canvas>
                    </div>
                </div>
                
                <div class="chart-card" style="grid-column: span 2;">
                    <h3>Distribución de Mix de Portafolio</h3>
                    <div class="chart-wrapper" style="height: 300px;">
                        <canvas id="chartPie"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="conclusiones-box">
                <h3>📝 Hallazgos Estratégicos y Auditoría Analítica</h3>
                <p class="conclusiones-text">{conclusiones_texto.replace('\n', '<br>')}</p>
            </div>
        </div>

        <script>
            // Configuración global de fuentes para Chart.js
            Chart.defaults.color = '#94a3b8';
            Chart.defaults.font.family = '-apple-system, sans-serif';

            window.onload = function() {{
                // 1. Gráfico de Líneas Estilizado
                new Chart(document.getElementById('chartLineas'), {{
                    type: 'line',
                    data: {{ 
                        labels: {linea_x_json}, 
                        datasets: [{{ 
                            label: 'Ventas Reales', 
                            data: {linea_y_json}, 
                            borderColor: '#3b82f6', 
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 3,
                            pointBackgroundColor: '#3b82f6',
                            tension: 0.3, 
                            fill: true 
                        }}] 
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            y: {{ grid: {{ color: '#334155' }}, ticks: {{ callback: v => '$' + v.toLocaleString() }} }},
                            x: {{ grid: {{ display: false }} }}
                        }}
                    }}
                }});

                // 2. Gráfico de Barras Profesional (Pareto)
                new Chart(document.getElementById('chartBarras'), {{
                    type: 'bar',
                    data: {{ 
                        labels: {barras_x_json}, 
                        datasets: [{{ 
                            data: {barras_y_json}, 
                            backgroundColor: '#10b981',
                            borderRadius: 6,
                            maxBarThickness: 40
                        }}] 
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            y: {{ grid: {{ color: '#334155' }}, ticks: {{ callback: v => '$' + v.toLocaleString() }} }},
                            x: {{ grid: {{ display: false }}, ticks: {{ autoSkip: false, maxRotation: 15 }} }}
                        }}
                    }}
                }});

                // 3. Gráfico de Torta / Dona Standard Limpio (No concéntrico)
                new Chart(document.getElementById('chartPie'), {{
                    type: 'doughnut',
                    data: {{ 
                        labels: {pie_labels_json}, 
                        datasets: [{{ 
                            data: {pie_values_json}, 
                            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ec4899'],
                            borderWidth: 4,
                            borderColor: '#1e293b'
                        }}] 
                    }},
                    options: {{ 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: {{ 
                            legend: {{ position: 'right', labels: {{ boxWidth: 15, padding: 20 }} }} 
                        }}
                    }}
                }});
            }};
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
