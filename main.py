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
    pie_labels: list, pie_values: list
) -> str:
    """
    Genera un Dashboard de BI completo con 4 secciones: 
    Métrica principal, Tendencia (Línea), Comparativa (Barras) y Distribución (Pie).
    """
    
    # 1. Crear estructura de cuadrícula (2 filas, 2 columnas)
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "indicator"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "domain"}]],
        subplot_titles=("Métrica Destacada", "Tendencia Temporal", "Comparativa de Categorías", "Distribución de Mercado")
    )

    # Gráfico 1: KPI (Indicador)
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=kpi_valor,
        title={'text': kpi_nombre},
        domain={'x': [0, 0.5], 'y': [0.5, 1]}
    ), row=1, col=1)

    # Gráfico 2: Tendencia (Líneas)
    fig.add_trace(go.Scatter(x=linea_x, y=linea_y, name="Tendencia", line=dict(color='#11caa0', width=4)), row=1, col=2)

    # Gráfico 3: Comparativa (Barras)
    fig.add_trace(go.Bar(x=barras_x, y=barras_y, name="Categorías", marker_color='#3b82f6'), row=2, col=1)

    # Gráfico 4: Distribución (Pie/Donas)
    fig.add_trace(go.Pie(labels=pie_labels, values=pie_values, name="Desglose", hole=.4), row=2, col=2)

    # 2. Configuración estética profesional y tamaño
    fig.update_layout(
        title_text=f"📊 {titulo}",
        template="plotly_dark",
        height=900,  # Aumentamos la altura para acomodar todo el dashboard
        showlegend=False,
        paper_bgcolor="#0f172a", # Fondo azul oscuro profesional
        plot_bgcolor="#0f172a",
        margin=dict(l=40, r=40, t=100, b=40)
    )

    # 3. Guardar y retornar URL
    os.makedirs("public", exist_ok=True)
    nombre_archivo = f"dashboard_bi_{uuid.uuid4().hex[:6]}.html"
    fig.write_html(f"public/{nombre_archivo}")
    
    dominio = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8080")
    return f"Dashboard generado exitosamente. Accede aquí para ver el reporte completo: {dominio}/public/{nombre_archivo}"

def levantar_servidor_web():
    PORT = int(os.getenv("PORT", 8080))
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=levantar_servidor_web, daemon=True).start()
    mcp.run()
