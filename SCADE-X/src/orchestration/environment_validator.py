"""
SCADE-X Environment Validator
=============================
Validates that all core and subsystem dependencies are installed and available
in the active Python interpreter before executing the pipeline stages.
"""
import sys
import logging

logger = logging.getLogger("SCADE-X-EnvValidator")

# Mapping from python import module names to pip package names
REQUIRED_IMPORTS = {
    "pm4py": "pm4py",
    "pandas": "pandas",
    "numpy": "numpy",
    "sklearn": "scikit-learn",
    "networkx": "networkx",
    "torch": "torch",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "yaml": "pyyaml",
    "flask": "flask"
}

def validate_environment(custom_logger=None) -> bool:
    """
    Checks that all required dependencies are importable.
    Logs explicit warnings and auto-generated install suggestions if any are missing.
    Returns True if all imports succeed, otherwise raises a detailed RuntimeError.
    """
    log = custom_logger if custom_logger is not None else logger
    missing_packages = []
    
    log.info("Starting automated environment dependency validation...")
    
    for module_name, pip_name in REQUIRED_IMPORTS.items():
        try:
            __import__(module_name)
            log.debug(f"Dependency check passed: {module_name}")
        except ImportError:
            missing_packages.append(pip_name)
            log.warning(f"Missing dependency: {module_name} (pip package: {pip_name})")
            
    if missing_packages:
        log.error("=" * 60)
        log.error("CRITICAL ENVIRONMENT VALIDATION FAILURE")
        log.error("=" * 60)
        log.error(f"The following required dependencies are missing: {', '.join(missing_packages)}")
        log.error("")
        
        # Auto-generate exact install suggestions
        install_command = f"pip install {' '.join(missing_packages)}"
        log.error(">>> SUGGESTED FIX:")
        log.error(f"    Run the following command to install the missing dependencies:")
        log.error(f"    {install_command}")
        log.error("    Or install the complete manifest via:")
        log.error("    pip install -r requirements.txt")
        log.error("=" * 60)
        
        raise RuntimeError(
            f"Environment validation failed. Missing packages: {', '.join(missing_packages)}. "
            f"Suggested fix: {install_command}"
        )
        
    log.info("✅ All core environment dependencies are successfully validated.")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        validate_environment()
    except RuntimeError as e:
        sys.exit(1)
