import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agent.session import SessionManager
from app.agent.interceptor import Interceptor

def main():
    print("=== Language IDE: Agent Sidecar Demo ===")
    print("This demo simulates a chat where the 'Interceptor' watches for contradictions.")
    print("Try saying: 'I have blue eyes.' then later 'I have brown eyes.'")
    print("Type 'exit' to quit.\n")

    session = SessionManager()
    interceptor = Interceptor()

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ('exit', 'quit'):
                break
            
            if not user_input.strip():
                continue

            print("... (Interceptor analyzing) ...")
            
            # Run the Interceptor
            warning = interceptor.check_and_inject(user_input, session)

            # DEBUG: Print assertions
            graph = session.get_graph()
            print(f"DEBUG: Current Graph Assertions ({len(graph.assertions)}):")
            for a in graph.assertions:
                print(f"  - {a.subject} --[{a.predicate}]--> {a.object}")

            if warning:
                print(f"\n🛑 INTERCEPTOR TRIGGERED 🛑")
                print(f"Injecting System Message to Agent:\n{warning}")
                print("\nAgent: Wait, I'm confused. " + warning.replace("[SYSTEM WARNING: ", "").replace("]", ""))
            else:
                print("Agent: I understand. (No issues detected)")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
