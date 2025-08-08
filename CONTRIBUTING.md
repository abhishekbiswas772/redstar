# Contributing to Redstar

Thank you for your interest in contributing to Redstar! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style and Conventions](#code-style-and-conventions)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Development Workflow](#development-workflow)
- [Architecture Guidelines](#architecture-guidelines)

## 🤝 Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to creating a positive environment include:**
- Being respectful and inclusive
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Helping newcomers get started

**Examples of unacceptable behavior include:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information without permission
- Any conduct that could reasonably be considered inappropriate in a professional setting

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Git for version control
- Basic understanding of Redis concepts
- Familiarity with network programming (helpful but not required)

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/redstar.git
   cd redstar
   ```

2. **Set Up Development Environment**
   ```bash
   # No external dependencies needed for core functionality
   # Optional: Set up virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Verify Setup**
   ```bash
   # Start the server
   python redstar_main.py
   
   # In another terminal, run tests
   python run_comprehensive_tests.py
   ```

## 🛠️ Development Setup

### Project Structure Understanding

Before contributing, familiarize yourself with the project structure:

```
redstar/
├── core_datastructures/     # Custom data structures (foundation layer)
├── redstar_core/           # Core Redis functionality (business logic)
├── redstar_commands/       # Command implementations (application layer)
├── redstar_server/         # Server and networking (presentation layer)
├── redstar_client/         # Client implementation (testing utilities)
└── tests/                  # Comprehensive test suites
```

### Key Design Principles

1. **No External Dependencies**: Core functionality must not depend on external libraries
2. **Custom Data Structures**: Use DArray instead of Python lists throughout
3. **Thread Safety**: All shared data must be properly synchronized
4. **RESP Compliance**: All protocol interactions must follow RESP specification
5. **Educational Focus**: Code should be clear and well-documented for learning

## 📝 Contributing Guidelines

### Types of Contributions Welcome

- **Bug Fixes**: Fix issues in existing functionality
- **New Commands**: Implement additional Redis commands
- **Performance Improvements**: Optimize existing implementations
- **Documentation**: Improve code documentation and guides
- **Tests**: Add test coverage for existing or new features
- **Code Quality**: Refactoring and code cleanup

### Before You Start

1. **Check Existing Issues**: Look for existing issues related to your contribution
2. **Create an Issue**: For significant changes, create an issue to discuss first
3. **Small Changes**: For small bug fixes, you can create a PR directly
4. **Breaking Changes**: Must be discussed in an issue before implementation

## 🎨 Code Style and Conventions

### Python Code Style

Follow PEP 8 with these specific guidelines:

```python
# Class names: PascalCase
class RedstarServer:
    pass

# Function and variable names: snake_case
def process_command(client_socket):
    command_data = parse_input()

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 1000
DEFAULT_PORT = 6379

# Private methods: leading underscore
def _internal_helper(self):
    pass
```

### Project-Specific Conventions

1. **Data Structures**
   ```python
   # Use DArray instead of Python lists
   from core_datastructures.dynamic_array import DArray
   
   # Good
   items = DArray()
   items.append("value")
   
   # Avoid
   items = []  # Don't use Python lists in core functionality
   ```

2. **Error Handling**
   ```python
   # Return proper RESP error format
   def handle_command_error(error_message):
       return f"-ERR {error_message}\r\n"
   ```

3. **Thread Safety**
   ```python
   # Use locks for shared data
   with self.data_lock:
       # Modify shared data here
       pass
   ```

### Documentation Standards

```python
def example_function(param1, param2):
    """
    Brief description of what the function does.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
    
    Returns:
        str: Description of return value
    
    Example:
        result = example_function("test", 42)
    """
    pass
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Redis Commands**: Use Redis naming (e.g., `HGETALL`, `LPUSH`)

## 🧪 Testing Requirements

### Testing Philosophy

- **Comprehensive Coverage**: All new features must include tests
- **Edge Cases**: Test boundary conditions and error scenarios
- **Integration Tests**: Test how components work together
- **Protocol Compliance**: Ensure RESP protocol compliance
- **Concurrency Testing**: Test thread safety for shared data

### Test Structure

```python
class MyFeatureTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_assert(self, condition, test_name, expected=None, actual=None):
        """Standard test assertion method"""
        if condition:
            print(f"✅ {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ {test_name}")
            if expected and actual:
                print(f"   Expected: {expected}")
                print(f"   Actual: {actual}")
            self.tests_failed += 1
    
    def test_basic_functionality(self):
        """Test basic feature functionality"""
        # Test implementation here
        pass
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Edge case tests here
        pass
```

### Writing Tests

1. **Create Test File**
   ```bash
   # Name: test_your_feature.py
   # Location: Root directory or tests/ subdirectory
   ```

2. **Include in Test Runner**
   ```python
   # Add to run_comprehensive_tests.py
   ("Your Feature", "test_your_feature.py"),
   ```

3. **Test Categories Required**
   - Basic functionality tests
   - Edge case and error handling tests
   - Protocol compliance tests
   - Thread safety tests (if applicable)

### Running Tests

```bash
# Run all tests
python run_comprehensive_tests.py

# Run specific test
python test_your_feature.py

# Run with verbose output
python test_your_feature.py -v
```

## 🔄 Pull Request Process

### Before Submitting

1. **Run All Tests**
   ```bash
   python run_comprehensive_tests.py
   ```

2. **Check Code Style**
   ```bash
   # Ensure code follows project conventions
   # No external linting tools required, but code should be clean
   ```

3. **Update Documentation**
   - Update CLAUDE.md if needed
   - Add docstrings to new functions
   - Update README.md for significant features

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Edge cases covered
- [ ] Protocol compliance verified

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] Documentation updated if needed
- [ ] No external dependencies added to core functionality
```

### PR Review Process

1. **Automated Checks**: Ensure all tests pass
2. **Code Review**: Maintainers will review code quality and design
3. **Testing**: Verify functionality works as expected
4. **Documentation**: Check that documentation is updated
5. **Merge**: After approval, changes will be merged

## 🐛 Issue Guidelines

### Reporting Bugs

Use this template for bug reports:

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Start server with '...'
2. Send command '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.9.0]
- Server version/commit: [e.g., main branch]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Feature Description**
A clear description of what you want to happen.

**Use Case**
Describe the use case for this feature.

**Redis Compatibility**
Is this feature present in Redis? If so, provide documentation links.

**Implementation Ideas**
Any ideas on how this could be implemented.
```

## 🔧 Development Workflow

### Branching Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: Brief description of changes"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Commit Message Format

```
Type: Brief description of changes

Longer description if needed, explaining what was changed and why.

- Bullet points for multiple changes
- Reference issues with #issue-number
```

**Commit Types:**
- `Add:` New features or functionality
- `Fix:` Bug fixes
- `Update:` Modifications to existing functionality
- `Remove:` Deletion of features or code
- `Docs:` Documentation changes
- `Test:` Adding or modifying tests
- `Refactor:` Code refactoring without functional changes

### Development Best Practices

1. **Small, Focused Commits**: Make commits that do one thing well
2. **Descriptive Messages**: Write clear commit messages
3. **Test Early**: Run tests frequently during development
4. **Document Changes**: Update documentation as you code
5. **Follow Conventions**: Stick to established patterns in the codebase

## 🏗️ Architecture Guidelines

### Adding New Data Structures

1. **Location**: Place in `core_datastructures/`
2. **Base Class**: Consider if a base interface is needed
3. **Memory Management**: Implement proper cleanup
4. **Thread Safety**: Add locking if needed for concurrent access
5. **Testing**: Comprehensive test coverage required

Example structure:
```python
class MyDataStructure:
    """
    Brief description of the data structure.
    
    This data structure implements... and is used for...
    """
    
    def __init__(self):
        self._data = DArray()
        self._lock = threading.RLock()
    
    def add_item(self, item):
        """Add an item to the data structure."""
        with self._lock:
            self._data.append(item)
    
    def get_size(self):
        """Get the number of items."""
        with self._lock:
            return len(self._data)
```

### Adding New Commands

1. **Command Processor**: Add to `redstar_commands/command_processor.py`
2. **Protocol Compliance**: Ensure proper RESP format responses
3. **Error Handling**: Handle all error conditions
4. **Documentation**: Document command behavior
5. **Testing**: Test all variations and edge cases

Example command implementation:
```python
def handle_mycommand(self, args):
    """
    Handle MYCOMMAND key [value]
    
    Args:
        args (DArray): Command arguments
    
    Returns:
        str: RESP formatted response
    """
    if len(args) < 1:
        return "-ERR wrong number of arguments for 'MYCOMMAND' command\r\n"
    
    key = args[0]
    
    # Implementation here
    
    return "+OK\r\n"
```

### Protocol Extensions

When extending the RESP protocol parser:

1. **Backward Compatibility**: Don't break existing functionality
2. **Error Handling**: Graceful handling of malformed input
3. **Performance**: Consider impact on parsing speed
4. **Testing**: Comprehensive protocol compliance testing

## 🎯 Areas Needing Contribution

### High Priority
- Performance optimizations for data structures
- Additional Redis commands implementation
- Memory usage optimizations
- Better error messages and handling

### Medium Priority
- Enhanced pub/sub pattern matching
- Additional data types (streams, bitmaps)
- Server configuration options
- Connection pooling improvements

### Low Priority
- Advanced Redis features (lua scripting, modules)
- Clustering support (educational implementation)
- Persistence mechanisms
- Administrative commands

## 📚 Resources

### Learning Resources
- [Redis Documentation](https://redis.io/documentation)
- [RESP Protocol Specification](https://redis.io/docs/reference/protocol-spec/)
- [Redis Commands Reference](https://redis.io/commands)

### Development Tools
- Python 3.7+ documentation
- Git documentation
- Threading in Python guides

## ❓ Getting Help

### Before Asking for Help
1. Check existing documentation (README.md, CLAUDE.md)
2. Search existing issues and discussions
3. Review the codebase for similar implementations
4. Run the comprehensive test suite to understand current functionality

### Where to Get Help
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Comments**: Many functions have detailed docstrings

### When Asking for Help
- Provide clear, specific questions
- Include relevant code snippets
- Describe what you've already tried
- Specify your development environment

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Git commit history
- Release notes for significant contributions

Thank you for contributing to Redstar! Your efforts help make this educational project better for everyone.