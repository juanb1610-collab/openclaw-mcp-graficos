import os
import uuid
from mcp.server.fastmcp import FastMCP
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from http.server import SimpleHTTPRequestHandler
from threading import Thread
import socketserver

mcp = FastMCP("VisualClaw_Pro")

@mcp.tool()
def generar_dashboard_completo(
    titulo: str, 
    kpi_nombre: str, kpi_valor: float,
    linea_x: list, linea_y: list,
    barras_x: list, barras_y: list,
    pie_labels: list, pie_values: list,
    conclusiones_texto: str  # <-- NUEVO: Cuadro de texto para el análisis
) -> str:
    """
    Genera un Dashboard de BI completo con gráficos y un cuadro de texto estructurado para conclusiones.
    Retorna el enlace directo para visualización en pantalla completa.
    """
    
    # 1. Configurar la cuadrícula de gráficos
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "indicator"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "domain"}]],
        subplot_titles=("Métrica Destacada", "Tendencia Temporal", "Comparativa de Categorías", "Distribución de Mercado")
    )

    fig.add_trace(go.Indicator(
        mode="number+delta", value=kpi_valor, title={'text': kpi_nombre}
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=linea_x, y=linea_y, name="Tendencia", line=dict(color='#11caa0', width=4)), row=1, col=2)
    fig.add_trace(go.Bar(x=barras_x, y=barras_y, name="Categorías", marker_color='#3b82f6'), row=2, col=1)
    fig.add_trace(go.Pie(labels=pie_labels, values=pie_values, name="Desglose", hole=.4), row=2, col=2)

    fig.update_layout(
        template="plotly_dark",
        height=800,
        showlegend=False,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        margin=dict(l=40, r=40, t=50, b=40)
    )

    # 2. Generar el HTML del gráfico por separado
    plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # 3. Construir una página web completa e incluir el cuadro de conclusiones con CSS elegante
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                background-color: #0b0f19;
                color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            .header {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 20px;
                border: 1px solid #334155;
            }}
            .conclusiones-box {{
                background-color: #1e293b;
                border-left: 6px solid #3b82f6;
                padding: 20px;
                border-radius: 8px;
                margin-top: 25px;
                font-size: 16px;
                line-height: 1.6;
                color: #cbd5e1;
            }}
            h1 {{ margin: 0; font-size: 28px; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 {titulo}</h1>
                <p style="color: #94a3b8; margin: 5px 0 0 0;">Análisis Automatizado OpenClaw + MCP</p>
            </div>
            
            <div style="background-color: #0f172a; border-radius: 12px; padding: 10px; border: 1px solid #1e293b;">
                {plotly_html}
            </div>
            
            <div class="conclusiones-box">
                <h3 style="margin-top: 0; color: #3b82f6; font-size: 18px;">📝 Conclusiones Ejecutivas y Recomendaciones</h3>
                {conclusiones_texto.replace('\n', '<br>')}
            </div>
        </div>
    </body>
    </html>
    """

    # 4. Guardar archivo en la carpeta pública
    os.makedirs("public", exist_ok=True)
    nombre_archivo = f"dashboard_bi_{uuid.uuid4().hex[:6]}.html"
    
    with open(f"public/{nombre_archivo}", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    dominio = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8080")
    url_final = f"{dominio}/public/{nombre_archivo}"
    
    # IMPORTANTE: Obligamos al agente a entregar el enlace limpio en texto
    return f"URL_DIRECTA: {url_final}"

def levantar_servidor_web():
    PORT = int(os.getenv("PORT", 8080))
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=levantar_servidor_web, daemon=True).start()
    mcp.run()
