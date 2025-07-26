# Security Policy

## Supported Versions

We actively support the following versions of SuperMini:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in SuperMini, please follow these steps:

### 1. **Do Not** Create a Public Issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send your vulnerability report to:
- **Email**: security@supermini.app (if available)
- **GitHub Security Advisory**: Use the ["Report a vulnerability"](https://github.com/MoRohn/supermini/security/advisories) feature

### 3. Include Details

Please include as much information as possible:
- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Proof of Concept**: If possible, include a minimal proof of concept
- **Environment**: Version, OS, Python version, dependencies
- **Suggested Fix**: If you have ideas for fixing the issue

### 4. Response Timeline

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 7 days
- **Regular Updates**: We will provide regular updates on our progress
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of SuperMini
2. **Secure API Keys**: 
   - Never commit API keys to version control
   - Use environment variables or secure config files
   - Regularly rotate your API keys
3. **Network Security**: 
   - Use HTTPS for all API communications
   - Be cautious when processing untrusted files
4. **File Permissions**: 
   - Ensure proper file permissions for generated outputs
   - Be careful with script execution permissions

### For Developers

1. **Input Validation**: 
   - Validate all user inputs
   - Sanitize file paths and names
   - Check file types and sizes
2. **API Security**: 
   - Use secure authentication methods
   - Implement rate limiting
   - Validate API responses
3. **Dependencies**: 
   - Keep dependencies updated
   - Monitor for security advisories
   - Use security scanning tools
4. **Code Review**: 
   - Review all code changes for security implications
   - Use static analysis tools
   - Test security-related functionality

## Security Features

SuperMini includes several security features:

### 1. **Local-First Processing**
- Most processing can be done locally with Ollama
- Optional cloud API usage only when configured

### 2. **Secure File Handling**
- Proper file path validation
- Safe temporary file creation
- Automatic cleanup of temporary files

### 3. **API Key Protection**
- Environment variable support
- Secure configuration storage
- No hardcoded credentials

### 4. **Autonomous Safety**
- Safe operation validation
- Restricted command execution
- User confirmation for high-risk actions

## Known Security Considerations

### 1. **AI Model Outputs**
- AI-generated code should be reviewed before execution
- Be cautious with automatically generated scripts
- Validate AI suggestions for security implications

### 2. **File Processing**
- Processing untrusted files may pose risks
- Large files can cause resource exhaustion
- Some file types may contain embedded code

### 3. **Network Communications**
- API communications are encrypted (HTTPS)
- Local Ollama connections use localhost
- No telemetry data is collected by default

## Vulnerability Disclosure Policy

When we receive a security vulnerability report:

1. **Confirmation**: We will confirm the vulnerability and its impact
2. **Development**: We will develop a fix and test it thoroughly
3. **Coordination**: We will coordinate the release with the reporter
4. **Disclosure**: We will publicly disclose the vulnerability after the fix is released
5. **Credit**: We will provide appropriate credit to the reporter (unless they prefer to remain anonymous)

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 2.0.1 → 2.0.2)
- Clearly marked in the changelog
- Announced through GitHub releases
- Documented with severity and impact assessment

## Bug Bounty

Currently, we do not have a formal bug bounty program. However, we greatly appreciate security researchers who responsibly disclose vulnerabilities and will:
- Provide public recognition (if desired)
- Include contributors in our security acknowledgments
- Consider featuring contributions in our project documentation

## Security Acknowledgments

We thank the following security researchers for their contributions:

<!-- This section will be updated as security reports are received and resolved -->

*No security issues have been reported yet. Be the first to help make SuperMini more secure!*

## Questions

If you have questions about this security policy, please:
- Create a public issue for general security questions
- Use private reporting channels for potential vulnerabilities
- Check our documentation for security best practices

## Legal

By reporting security vulnerabilities, you agree to:
- Give us reasonable time to fix the issue before public disclosure
- Not exploit the vulnerability beyond what's necessary for verification
- Not access or modify user data without explicit permission
- Follow responsible disclosure practices

We commit to:
- Respond to reports in a timely manner
- Keep your information confidential
- Provide credit for your discovery (if desired)
- Not pursue legal action for good-faith security research