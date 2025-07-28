import ast
import re
import os
import yaml
import json
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import fnmatch
from datetime import datetime


class PolicySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyAction(Enum):
    WARN = "warn"
    BLOCK = "block"
    LOG = "log"


@dataclass
class PolicyViolation:
    rule_id: str
    rule_name: str
    severity: PolicySeverity
    action: PolicyAction
    description: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    matched_content: Optional[str] = None
    suggestion: Optional[str] = None
    policy_category: str = "custom"


@dataclass
class PolicyRule:
    id: str
    name: str
    description: str
    severity: PolicySeverity
    action: PolicyAction
    enabled: bool = True
    patterns: List[str] = field(default_factory=list)
    forbidden_imports: List[str] = field(default_factory=list)
    forbidden_functions: List[str] = field(default_factory=list)
    forbidden_directories: List[str] = field(default_factory=list)
    forbidden_env_vars: List[str] = field(default_factory=list)
    forbidden_file_operations: List[str] = field(default_factory=list)
    allowed_exceptions: List[str] = field(default_factory=list)
    context_conditions: Dict[str, Any] = field(default_factory=dict)
    custom_ast_checks: List[str] = field(default_factory=list)
    category: str = "custom"
    tags: List[str] = field(default_factory=list)


class PolicyEngine:
    """
    Advanced policy engine for customizable code security analysis.
    Supports YAML/JSON configuration for defining organizational security policies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.rules: Dict[str, PolicyRule] = {}
        self.global_settings: Dict[str, Any] = {}
        self.config_path = config_path or "policies/security_policies.yaml"
        self.violation_history: List[PolicyViolation] = []
        
        # Initialize with default config if exists
        if os.path.exists(self.config_path):
            self.load_policies(self.config_path)
        else:
            self._create_default_policies()
    
    def load_policies(self, config_path: str) -> None:
        """Load policies from YAML or JSON configuration file"""
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    config = json.load(f)
                else:
                    raise ValueError("Config file must be YAML or JSON")
            
            self._parse_config(config)
            
        except Exception as e:
            print(f"Error loading policies from {config_path}: {e}")
            self._create_default_policies()
    
    def _parse_config(self, config: Dict[str, Any]) -> None:
        """Parse configuration and create policy rules"""
        # Load global settings
        self.global_settings = config.get('global_settings', {})
        
        # Load policy rules
        rules_config = config.get('policies', {})
        self.rules = {}
        
        for rule_id, rule_data in rules_config.items():
            try:
                rule = PolicyRule(
                    id=rule_id,
                    name=rule_data.get('name', rule_id),
                    description=rule_data.get('description', ''),
                    severity=PolicySeverity(rule_data.get('severity', 'medium')),
                    action=PolicyAction(rule_data.get('action', 'warn')),
                    enabled=rule_data.get('enabled', True),
                    patterns=rule_data.get('patterns', []),
                    forbidden_imports=rule_data.get('forbidden_imports', []),
                    forbidden_functions=rule_data.get('forbidden_functions', []),
                    forbidden_directories=rule_data.get('forbidden_directories', []),
                    forbidden_env_vars=rule_data.get('forbidden_env_vars', []),
                    forbidden_file_operations=rule_data.get('forbidden_file_operations', []),
                    allowed_exceptions=rule_data.get('allowed_exceptions', []),
                    context_conditions=rule_data.get('context_conditions', {}),
                    custom_ast_checks=rule_data.get('custom_ast_checks', []),
                    category=rule_data.get('category', 'custom'),
                    tags=rule_data.get('tags', [])
                )
                self.rules[rule_id] = rule
            except Exception as e:
                print(f"Error parsing rule {rule_id}: {e}")
    
    def _create_default_policies(self) -> None:
        """Create default security policies"""
        default_rules = {
            'prod_env_modification': PolicyRule(
                id='prod_env_modification',
                name='Production Environment Modification',
                description='Prevents modification of production environment variables',
                severity=PolicySeverity.CRITICAL,
                action=PolicyAction.BLOCK,
                forbidden_env_vars=['PROD_*', 'PRODUCTION_*', '*_PROD', '*_PRODUCTION'],
                patterns=[
                    r'os\.environ\[[\'"]PROD',
                    r'os\.environ\[[\'"]\w*PROD',
                    r'setenv.*PROD',
                    r'export.*PROD'
                ],
                category='environment'
            ),
            'sensitive_directory_access': PolicyRule(
                id='sensitive_directory_access',
                name='Sensitive Directory Access',
                description='Prevents access to sensitive system directories',
                severity=PolicySeverity.HIGH,
                action=PolicyAction.WARN,
                forbidden_directories=['/etc/*', '/sys/*', '/proc/*', '/root/*', 'C:\\Windows\\*'],
                patterns=[
                    r'open\([\'\"]/etc/',
                    r'open\([\'\"]/sys/',
                    r'open\([\'\"]/proc/',
                    r'Path\([\'\"]/etc/',
                ],
                category='filesystem'
            ),
            'dangerous_libraries': PolicyRule(
                id='dangerous_libraries',
                name='Dangerous Library Usage',
                description='Prevents usage of potentially dangerous libraries',
                severity=PolicySeverity.HIGH,
                action=PolicyAction.WARN,
                forbidden_imports=['pickle', 'dill', 'marshal', 'shelve'],
                patterns=[
                    r'import\s+pickle',
                    r'from\s+pickle\s+import',
                    r'import\s+marshal',
                    r'subprocess\.call.*shell=True'
                ],
                category='imports'
            ),
            'database_credential_exposure': PolicyRule(
                id='database_credential_exposure',
                name='Database Credential Exposure',
                description='Prevents hardcoded database credentials',
                severity=PolicySeverity.CRITICAL,
                action=PolicyAction.BLOCK,
                patterns=[
                    r'password\s*=\s*[\'\"]\w+[\'"]',
                    r'passwd\s*=\s*[\'\"]\w+[\'"]',
                    r'mysql://.*:.*@',
                    r'postgresql://.*:.*@',
                    r'mongodb://.*:.*@'
                ],
                category='credentials'
            ),
            'file_system_modifications': PolicyRule(
                id='file_system_modifications',
                name='File System Modifications',
                description='Controls file system modification operations',
                severity=PolicySeverity.MEDIUM,
                action=PolicyAction.WARN,
                forbidden_file_operations=['rm -rf', 'rmdir', 'del /f', 'format'],
                patterns=[
                    r'os\.remove\(',
                    r'os\.rmdir\(',
                    r'shutil\.rmtree\(',
                    r'pathlib.*\.unlink\(',
                    r'subprocess.*rm\s+-rf'
                ],
                category='filesystem'
            ),
            'network_requests': PolicyRule(
                id='network_requests',
                name='External Network Requests',
                description='Controls external network access',
                severity=PolicySeverity.MEDIUM,
                action=PolicyAction.LOG,
                patterns=[
                    r'requests\.(get|post|put|delete)',
                    r'urllib\.request',
                    r'http\.client',
                    r'socket\.connect'
                ],
                allowed_exceptions=['localhost', '127.0.0.1', '*.internal.com'],
                category='network'
            )
        }
        
        self.rules = default_rules
        self.global_settings = {
            'strict_mode': False,
            'log_violations': True,
            'auto_block_critical': True,
            'notification_webhook': None
        }
    
    def analyze_code(self, code: str, 
                    file_path: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> List[PolicyViolation]:
        """
        Analyze code against all enabled policy rules
        
        Args:
            code: Python code to analyze
            file_path: Optional file path for context
            context: Additional context information
            
        Returns:
            List of policy violations found
        """
        violations = []
        context = context or {}
        
        # Parse code for AST analysis
        ast_tree = None
        try:
            ast_tree = ast.parse(code)
        except SyntaxError:
            pass  # Continue with string analysis if AST parsing fails
        
        # Check each enabled rule
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            rule_violations = self._check_rule(code, rule, ast_tree, file_path, context)
            violations.extend(rule_violations)
        
        # Store violations in history
        self.violation_history.extend(violations)
        
        return violations
    
    def _check_rule(self, code: str, rule: PolicyRule, ast_tree: Optional[ast.AST],
                   file_path: Optional[str], context: Dict[str, Any]) -> List[PolicyViolation]:
        """Check a specific rule against the code"""
        violations = []
        lines = code.split('\n')
        
        # Check pattern-based rules
        violations.extend(self._check_patterns(code, rule, lines))
        
        # Check import restrictions
        if ast_tree:
            violations.extend(self._check_imports(ast_tree, rule))
            violations.extend(self._check_functions(ast_tree, rule))
            violations.extend(self._check_ast_rules(ast_tree, rule))
        
        # Check directory access
        violations.extend(self._check_directory_access(code, rule, lines))
        
        # Check environment variable access
        violations.extend(self._check_env_vars(code, rule, lines))
        
        # Check file operations
        violations.extend(self._check_file_operations(code, rule, lines))
        
        # Apply context conditions
        violations = self._apply_context_conditions(violations, rule, context, file_path)
        
        return violations
    
    def _check_patterns(self, code: str, rule: PolicyRule, lines: List[str]) -> List[PolicyViolation]:
        """Check regex patterns against code"""
        violations = []
        
        for pattern in rule.patterns:
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    if not self._is_exception_allowed(match.group(), rule.allowed_exceptions):
                        violation = PolicyViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            action=rule.action,
                            description=f"{rule.description}: Pattern '{pattern}' matched",
                            line_number=line_num,
                            matched_content=match.group(),
                            suggestion=f"Avoid using pattern '{pattern}' as it violates policy {rule.name}",
                            policy_category=rule.category
                        )
                        violations.append(violation)
        
        return violations
    
    def _check_imports(self, ast_tree: ast.AST, rule: PolicyRule) -> List[PolicyViolation]:
        """Check forbidden imports using AST"""
        violations = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    module_name = alias.name
                    if isinstance(node, ast.ImportFrom) and node.module:
                        module_name = f"{node.module}.{alias.name}"
                    
                    for forbidden in rule.forbidden_imports:
                        if fnmatch.fnmatch(module_name, forbidden):
                            if not self._is_exception_allowed(module_name, rule.allowed_exceptions):
                                violation = PolicyViolation(
                                    rule_id=rule.id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    action=rule.action,
                                    description=f"{rule.description}: Forbidden import '{module_name}'",
                                    line_number=getattr(node, 'lineno', None),
                                    matched_content=module_name,
                                    suggestion=f"Import '{module_name}' is forbidden by policy {rule.name}",
                                    policy_category=rule.category
                                )
                                violations.append(violation)
        
        return violations
    
    def _check_functions(self, ast_tree: ast.AST, rule: PolicyRule) -> List[PolicyViolation]:
        """Check forbidden function calls using AST"""
        violations = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                for forbidden in rule.forbidden_functions:
                    if fnmatch.fnmatch(func_name, forbidden):
                        if not self._is_exception_allowed(func_name, rule.allowed_exceptions):
                            violation = PolicyViolation(
                                rule_id=rule.id,
                                rule_name=rule.name,
                                severity=rule.severity,
                                action=rule.action,
                                description=f"{rule.description}: Forbidden function '{func_name}'",
                                line_number=getattr(node, 'lineno', None),
                                matched_content=func_name,
                                suggestion=f"Function '{func_name}' is forbidden by policy {rule.name}",
                                policy_category=rule.category
                            )
                            violations.append(violation)
        
        return violations
    
    def _check_directory_access(self, code: str, rule: PolicyRule, lines: List[str]) -> List[PolicyViolation]:
        """Check access to forbidden directories"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            for forbidden_dir in rule.forbidden_directories:
                # Check for directory access patterns
                patterns = [
                    rf'[\'\"]{re.escape(forbidden_dir.replace("*", ".*"))}[\'"]',
                    rf'Path\([\'\"]{re.escape(forbidden_dir.replace("*", ".*"))}[\'\"]\)',
                    rf'open\([\'\"]{re.escape(forbidden_dir.replace("*", ".*"))}[\'\"]\)'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if not self._is_exception_allowed(forbidden_dir, rule.allowed_exceptions):
                            violation = PolicyViolation(
                                rule_id=rule.id,
                                rule_name=rule.name,
                                severity=rule.severity,
                                action=rule.action,
                                description=f"{rule.description}: Access to forbidden directory '{forbidden_dir}'",
                                line_number=line_num,
                                matched_content=line.strip(),
                                suggestion=f"Access to directory '{forbidden_dir}' is forbidden by policy {rule.name}",
                                policy_category=rule.category
                            )
                            violations.append(violation)
        
        return violations
    
    def _check_env_vars(self, code: str, rule: PolicyRule, lines: List[str]) -> List[PolicyViolation]:
        """Check access to forbidden environment variables"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            for forbidden_var in rule.forbidden_env_vars:
                patterns = [
                    rf'os\.environ\[[\'\"]{re.escape(forbidden_var.replace("*", ".*"))}[\'\"]\]',
                    rf'getenv\([\'\"]{re.escape(forbidden_var.replace("*", ".*"))}[\'\"]\)',
                    rf'export\s+{re.escape(forbidden_var.replace("*", ".*"))}',
                    rf'setenv\([\'\"]{re.escape(forbidden_var.replace("*", ".*"))}[\'\"]\)'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if not self._is_exception_allowed(forbidden_var, rule.allowed_exceptions):
                            violation = PolicyViolation(
                                rule_id=rule.id,
                                rule_name=rule.name,
                                severity=rule.severity,
                                action=rule.action,
                                description=f"{rule.description}: Access to forbidden environment variable '{forbidden_var}'",
                                line_number=line_num,
                                matched_content=line.strip(),
                                suggestion=f"Environment variable '{forbidden_var}' access is forbidden by policy {rule.name}",
                                policy_category=rule.category
                            )
                            violations.append(violation)
        
        return violations
    
    def _check_file_operations(self, code: str, rule: PolicyRule, lines: List[str]) -> List[PolicyViolation]:
        """Check forbidden file operations"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            for forbidden_op in rule.forbidden_file_operations:
                if forbidden_op.lower() in line.lower():
                    if not self._is_exception_allowed(forbidden_op, rule.allowed_exceptions):
                        violation = PolicyViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            action=rule.action,
                            description=f"{rule.description}: Forbidden file operation '{forbidden_op}'",
                            line_number=line_num,
                            matched_content=line.strip(),
                            suggestion=f"File operation '{forbidden_op}' is forbidden by policy {rule.name}",
                            policy_category=rule.category
                        )
                        violations.append(violation)
        
        return violations
    
    def _check_ast_rules(self, ast_tree: ast.AST, rule: PolicyRule) -> List[PolicyViolation]:
        """Check custom AST-based rules"""
        violations = []
        
        # This is a placeholder for custom AST checks
        # In a real implementation, this would evaluate custom AST expressions
        for ast_check in rule.custom_ast_checks:
            # Custom AST check logic would go here
            pass
        
        return violations
    
    def _apply_context_conditions(self, violations: List[PolicyViolation], rule: PolicyRule,
                                 context: Dict[str, Any], file_path: Optional[str]) -> List[PolicyViolation]:
        """Apply context conditions to filter violations"""
        if not rule.context_conditions:
            return violations
        
        filtered_violations = []
        
        for violation in violations:
            should_include = True
            
            # Check file path conditions
            if 'file_patterns' in rule.context_conditions and file_path:
                patterns = rule.context_conditions['file_patterns']
                if not any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns):
                    should_include = False
            
            # Check environment conditions
            if 'environment' in rule.context_conditions:
                required_env = rule.context_conditions['environment']
                current_env = context.get('environment', 'development')
                if current_env not in required_env:
                    should_include = False
            
            # Check time-based conditions
            if 'time_restrictions' in rule.context_conditions:
                # Time-based restrictions would be implemented here
                pass
            
            if should_include:
                filtered_violations.append(violation)
        
        return filtered_violations
    
    def _get_function_name(self, node: ast.AST) -> str:
        """Extract function name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_function_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        else:
            return ""
    
    def _is_exception_allowed(self, value: str, exceptions: List[str]) -> bool:
        """Check if a value is in the allowed exceptions list"""
        for exception in exceptions:
            if fnmatch.fnmatch(value, exception):
                return True
        return False
    
    def add_rule(self, rule: PolicyRule) -> None:
        """Add a new policy rule"""
        self.rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a policy rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a policy rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False
    
    def get_violations_by_severity(self, severity: PolicySeverity) -> List[PolicyViolation]:
        """Get violations filtered by severity"""
        return [v for v in self.violation_history if v.severity == severity]
    
    def get_violations_by_category(self, category: str) -> List[PolicyViolation]:
        """Get violations filtered by category"""
        return [v for v in self.violation_history if v.policy_category == category]
    
    def export_config(self, output_path: str) -> None:
        """Export current policy configuration to YAML/JSON"""
        config = {
            'global_settings': self.global_settings,
            'policies': {}
        }
        
        for rule_id, rule in self.rules.items():
            config['policies'][rule_id] = {
                'name': rule.name,
                'description': rule.description,
                'severity': rule.severity.value,
                'action': rule.action.value,
                'enabled': rule.enabled,
                'patterns': rule.patterns,
                'forbidden_imports': rule.forbidden_imports,
                'forbidden_functions': rule.forbidden_functions,
                'forbidden_directories': rule.forbidden_directories,
                'forbidden_env_vars': rule.forbidden_env_vars,
                'forbidden_file_operations': rule.forbidden_file_operations,
                'allowed_exceptions': rule.allowed_exceptions,
                'context_conditions': rule.context_conditions,
                'custom_ast_checks': rule.custom_ast_checks,
                'category': rule.category,
                'tags': rule.tags
            }
        
        with open(output_path, 'w') as f:
            if output_path.endswith('.yaml') or output_path.endswith('.yml'):
                yaml.dump(config, f, default_flow_style=False, indent=2)
            else:
                json.dump(config, f, indent=2)
    
    def generate_violation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive violation report"""
        report = {
            'summary': {
                'total_violations': len(self.violation_history),
                'critical': len([v for v in self.violation_history if v.severity == PolicySeverity.CRITICAL]),
                'high': len([v for v in self.violation_history if v.severity == PolicySeverity.HIGH]),
                'medium': len([v for v in self.violation_history if v.severity == PolicySeverity.MEDIUM]),
                'low': len([v for v in self.violation_history if v.severity == PolicySeverity.LOW])
            },
            'violations_by_category': {},
            'violations_by_rule': {},
            'recent_violations': []
        }
        
        # Group by category
        for violation in self.violation_history:
            category = violation.policy_category
            if category not in report['violations_by_category']:
                report['violations_by_category'][category] = []
            report['violations_by_category'][category].append({
                'rule_id': violation.rule_id,
                'rule_name': violation.rule_name,
                'severity': violation.severity.value,
                'description': violation.description
            })
        
        # Group by rule
        for violation in self.violation_history:
            rule_id = violation.rule_id
            if rule_id not in report['violations_by_rule']:
                report['violations_by_rule'][rule_id] = 0
            report['violations_by_rule'][rule_id] += 1
        
        # Recent violations (last 10)
        report['recent_violations'] = [
            {
                'rule_name': v.rule_name,
                'severity': v.severity.value,
                'description': v.description,
                'line_number': v.line_number
            }
            for v in self.violation_history[-10:]
        ]
        
        return report


# Convenience function for direct usage
def analyze_code_with_policies(code: str, 
                              config_path: Optional[str] = None,
                              file_path: Optional[str] = None,
                              context: Optional[Dict[str, Any]] = None) -> List[PolicyViolation]:
    """
    Convenience function to analyze code with policy engine
    
    Args:
        code: Python code to analyze
        config_path: Path to policy configuration file
        file_path: Optional file path for context
        context: Additional context information
        
    Returns:
        List of policy violations
    """
    engine = PolicyEngine(config_path)
    return engine.analyze_code(code, file_path, context) 