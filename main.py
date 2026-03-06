import json
import os
import argparse
import sqlite3
import webbrowser
import database
import collector
import ai_analyzer
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Inicializa as cores do terminal e o console do Rich
init(autoreset=True)
console = Console()

RISK_COLORS = {
    "VERDE": "green",
    "AMARELO": "yellow",
    "LARANJA": "dark_orange",
    "VERMELHO": "red"
}

# Cores legadas para o scan
COLORAMA_RISK_COLORS = {
    "VERDE": Fore.GREEN,
    "AMARELO": Fore.YELLOW,
    "LARANJA": Fore.MAGENTA,
    "VERMELHO": Fore.RED
}

def migrate_config_to_db():
    """Migra feeds do config.json para o banco de dados na primeira execução."""
    config_path = "config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            feeds = config.get("feeds", [])
            for url in feeds:
                database.insert_source(url, url)
            os.rename(config_path, config_path + ".bak")
            console.print("[green]Migração de fontes do config.json concluída.[/green]")
        except Exception as e:
            console.print(f"[red]Erro na migração: {e}[/red]")

def add_source(url, nome=None):
    """Adiciona uma nova URL de feed ao banco de dados."""
    if not nome:
        nome = url
    if database.insert_source(nome, url):
        console.print(f"[green]Fonte adicionada com sucesso:[/green] {nome} ({url})")
    else:
        console.print(f"[yellow]Não foi possível adicionar a fonte. Verifique se a URL já existe.[/yellow]")

def list_sources():
    """Lista todas as fontes cadastradas no banco de dados."""
    sources = database.get_all_sources()
    if not sources:
        console.print("[yellow]Nenhuma fonte configurada no banco de dados.[/yellow]")
        return
    table = Table(title="Fontes OSINT Monitoradas", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=3)
    table.add_column("Nome", width=20)
    table.add_column("URL do Feed RSS")
    table.add_column("Status", width=10)
    for sid, nome, url, ativo in sources:
        status = "[green]Ativo[/green]" if ativo else "[red]Inativo[/red]"
        table.add_row(str(sid), nome, url, status)
    console.print(table)

def remove_source(sid):
    """Remove uma fonte do banco de dados pelo ID."""
    if database.remove_source(sid):
        console.print(f"[green]Fonte #{sid} removida com sucesso.[/green]")
    else:
        console.print(f"[red]Erro: Fonte #{sid} não encontrada.[/red]")

def run_scan():
    """Executa a rotina de busca e análise utilizando fontes do banco de dados."""
    print(f"{Fore.CYAN}--- Iniciando Scan de Fontes OSINT ---{Style.RESET_ALL}\n")
    database.setup_database()
    sources_info = database.get_active_sources_info()
    if not sources_info:
        print(f"{Fore.RED}Nenhuma fonte ativa encontrada no banco de dados.{Style.RESET_ALL}")
        return
    
    source_ids = {url: sid for sid, url in sources_info}
    urls = [url for sid, url in sources_info]

    print(f"Coletando feeds RSS de {len(urls)} fontes ativas...")
    news_items = collector.fetch_rss_feeds(urls)
    print(f"Total de {len(news_items)} itens encontrados.")

    new_alerts_count = 0
    for item in news_items:
        link = item['link']
        if database.link_exists(link):
            continue
            
        new_alerts_count += 1
        print(f"\n--- Novo Alerta Detectado ---")
        print(f"Título: {item['titulo']}")
        print(f"Fonte: {item['fonte']}")
        
        # Tenta mapear o link de volta para o source_id original
        # Collector.py atualmente não retorna a URL do feed, apenas o nome da fonte extraído do feed
        # Como as URLs são únicas, podemos tentar inferir ou ajustar o collector
        # Simplificação: Usaremos o primeiro source_id que corresponda se necessário, 
        # mas aqui passaremos o que temos.
        # Idealmente o collector deveria retornar o feed_url original.
        # Por agora, usaremos 0 ou tentaremos encontrar nos urls.
        sid = 0
        for f_url, f_id in source_ids.items():
            if f_url in link: # Heurística simples
                sid = f_id
                break

        print("Analisando com Gemini IA...")
        analysis = ai_analyzer.analyze_risk(f"{item['titulo']}. {item['descricao']}")
        
        nivel = analysis.get('nivel_risco', 'DESCONHECIDO').upper()
        resumo = analysis.get('resumo_tatico', 'N/A')
        
        database.save_alerta(
            source_id=sid,
            fonte=item['fonte'],
            titulo=item['titulo'],
            link=item['link'],
            nivel_risco=nivel,
            resumo_tatico=resumo,
            full_content=item['descricao']
        )
        
        color = COLORAMA_RISK_COLORS.get(nivel, Fore.WHITE)
        print(f"{color}[RISCO: {nivel}]{Style.RESET_ALL}")
        print(f"{color}Resumo: {resumo}{Style.RESET_ALL}")
        
        if nivel == "VERMELHO":
            print(f"{Fore.RED}*** ALERTA CRÍTICO ATIVADO ***{Style.RESET_ALL}")

    if new_alerts_count == 0:
        print(f"\n{Fore.GREEN}Nenhum novo alerta encontrado.{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}--- Scan Concluído ---{Style.RESET_ALL}")

