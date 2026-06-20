import os
import sys
import uuid
import json
import click
from rich.console import Console
from rich.panel import Panel

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.graph import build_graph

console = Console()

def get_persona_emoji(persona: str) -> str:
    if persona == "TECHNICAL_EXPERT":
        return "🔧 TECHNICAL EXPERT"
    elif persona == "FRUSTRATED_USER":
        return "😤 FRUSTRATED USER"
    elif persona == "BUSINESS_EXECUTIVE":
        return "💼 BUSINESS EXECUTIVE"
    return "👤 UNKNOWN"

def get_sentiment_emoji(score: float) -> str:
    if score > 0.2:
        return "📈 Positive"
    elif score < -0.2:
        return "📉 Negative"
    return "➡️ Neutral"

@click.command()
def main():
    # Print welcome banner
    console.print(Panel.fit(
        "[bold green]NovaSuite AI Support Agent v1.0.0[/bold green]\n"
        "Interactive CLI REPL mode. Type 'quit' or 'exit' to end, 'reset' to clear history.",
        title="Welcome"
    ))

    # Compile the LangGraph
    graph = build_graph()
    session_id = str(uuid.uuid4())[:8]
    console.print(f"[dim]Session ID: {session_id}[/dim]\n")

    # Initial state
    state = {
        "session_id": session_id,
        "messages": [],
        "current_message": "",
        "persona": "",
        "persona_confidence": 0.0,
        "retrieved_chunks": [],
        "retrieval_confidence": 0.0,
        "response": "",
        "escalate": False,
        "escalation_reason": "",
        "handoff_summary": None,
        "turn_count": 0,
        "resolution_attempts": 0,
        "sentiment_scores": [],
        "attempted_steps": []
    }

    while True:
        try:
            user_input = click.prompt("You")
            if user_input.strip().lower() in ["quit", "exit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if user_input.strip().lower() == "reset":
                session_id = str(uuid.uuid4())[:8]
                state = {
                    "session_id": session_id,
                    "messages": [],
                    "current_message": "",
                    "persona": "",
                    "persona_confidence": 0.0,
                    "retrieved_chunks": [],
                    "retrieval_confidence": 0.0,
                    "response": "",
                    "escalate": False,
                    "escalation_reason": "",
                    "handoff_summary": None,
                    "turn_count": 0,
                    "resolution_attempts": 0,
                    "sentiment_scores": [],
                    "attempted_steps": []
                }
                console.print(f"[bold yellow]Session reset. New Session ID: {session_id}[/bold yellow]\n")
                continue

            if not user_input.strip():
                continue

            # Update current message in state
            state["current_message"] = user_input

            # Run through graph
            with console.status("[bold green]Agent thinking..."):
                state = graph.invoke(state)

            # Extract info
            persona = state.get("persona", "UNKNOWN")
            persona_conf = state.get("persona_confidence", 0.0)
            retrieved_chunks = state.get("retrieved_chunks", [])
            sentiment_scores = state.get("sentiment_scores", [0.0])
            latest_sentiment = sentiment_scores[-1] if sentiment_scores else 0.0
            escalate = state.get("escalate", False)

            # Print metadata details
            console.print(f"[bold blue]\[Persona Detected][/bold blue]  {get_persona_emoji(persona)} (confidence: {persona_conf:.2f})")
            
            sources = ", ".join(list(set(c.get("source") for c in retrieved_chunks if c.get("source"))))
            if sources:
                console.print(f"[bold blue]\[Sources Retrieved][/bold blue] {sources}")
            else:
                console.print(f"[bold blue]\[Sources Retrieved][/bold blue] None")

            console.print(f"[bold blue]\[Sentiment][/bold blue]         {get_sentiment_emoji(latest_sentiment)} ({latest_sentiment:.2f})")
            console.print(f"[bold blue]\[Escalation][/bold blue]        {'[red]TRIGGERED[/red]' if escalate else 'Not triggered'}")
            console.print()

            # Output response or handoff summary
            if escalate:
                console.print("[bold red]⚠️ ESCALATION HANDOFF SUMMARY GENERATED:[/bold red]")
                handoff_json = json.dumps(state.get("handoff_summary", {}), indent=2)
                console.print(Panel(handoff_json, title="Handoff Summary (JSON)", border_style="red"))
                console.print("[yellow]System paused. Session escalated to human.[/yellow]")
                break
            else:
                response = state.get("response", "")
                console.print(f"[bold green]Agent:[/bold green] {response}")
                console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error executing turn: {e}[/bold red]")

if __name__ == "__main__":
    main()
