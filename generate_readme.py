# generate_readme.py
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Створюємо структуру
print("🔧 Генеруємо структуру проєкту...")
subprocess.run("python generate_structure.py", shell=True)

# Читаємо структуру
with open("PROJECT-STRUCTURE.md") as f:
    project_structure = f.read()

# Завантажуємо шаблон
with open("README_template.md") as f:
    template = f.read()

# Підставляємо значення
readme = template.replace("{{project_name}}", "Arbitrage Bot")
readme = readme.replace("{{description}}", "Крипто арбітражний бот із підтримкою декількох бірж, аналізом спредів та API.")
readme = readme.replace("{{quickstart_code}}", "python3 -m venv venv\npip install -r requirements.txt\nflask db upgrade\npython run.py")
readme = readme.replace("{{project_structure}}", project_structure.strip())

# Записуємо
with open("README.md", "w") as f:
    f.write(readme)

print("✅ README.md згенеровано!")