def list_alerts(limit=10, nivel=None, unread=False):
    """Lista os alertas salvos no banco de dados com filtros."""
    title = f"Últimos {limit} Alertas"
    if nivel: title += f" [Nível: {nivel.upper()}]"
    if unread: title += " [Somente Não Lidos]"
    
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Data", style="dim", width=20)
    table.add_column("Nível", width=10)
    table.add_column("Status", width=8)
    table.add_column("Título", style="bold")

    rows = database.get_alerts(limit=limit, nivel=nivel, only_unread=unread)
    
    if not rows:
        console.print("[yellow]Nenhum alerta encontrado com os filtros aplicados.[/yellow]")
    else:
        for idx, data, n, titulo, read in rows:
            color = RISK_COLORS.get(n.upper(), "white")
            status = "[dim]Lido[/dim]" if read else "[bold green]NOVO[/bold green]"
            table.add_row(str(idx), data, f"[{color}]{n}[/{color}]", status, titulo)
        console.print(table)

def show_alert(alert_id):
    """Exibe detalhes completos de um alerta e marca como lido."""
    row = database.get_alert_by_id(alert_id)
    if not row:
        console.print(f"[red]Alerta com ID {alert_id} não encontrado.[/red]")
        return

    idx, data, fonte, titulo, link, nivel, resumo, content, read = row
    color = RISK_COLORS.get(nivel.upper(), "white")

    msg = f"[bold]Data:[/bold] {data}\n"
    msg += f"[bold]Fonte:[/bold] {fonte}\n"
    msg += f"[bold]Nível de Risco:[/bold] [{color}]{nivel}[/{color}]\n\n"
    msg += f"[bold]Resumo Tático:[/bold]\n{resumo}\n\n"
    msg += f"[bold]Conteúdo Original:[/bold]\n{content or 'Não disponível'}\n\n"
    msg += f"[bold]Link:[/bold] {link}"

    panel = Panel(msg, title=f"[bold cyan]Alerta #{idx}: {titulo}[/bold cyan]", expand=False)
    console.print(panel)
    
    database.mark_as_read(alert_id)

def open_alert_link(alert_id):
    """Abre o link original e marca o alerta como lido."""
    row = database.get_alert_by_id(alert_id)
    if not row:
        console.print(f"[red]Alerta com ID {alert_id} não encontrado.[/red]")
        return

    link = row[4]
    console.print(f"[cyan]Abrindo link no navegador:[/cyan] {link}")
    webbrowser.open(link)
    database.mark_as_read(alert_id)

