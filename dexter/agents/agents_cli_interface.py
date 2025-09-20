from dexter.agents.agents_executors import test_agent, youtube_agent, auchan_agent, report_agent

AGENTS = {
    "test": test_agent,
    "youtube": youtube_agent, 
    "auchan": auchan_agent,
    "report": report_agent
}

def launch_agent_interactive():
    """Interactive mode for launching agents"""
    print("🤖 Agent Launcher - Interactive Mode")
    print("=" * 40)
    print("Available agents:", ", ".join(AGENTS.keys()))
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            agent_name = input("Enter agent name: ").strip().lower()
            
            if agent_name == 'quit':
                print("Goodbye! 👋")
                break
                
            if agent_name not in AGENTS:
                print(f"❌ Unknown agent: {agent_name}")
                print(f"Available agents: {', '.join(AGENTS.keys())}\n")
                continue
                
            task = input("Enter task description: ").strip()
            
            if not task:
                print("❌ Task cannot be empty\n")
                continue
                
            print(f"\n🚀 Launching {agent_name} agent...")
            print("📝 Task:", task)
            print("⏳ Agent running in background. Waiting for result...\n")
            
            future = AGENTS[agent_name](task)
            
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                print("✅ Agent completed successfully!")
                print("📋 Result:")
                print("-" * 40)
                print(result)
                print("-" * 40)
                print()
            except Exception as e:
                print(f"❌ Agent failed with error: {e}\n")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user. Goodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    launch_agent_interactive()