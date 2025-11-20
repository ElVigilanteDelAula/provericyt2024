import sys
import subprocess

def check_python_version():
    """Verificar versión de Python."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  Se recomienda Python 3.8 o superior")
    return True

def check_package(package_name, import_name=None):
    """Verificar si un paquete está instalado."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} instalado")
        return True
    except ImportError:
        print(f" {package_name} NO instalado")
        return False

def check_nilearn_data():
    """Verificar si los datos de nilearn están descargados."""
    try:
        from nilearn import datasets
        import os
        
        print("\n--- Verificando datos de Nilearn ---")
        print("Intentando descargar/verificar datos anatómicos del cerebro...")
        print("(Esto puede tardar varios minutos la primera vez)\n")
        
        # Esto descargará los datos si no existen
        fsaverage = datasets.fetch_surf_fsaverage()
        
        # Verificar que los archivos existan
        if os.path.exists(fsaverage.pial_right) and os.path.exists(fsaverage.pial_left):
            print("✓ Datos anatómicos del cerebro descargados correctamente")
            print(f"  Ubicación: {os.path.dirname(fsaverage.pial_right)}")
            return True
        else:
            print("Error: Los archivos de datos no se encontraron")
            return False
            
    except Exception as e:
        print(f"Error al verificar datos de nilearn: {str(e)}")
        return False

def check_config_file():
    """Verificar si existe el archivo config.json."""
    import os
    if os.path.exists('config.json'):
        print("✓ config.json encontrado")
        return True
    else:
        print("config.json NO encontrado")
        print("  → Duplica 'config_template.json' y renómbralo a 'config.json'")
        return False

def main():
    print("=" * 60)
    print("VERIFICACIÓN DE INSTALACIÓN - Proyecto EEG")
    print("=" * 60)
    print()
    
    # Verificar Python
    print("--- Verificando Python ---")
    check_python_version()
    print()
    
    # Verificar paquetes principales
    print("--- Verificando paquetes principales ---")
    packages = [
        ('dash', 'dash'),
        ('dash-bootstrap-components', 'dash_bootstrap_components'),
        ('flask', 'flask'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('plotly', 'plotly'),
        ('requests', 'requests'),
    ]
    
    all_installed = True
    for pkg_name, import_name in packages:
        if not check_package(pkg_name, import_name):
            all_installed = False
    
    print()
    
    # Verificar nilearn (opcional)
    print("--- Verificando visualización 3D (opcional) ---")
    nilearn_installed = check_package('nilearn', 'nilearn')
    
    if nilearn_installed:
        nilearn_data_ok = check_nilearn_data()
    else:
        print("   Para habilitar la visualización 3D del cerebro:")
        print("     pip install nilearn")
        nilearn_data_ok = False
    
    print()
    
    # Verificar archivo de configuración
    print("--- Verificando configuración ---")
    config_ok = check_config_file()
    print()
    
    # Resumen
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    if all_installed and config_ok:
        print("✓ Instalación básica completa")
        print("\nPuedes ejecutar:")
        print("  python live_app.py  # Aplicación en vivo")
        print("  python app.py       # Explorador de base de datos")
    else:
        print("Faltan componentes por instalar")
    
    if nilearn_installed and not nilearn_data_ok:
        print("\n Nilearn está instalado pero los datos no se descargaron correctamente")
    
    if nilearn_installed and nilearn_data_ok:
        print("\n✓ Visualización 3D del cerebro lista para usar")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