def run_sitrep(hours=24):
    """Gera um Relatório Situacional Agregado (SitRep)."""
    console.print(f"[bold cyan]--- Gerando SitRep (Últimas {hours}h) ---[/bold cyan]\n")
    recent_alerts = database.get_recent_alerts(hours=hours)
    if not recent_alerts:
        console.print("[yellow]Nenhum alerta recente para gerar um relatório.[/yellow]")
        return
    summaries = [row[0] for row in recent_alerts]
    console.print(f"Sintetizando {len(summaries)} alertas com IA...")
    sitrep = ai_analyzer.generate_sitrep(summaries)
    
    # Salva no banco de dados para consulta histórica
    database.save_sitrep(hours, sitrep)
    
    panel = Panel(sitrep, title="[bold red]SITREP: RELATÓRIO SITUACIONAL[/bold red]", expand=False)
    console.print(panel)

def list_sitreps(limit=5):
    """Lista o histórico de relatórios situacionais."""
    console.print(f"[bold cyan]--- Histórico de SitReps (Últimos {limit}) ---[/bold cyan]\n")
    rows = database.get_latest_sitreps(limit=limit)
    if not rows:
        console.print("[yellow]Nenhum SitRep encontrado no histórico.[/yellow]")
        return
    for idx, data, horas, conteudo in rows:
        panel = Panel(conteudo, title=f"SitRep #{idx} - Gerado em {data} ({horas}h)", expand=False)
        console.print(panel)
        console.print("\n")

def main():
    database.setup_database()
    migrate_config_to_db()
    parser = argparse.ArgumentParser(description="Gvatanto OSINT")
    subparsers = parser.add_subparsers(dest="command", help="Comandos")

    subparsers.add_parser("scan", help="Scan de novos alertas")

    list_p = subparsers.add_parser("list", help="Lista alertas")
    list_p.add_argument("--limit", type=int, default=10)
    list_p.add_argument("--nivel", choices=["VERDE", "AMARELO", "LARANJA", "VERMELHO"])
    list_p.add_argument("--unread", action="store_true", help="Mostrar apenas alertas não lidos")

    show_p = subparsers.add_parser("show", help="Detalhes do alerta")
    show_p.add_argument("id", type=int)

    open_p = subparsers.add_parser("open", help="Abrir link no browser")
    open_p.add_argument("id", type=int)

    sit_p = subparsers.add_parser("sitrep", help="Relatório situacional")
    sit_p.add_argument("--hours", type=int, default=24, help="Janela de horas para novo relatório")
    sit_p.add_argument("--history", action="store_true", help="Ver histórico de relatórios salvos")
    sit_p.add_argument("--limit", type=int, default=5, help="Limite de relatórios no histórico")

    src_p = subparsers.add_parser("source", help="Gerenciar fontes")
    src_sub = src_p.add_subparsers(dest="source_command")
    
    add_p = src_sub.add_parser("add", help="Adicionar fonte")
    add_p.add_argument("url")
    add_p.add_argument("--nome")
    
    src_sub.add_parser("list", help="Listar fontes")
    
    rem_p = src_sub.add_parser("remove", help="Remover fonte")
    rem_p.add_argument("id", type=int)

    args = parser.parse_args()

    if args.command == "scan": run_scan()
    elif args.command == "list": list_alerts(args.limit, args.nivel, args.unread)
    elif args.command == "show": show_alert(args.id)
    elif args.command == "open": open_alert_link(args.id)
    elif args.command == "sitrep":
        if args.history:
            list_sitreps(args.limit)
        else:
            run_sitrep(args.hours)
    elif args.command == "source":
        if args.source_command == "add": add_source(args.url, args.nome)
        elif args.source_command == "list": list_sources()
        elif args.source_command == "remove": remove_source(args.id)
        else: src_p.print_help()
    else: parser.print_help()

if __name__ == "__main__":
    main()
