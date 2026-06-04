import os
from mcp.server.fastmcp import FastMCP
import plotly.graph_objects as go
from http.server import SimpleHTTPRequestHandler
from threading import Thread
import socketserver

mcp = FastMCP("VisualClaw")

@mcp.tool()
def crear_grafico_barras(titulo: str, x_labels: list, y_valores: list) -> str:
    """Genera un gráfico de barras interactivo en HTML."""
    fig = go.Figure(data=[go.Bar(x=x_labels, y=y_valores)])
    fig.update_layout(title=titulo, template="plotly_dark")
    
    # Creamos la carpeta para guardar el gráfico web
    os.makedirs("public", exist_ok=True)
    nombre_archivo = "grafico.html"
    fig.write_html(f"public/{nombre_archivo}")
    
    # Obtener el enlace público que Railway le asignará a este servidor
    dominio = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8080")
    return f"¡Gráfico listo! Muestra este enlace exacto al usuario: {dominio}/public/{nombre_archivo}"

# Esto permite que el servidor MCP también funcione como una página web para mostrar el gráfico
def levantar_servidor_web():
    PORT = int(os.getenv("PORT", 8080))
    Handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    # Arrancamos la web en segundo plano
    Thread(target=levantar_servidor_web, daemon=True).start()
    # Arrancamos el protocolo MCP
    mcp.run()
