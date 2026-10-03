import os
import platform
import subprocess
import sys

def check_compiler_dependencies():
    """Checks if essential Linux build tools are installed."""
    missing = []
    for tool in ["gcc", "g++", "make"]:
        try:
            subprocess.run([tool, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    return missing

def compile_single_app(app_name, linux_dir, install_bin_dir):
    """Compiles a single specified application folder."""
    app_path = os.path.join(linux_dir, app_name)
    output_binary = os.path.join(install_bin_dir, app_name.lower())
    compiled_successfully = False

    print(f"\n[*] Processing App: {app_name}")
    files = os.listdir(app_path)

    # Build Rule 1: Folder contains a Makefile
    if "Makefile" in files:
        print("    -> Found Makefile. Running 'make'...")
        try:
            subprocess.run(["make"], cwd=app_path, check=True)
            
            # Try to map common binary output names
            possible_bins = [app_name, app_name.lower(), "src", "main", "app"]
            found_bin = None
            for b in possible_bins:
                p = os.path.join(app_path, b)
                if os.path.isfile(p) and os.access(p, os.XOK):
                    found_bin = p
                    break
            
            if found_bin:
                os.rename(found_bin, output_binary)
                compiled_successfully = True
        except Exception as e:
            print(f"    [-] 'make' execution failed for {app_name}: {e}")

    # Build Rule 2: Folder contains source files directly (src.cpp or src.c)
    else:
        source_file = None
        compiler = None

        if "src.cpp" in files:
            source_file = "src.cpp"
            compiler = "g++"
        elif "src.c" in files:
            source_file = "src.c"
            compiler = "gcc"

        if source_file and compiler:
            full_source_path = os.path.join(app_path, source_file)
            print(f"    -> Found {source_file}. Compiling via {compiler}...")
            try:
                subprocess.run([compiler, full_source_path, "-o", output_binary], check=True)
                compiled_successfully = True
            except Exception as e:
                print(f"    [-] Native compilation failed for {source_file}: {e}")

    if compiled_successfully:
        os.chmod(output_binary, 0o755)
        print(f"    [+] Compiled successfully! Saved executable to: {output_binary}")
    else:
        print(f"    [i] No source code rules or Makefiles managed to build {app_name}.")

def interactive_linux_menu(linux_dir, install_bin_dir):
    """Displays interactive menu allowing users to choose what to install."""
    if not os.path.isdir(linux_dir):
        print(f"[!] 'Linux/' folder not found at: {linux_dir}")
        return

    # Scan and filter out files, only keeping application directories
    apps = [d for d in os.listdir(linux_dir) if os.path.isdir(os.path.join(linux_dir, d))]
    
    if not apps:
        print("[!] No application directories found inside the 'Linux/' folder.")
        return

    # Verify build tools before compilation loop
    missing_tools = check_compiler_dependencies()
    if missing_tools:
        print(f"[-] Warning: Missing compiler utilities: {', '.join(missing_tools)}")
        print("[-] Compilation might fail. Install them via: sudo apt install build-essential")

    while True:
        print("\n=== Linux Application Installation Menu ===")
        for idx, app in enumerate(apps, start=1):
            print(f" [{idx}] Install {app}")
        print(f" [{len(apps) + 1}] Install ALL Available Apps")
        print(" [Q] Quit Installer")

        choice = input("\nEnter your choice: ").strip()

        if choice.lower() == 'q':
            print("[i] Exiting installation wizard.")
            break

        # Check for "Install ALL" option
        if choice == str(len(apps) + 1):
            print("\n[!] Installing all applications...")
            for app in apps:
                compile_single_app(app, linux_dir, install_bin_dir)
            break

        # Check for specific single app choice
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(apps):
                selected_app = apps[choice_idx]
                compile_single_app(selected_app, linux_dir, install_bin_dir)
                break
            else:
                print("[-] Invalid number selection. Please choose an option from the menu.")
        except ValueError:
            print("[-] Invalid input format. Please enter a number or 'Q'.")

def main():
    # 1. Mandatory plain announcement
    print("\n" + "=" * 65)
    print("look at the lucas730-bug account on github for the apps")
    print("=" * 65 + "\n")

    current_os = platform.system().lower()
    
    # Safely pinpoint the local repo paths relative to this script
    repo_root = os.path.dirname(os.path.abspath(__file__))
    linux_apps_path = os.path.join(repo_root, "Linux")
    
    # Establish centralized output workspace paths inside user's Home directory
    home_dir = os.path.expanduser("~")
    install_dir = os.path.join(home_dir, ".iz4c810_tools")
    install_bin_dir = os.path.join(install_dir, "bin")
    
    try:
        if not os.path.exists(install_bin_dir):
            os.makedirs(install_bin_dir)
    except Exception as e:
        print(f"[-] Error writing tool directories: {e}")
        sys.exit(1)

    # 2. Windows Deployment Target
    if current_os == "windows":
        bat_path = os.path.join(install_dir, "launcher.bat")
        bat_content = (
            "@echo off\n"
            "title Tools Launcher\n"
            "cls\n"
            "echo ==========================================================\n"
            "echo look at the lucas730-bug account on github for the apps\n"
            "echo ==========================================================\n"
            "echo.\n"
            "echo Press any key to exit...\n"
            "pause > nul\n"
        )
        try:
            with open(bat_path, "w") as f:
                f.write(bat_content)
            print(f"[+] Windows plain text launcher generated at: {bat_path}")
        except Exception as e:
            print(f"[-] Failed to write Windows launcher tool: {e}")

    # 3. Linux Deployment Target (With Interactive Selection)
    elif current_os == "linux":
        sh_path = os.path.join(install_dir, "launcher.sh")
        sh_content = (
            "#!/bin/bash\n"
            "clear\n"
            "echo \"==========================================================\"\n"
            "echo \"look at the lucas730-bug account on github for the apps\"\n"
            "echo \"==========================================================\"\n"
            "echo \"\"\n"
            "read -n 1 -s -r -p \"Press any key to exit...\"\n"
            "echo \"\"\n"
        )
        try:
            with open(sh_path, "w") as f:
                f.write(sh_content)
            os.chmod(sh_path, 0o755)
            print(f"[+] Text notice launcher created at: {sh_path}")
        except Exception as e:
            print(f"[-] Failed to build Linux text notice asset: {e}")

        # Execute interactive selection menu
        interactive_linux_menu(linux_apps_path, install_bin_dir)

    else:
        print(f"[!] Operating System environment '{platform.system()}' is unsupported.")

if __name__ == "__main__":
    main()
