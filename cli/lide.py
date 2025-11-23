#!/usr/bin/env python3
"""
L-ide CLI Tool - Attach to any AI conversation

Usage:
    lide attach [--session SESSION_ID]
    lide export SESSION_ID [--format markdown|json]
    lide list
    lide --version

The CLI tool monitors your AI conversations and provides real-time
warnings about contradictions, ambiguities, and context issues.
"""

import sys
import argparse
import requests
import json
from typing import Optional
import time

API_BASE = "http://localhost:8000/v0"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LideCLI:
    """L-ide Command Line Interface"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.current_session_id: Optional[str] = None
        
    def check_backend(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def create_session(self, initial_text: str = "") -> str:
        """Create a new session"""
        response = requests.post(
            f"{self.api_base}/sessions",
            json={"text": initial_text, "lang": "en"}
        )
        response.raise_for_status()
        return response.json()["id"]
    
    def send_message(self, text: str, session_id: str) -> dict:
        """Send a message for analysis"""
        # Create document
        doc_response = requests.post(
            f"{self.api_base}/docs",
            json={"text": text, "lang": "en"}
        )
        doc_response.raise_for_status()
        doc_id = doc_response.json()["id"]
        
        # Analyze
        analyze_response = requests.post(
            f"{self.api_base}/analyze",
            json={
                "docId": doc_id,
                "options": {"processing_mode": "Map"}
            }
        )
        analyze_response.raise_for_status()
        
        # Get graph
        graph_response = requests.get(f"{self.api_base}/docs/{doc_id}/graph")
        graph_response.raise_for_status()
        
        return graph_response.json()
    
    def display_diagnostics(self, graph: dict):
        """Display diagnostics in terminal with color coding"""
        diagnostics = graph.get("diagnostics", [])
        
        if not diagnostics:
            print(f"{Colors.OKGREEN}✓ No issues detected{Colors.ENDC}")
            return
        
        print(f"\n{Colors.BOLD}=== L-ide Diagnostics ==={Colors.ENDC}\n")
        
        # Group by severity
        errors = [d for d in diagnostics if d.get("severity") == "error"]
        warnings = [d for d in diagnostics if d.get("severity") == "warning"]
        
        if errors:
            print(f"{Colors.FAIL}ERRORS:{Colors.ENDC}")
            for diag in errors:
                print(f"  ❌ [{diag['kind']}] {diag['message']}")
            print()
        
        if warnings:
            print(f"{Colors.WARNING}WARNINGS:{Colors.ENDC}")
            for diag in warnings:
                print(f"  ⚠️  [{diag['kind']}] {diag['message']}")
            print()
        
        # Show stats
        node_count = len(graph.get("nodes", []))
        edge_count = len(graph.get("edges", []))
        print(f"{Colors.OKCYAN}Graph: {node_count} nodes, {edge_count} edges{Colors.ENDC}")
    
    def attach_mode(self, session_id: Optional[str] = None):
        """Enter interactive attach mode"""
        if not self.check_backend():
            print(f"{Colors.FAIL}Error: L-ide backend is not running{Colors.ENDC}")
            print("Start it with: cd prototype/backend && uvicorn main:app --reload")
            return 1
        
        # Create or use existing session
        if session_id:
            self.current_session_id = session_id
            print(f"{Colors.OKGREEN}Attached to session: {session_id}{Colors.ENDC}")
        else:
            self.current_session_id = self.create_session()
            print(f"{Colors.OKGREEN}Created new session: {self.current_session_id}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}L-ide is monitoring your conversation{Colors.ENDC}")
        print("Enter your messages below (or 'quit' to exit):\n")
        
        message_count = 0
        
        try:
            while True:
                # Get user input
                try:
                    text = input(f"{Colors.OKCYAN}You:{Colors.ENDC} ")
                except EOFError:
                    break
                
                if not text.strip():
                    continue
                
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                
                message_count += 1
                
                # Analyze message
                print(f"{Colors.OKBLUE}Analyzing...{Colors.ENDC}", end='\r')
                try:
                    graph = self.send_message(text, self.current_session_id)
                    print(" " * 50, end='\r')  # Clear "Analyzing..."
                    self.display_diagnostics(graph)
                except Exception as e:
                    print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
                
                print()  # Blank line for readability
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}Session complete!{Colors.ENDC}")
        print(f"Messages analyzed: {message_count}")
        print(f"Session ID: {self.current_session_id}")
        print(f"\nExport with: lide export {self.current_session_id}")
        
        return 0
    
    def list_sessions(self):
        """List all sessions"""
        if not self.check_backend():
            print(f"{Colors.FAIL}Error: Backend not running{Colors.ENDC}")
            return 1
        
        response = requests.get(f"{self.api_base}/sessions")
        response.raise_for_status()
        sessions = response.json()
        
        if not sessions:
            print("No sessions found")
            return 0
        
        print(f"\n{Colors.BOLD}Sessions:{Colors.ENDC}\n")
        for session in sessions:
            print(f"  {Colors.OKCYAN}{session['id']}{Colors.ENDC}")
            print(f"    Created: {session['created_at']}")
            print(f"    Nodes: {session['node_count']}, Edges: {session['edge_count']}")
            if session['diagnostic_count'] > 0:
                print(f"    Diagnostics: {Colors.WARNING}{session['diagnostic_count']}{Colors.ENDC}")
            print()
        
        return 0
    
    def export_session(self, session_id: str, format: str = "markdown"):
        """Export a session"""
        if not self.check_backend():
            print(f"{Colors.FAIL}Error: Backend not running{Colors.ENDC}")
            return 1
        
        response = requests.get(
            f"{self.api_base}/sessions/{session_id}/export",
            params={"format": format}
        )
        response.raise_for_status()
        data = response.json()
        
        if format == "markdown":
            print(data["content"])
        else:
            print(json.dumps(data, indent=2))
        
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="L-ide - GPS for AI Conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lide attach                    # Start new session
  lide attach --session abc123   # Resume session
  lide list                      # List all sessions
  lide export abc123             # Export as Markdown
  lide export abc123 --format json
        """
    )
    
    parser.add_argument('--version', action='version', version='L-ide 0.1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Attach command
    attach_parser = subparsers.add_parser('attach', help='Attach to conversation')
    attach_parser.add_argument('--session', help='Session ID to resume')
    
    # List command
    subparsers.add_parser('list', help='List all sessions')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export session')
    export_parser.add_argument('session_id', help='Session ID to export')
    export_parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = LideCLI()
    
    if args.command == 'attach':
        return cli.attach_mode(args.session)
    elif args.command == 'list':
        return cli.list_sessions()
    elif args.command == 'export':
        return cli.export_session(args.session_id, args.format)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
