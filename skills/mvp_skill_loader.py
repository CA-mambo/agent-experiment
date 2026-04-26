# -*- coding: utf-8 -*-
"""
MVP Simulation: Agent Skill Management
1. Directory Discovery & Parsing (SKILL.md simulation)
2. Environment Isolation (Config Injection)
3. Conflict Resolution (Auto-renaming)
"""

import os
import json
import time
import shutil
from pathlib import Path

class SkillManager:
    def __init__(self, pool_path: str):
        self.pool_path = Path(pool_path)
        self.pool_path.mkdir(exist_ok=True)
        self.registry = {}
        self._load_registry()

    def _load_registry(self):
        """Simulate parsing skill.json or directory"""
        manifest = self.pool_path / "skill.json"
        if manifest.exists():
            try:
                self.registry = json.loads(manifest.read_text())
            except json.JSONDecodeError:
                self.registry = {}

    def install_skill(self, name: str, description: str, script_content: str):
        """Install a new skill (Simulate dropping a folder)"""
        print(f"[Manager] Installing skill: '{name}'...")
        
        # Conflict Resolution
        target_path = self.pool_path / name
        if target_path.exists():
            # Auto-rename logic
            timestamp = int(time.time())
            new_name = f"{name}-{timestamp}"
            target_path = self.pool_path / new_name
            print(f"[Manager] [Warning] Name conflict! Auto-renamed to '{new_name}'.")
            self.registry[new_name] = {
                "original_name": name,
                "description": description,
                "status": "active"
            }
        else:
            self.registry[name] = {
                "description": description,
                "status": "active"
            }

        # Create directory and script
        target_path.mkdir(exist_ok=True)
        (target_path / "SKILL.md").write_text(f"# {name}\n{description}")
        (target_path / "action.py").write_text(script_content)
        
        self._save_registry()

    def _save_registry(self):
        manifest = self.pool_path / "skill.json"
        manifest.write_text(json.dumps(self.registry, indent=2))

    def execute_skill(self, name: str):
        """Simulate skill execution with Env Isolation"""
        if name not in self.registry:
            print(f"[Error] Skill '{name}' not found.")
            return

        skill_path = self.pool_path / name
        config = {"QWENPAW_SKILL_ID": name, "QWENPAW_ACTION": "run"}
        
        print(f"\n[Runner] Executing skill: '{name}'")
        
        # 1. Inject Environment Variables
        original_env = os.environ.copy()
        os.environ.update(config)
        print(f"[Runner] [Inject] Injected Env: {config}")

        try:
            # 2. Run the skill (Simulation)
            script_path = skill_path / "action.py"
            if script_path.exists():
                print(f"[Runner] Executing {script_path.name}...")
                # In real QwenPaw, this would be executed in a subprocess or eval'd
                exec(compile(script_path.read_text(), str(script_path), 'exec'))
            
            print(f"[Runner] [OK] Skill '{name}' completed successfully.")
        finally:
            # 3. Restore Environment (Cleanup)
            os.environ.clear()
            os.environ.update(original_env)
            print(f"[Runner] [Cleanup] Environment restored.")

# ================= MVP Run =================

def main():
    print("--- Agent Skill Manager MVP ---")
    
    import_dir = "./temp_skill_pool"
    shutil.rmtree(import_dir, ignore_errors=True) # Ensure clean start
    manager = SkillManager(import_dir)

    # 1. Install First Skill
    manager.install_skill(
        name="weather_tool",
        description="Fetches weather data",
        script_content="print(f'  -> Weather for {os.environ.get(\"QWENPAW_SKILL_ID\")} is Sunny!')"
    )
    manager.execute_skill("weather_tool")

    # 2. Install Duplicate Skill (Test Conflict Resolution)
    print("\n--- Testing Conflict Resolution ---")
    manager.install_skill(
        name="weather_tool", # Same name
        description="Fetches better weather data",
        script_content="print('  -> Fetching advanced weather data...')"
    )

    # 3. List all skills
    print("\n[Manager] Current Registry:")
    for name, info in manager.registry.items():
        print(f" - {name}: {info['description']}")

    # Cleanup
    shutil.rmtree(import_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
